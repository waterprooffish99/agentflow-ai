import uuid
from datetime import datetime, date
from unittest.mock import AsyncMock, MagicMock
import pytest
from app.services.ai_orchestrator_service import AIOrchestratorService

@pytest.mark.asyncio
async def test_check_availability_tool_formats_slots_correctly() -> None:
    # Setup orchestrator service with mocked db and services
    db = MagicMock()
    svc = AIOrchestratorService(db=db)
    
    # Mock availability service
    svc.availability_service = MagicMock()
    start_dt = datetime(2026, 6, 20, 15, 0)
    end_dt = datetime(2026, 6, 20, 15, 30)
    # get_available_slots returns List[Tuple[datetime, datetime]]
    svc.availability_service.get_available_slots = AsyncMock(return_value=[(start_dt, end_dt)])
    
    # Mock tool call object
    tool_call = MagicMock()
    tool_call.function.name = "check_availability"
    tool_call.function.arguments = '{"start_date": "2026-06-20", "end_date": "2026-06-20"}'
    
    tenant_id = uuid.uuid4()
    conversation_id = uuid.uuid4()
    context = {}
    
    result = await svc._handle_tool_call(tool_call, conversation_id, tenant_id, context)
    
    assert result == {"available_slots": ["2026-06-20T15:00:00"]}
    svc.availability_service.get_available_slots.assert_called_once_with(
        tenant_id, date(2026, 6, 20), date(2026, 6, 20)
    )
