import asyncio
import httpx
import sys

async def main():
    tenant_id = "b8e65ec3-792a-4566-aefb-0ff1b3764d15"
    headers = {"X-API-Key": "change-me"}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Start conversation
        print("Starting conversation...")
        res = await client.post(
            "http://localhost:8000/api/v1/chat/start",
            json={"tenant_id": tenant_id},
            headers=headers
        )
        if res.status_code != 200:
            print(f"Failed to start conversation: {res.status_code} - {res.text}")
            sys.exit(1)
        
        convo_id = res.json()["conversation_id"]
        print(f"Conversation started. Convo ID: {convo_id}")
        
        # 2. Send chat message
        print("Sending message...")
        res = await client.post(
            "http://localhost:8000/api/v1/chat/message",
            json={
                "conversation_id": convo_id,
                "tenant_id": tenant_id,
                "content": "Do you have Balochi bridal dresses?"
            },
            headers=headers
        )
        if res.status_code != 202:
            print(f"Failed to enqueue message: {res.status_code} - {res.text}")
            sys.exit(1)
            
        task_id = res.json()["task_id"]
        print(f"Message enqueued. Task ID: {task_id}")
        
        # 3. Poll task status
        print("Polling task result...")
        for _ in range(30):
            res = await client.get(
                f"http://localhost:8000/api/v1/chat/task/{task_id}",
                headers=headers
            )
            if res.status_code == 200:
                data = res.json()
                print(f"Task status: {data['status']}")
                if data["status"] == "SUCCESS":
                    print("\n--- AI Response ---")
                    print(data["result"]["content"])
                    print("-------------------\n")
                    return
                elif data["status"] == "FAILURE":
                    print(f"Task failed: {data}")
                    sys.exit(1)
            else:
                print(f"Failed to poll task: {res.status_code} - {res.text}")
                sys.exit(1)
            await asyncio.sleep(1.0)
            
        print("Timed out waiting for task completion")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
