import uuid
from locust import HttpUser, task, between

class AgentFlowUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Setup a dummy tenant or use existing one
        self.tenant_id = "00000000-0000-0000-0000-000000000001" # Replace with real dummy
        self.conversation_id = str(uuid.uuid4())

    @task(3)
    def health_check(self):
        self.client.get("/health")

    @task(2)
    def chat_message(self):
        self.client.post("/api/v1/chat/message", json={
            "conversation_id": self.conversation_id,
            "tenant_id": self.tenant_id,
            "content": "Hello, I would like to book an appointment"
        })

    @task(1)
    def get_services(self):
        # This requires auth, so we might need a test token
        pass
