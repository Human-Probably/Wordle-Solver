import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request
from flask_socketio import SocketIO, disconnect
import threading
import queue
import builtins
import sys
import io

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

active_session = {
    "sid": None,
    "queue": None,
    "stop": None,
    "thread": None,
}


class SocketOutput(io.StringIO):
    def __init__(self, sid):
        super().__init__()
        self.sid = sid

    def write(self, text):
        if text:
            socketio.emit("output", text, to=self.sid)
        return len(text)


def socket_input(sid, prompt=""):
    socketio.emit("output", prompt, to=sid)

    q = active_session["queue"]
    stop_event = active_session["stop"]

    while True:
        if stop_event.is_set():
            raise SystemExit

        try:
            data = q.get(timeout=0.2)
        except queue.Empty:
            continue

        if data is None:
            continue

        return data


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("connect")
def handle_connect():
    sid = request.sid

    if active_session["sid"] is not None:
        socketio.emit(
            "busy",
            {"message": "Another session is active. Please refresh this page after it leaves."},
            to=sid
        )

        def kick():
            socketio.sleep(0.1)
            disconnect(sid=sid)

        socketio.start_background_task(kick)
        return

    active_session["sid"] = sid
    active_session["queue"] = queue.Queue()
    active_session["stop"] = threading.Event()

    thread = threading.Thread(target=run_program, args=(sid,), daemon=True)
    active_session["thread"] = thread
    thread.start()


@socketio.on("disconnect")
def handle_disconnect():
    sid = request.sid

    if active_session["sid"] == sid:
        if active_session["stop"] is not None:
            active_session["stop"].set()

        if active_session["queue"] is not None:
            active_session["queue"].put(None)


@socketio.on("input")
def handle_input(data):
    sid = request.sid

    if active_session["sid"] != sid:
        return

    # IMPORTANT: do not strip here; your program needs empty input for confirmations.
    if active_session["queue"] is not None:
        active_session["queue"].put("" if data is None else data)


def run_program(sid):
    import main

    original_input = builtins.input
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    builtins.input = lambda prompt="": socket_input(sid, prompt)
    sys.stdout = SocketOutput(sid)
    sys.stderr = SocketOutput(sid)

    try:
        while True:
            if active_session["stop"] is not None and active_session["stop"].is_set():
                break

            if not main.main():
                break
    except SystemExit:
        pass
    except Exception as e:
        socketio.emit("output", f"\nError: {e}\n", to=sid)
    finally:
        builtins.input = original_input
        sys.stdout = original_stdout
        sys.stderr = original_stderr

        if active_session["sid"] == sid:
            active_session["sid"] = None
            active_session["queue"] = None
            active_session["stop"] = None
            active_session["thread"] = None


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)