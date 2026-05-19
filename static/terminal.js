const socket = io();

const term = new Terminal({
    cursorBlink: true,
    convertEol: true,
    disableStdin: false,
});

term.open(document.getElementById("terminal"));
term.focus();

let buffer = "";

// Show something immediately so it is obvious the page loaded
term.write("Loading...\\r\\n");

socket.on("connect", () => {
    term.write("Connected.\\r\\n");
});

socket.on("connect_error", (err) => {
    term.write("\\r\\nConnection error: " + err.message + "\\r\\n");
});

socket.on("output", (data) => {
    term.write(data);
});

term.onData(data => {
    if (data === "\r") {
        socket.emit("input", buffer);
        term.write("\r\n");
        buffer = "";
        return;
    }

    if (data === "\x7f") {
        if (buffer.length > 0) {
            buffer = buffer.slice(0, -1);
            term.write("\b \b");
        }
        return;
    }

    if (data.length !== 1) {
        return;
    }

    // Allow normal typing only
    if (!/^[\x20-\x7E]$/.test(data)) {
        return;
    }

    buffer += data;
    term.write(data);
});