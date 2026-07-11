import json
import logging
import uuid
import time
from typing import Dict, Any, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Tenant, BusinessProfile, Service, AIConfiguration, MessageRole, ConversationStatus, Conversation, Customer
from app.services.conversation_service import ConversationService
from app.services.memory_service import MemoryService
from app.services.lead_qualification_service import LeadQualificationService
from app.services.faq_retrieval_service import FAQRetrievalService
from app.services.customer_memory_service import CustomerMemoryService
from app.services.ai_service import AIService
from app.services.availability_engine_service import AvailabilityEngineService
from app.services.booking_service import BookingService
from app.agents.prompts import get_system_prompt
from app.agents.tools import get_available_tools
from datetime import datetime, date, timedelta, timezone

logger = logging.getLogger(__name__)

class AIOrchestratorService:
    MAX_TOOL_TURNS = 5

    def __init__(self, db: AsyncSession):
        self.db = db
        self.conversation_service = ConversationService(db)
        self.memory_service = MemoryService(db)
        self.lead_service = LeadQualificationService(db)
        self.faq_service = FAQRetrievalService(db)
        self.customer_memory = CustomerMemoryService(db)
        self.ai_service = AIService()
        self.availability_service = AvailabilityEngineService(db)
        self.booking_service = BookingService(db)

    async def start_conversation(self, tenant_id: uuid.UUID, customer_id: Optional[uuid.UUID] = None) -> Dict[str, Any]:
        """Initialize a conversation and return the first AI message."""
        conversation = await self.conversation_service.create_conversation(tenant_id, customer_id)
        await self.db.commit()
        
        return {
            "conversation_id": conversation.id,
            "status": conversation.status,
        }

    async def handle_message(
        self, 
        conversation_id: uuid.UUID, 
        tenant_id: uuid.UUID, 
        content: str
    ) -> Dict[str, Any]:
        """The main orchestration loop for a user message."""
        t_start = time.perf_counter()
        db_time = 0.0
        ai_time = 0.0
        tool_time = 0.0
        
        # 1. Load Conversation & Context
        t_db_start = time.perf_counter()
        conversation = await self.conversation_service.get_conversation(conversation_id, tenant_id=tenant_id)
        db_time += time.perf_counter() - t_db_start

        if not conversation:
            raise ValueError("Conversation not found")
        if conversation.tenant_id != tenant_id:
            raise ValueError("Tenant isolation violation")
        
        # 2. Persist User Message
        t_db_start = time.perf_counter()
        await self.conversation_service.add_message(
            conversation_id, tenant_id, MessageRole.USER, content
        )
        db_time += time.perf_counter() - t_db_start

        # Check sentiment budget escalation first
        from app.agents.escalation import analyze_sentiment_is_negative, escalate_conversation
        if analyze_sentiment_is_negative(content):
            await escalate_conversation(self.db, conversation_id, "Negative sentiment detected")
            escalation_msg = "I understand your frustration. I am escalating this conversation to a human representative who will assist you shortly."
            await self.conversation_service.add_message(
                conversation_id, tenant_id, MessageRole.ASSISTANT, escalation_msg
            )
            from app.models.correction import Correction
            correction = Correction(
                tenant_id=tenant_id,
                conversation_id=conversation_id,
                ai_draft_message=escalation_msg,
                was_edited=None
            )
            self.db.add(correction)
            await self.db.commit()
            return {
                "content": escalation_msg,
                "role": "assistant",
                "conversation_id": conversation_id
            }

        # 3. Load Context (Tenant + Customer)
        t_db_start = time.perf_counter()
        tenant_context = await self._get_tenant_context(tenant_id)
        db_time += time.perf_counter() - t_db_start

        customer_context = ""
        if conversation.customer_id:
            t_db_start = time.perf_counter()
            customer_context = await self.customer_memory.get_customer_context(conversation.customer_id)
            db_time += time.perf_counter() - t_db_start
        
        # 4. Prepare AI Messages (System + History Window)
        t_db_start = time.perf_counter()
        history = await self.conversation_service.list_messages(conversation_id, tenant_id=tenant_id)
        db_time += time.perf_counter() - t_db_start
        
        # WINDOWING: Take last 10 messages
        history_window = history[-10:]
        
        system_content = get_system_prompt(tenant_context)
        if customer_context:
            system_content += f"\n\nCUSTOMER CONTEXT:\n{customer_context}"
            
        # Include current datetime context to help the AI calculate relative dates (e.g. "this Saturday") correctly
        current_time_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        system_content += f"\n\nCURRENT DATE & TIME: {current_time_str}"
            
        ai_messages = [{"role": "system", "content": system_content}]
        for msg in history_window:
            role = msg.role.value if hasattr(msg.role, "value") else msg.role
            ai_messages.append({"role": role, "content": msg.content})

        # 5. Multi-turn Orchestration Loop (Tool Feedback)
        tools = get_available_tools()
        turn_count = 0
        final_content = ""
        
        while turn_count < self.MAX_TOOL_TURNS:
            t_ai_start = time.perf_counter()
            response = await self.ai_service.chat_completion(
                messages=ai_messages,
                tenant_id=tenant_id,
                tier=tenant_context.get("subscription_tier"),
                model=tenant_context.get("model_name"),
                temperature=tenant_context.get("temperature", 0.7),
                tools=tools
            )
            ai_time += time.perf_counter() - t_ai_start

            ai_msg = response.choices[0].message
            
            # ULTIMATE FIX: Ensure everything is a pure serializable dict
            msg_dict = {"role": "assistant", "content": ai_msg.content or ""}
            if ai_msg.tool_calls:
                msg_dict["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in ai_msg.tool_calls
                ]
            
            ai_messages.append(msg_dict) 
            
            if not ai_msg.tool_calls:
                final_content = ai_msg.content or ""
                break
                
            # Handle Tool Calls
            for tool_call in ai_msg.tool_calls:
                # Check permission budget for this action
                from app.agents.escalation import check_action_permitted
                is_permitted = await check_action_permitted(self.db, tenant_id, conversation_id, tool_call.function.name)
                if not is_permitted:
                    escalation_msg = "This request requires manager approval. I am escalating this to a human representative to assist you."
                    await self.conversation_service.add_message(
                        conversation_id, tenant_id, MessageRole.ASSISTANT, escalation_msg
                    )
                    from app.models.correction import Correction
                    correction = Correction(
                        tenant_id=tenant_id,
                        conversation_id=conversation_id,
                        ai_draft_message=escalation_msg,
                        was_edited=None
                    )
                    self.db.add(correction)
                    await self.db.commit()
                    return {
                        "content": escalation_msg,
                        "role": "assistant",
                        "conversation_id": conversation_id
                    }

                t_tool_start = time.perf_counter()
                result = await self._handle_tool_call(
                    tool_call, conversation_id, tenant_id, tenant_context
                )
                tool_time += time.perf_counter() - t_tool_start
                ai_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": json.dumps(result)
                })
            
            turn_count += 1

        # 6. Persist AI Message (Final Answer)
        content_out = final_content or "I'm sorry, I'm having trouble processing that right now."
        t_db_start = time.perf_counter()
        await self.conversation_service.add_message(
            conversation_id, tenant_id, MessageRole.ASSISTANT, content_out
        )

        # Create Correction row for the AI draft (was_edited=None means pending review)
        from app.models.correction import Correction
        correction = Correction(
            tenant_id=tenant_id,
            conversation_id=conversation_id,
            ai_draft_message=content_out,
            was_edited=None
        )
        self.db.add(correction)

        await self.db.commit()
        db_time += time.perf_counter() - t_db_start
        
        t_total = time.perf_counter() - t_start
        logger.info(
            f"=== Chat Timing Breakdown ===\n"
            f"Database: {db_time:.4f} seconds\n"
            f"AI model call: {ai_time:.4f} seconds\n"
            f"Tool calls: {tool_time:.4f} seconds\n"
            f"Total: {t_total:.4f} seconds"
        )
        
        return {
            "content": content_out,
            "role": "assistant",
            "conversation_id": conversation_id
        }

    async def _get_tenant_context(self, tenant_id: uuid.UUID) -> Dict[str, Any]:
        """Fetch all relevant data to build the AI's world view."""
        tenant_result = await self.db.execute(select(Tenant).where(Tenant.id == tenant_id))
        tenant = tenant_result.scalar_one()
        
        profile_result = await self.db.execute(select(BusinessProfile).where(BusinessProfile.tenant_id == tenant_id))
        profile = profile_result.scalar_one_or_none()
        
        ai_config_result = await self.db.execute(select(AIConfiguration).where(AIConfiguration.tenant_id == tenant_id))
        ai_config = ai_config_result.scalar_one_or_none()

        return {
            "business_name": tenant.business_name,
            "subscription_tier": tenant.subscription_tier,
            "business_description": profile.description if profile else "",
            "personality_context": ai_config.personality_traits if ai_config else "Professional",
            "temperature": ai_config.temperature if ai_config else 0.7,
            "model_name": ai_config.model_name if ai_config else "openai/gpt-3.5-turbo",
        }

    async def _handle_tool_call(
        self, 
        tool_call: Any, 
        conversation_id: uuid.UUID, 
        tenant_id: uuid.UUID,
        context: Dict[str, Any]
    ) -> Any:
        """Execute backend logic based on AI tool selection."""
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        
        logger.info(f"AI Tool Call: {name} with args {args}")

        if name == "capture_lead_info":
            conv = await self.conversation_service.get_conversation(conversation_id)
            if conv:
                if not conv.customer_id:
                    name_val = args.get("name") or "Interested Lead"
                    email = args.get("email")
                    phone = args.get("phone")
                    
                    # Try to find existing customer by email or phone
                    customer = None
                    if email:
                        cust_res = await self.db.execute(
                            select(Customer).where(Customer.tenant_id == tenant_id, Customer.email == email)
                        )
                        customer = cust_res.scalar_one_or_none()
                    if not customer and phone:
                        cust_res = await self.db.execute(
                            select(Customer).where(Customer.tenant_id == tenant_id, Customer.phone == phone)
                        )
                        customer = cust_res.scalar_one_or_none()
                        
                    if not customer:
                        customer = Customer(
                            tenant_id=tenant_id,
                            name=name_val,
                            email=email,
                            phone=phone
                        )
                        self.db.add(customer)
                        await self.db.flush()
                    else:
                        # Update customer fields if they were provided and not already set
                        updated = False
                        if name_val and name_val != "Interested Lead" and customer.name == "Interested Lead":
                            customer.name = name_val
                            updated = True
                        if email and not customer.email:
                            customer.email = email
                            updated = True
                        if phone and not customer.phone:
                            customer.phone = phone
                            updated = True
                        if updated:
                            await self.db.flush()
                        
                    conv.customer_id = customer.id
                    await self.db.flush()
                    
                lead = await self.lead_service.get_or_create_lead(tenant_id, conv.customer_id, conversation_id)
                for field, value in args.items():
                    await self.lead_service.capture_field(tenant_id, lead.id, conversation_id, field, value)
                    if field in ["budget", "service"]:
                        await self.customer_memory.update_preferences(conv.customer_id, {field: value})
                return {"status": "success", "message": "Lead info captured"}

        elif name == "search_knowledge_base":
            query = args.get("query")
            if query:
                results = await self.faq_service.search_faqs(tenant_id, query)
                return {"results": [r.answer for r in results] if results else "No information found."}

        elif name == "check_availability":
            start_date_str = args.get("start_date")
            end_date_str = args.get("end_date") or start_date_str
            try:
                start_date = date.fromisoformat(start_date_str)
                end_date = date.fromisoformat(end_date_str)
                slots = await self.availability_service.get_available_slots(tenant_id, start_date, end_date)
                return {"available_slots": [s[0].isoformat() for s in slots]}
            except ValueError as e:
                return {"error": "Invalid date format"}

        elif name == "create_booking":
            start_time_str = args.get("start_time")
            service_type = args.get("service_type")
            try:
                start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
                end_time = start_time + timedelta(minutes=30)
                
                conv = await self.conversation_service.get_conversation(conversation_id)
                if not conv:
                    return {"status": "error", "message": "Conversation not found"}
                    
                if not conv.customer_id:
                    return {
                        "status": "error", 
                        "message": "No customer is associated with this conversation. Please collect customer name, phone or email, and call capture_lead_info first."
                    }
                    
                appointment = await self.booking_service.create_appointment(
                    tenant_id=tenant_id,
                    customer_id=conv.customer_id,
                    service_type=service_type,
                    start_time=start_time,
                    end_time=end_time,
                    lead_id=conv.lead_id,
                    actor_type="ai"
                )
                return {"status": "success", "booking_id": str(appointment.id)}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        elif name == "get_business_services":
            services_result = await self.db.execute(
                select(Service).where(Service.tenant_id == tenant_id, Service.is_active == True)
            )
            services = services_result.scalars().all()
            return {"services": [{"name": s.name, "description": s.description, "price": str(s.price)} for s in services]}

        elif name == "escalate_to_human":
            reason = args.get("reason", "No reason provided")
            result = await self.db.execute(select(Conversation).where(Conversation.id == conversation_id))
            conversation = result.scalar_one_or_none()
            if conversation:
                conversation.status = ConversationStatus.ESCALATED
                conversation.escalated_reason = reason
                return {"status": "success", "message": "Conversation escalated to human staff."}
            return {"status": "error", "message": "Conversation not found"}

        return {"error": "Unknown tool"}
