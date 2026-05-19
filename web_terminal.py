from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import queue
import builtins
import sys
import io
import eventlet
eventlet.monkey_patch()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

input_queue = queue.Queue()


class SocketOutput(io.StringIO):
    def write(self, text):
        if text:
            socketio.emit("output", text)
        return len(text)


def socket_input(prompt=""):
    socketio.emit("output", prompt)

    while True:
        data = input_queue.get()

        if data is None:
            continue

        data = data.strip()

        if data != "":
            return data


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("input")
def handle_input(data):
    clean = (data or "").strip()

    # reject empty / garbage input
    if clean == "":
        return

    input_queue.put(clean)


def run_program():
    import main

    builtins.input = socket_input

    sys.stdout = SocketOutput()
    sys.stderr = SocketOutput()

    try:
        while True:
            if not main.main():
                break
    except KeyboardInterrupt:
        pass


@socketio.on("connect")
def handle_connect():
    thread = threading.Thread(target=run_program)
    thread.daemon = True
    thread.start()


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
