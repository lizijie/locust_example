class BaseMod:
    def __init__(self, user):
        self.user = user

    def start(self):
        pass

    def stop(self):
        pass

    def get_message_handlers():
        pass

    def run_tasks(self):
        self.user.run_tasks()

    def connect(self, name, host, on_open):
        self.user.connect(name, host, on_open)

    def disconnect(self, name):
        self.user.disconnect(name)

    def send(self, name, pkg_name, pkg):
        self.user.send(name, pkg_name, pkg),