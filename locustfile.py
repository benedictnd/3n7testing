from locust import HttpUser, task, between
import random
from datetime import datetime, timedelta

class TrainingPlatformUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Authenticate once per user
        res = self.client.post("/auth/login", json={
            "email": "user@test.com",
            "password": "test123"
        })
        self.token = res.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def view_calendar(self):
        self.client.get("/calendar", headers=self.headers)
    
    @task(2)
    def generate_pdf_report(self):
        date_range = {
            "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "end_date": datetime.now().isoformat()
        }
        self.client.post("/reports/pdf", json=date_range, headers=self.headers)
    
    @task(1)
    def generate_ppt_report(self):
        date_range = {
            "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "end_date": datetime.now().isoformat()
        }
        self.client.post("/reports/ppt", json=date_range, headers=self.headers)
    
    @task(4)
    def view_training_sessions(self):
        self.client.get("/training-sessions", headers=self.headers)
    
    @task(1)
    def send_test_email(self):
        self.client.post("/email/send-test", headers=self.headers)

class EmailTestUser(HttpUser):
    """Special user for testing email functionality"""
    wait_time = between(0.5, 1)
    
    def on_start(self):
        # Authenticate once per user
        res = self.client.post("/auth/login", json={
            "email": "user@test.com",
            "password": "test123"
        })
        self.token = res.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(1)
    def send_test_email(self):
        self.client.post("/email/send-test", headers=self.headers)
    
    @task(1)
    def send_custom_email(self):
        email_data = {
            "to_email": "test@example.com",
            "subject": f"Test Email {datetime.now().isoformat()}",
            "html_content": "<h1>Test Email</h1><p>This is a test email sent during load testing.</p>"
        }
        self.client.post("/email/send", json=email_data, headers=self.headers)

class SpikeTestUser(HttpUser):
    """Special scenario for sudden traffic spikes"""
    wait_time = between(0.1, 0.5)
    
    @task
    def report_generation_spike(self):
        self.client.post("/reports/pdf", json={
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        })
    
    @task
    def email_spike(self):
        self.client.post("/email/send-test", json={}) 