from locust import HttpUser, task, between
import random

def random_url():
    return f"https://example{random.randint(1, 10000)}.com"

class LinkShortenerUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def create_link(self):
        self.client.post("/links/shorten", json={"original_url": random_url(), "expire_at": "2030-01-01T00:00:00+00:00"})

    @task(1)
    def redirect_link(self):
        self.client.get("/abc123", allow_redirects=False)