const socket = io();

const term = new Terminal({
    cursorBlink: true,
    convertEol: true,
    disableStdin: false,
});

term.open(document.getElementById("terminal"));

let buffer = "";

// ONLY accept clean printable characters
term.onData(data => {

    // ENTER
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

    // BLOCK control / weird IME / mobile junk
    if (data.length > 1) return;

    const char = data;

    // only allow safe ASCII
    if (!/[a-zA-Z%\/\\\-#!?@+]/.test(char) && char !== " ") {
        return;
    }

    buffer += char;
    term.write(char);
});