from locust import HttpUser, task
from random import randint

class AwesomeApplication(HttpUser):
    @task
    def hello(self):
        self.client.get("/pocket-watch")
        
    @task
    def world(self):
        self.client.get("/")     