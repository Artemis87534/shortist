from locust import HttpUser, task, between
import uuid


class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.email = f"user-{uuid.uuid4().hex[:6]}@example.com"
        self.password = "string"

        self.client.post("/auth/register", json={
            "email": self.email,
            "password": self.password,
            "is_active": True,
            "is_superuser": False,
            "is_verified": False
        })

        login = self.client.post("/auth/jwt/login", data={
            "username": self.email,
            "password": self.password,
            "grant_type": "password"
        })
        cookie = login.headers.get("set-cookie")
        if cookie:
            self.client.headers.update({"cookie": cookie})

    @task
    def create_link(self):
        self.client.post("/links/shorten", json={
            "original_url": "https://example.com",
            "custom_alias": f"locust-{uuid.uuid4().hex[:6]}",
            "expire_at": "2025-12-31T23:59:59+00:00"
        })

    @task
    def search_links(self):
        self.client.get("/links/search/", params={"original_url": "https://example.com"})

    @task
    def get_stats(self):
        self.client.get("/links/doesnotexist/stats")