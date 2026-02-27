import threading
import socketio
from queue import Queue, Empty
from config import URL_, headers

class SocketClient:
    def __init__(self):
        self.sio = socketio.Client(logger=False, engineio_logger=False)
        self.responses = {}
        self.lock = threading.Lock()

        self.sio.connect(
            URL_,
            socketio_path="/new",
            headers=headers,
            transports=["polling"],
            wait_timeout=5
        )

    def _ensure_event(self, event_name):
        if event_name in self.responses:
            return

        q = Queue()
        self.responses[event_name] = q

        @self.sio.on(event_name)
        def handler(*args):
            data = args[0] if len(args) == 1 else args
            q.put(data)

    def request(self, event_name, emit_event=None, *emit_args, timeout=1):
        with self.lock:
            self._ensure_event(event_name)

            self.sio.emit(emit_event or event_name, *emit_args)

            try:
                return self.responses[event_name].get(timeout=timeout)
            except Empty:
                print(f"Timeout: {event_name}")

    def close(self):
        if self.sio.connected:
            self.sio.disconnect()