import os
import random
import subprocess
import sys
import threading
import time
from pathlib import Path

from flask import Flask, abort, jsonify, request, send_from_directory

APP_DIR = Path(__file__).resolve().parent
SUFFIX = "_backgrounds"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
SCRIPTS = [s.strip() for s in os.getenv("SCRIPTS", "").split(",") if s.strip()]
INTERVAL_HOURS = float(os.getenv("INTERVAL_HOURS", "24"))

app = Flask(__name__)


def layouts():
    return sorted(p.name[: -len(SUFFIX)] for p in APP_DIR.glob(f"*{SUFFIX}") if p.is_dir())


def images(layout):
    names = [layout] if layout in layouts() else layouts()
    return [
        f"{name}/{f.name}"
        for name in names
        for f in (APP_DIR / f"{name}{SUFFIX}").glob("*")
        if f.suffix.lower() in IMAGE_EXTS
    ]


@app.get("/api/wallpaper/status")
def wallpaper_status():
    candidates = images(request.args.get("layout"))
    if not candidates:
        abort(404)
    return jsonify(imageUrl=f"{request.host_url}images/{random.choice(candidates)}", actionUrl=None)


@app.get("/images/<layout>/<path:filename>")
def image(layout, filename):
    if layout not in layouts():
        abort(404)
    return send_from_directory(APP_DIR / f"{layout}{SUFFIX}", filename)


@app.get("/api/layouts/list")
def layouts_list():
    return jsonify(layouts())


@app.get("/api/genres/list")
@app.get("/api/ages/list")
@app.get("/api/year/list")
def empty_list():
    return jsonify([])


def run_scripts():
    while True:
        for script in SCRIPTS:
            print(f"Running {script}.py", flush=True)
            subprocess.run([sys.executable, f"{script}.py"], cwd=APP_DIR)
        time.sleep(INTERVAL_HOURS * 3600)


if __name__ == "__main__":
    threading.Thread(target=run_scripts, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
