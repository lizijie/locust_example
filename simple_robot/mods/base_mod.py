class BaseMod:
    def __init__(self, user):
        self.user = user

    def on_start(self):
        pass

    def on_stop(self):
        pass

    def get_message_handlers():
        pass

    def connect(self, name, host, on_open):
        self.user.connect(name, host, on_open)

    def disconnect(self, name):
        self.user.disconnect(name)

    def send(self, name, pkg_name, pkg):
        self.user.send(name, pkg_name, pkg),