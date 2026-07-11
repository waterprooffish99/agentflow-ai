import json
import asyncio
from typing import AsyncGenerator

class SSEService:
    @staticmethod
    async def stream_ai_response(
        response_generator: AsyncGenerator[str, None]
    ) -> AsyncGenerator[str, None]:
        """Stream AI response tokens as SSE events."""
        try:
            async for token in response_generator:
                if token:
                    data = json.dumps({"token": token})
                    yield f"data: {data}\n\n"
                else:
                    # Keepalive frame to reduce idle proxy disconnects.
                    yield ": keepalive\n\n"
                await asyncio.sleep(0)
            yield "data: [DONE]\n\n"
        except asyncio.CancelledError:
            # Client disconnected; terminate stream without error cascade.
            return
