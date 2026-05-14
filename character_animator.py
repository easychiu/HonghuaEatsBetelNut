"""Character sprite animator for the Honghua visual novel.

Provides simple Live2D-like effects — breathing, blinking, and gentle
floating — applied to a single PIL Image and rendered on a tkinter Canvas
via the ``after()`` scheduler.  All effects are purely procedural; no
separate layer images are required.
"""
from __future__ import annotations

import math
import random
from typing import Optional

try:
    from PIL import Image, ImageTk
    _PIL = True
except ImportError:
    _PIL = False

# ── animation states ───────────────────────────────────────────────────────────
STATE_IDLE    = "idle"
STATE_TALKING = "talking"
STATE_EXCITED = "excited"


class CharacterAnimator:
    """Animate a character image on a tkinter Canvas using PIL transforms.

    Effects
    -------
    *Breathing* — subtle vertical scale oscillation (~4 s cycle).
    *Floating*  — gentle sine-wave vertical drift (~6 s cycle).
    *Blinking*  — eye-close / open at random intervals (3–7 s).

    The amplitude of each effect scales with the current animation state:
    ``idle`` < ``talking`` < ``excited``.

    Usage::

        animator = CharacterAnimator(canvas, width=460, height=490)
        animator.load_image(pil_image)   # PIL RGBA Image, pre-resized
        animator.set_state("idle")
        animator.start()

        # when switching scenes:
        animator.stop()
        canvas.delete("all")
    """

    FPS         = 20            # target frames per second
    INTERVAL_MS = 1000 // FPS  # ms between frames

    # Breathing (vertical zoom oscillation)
    BREATH_AMP   = 0.005   # ±0.5 % height change per breath
    BREATH_CYCLE = 4.0     # seconds per full breath cycle

    # Gentle float (vertical sine drift)
    FLOAT_AMP   = 2.0     # ±2 px max drift
    FLOAT_CYCLE = 6.0     # seconds per float cycle

    # Blink timing (in animation frames at FPS)
    BLINK_INTERVAL_MIN = 3 * FPS   # ≈ 3 s
    BLINK_INTERVAL_MAX = 7 * FPS   # ≈ 7 s
    BLINK_CLOSE_FRAMES = 2
    BLINK_SHUT_FRAMES  = 1
    BLINK_OPEN_FRAMES  = 2

    # Eye region as fraction of image height (centre of face ≈ 22–30 %)
    EYE_Y1_FRAC = 0.22
    EYE_Y2_FRAC = 0.30

    def __init__(self, canvas: object, width: int, height: int) -> None:
        self._canvas   = canvas
        self._w        = width
        self._h        = height
        self._base     : Optional[object] = None  # PIL RGBA Image
        self._photo    : Optional[object] = None  # ImageTk.PhotoImage (kept alive)
        self._item_id  : Optional[int]    = None  # canvas image item ID
        self._after_id : Optional[str]    = None  # pending after() job
        self._state    = STATE_IDLE
        self._frame    = 0
        self._next_blink     = self._rand_blink_interval()
        self._blink_phase    = 0   # 0=open  1=closing  2=shut  3=opening
        self._blink_subframe = 0

    # ── public API ─────────────────────────────────────────────────────────────

    def load_image(self, pil_image: object) -> None:
        """Set the PIL Image to animate (should be RGBA, sized to canvas)."""
        if not _PIL:
            return
        self._base           = pil_image.convert("RGBA")
        self._frame          = 0
        self._next_blink     = self._rand_blink_interval()
        self._blink_phase    = 0
        self._blink_subframe = 0

    def set_state(self, state: str) -> None:
        """Switch animation state: ``idle`` | ``talking`` | ``excited``."""
        self._state = state

    def start(self) -> None:
        """Begin (or restart) the animation loop."""
        if self._after_id is not None:
            self._canvas.after_cancel(self._after_id)
            self._after_id = None
        if _PIL and self._base is not None:
            self._tick()

    def stop(self) -> None:
        """Cancel the animation loop.

        Canvas items are *not* removed here — call ``canvas.delete("all")``
        externally to clear the display.  The internal item reference is
        reset so the next ``start()`` creates a fresh item.
        """
        if self._after_id is not None:
            self._canvas.after_cancel(self._after_id)
            self._after_id = None
        # These become stale after the next canvas.delete("all").
        self._item_id = None
        self._photo   = None

    # ── internals ──────────────────────────────────────────────────────────────

    def _rand_blink_interval(self) -> int:
        return random.randint(self.BLINK_INTERVAL_MIN, self.BLINK_INTERVAL_MAX)

    def _tick(self) -> None:
        rendered    = self._render_frame()
        self._photo = ImageTk.PhotoImage(rendered.convert("RGB"))
        if self._item_id is None:
            self._item_id = self._canvas.create_image(
                0, 0, anchor="nw", image=self._photo, tags=("char_anim",)
            )
            # Keep animated image below any hotspot overlays drawn later.
            self._canvas.tag_lower("char_anim")
        else:
            self._canvas.itemconfig(self._item_id, image=self._photo)
        self._frame   += 1
        self._after_id = self._canvas.after(self.INTERVAL_MS, self._tick)

    def _render_frame(self) -> object:
        """Return a PIL Image for the current frame."""
        t = self._frame

        # State-dependent amplitude multipliers
        if self._state == STATE_EXCITED:
            breath_mult, float_mult = 1.8, 1.5
        elif self._state == STATE_TALKING:
            breath_mult, float_mult = 1.3, 0.7
        else:
            breath_mult, float_mult = 1.0, 1.0

        w, h = self._w, self._h

        # ── breathing (subtle vertical zoom) ───────────────────────────────────
        bphase = 2 * math.pi * t / (self.FPS * self.BREATH_CYCLE)
        scale  = 1.0 + self.BREATH_AMP * breath_mult * math.sin(bphase)
        new_h  = int(h * scale)
        scaled = self._base.resize((w, new_h), Image.BILINEAR)
        crop_y = (new_h - h) // 2
        img    = scaled.crop((0, crop_y, w, crop_y + h))

        # ── gentle float (vertical sine drift) ─────────────────────────────────
        fphase = 2 * math.pi * t / (self.FPS * self.FLOAT_CYCLE)
        dy     = int(self.FLOAT_AMP * float_mult * math.sin(fphase))
        if dy != 0:
            canvas_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            if dy > 0:
                canvas_img.paste(img.crop((0, 0, w, h - dy)), (0, dy))
            else:
                canvas_img.paste(img.crop((0, -dy, w, h)), (0, 0))
            img = canvas_img

        # ── blinking ───────────────────────────────────────────────────────────
        self._next_blink -= 1
        if self._next_blink <= 0 and self._blink_phase == 0:
            self._blink_phase    = 1
            self._blink_subframe = 0
        if self._blink_phase > 0:
            img = self._apply_blink(img, w, h)

        return img

    def _apply_blink(self, img: object, w: int, h: int) -> object:
        """Overlay a sliding eyelid strip to simulate natural blinking."""
        eye_y1 = int(h * self.EYE_Y1_FRAC)
        eye_y2 = int(h * self.EYE_Y2_FRAC)
        eye_h  = max(1, eye_y2 - eye_y1)

        if self._blink_phase == 1:           # closing
            progress = self._blink_subframe / max(1, self.BLINK_CLOSE_FRAMES)
            lid_h    = int(eye_h * progress)
            self._blink_subframe += 1
            if self._blink_subframe >= self.BLINK_CLOSE_FRAMES:
                self._blink_phase    = 2
                self._blink_subframe = 0
        elif self._blink_phase == 2:         # shut
            lid_h = eye_h
            self._blink_subframe += 1
            if self._blink_subframe >= self.BLINK_SHUT_FRAMES:
                self._blink_phase    = 3
                self._blink_subframe = 0
        elif self._blink_phase == 3:         # opening
            progress = 1.0 - self._blink_subframe / max(1, self.BLINK_OPEN_FRAMES)
            lid_h    = int(eye_h * progress)
            self._blink_subframe += 1
            if self._blink_subframe >= self.BLINK_OPEN_FRAMES:
                self._blink_phase    = 0
                self._blink_subframe = 0
                self._next_blink     = self._rand_blink_interval()
        else:
            return img

        if lid_h <= 0:
            return img

        # Slide a strip sampled from just above the eye downward over the iris.
        # This mimics a skin-toned eyelid covering the eye as it closes.
        lid_src_y1 = max(0, eye_y1 - 4)
        lid_src_y2 = max(lid_src_y1 + 1, eye_y1)
        lid_strip  = img.crop((0, lid_src_y1, w, lid_src_y2))
        lid_strip  = lid_strip.resize((w, lid_h), Image.NEAREST)
        result     = img.copy()
        result.paste(lid_strip, (0, eye_y1))
        return result
