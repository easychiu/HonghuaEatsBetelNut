"""Image-only character animator (no Live2D / webview runtime)."""
from __future__ import annotations

try:
    from PIL import Image, ImageTk
    _PIL = True
    _RESAMPLING = getattr(Image, "Resampling", None)
    _LANCZOS = _RESAMPLING.LANCZOS if _RESAMPLING else Image.LANCZOS  # type: ignore[attr-defined]
except ImportError:
    _PIL = False
    _LANCZOS = 1  # unused when _PIL is False


class CharacterAnimator:
    """Canvas-based static character image display (no animation effects)."""

    def __init__(self, canvas: object, width: int, height: int) -> None:
        self._canvas = canvas
        self._width = width
        self._height = height

        self._base_image: object | None = None
        self._photo: object | None = None
        self._item_id: object | None = None
        self._running = False

    def load_image(self, pil_image: object) -> None:
        if not _PIL:
            return
        if not isinstance(pil_image, Image.Image):
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
        pass  # no animation states — image is displayed as-is

    def set_focus_point(self, x: int, y: int) -> None:
        pass  # no focus tracking

    def clear_focus(self) -> None:
        pass

    def set_lip_sync_intensity(self, intensity: float) -> None:
        pass  # no lip sync animation

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False
        self._item_id = None
        self._photo = None

    def _render_frame(self) -> None:
        if not _PIL or self._base_image is None:
            return

        self._photo = ImageTk.PhotoImage(self._base_image)
        if self._item_id is None:
            self._item_id = self._canvas.create_image(
                0, 0, anchor="nw", image=self._photo, tags=("character_animator",)
            )
        else:
            self._canvas.itemconfigure(self._item_id, image=self._photo)
        self._canvas.tag_raise(self._item_id)
        if self._canvas.find_withtag("hotspot"):
            self._canvas.tag_lower(self._item_id, "hotspot")
