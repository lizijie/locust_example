import websocket
import websockets
websockets.connect

from common.sproto_utils import sproto_encode, sproto_decode

class GameConnection:
    
    def __init__(self, user):
        self.ws = None
        self.on_open = None
        self.on_message = None
        self.user = user

    def connect(self, host):
        self.ws = websocket.WebSocketApp(
            host,
            on_open= self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
        self.user.group.spawn(self.ws.run_forever)

    def _on_open(self, ws):
        if callable(self.on_open):
            self.on_open()

    def _on_message(self, ws, bytes):
        if callable(self.on_message):
            try:
                name, pkg = sproto_decode(bytes)
                self.on_message(name, pkg)

                self.user.environment.events.request.fire(
                    request_type="_on_message",
                    name=name,
                    response_time=0,
                    response_length=len(bytes),
                    exception=None,
                )
            except Exception as e:
                self.user.environment.events.request.fire(
                    request_type="_on_message",
                    name=name,
                    response_time=0,
                    response_length=len(bytes),
                    exception=e,
                )

    def _on_error(self, ws, error):
        self.user.environment.events.request.fire(
            request_type="_on_error",
            name="error",
            response_time=0,
            response_length=0,
            exception=error,
        )

    def _on_close(self, ws, close_status_code, close_msg):
        self.user.environment.events.request.fire(
            request_type="_on_close",
            name=f"code:{close_status_code} msg:{close_msg}",
            response_time=0,
            response_length=0,
            exception=None,
        )

    def _send(self, data, name="send", opcode=websocket.ABNF.OPCODE_BINARY):
        if self.ws is None:
            return

        self.ws.send(data, opcode)
        self.user.environment.events.request.fire(
            request_type="_send",
            name=name,
            response_time=None,
            response_length=len(data),
            exception=None,
        )

    def send(self, name, pkg):
        self._send(sproto_encode(name, pkg), name)

    def disconnect(self):
        if self.ws:
            self.ws.close()
        self.on_open = None
        self.on_message = None