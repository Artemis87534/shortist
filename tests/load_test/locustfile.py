from locust import HttpUser, task

class ShortistUser(HttpUser):
    @task
    def create_short_link(self):
        self.client.post("/links/shorten", json={
            "original_url": "https://example.com"
        })

    @task(3)
    def access_short_link(self):
        self.client.get("/links/abc123")