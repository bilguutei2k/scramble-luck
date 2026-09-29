"""The script desk on this Mac: edit the narration and record your own takes beside the frames.

    python3 studio/tools/desk.py studio/episodes/<id> [--port 8765] [--no-open]

Serves the storyboard page (build it first with storyboard.py) at http://127.0.0.1:<port>, and only
there, with recording switched on: a browser lets a page use the microphone on this computer's own address, which a
claude.ai page cannot. Line and note edits save to <episode>/desk/edits.json (in git: it is the
working draft of the script). Takes save under <episode>/voice/ (not in git): the browser's
recording, a 48 kHz mono WAV made from it, and voice/takes.json, which lists every take and the
one chosen for each line or scene. Stop with Ctrl-C.
"""

import argparse
import json
import re
import subprocess
import threading
import webbrowser
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

ID = re.compile(r"^[A-Za-z0-9-]{1,40}$")
TYPES = {".html": "text/html; charset=utf-8", ".jpg": "image/jpeg", ".mp3": "audio/mpeg", ".webm": "audio/webm",
         ".mp4": "audio/mp4", ".ogg": "audio/ogg", ".wav": "audio/wav", ".json": "application/json"}
LOCK = threading.Lock()


class Desk:
    def __init__(self, episode):
        self.episode = episode
        self.board = episode / "renders/storyboard"
        self.edits_path = episode / "desk/edits.json"
        self.voice = episode / "voice"
        self.takes_path = self.voice / "takes.json"
        if not (self.board / "page.html").exists():
            raise SystemExit("No storyboard yet: run python3 studio/tools/storyboard.py " + str(episode))

    def read(self, path, empty):
        return json.loads(path.read_text()) if path.exists() else empty

    def write(self, path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
        tmp.replace(path)

    def state(self):
        edits = self.read(self.edits_path, {"lines": {}, "notes": {}})
        return {"lines": edits.get("lines", {}), "notes": edits.get("notes", {}), "takes": self.read(self.takes_path, {})}

    def save_text(self, kind, ident, text):
        with LOCK:
            edits = self.read(self.edits_path, {"lines": {}, "notes": {}})
            edits.setdefault(kind, {})
            if text is None:
                edits[kind].pop(ident, None)
            else:
                edits[kind][ident] = text
            edits["updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            self.write(self.edits_path, edits)

    def save_take(self, kind, ident, ext, body):
        key = kind + "-" + ident
        folder = self.voice / key
        folder.mkdir(parents=True, exist_ok=True)
        with LOCK:
            takes = self.read(self.takes_path, {})
            entry = takes.setdefault(key, {"takes": [], "chosen": None})
            n = max([t["n"] for t in entry["takes"]], default=0) + 1
            original = folder / ("%02d.%s" % (n, ext))
            original.write_bytes(body)
            wav = original.with_suffix(".wav")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(original), "-ac", "1", "-ar", "48000",
                            "-c:a", "pcm_s24le", str(wav)], check=True)
            seconds = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                            str(wav)], capture_output=True, text=True, check=True).stdout.strip() or 0)
            entry["takes"].append({"n": n, "file": key + "/" + wav.name, "original": key + "/" + original.name,
                                   "seconds": round(seconds, 2), "created": datetime.now(timezone.utc).isoformat(timespec="seconds")})
            entry["chosen"] = n
            self.write(self.takes_path, takes)
            return entry

    def choose(self, kind, ident, n):
        key = kind + "-" + ident
        with LOCK:
            takes = self.read(self.takes_path, {})
            entry = takes.get(key)
            if not entry or n not in [t["n"] for t in entry["takes"]]:
                return None
            entry["chosen"] = n
            self.write(self.takes_path, takes)
            return entry


def handler_for(desk):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass

        def send(self, status, body=b"", kind="application/json"):
            self.send_response(status)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def send_json(self, data, status=200):
            self.send(status, json.dumps(data).encode())

        def body(self):
            return self.rfile.read(int(self.headers.get("Content-Length") or 0))

        def do_GET(self):
            path = unquote(urlparse(self.path).path)
            if path in ("/", "/index.html"):
                page = (desk.board / "page.html").read_text()
                return self.send(200, ("<script>window.DESK_LOCAL = true;</script>\n" + page).encode(), TYPES[".html"])
            if path == "/api/state":
                return self.send_json(desk.state())
            root, rel = (desk.voice, path[len("/voice/"):]) if path.startswith("/voice/") else (desk.board, path.lstrip("/"))
            target = (root / rel).resolve()
            if root.resolve() not in target.parents or not target.is_file() or target.suffix not in TYPES:
                return self.send(404, b"not found", "text/plain")
            return self.send(200, target.read_bytes(), TYPES[target.suffix])

        def do_PUT(self):
            parts = unquote(urlparse(self.path).path).strip("/").split("/")
            try:
                data = json.loads(self.body() or b"{}")
            except ValueError:
                return self.send(400, b"bad json", "text/plain")
            if len(parts) == 3 and parts[0] == "api" and parts[1] in ("lines", "notes") and ID.match(parts[2]):
                text = data.get("text")
                if text is not None and not isinstance(text, str):
                    return self.send(400, b"text must be a string", "text/plain")
                desk.save_text(parts[1], parts[2], text)
                return self.send_json({"ok": True})
            if len(parts) == 4 and parts[:2] == ["api", "choose"] and parts[2] in ("line", "scene") and ID.match(parts[3]):
                entry = desk.choose(parts[2], parts[3], data.get("n"))
                return self.send_json(entry) if entry else self.send(404, b"no such take", "text/plain")
            return self.send(404, b"not found", "text/plain")

        def do_POST(self):
            url = urlparse(self.path)
            parts = unquote(url.path).strip("/").split("/")
            ext = parse_qs(url.query).get("ext", ["webm"])[0]
            if (len(parts) == 4 and parts[:2] == ["api", "takes"] and parts[2] in ("line", "scene") and ID.match(parts[3])
                    and ext in ("webm", "mp4", "ogg")):
                body = self.body()
                if not body:
                    return self.send(400, b"empty recording", "text/plain")
                try:
                    return self.send_json(desk.save_take(parts[2], parts[3], ext, body))
                except subprocess.CalledProcessError:
                    return self.send(500, b"could not convert the recording", "text/plain")
            return self.send(404, b"not found", "text/plain")

    return Handler


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("episode", type=Path)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-open", action="store_true")
    args = parser.parse_args(argv)
    desk = Desk(args.episode.resolve())
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler_for(desk))
    url = "http://127.0.0.1:%d/" % args.port
    print("Script desk at %s (edits: %s; takes: %s). Ctrl-C to stop." % (url, desk.edits_path, desk.voice))
    if not args.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
