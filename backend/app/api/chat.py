import uuid
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from celery.result import AsyncResult

from app.api.deps import get_db
from app.core.sanitization import sanitize_text
from app.services.ai_orchestrator_service import AIOrchestratorService
from app.services.sse_service import SSEService
from app.tasks.chat_tasks import process_chat_message
from app.core.celery import celery_app

router = APIRouter(prefix="/chat", tags=["chat"])

logger = logging.getLogger(__name__)

# Track eager task results in-memory during test runs
_eager_results = {}


def _get_task_result(task_id: str) -> AsyncResult:
    if celery_app.conf.task_always_eager and task_id in _eager_results:
        return _eager_results[task_id]
    return AsyncResult(task_id, app=celery_app)


class ChatStartRequest(BaseModel):
    customer_id: Optional[uuid.UUID] = None
    tenant_id: uuid.UUID


class ChatMessageRequest(BaseModel):
    conversation_id: uuid.UUID
    tenant_id: uuid.UUID
    content: str = Field(min_length=1, max_length=4000)


class ChatMessageAcceptedResponse(BaseModel):
    task_id: str
    conversation_id: uuid.UUID
    status: str = "queued"


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[dict] = None


@router.post("/start")
async def start_chat(data: ChatStartRequest, db: AsyncSession = Depends(get_db)):
    orchestrator = AIOrchestratorService(db)
    return await orchestrator.start_conversation(data.tenant_id, data.customer_id)


@router.post("/message", response_model=ChatMessageAcceptedResponse, status_code=status.HTTP_202_ACCEPTED)
async def send_message(data: ChatMessageRequest):
    try:
        # Enqueue Celery task
        task = process_chat_message.delay(
            str(data.conversation_id),
            str(data.tenant_id),
            sanitize_text(data.content),
        )
        if celery_app.conf.task_always_eager:
            _eager_results[task.id] = task
        return ChatMessageAcceptedResponse(
            task_id=task.id,
            conversation_id=data.conversation_id,
            status="queued"
        )
    except Exception as exc:
        logger.exception("Failed to enqueue chat message task")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enqueue chat message: {str(exc)}",
        ) from exc


@router.post("/stream")
async def stream_message(data: ChatMessageRequest):
    try:
        # Enqueue background Celery task
        task = process_chat_message.delay(
            str(data.conversation_id),
            str(data.tenant_id),
            sanitize_text(data.content),
        )
        if celery_app.conf.task_always_eager:
            _eager_results[task.id] = task
    except Exception as exc:
        logger.exception("Failed to enqueue chat message task for stream")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enqueue chat message: {str(exc)}",
        ) from exc

    async def event_generator():
        import asyncio
        res = _get_task_result(task.id)
        while not res.ready():
            yield ""  # Yield empty to trigger keepalive check in SSEService
            await asyncio.sleep(0.1)
        
        if res.failed():
            logger.error(f"Celery task {task.id} failed: {res.result}")
            yield "I'm sorry, I'm having trouble processing that right now."
        else:
            result = res.result
            yield result.get("content", "")

    return StreamingResponse(
        SSEService.stream_ai_response(event_generator()), media_type="text/event-stream"
    )


@router.get("/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    res = _get_task_result(task_id)
    if res.failed():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Task failed: {str(res.result)}",
        )
    return TaskStatusResponse(
        task_id=task_id,
        status=res.status,
        result=res.result if res.ready() else None
    )
