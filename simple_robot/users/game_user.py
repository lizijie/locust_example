import traceback, os,  importlib.util
from pathlib import Path
from locust import *

from simple_robot.common.game_connection import GameConnection
from simple_robot.mods.base_mod import BaseMod

def foreach_mod_cls(mod_dir: str, cb):
    if callable(cb) is None:
        return

    base_path = Path(mod_dir)
    for subdir in base_path.iterdir():
        mod_file = subdir / f"{subdir.name}_mod.py"
        if subdir.is_dir() and mod_file.exists():
            module_name = f"{subdir.name}"
            spec = importlib.util.spec_from_file_location(module_name, mod_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, BaseMod) and attr is not BaseMod:
                    cb(attr)

def load_tasks(mod_dir: str):
    tasks = []

    def _cb(attr):
        if attr.tasks:
            tasks.extend(attr.tasks)

    foreach_mod_cls(mod_dir, _cb)

    return tasks

class GameUser(User):
    wait_time = between(1, 5)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mods = self.load_mods(self.environment.parsed_options.my_mods_path)
        self.handlers = self.load_handlers(self.mods)
        self.conns = {}

        if not GameUser.tasks:
            GameUser.tasks = load_tasks(self.environment.parsed_options.my_mods_path)

    def start(self, group):
        # super().start会启动task
        # 但是总会有部分逻辑，要先Task执行，如登录成功后，才执行Task
        # 所以不在此处调用super().start，而是延后到run_tasks
        # super().start()
        self._group = group

        for mod in self.mods.values():
            mod.start()

    def stop(self):
        super().stop()

        for mod in self.mods.values():
            mod.stop()

        for _, socket in self.conns.items():
            socket.disconnect()

    def run_tasks(self):
        super().start(self._group)

    def connect(self, name, host, on_open):
        socket = GameConnection(self)
        self.conns[name] = socket

        socket.on_open = on_open
        socket.on_message = self.on_message
        socket.connect(host)

    def disconnect(self, name):
        self.conns[name].disconnect()

    def send(self, name, pkg_name, pkg):
        self.conns[name].send(pkg_name, pkg),

    def on_message(self, name, pkg):
        self.fire_message(name, pkg)

    def fire_message(self, name, pkg):
        list = self.handlers[name]
        if not list:
            print("No handlers for message:", name)
            return

        for hdl in list:
            try:
                hdl(pkg)
            except Exception:
                print(f"Uncaught exception in event hdl: name:{name}, pkg:{pkg}\n{traceback.format_exc()}")
            
    def load_mods(self, mod_dir: str):
        mods = {}

        def _cb(attr):
            mods[attr.__name__] = attr(self)
        foreach_mod_cls(mod_dir, _cb)

        return mods

    def load_handlers(self, mods):
        handlers = {}
        for m in mods.values():
            dict = m.get_message_handlers()
            if dict:
                for name, hdl in dict.items():
                    if name not in handlers:
                        handlers[name] = []
                    handlers[name].append(hdl)

        return handlers