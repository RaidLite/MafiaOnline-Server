from random import randint

_shuffle_array = lambda arr: (
    arr.__setitem__((0, 1, 3, -1), (arr[-1], arr[3], arr[1], arr[0]))
    if len(arr) >= 5 else None
)
_obfuscate_for_send = lambda obj, shift=0: _encode(obj, shift)
_copy_dict = lambda data: {k: v for k, v in data.items()}
encode = lambda obj, shift=0: _encode(obj, shift)
decode = lambda obj, shift=0: _decode(obj, shift, MafDecoder.shift)

def _obfuscate_value(obj, shift):
    if isinstance(obj, (str, int, float)):
        is_num = isinstance(obj, (int, float))
        result = ''.join(chr(ord(c) + shift) for c in str(obj))
        return result + " " if is_num else result
    elif isinstance(obj, list):
        new_list = [_obfuscate_value(item, shift) for item in obj]
        if len(new_list) >= 5:
            _shuffle_array(new_list)
        return new_list
    return obj

def _encode(obj, shift=0):
    if isinstance(obj, dict):
        obj = _copy_dict(obj)
        if shift == 0:
            shift = randint(100, 200)
        for key in list(obj.keys()):
            value = obj[key]
            new_key = _obfuscate_value(key, shift)
            new_value = _encode(value, shift) if isinstance(value, dict) else _obfuscate_value(value, shift)
            obj[new_key] = new_value
            if key in obj:
                del obj[key]
        obj["lfm5"] = shift
        return obj
    return obj


def _decode_value(obj, shift):
    if isinstance(obj, list):
        new_list = [_decode_value(item, shift) for item in obj]
        if len(new_list) >= 5:
            _shuffle_array(new_list)
        return new_list
    if isinstance(obj, bool):
        return obj
    if not isinstance(obj, str):
        obj = str(obj)
    chars = list(obj)
    for i in range(len(chars)):
        if i == len(chars) - 1 and chars[i] == ' ':
            try:
                return int(''.join(chars[:i]))
            except ValueError:
                return ''.join(chars[:i])
        chars[i] = chr(ord(chars[i]) - shift)
    return ''.join(chars)


def _decode(obj, shift=0, base_shift=0):
    if obj is None:
        return obj
    try:
        if isinstance(obj, list):
            for i in range(len(obj)):
                item = obj[i]
                if isinstance(item, dict) or (
                        isinstance(item, list) and len(item) > 0 and isinstance(item[0], (dict, list))):
                    _decode(item, shift, base_shift)
                else:
                    obj[i] = _decode_value(item, shift)
            if len(obj) >= 5:
                _shuffle_array(obj)
            return obj
        if isinstance(obj, dict):
            if shift == 0:
                if "lfm1" in obj:
                    shift = base_shift
                elif "lfm5" in obj:
                    shift = obj["lfm5"]
            for key in list(obj.keys()):
                value = obj[key]
                is_complex = isinstance(value, dict) or (
                        isinstance(value, list) and len(value) > 0 and isinstance(value[0], (dict, list)))
                if is_complex:
                    new_key = _decode_value(key, shift)
                    obj[new_key] = _decode(value, shift, base_shift)
                elif key not in {"lfm1", "lfm2", "lfm3", "lfm4", "lfm5"}:
                    new_key = _decode_value(key, shift)
                    obj[new_key] = value if new_key == "logo" else _decode_value(value, shift)
                if key in obj:
                    del obj[key]
            return obj
    except (IndexError, TypeError, KeyError, ValueError):
        return obj
    return obj

class MafSocket:
    _shift = 0

    def __init__(self, socket):
        self.socket = socket

    def emit(self, event, *args):
        if args:
            args_list = list(args)
            if args_list:
                args_list[0] = _obfuscate_for_send(args_list[0], 0)
            return self.socket.emit(event, *args_list)
        return self.socket.emit(event)

    def on(self, event, listener):
        def wrapped(*args):
            deobf_args = [self.deobfuscate(arg, 0) for arg in args]
            listener(*deobf_args)

        self.socket.on(event, wrapped)
        return self

    emit_plain = lambda self, event, *args: self.socket.emit(event, *args)
    deobfuscate = lambda self, obj, shift=0: _decode(obj, shift, MafSocket._shift)
    once = lambda self, event, listener: self.socket.once(event, listener)
    off = lambda self: self.socket.off()
    off_event = lambda self, event: self.socket.off(event)
    off_listener = lambda self, event, listener: self.socket.off(event, listener)
    open = lambda self: self.socket.connect()
    connect = lambda self: self.socket.connect()
    send = lambda self, *args: self.socket.send(*args)
    emit_with_ack = lambda self, event, *args: self.socket.emit(event, *args)
    close = lambda self: self.socket.disconnect()
    disconnect = lambda self: self.socket.disconnect()
    is_connected = lambda self: self.socket.connected
    set_base_shift = lambda i: setattr(MafSocket, '_shift', i)
    set_shift_diff = lambda i, i2: setattr(MafSocket, '_shift', (i2 - i) + 150)

class MafDecoder:
    shift = 0
    set_base_shift = lambda i: setattr(MafDecoder, 'shift', i)
    set_shift_diff = lambda i, i2: setattr(MafDecoder, 'shift', (i2 - i) + 150)