"""Real Live2D bridge (replaces the previous pseudo Live2D animator).

This module starts a local HTTP server and launches a webview window that
renders a Cubism model via pixi-live2d-display (Live2D Web runtime path).
"""
from __future__ import annotations

import json
import os
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode

try:
    import webview as _webview
    _WEBVIEW = True
except ImportError:
    _WEBVIEW = False
    _webview = None  # type: ignore[assignment]

_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
LIVE2D_DIR = _DIR / "assets" / "live2d"
PLAYER_HTML = LIVE2D_DIR / "player.html"
MODEL_REL_PATH = "honghua/model3.json"
MODEL_PATH = LIVE2D_DIR / MODEL_REL_PATH
CANVAS_WIDTH = 460.0
CANVAS_HEIGHT = 490.0


class _StateStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._state: dict[str, object] = {
            "state": "idle",
            "focus_x": 0.0,
            "focus_y": 0.0,
            "lip_sync": 0.0,
        }

    def set(self, key: str, value: object) -> None:
        with self._lock:
            self._state[key] = value

    def snapshot_bytes(self) -> bytes:
        with self._lock:
            payload = json.dumps(self._state, ensure_ascii=False).encode("utf-8")
        return payload


class _Live2DHandler(SimpleHTTPRequestHandler):
    state_store: _StateStore
    # Populated via dynamic subclass creation in CharacterAnimator._start_http_server.
    root_dir: Path

    def __init__(self, *args: object, **kwargs: object):
        super().__init__(*args, directory=str(self.root_dir), **kwargs)

    def do_GET(self) -> None:  # noqa: N802
        if self.path.startswith("/api/state"):
            body = self.state_store.snapshot_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        return super().do_GET()

    def log_message(self, fmt: str, *args) -> None:
        # Keep game output clean.
        return


class CharacterAnimator:
    """Compatibility shim with real Live2D backend.

    Public methods keep the same interface as the old animator so `game.py`
    can keep driving state/focus/lip-sync in the same way.
    """

    def __init__(self, _canvas: object, _width: int, _height: int) -> None:
        self._state_store = _StateStore()
        self._server: Optional[ThreadingHTTPServer] = None
        self._server_thread: Optional[threading.Thread] = None
        self._view_thread: Optional[threading.Thread] = None
        self._started = False

    def load_image(self, _pil_image: object) -> None:
        # Live2D path does not consume a PIL image.
        return

    def set_state(self, state: str) -> None:
        self._state_store.set("state", state)

    def set_focus_point(self, x: int, y: int) -> None:
        # The caller sends canvas coordinates; normalize against canonical size.
        nx = max(-1.0, min(1.0, (x / CANVAS_WIDTH) * 2.0 - 1.0))
        ny = max(-1.0, min(1.0, (y / CANVAS_HEIGHT) * 2.0 - 1.0))
        self._state_store.set("focus_x", nx)
        self._state_store.set("focus_y", ny)

    def clear_focus(self) -> None:
        self._state_store.set("focus_x", 0.0)
        self._state_store.set("focus_y", 0.0)

    def set_lip_sync_intensity(self, intensity: float) -> None:
        value = max(0.0, min(1.0, float(intensity)))
        self._state_store.set("lip_sync", value)

    def start(self) -> None:
        if self._started or not _WEBVIEW:
            return
        if not PLAYER_HTML.exists() or not MODEL_PATH.exists():
            return
        self._start_http_server()
        if self._server is None:
            return
        self._view_thread = threading.Thread(target=self._run_webview, daemon=True)
        self._view_thread.start()
        self._started = True

    def stop(self) -> None:
        # Keep the Live2D window alive across scene transitions.
        return

    def _start_http_server(self) -> None:
        handler_cls = type(
            "Live2DHandler",
            (_Live2DHandler,),
            {"state_store": self._state_store, "root_dir": LIVE2D_DIR},
        )
        try:
            self._server = ThreadingHTTPServer(("127.0.0.1", 0), handler_cls)
        except OSError:
            self._server = None
            return
        self._server_thread = threading.Thread(
            target=self._server.serve_forever,
            kwargs={"poll_interval": 0.2},
            daemon=True,
        )
        self._server_thread.start()

    def _run_webview(self) -> None:
        if self._server is None or _webview is None:
            return
        _, port = self._server.server_address
        query = urlencode({"model": MODEL_REL_PATH})
        url = f"http://127.0.0.1:{port}/player.html?{query}"
        try:
            _webview.create_window("紅花 Live2D", url=url, width=520, height=640)
            _webview.start()
        except Exception:
            return
