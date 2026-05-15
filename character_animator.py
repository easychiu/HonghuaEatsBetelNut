"""Image-only character animator (no Live2D / webview runtime)."""
from __future__ import annotations

import math

try:
    from PIL import Image, ImageTk
    _PIL = True
    _RESAMPLING = getattr(Image, "Resampling", None)
    _LANCZOS = _RESAMPLING.LANCZOS if _RESAMPLING else Image.LANCZOS  # type: ignore[attr-defined]
except ImportError:
    _PIL = False
    _LANCZOS = 1  # unused when _PIL is False

TICK_MS = 33
FOCUS_SMOOTH = 0.16
LIP_DECAY = 0.90

_STATE_CFG: dict[str, tuple[float, float]] = {
    # state: (breathing amplitude, floating amplitude)
    "idle": (0.007, 1.6),
    "talking": (0.010, 2.4),
    "excited": (0.014, 3.2),
    "impatient": (0.009, 2.2),
    "peaceful": (0.006, 1.5),
    "friendly": (0.008, 1.9),
    "trusted": (0.0085, 2.0),
}


class CharacterAnimator:
    """Canvas-based pseudo animation using a static character image."""

    def __init__(self, canvas: object, width: int, height: int) -> None:
        self._canvas = canvas
        self._width = width
        self._height = height

        self._base_image: object | None = None
        self._photo: object | None = None
        self._item_id: object | None = None
        self._job: object | None = None
        self._running = False

        self._state = "idle"
        self._phase = 0.0
        self._target_focus_x = 0.0
        self._target_focus_y = 0.0
        self._focus_x = 0.0
        self._focus_y = 0.0
        self._lip_sync = 0.0

    def load_image(self, pil_image: object) -> None:
        if not _PIL:
            return
        if not hasattr(pil_image, "copy") or not hasattr(pil_image, "convert"):
            self._base_image = None
            return
        try:
            img = pil_image.copy().convert("RGBA")
            if img.size != (self._width, self._height):
                img = img.resize((self._width, self._height), _LANCZOS)
            self._base_image = img
        except Exception:
            self._base_image = None
            return
        self._render_frame()

    def set_state(self, state: str) -> None:
        self._state = state if state in _STATE_CFG else "idle"

    def set_focus_point(self, x: int, y: int) -> None:
        self._target_focus_x = self._normalize_coordinate(x, self._width)
        self._target_focus_y = self._normalize_coordinate(y, self._height)

    def clear_focus(self) -> None:
        self._target_focus_x = 0.0
        self._target_focus_y = 0.0

    def set_lip_sync_intensity(self, intensity: float) -> None:
        self._lip_sync = max(0.0, min(1.0, float(intensity)))

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._schedule_tick()

    def stop(self) -> None:
        self._running = False
        if self._job is not None:
            try:
                self._canvas.after_cancel(self._job)
            except Exception:
                pass
        self._job = None
        self._item_id = None
        self._photo = None

    def _schedule_tick(self) -> None:
        if not self._running:
            return
        self._tick()
        self._job = self._canvas.after(TICK_MS, self._schedule_tick)

    def _tick(self) -> None:
        self._phase += 1.0
        self._focus_x += (self._target_focus_x - self._focus_x) * FOCUS_SMOOTH
        self._focus_y += (self._target_focus_y - self._focus_y) * FOCUS_SMOOTH
        self._lip_sync *= LIP_DECAY
        self._render_frame()

    def _render_frame(self) -> None:
        if not _PIL or self._base_image is None:
            return

        breath_amp, float_amp = _STATE_CFG.get(self._state, _STATE_CFG["idle"])
        breath = math.sin(self._phase * 0.12) * breath_amp
        float_y = math.sin(self._phase * 0.08) * float_amp
        mouth_boost = self._lip_sync * 0.010
        scale = max(0.92, 1.0 + breath + mouth_boost)

        w = max(1, int(self._width * scale))
        h = max(1, int(self._height * scale))
        resized = self._base_image.resize((w, h), _LANCZOS)

        frame = Image.new("RGBA", (self._width, self._height), (0, 0, 0, 0))
        x = (self._width - w) // 2 + int(self._focus_x * 7)
        y = (self._height - h) // 2 + int(float_y + self._focus_y * 5)
        frame.alpha_composite(resized, (x, y))

        self._photo = ImageTk.PhotoImage(frame)
        if self._item_id is None:
            self._item_id = self._canvas.create_image(
                0, 0, anchor="nw", image=self._photo, tags=("character_animator",)
            )
        else:
            self._canvas.itemconfigure(self._item_id, image=self._photo)
        self._canvas.tag_raise(self._item_id)
        self._canvas.tag_lower(self._item_id, "hotspot")

    @staticmethod
    def _normalize_coordinate(coord: int, size: int) -> float:
        return max(-1.0, min(1.0, (coord / max(1, size)) * 2.0 - 1.0))
