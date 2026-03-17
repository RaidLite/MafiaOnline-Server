from queue import Queue, Empty
from threading import Lock
from config import URL_, headers
from socketio import Client

class SocketClient:
    def __init__(self):
        self.sio = Client(logger=False, engineio_logger=False)
        self.res, self.lock = {}, Lock()
        self.sio.connect(URL_, socketio_path="/new", headers=headers, transports=["polling"], wait_timeout=5)
        self.reg = lambda ev: (self.res.update({ev: Queue()}), self.sio.on(ev, lambda *a: self.res[ev].put(a[0] if len(a) == 1 else a)))

    def request(self, ev, emit_ev=None, *args, timeout=1):
        with self.lock:
            if ev not in self.res: self.reg(ev)
            self.sio.emit(emit_ev or ev, *args)
            try: return self.res[ev].get(timeout=timeout)
            except Empty: print(f"Timeout: {ev}")

    def close(self):
        if self.sio.connected: self.sio.disconnect()