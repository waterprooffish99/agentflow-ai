import time
import uuid
from locust import HttpUser, task, between, events

class EnduranceUser(HttpUser):
    wait_time = between(2, 5)
    
    def on_start(self):
        # We assume a set of pre-provisioned tenants for endurance testing
        self.tenant_id = "00000000-0000-0000-0000-000000000001" 
        self.conversation_id = str(uuid.uuid4())

    @task(5)
    def chat_flow(self):
        """Simulate a sustained chat conversation."""
        self.client.post("/api/v1/chat/message", json={
            "conversation_id": self.conversation_id,
            "tenant_id": self.tenant_id,
            "content": "Sustainability test message"
        }, name="/chat/message [Endurance]")

    @task(1)
    def health_heartbeat(self):
        self.client.get("/health/ready", name="/health/ready [Endurance]")

    @task(2)
    def check_billing(self):
        # Requires auth in real world, using public check for now if available
        pass

@events.init_command_line_parser.add_listener
def _(parser):
    parser.add_argument("--endurance-mode", action="store_true", help="Enable endurance metrics")

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    if exception:
        print(f"Request {name} failed: {exception}")
