const socket = io();

const term = new Terminal({
    cursorBlink: true,
    convertEol: true,
});

term.open(document.getElementById("terminal"));
term.focus();

let buffer = "";

socket.on("output", (data) => {
    term.write(data);
});

term.onData(data => {

    // ENTER → ALWAYS allow empty or non-empty input
    if (data === "\r") {
        socket.emit("input", buffer);
        term.write("\r\n");
        buffer = "";
        return;
    }

    // BACKSPACE
    if (data === "\x7f") {
        if (buffer.length > 0) {
            buffer = buffer.slice(0, -1);
            term.write("\b \b");
        }
        return;
    }

    // IGNORE multi-char control sequences (safe filtering)
    if (data.length !== 1) {
        return;
    }

    // allow all visible ASCII (DO NOT restrict to letters)
    const code = data.charCodeAt(0);
    if (code < 32 || code > 126) {
        return;
    }

    buffer += data;
    term.write(data);
});