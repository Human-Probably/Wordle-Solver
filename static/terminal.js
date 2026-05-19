const socket = io();

const term = new Terminal({
    cursorBlink: true,
    convertEol: true,
    theme: {
        background: "#000000"
    }
});

term.open(document.getElementById("terminal"));

let currentLine = "";


socket.on("output", (data) => {
    term.write(data);
});


term.textarea.setAttribute("autocorrect", "off");
term.textarea.setAttribute("autocapitalize", "none");
term.textarea.setAttribute("autocomplete", "off");
term.textarea.setAttribute("spellcheck", "false");


term.onData(data => {

    // ENTER
    if (data === "\r") {
        socket.emit("input", currentLine);
        term.write("\r\n");
        currentLine = "";
        return;
    }

    // BACKSPACE
    if (data === "\x7f") {
        if (currentLine.length > 0) {
            currentLine = currentLine.slice(0, -1);
            term.write("\b \b");
        }
        return;
    }

    // Ignore weird mobile control sequences
    if (data.charCodeAt(0) < 32) {
        return;
    }

    currentLine += data;
    term.write(data);
});