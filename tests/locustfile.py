from locust import HttpUser, task, between

class ApiUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Логинимся и получаем токен
        response = self.client.post("/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def get_dialogs(self):
        self.client.get("/api/dialogs/", headers=self.headers)
    
    @task(2)
    def get_knowledge(self):
        self.client.get("/api/knowledge/", headers=self.headers)
    
    @task(1)
    def get_stats(self):
        self.client.get("/api/dialogs/stats/summary", headers=self.headers)
