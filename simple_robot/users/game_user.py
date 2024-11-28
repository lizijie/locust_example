import traceback, os,  importlib.util
from pathlib import Path
from locust import *

from simple_robot.common.game_connection import GameConnection
from simple_robot.mods.base_mod import BaseMod

def foread_mod_cls(mod_dir: str, cb):
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

    foread_mod_cls(mod_dir, _cb)

    return tasks

class GameUser(User):
    wait_time = between(1, 5)
    tasks = load_tasks("mods")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mods = self.load_mods("mods")
        self.handlers = self.load_handlers(self.mods)
        self.conns = {}

    def on_start(self):
        for mod in self.mods.values():
            mod.on_start()

    def on_stop(self):
        for mod in self.mods.values():
            mod.on_stop()

        for _, socket in self.conns.items():
            socket.disconnect()

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
        foread_mod_cls(mod_dir, _cb)

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