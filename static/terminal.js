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

    if (data.length !== 1) return;

    const code = data.charCodeAt(0);
    if (code < 32 || code > 126) return;

    buffer += data;
    term.write(data);
});