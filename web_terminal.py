import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request
from flask_socketio import SocketIO
import threading
import queue
import builtins
import sys
import io

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# store per-client state
clients = {}


class SocketOutput(io.StringIO):
    def __init__(self, sid):
        super().__init__()
        self.sid = sid

    def write(self, text):
        if text:
            socketio.emit("output", text, to=self.sid)
        return len(text)


def make_input_function(sid):
    def socket_input(prompt=""):
        socketio.emit("output", prompt, to=sid)

        q = clients[sid]["queue"]

        while True:
            data = q.get()

            if data is None:
                continue

            data = data.strip()

            if data != "":
                return data

    return socket_input


def run_program(sid):
    import main

    builtins.input = make_input_function(sid)

    sys.stdout = SocketOutput(sid)
    sys.stderr = SocketOutput(sid)

    try:
        while True:
            if not main.main():
                break
    except Exception as e:
        socketio.emit("output", f"\nError: {e}\n", to=sid)


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("connect")
def handle_connect():
    sid = request.sid

    clients[sid] = {
        "queue": queue.Queue(),
        "thread": None
    }

    thread = threading.Thread(target=run_program, args=(sid,))
    thread.daemon = True
    thread.start()

    clients[sid]["thread"] = thread


@socketio.on("disconnect")
def handle_disconnect():
    sid = request.sid
    if sid in clients:
        del clients[sid]


@socketio.on("input")
def handle_input(data):
    sid = request.sid

    if sid not in clients:
        return

    clean = (data or "").strip()

    # IMPORTANT: allow empty input (your program needs it)
    clients[sid]["queue"].put(clean)


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)