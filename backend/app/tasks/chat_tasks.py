import asyncio
import logging
import uuid
import threading
from typing import Dict, Any

from app.core.celery import celery_app
from app.core.database import async_session_maker, engine
from app.services.ai_orchestrator_service import AIOrchestratorService

logger = logging.getLogger(__name__)


def run_async_in_new_loop(coro) -> Any:
    """Run an async coroutine inside a new event loop on a separate thread."""
    result = None
    exception = None

    def worker():
        nonlocal result, exception
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(coro)
        except Exception as e:
            exception = e
        finally:
            loop.close()

    thread = threading.Thread(target=worker)
    thread.start()
    thread.join()

    if exception:
        raise exception
    return result


def run_async_task(coro) -> Any:
    """Run an async coroutine safely.
    
    In a standard Celery worker process, there is no running event loop, so we run the
    task directly on the main thread to align with SQLAlchemy's connection pooling.
    During tests (eager execution), a loop is already running on the calling thread, so
    we run the task in a new thread.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # Safe to run directly in uvicorn/celery worker thread (production)
        return asyncio.run(coro)
    else:
        # Running loop exists (pytest eager execution)
        return run_async_in_new_loop(coro)


@celery_app.task(name="app.tasks.chat_tasks.process_chat_message")
def process_chat_message(
    conversation_id_str: str,
    tenant_id_str: str,
    content: str,
) -> Dict[str, Any]:
    """Process a conversational turn in a background Celery task."""
    conversation_id = uuid.UUID(conversation_id_str)
    tenant_id = uuid.UUID(tenant_id_str)
    return run_async_task(_process_chat_message_async(conversation_id, tenant_id, content))


async def _process_chat_message_async(
    conversation_id: uuid.UUID,
    tenant_id: uuid.UUID,
    content: str,
) -> Dict[str, Any]:
    try:
        async with async_session_maker() as db:
            orchestrator = AIOrchestratorService(db)
            result = await orchestrator.handle_message(
                conversation_id=conversation_id,
                tenant_id=tenant_id,
                content=content,
            )
            # Convert UUID to string for JSON serialization compatibility in Celery result backend
            if "conversation_id" in result:
                result["conversation_id"] = str(result["conversation_id"])
            return result
    finally:
        # Crucial: dispose connection pool to clear cached connections bound to closed event loops
        await engine.dispose()
