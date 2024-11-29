from simple_robot.mods.base_mod import BaseMod

from simple_robot.mods.role.my_task import *

class RoleMod(BaseMod):
    tasks = [RoleTask1, RoleTask2]
     
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.my_value = 0

    def start(self):
        def _open():
            self.send("YOUR_SOCKET_NAME", "ServerListRequest", {}),
        self.connect("YOUR_SOCKET_NAME", self.user.host, _open)

    def stop(self):
        pass

    def get_message_handlers(self):
        return {
            "ServerListResponse": self.on_ServerListResponse,
            "LoginRespone": self.on_LoginRespone
        }

    def on_ServerListResponse(self, pkg):
        addr = pkg["ServerList"][0]
        if not addr:
            return

        self.disconnect("YOUR_SOCKET_NAME")
        def _open():
            self.send("YOUR_SOCKET_NAME", "LoginReuest", {}),
        self.connect("YOUR_SOCKET_NAME", f"ws://{addr}", _open)

    def on_LoginRespone(self, pkg):
        self.my_value = pkg["MyValue"]
        
        self.run_tasks()