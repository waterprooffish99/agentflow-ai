from typing import List, Dict, Any

def get_lead_qualification_tool() -> Dict[str, Any]:
    """Tool for capturing lead information."""
    return {
        "type": "function",
        "function": {
            "name": "capture_lead_info",
            "description": "Capture structured information from the lead such as name, email, phone, service interest, budget, and urgency.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Customer full name"},
                    "email": {"type": "string", "description": "Customer email address"},
                    "phone": {"type": "string", "description": "Customer phone number"},
                    "service": {"type": "string", "description": "The service they are interested in"},
                    "budget": {"type": "string", "description": "Customer budget range"},
                    "urgency": {
                        "type": "string", 
                        "enum": ["low", "medium", "high", "urgent"],
                        "description": "How quickly they need the service"
                    },
                },
                "required": []
            }
        }
    }

def get_faq_search_tool() -> Dict[str, Any]:
    """Tool for searching the knowledge base."""
    return {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "Search for answers to specific customer questions about the business, services, pricing, and policies.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query or question"}
                },
                "required": ["query"]
            }
        }
    }

def get_check_availability_tool() -> Dict[str, Any]:
    """Tool for checking available slots."""
    return {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check for available appointment slots on a specific date or date range.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "Start date in YYYY-MM-DD format"},
                    "end_date": {"type": "string", "description": "End date in YYYY-MM-DD format (optional)"},
                    "service_type": {"type": "string", "description": "Type of service requested"}
                },
                "required": ["start_date"]
            }
        }
    }

def get_create_booking_tool() -> Dict[str, Any]:
    """Tool for creating a booking."""
    return {
        "type": "function",
        "function": {
            "name": "create_booking",
            "description": "Create a new appointment booking for a customer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_time": {"type": "string", "description": "Appointment start time in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)"},
                    "service_type": {"type": "string", "description": "Type of service to book"},
                    "notes": {"type": "string", "description": "Optional notes from the customer"}
                },
                "required": ["start_time", "service_type"]
            }
        }
    }

def get_available_tools() -> List[Dict[str, Any]]:
    return [
        get_lead_qualification_tool(),
        get_faq_search_tool(),
        get_check_availability_tool(),
        get_create_booking_tool(),
        get_business_services_tool(),
        get_escalate_to_human_tool(),
    ]

def get_business_services_tool() -> Dict[str, Any]:
    """Tool for fetching available services."""
    return {
        "type": "function",
        "function": {
            "name": "get_business_services",
            "description": "Get a list of services offered by the business including descriptions and prices.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }

def get_escalate_to_human_tool() -> Dict[str, Any]:
    """Tool for escalating to a human staff member."""
    return {
        "type": "function",
        "function": {
            "name": "escalate_to_human",
            "description": "Escalate the conversation to a human staff member when the AI cannot help or the customer is frustrated.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {"type": "string", "description": "The reason for escalation"}
                },
                "required": ["reason"]
            }
        }
    }
