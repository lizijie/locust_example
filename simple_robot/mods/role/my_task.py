from locust import SequentialTaskSet, task, TaskSet
import random

class RoleTask1(SequentialTaskSet):
    @task
    def task_1(self):
        print("RoleTask1:task_1")

    @task
    def task_2(self):
        print("RoleTask1:task_2")
        self.interrupt()

class RoleTask2(TaskSet):
    @task
    def task(self):
        role = self.user.mods["RoleMod"]
        if role:
            if role.my_value > random.randint(1, 50):
                self.user.send("YOUR_SOCKET_NAME", "EchoRequest", {"Text":"hello world"})
        self.interrupt()