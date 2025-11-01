import queue
import threading
import socket
import struct
import json
import time


class Channel:
    def __init__(self):
        self.queue = queue.Queue()
    
    def send(self, *values):
        self.queue.put(values)
    
    def receive(self, count=1):
        values = self.queue.get(block=True)
        if count == 1:
            return values[0] if len(values) == 1 else values
        return values[:count]
    
    def is_empty(self):
        return self.queue.empty()


class NetworkChannel(Channel):
    """Channel backed by a TCP connection. Supports one-to-one communication.

    Two modes:
    - server (bind): listens on host:port and accepts a single connection.
    - client (connect): connects to remote host:port.

    Uses a small framing protocol: 4-byte big-endian length prefix followed by JSON payload.
    Payload format: {"op": "send", "values": [ {"t":"INT","v":5}, ... ] }
    """

    def __init__(self, mode: str, host: str, port: int, type_tag=True, reconnect=True):
        super().__init__()
        self.mode = mode  # 'server' or 'client'
        self.host = host
        self.port = int(port)
        self.sock = None
        self.conn = None
        self.listener_thread = None
        self.running = False
        self.type_tag = type_tag
        self.reconnect = reconnect
        self._start()

    # --- framing utils ---
    def _send_json(self, sock, obj):
        data = json.dumps(obj).encode('utf-8')
        length = struct.pack('>I', len(data))
        sock.sendall(length + data)

    def _recv_exact(self, sock, n):
        buf = b''
        while len(buf) < n:
            chunk = sock.recv(n - len(buf))
            if not chunk:
                raise ConnectionError('socket closed')
            buf += chunk
        return buf

    def _recv_json(self, sock):
        header = self._recv_exact(sock, 4)
        length = struct.unpack('>I', header)[0]
        data = self._recv_exact(sock, length)
        return json.loads(data.decode('utf-8'))

    # --- network setup ---
    def _start(self):
        self.running = True
        if self.mode == 'server':
            # Start listening socket and accept in background
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.host, self.port))
            self.sock.listen(1)
            self.listener_thread = threading.Thread(target=self._accept_loop, daemon=True)
            self.listener_thread.start()
        else:
            # client mode: connect and start reader
            self.listener_thread = threading.Thread(target=self._client_connect_loop, daemon=True)
            self.listener_thread.start()

    def _accept_loop(self):
        while self.running:
            try:
                conn, addr = self.sock.accept()
                self.conn = conn
                # start reader for this connection
                self._reader_loop(conn)
            except Exception:
                time.sleep(0.5)

    def _client_connect_loop(self):
        while self.running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.host, self.port))
                self.conn = s
                self._reader_loop(s)
            except Exception:
                if not self.reconnect:
                    break
                time.sleep(1)

    def _reader_loop(self, conn):
        try:
            while self.running:
                msg = self._recv_json(conn)
                if not isinstance(msg, dict):
                    continue
                if msg.get('op') == 'send':
                    values = []
                    for it in msg.get('values', []):
                        if isinstance(it, dict) and 't' in it and 'v' in it:
                            values.append(it['v'])
                        else:
                            values.append(it)
                    # push into local queue as tuple
                    self.queue.put(tuple(values))
        except Exception:
            # connection closed
            self.conn = None
            return

    # --- send/receive overrides ---
    def send(self, *values):
        # Prepare payload with simple type tagging if requested
        out = []
        for v in values:
            if self.type_tag:
                if isinstance(v, int):
                    out.append({'t': 'INT', 'v': v})
                elif isinstance(v, float):
                    out.append({'t': 'FLOAT', 'v': v})
                elif isinstance(v, str):
                    out.append({'t': 'STRING', 'v': v})
                else:
                    out.append({'t': 'OBJECT', 'v': str(v)})
            else:
                out.append(v)

        payload = {'op': 'send', 'values': out}

        # If connection available, send immediately; otherwise queue locally (best-effort)
        sock = self.conn
        if sock:
            try:
                self._send_json(sock, payload)
            except Exception:
                # on failure, fallback to local queue
                self.queue.put(tuple(values))
        else:
            # no network connection - enqueue locally so local receive can still get it
            self.queue.put(tuple(values))

    def receive(self, count=1):
        # Blocking read from local queue (populated by network reader or local send fallback)
        values = super().receive(count)
        return values

    def close(self):
        self.running = False
        try:
            if self.conn:
                self.conn.close()
        except Exception:
            pass
        try:
            if self.sock:
                self.sock.close()
        except Exception:
            pass
