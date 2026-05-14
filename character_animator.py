"""Character sprite animator for the Honghua visual novel.

Provides Live2D-like effects — breathing, blinking, gentle floating, hair
sway, eye highlight, and a talking-mouth animation — applied to a single PIL
Image and rendered on a tkinter Canvas via the ``after()`` scheduler.  All
effects are purely procedural; no separate layer images are required.
"""
from __future__ import annotations

import math
import random
from typing import Optional

try:
    from PIL import Image, ImageDraw
    _PIL = True
    # Use Resampling enum (Pillow ≥ 9.1); fall back to legacy constants on 9.0.
    _RESAMPLING = getattr(Image, "Resampling", None)
    _BILINEAR   = _RESAMPLING.BILINEAR if _RESAMPLING else Image.BILINEAR  # type: ignore[attr-defined]
    _LANCZOS    = _RESAMPLING.LANCZOS  if _RESAMPLING else Image.LANCZOS   # type: ignore[attr-defined]
    _NEAREST    = _RESAMPLING.NEAREST  if _RESAMPLING else Image.NEAREST   # type: ignore[attr-defined]
except ImportError:
    _PIL = False
    _BILINEAR = _LANCZOS = _NEAREST = 2  # unused when _PIL is False

try:
    from PIL import ImageTk
    _IMAGETK = True
except ImportError:
    _IMAGETK = False

# ── animation states ───────────────────────────────────────────────────────────
STATE_IDLE      = "idle"
STATE_TALKING   = "talking"
STATE_EXCITED   = "excited"
# Trust-level states (map to trust thresholds in game.py)
STATE_IMPATIENT = "impatient"   # 不耐煩 — lowest trust tier (trust < TRUST_THRESHOLD_OBSERVE)
STATE_PEACEFUL  = "peaceful"    # 和平   — observing tier (TRUST_THRESHOLD_OBSERVE ≤ trust < TRUST_THRESHOLD_TRUE)
STATE_FRIENDLY  = "friendly"    # 友善   — growing trust (TRUST_THRESHOLD_TRUE ≤ trust < TRUST_THRESHOLD_SECRET)
STATE_TRUSTED   = "trusted"     # 信任   — highest trust (trust ≥ TRUST_THRESHOLD_SECRET)


class CharacterAnimator:
    """Animate a character image on a tkinter Canvas using PIL transforms.

    Effects
    -------
    *Breathing*      — subtle vertical scale oscillation (~4 s cycle).
    *Floating*       — gentle sine-wave vertical drift (~6 s cycle).
    *Blinking*       — eye-close / open at random intervals (3–7 s).
    *Hair sway*      — 3-band horizontal shift of the top image region (~3.5 s).
    *Eye highlight*  — twinkling specular dot in the eye area
                       (idle, friendly, and trusted states).
    *Talking mouth*  — shadow oval that pulses at the mouth
                       (talking, excited, friendly, and trusted states).
    *Impatient expr* — furrowed-brow shadow + tight lip bar (impatient state).
    *Cheek flush*    — rosy ellipses on both cheeks, optional warm glow
                       (friendly and trusted states).

    The amplitude of each effect scales with the current animation state:
    ``trusted`` ≈ ``peaceful`` < ``idle`` < ``talking`` < ``excited``
    (breathing amp; floating amp varies inversely).  Trust-level states
    (``impatient``, ``peaceful``, ``friendly``, ``trusted``) also add
    expression overlays that reflect Honghua's emotional disposition.

    Usage::

        animator = CharacterAnimator(canvas, width=460, height=490)
        animator.load_image(pil_image)   # PIL RGBA Image, pre-resized
        animator.set_state("talking")
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

    # Hair sway — top HAIR_Y2_FRAC of image shifts horizontally
    HAIR_Y2_FRAC    = 0.32   # hair occupies the top 32 % of the image
    HAIR_SWAY_AMP   = 4      # ±4 px max horizontal shift at hair tips
    HAIR_SWAY_CYCLE = 3.5    # seconds per sway cycle

    # Eye highlight — brief specular dot (idle state only)
    EYE_HL_X_FRAC = 0.42   # horizontal position of highlight (fraction of w)
    EYE_HL_Y_FRAC = 0.25   # vertical position of highlight (fraction of h)
    EYE_HL_R      = 3      # dot radius in pixels
    EYE_HL_CYCLE  = 5.0    # seconds per twinkle pulse

    # Talking mouth — shadow oval pulsing at the mouth region
    # TALK_CYCLE ≈ 0.38 s → ~2.6 mouth open/close cycles per second,
    # which matches natural fast speech cadence (2–3 syllables/s).
    MOUTH_X1_FRAC = 0.25   # mouth region left bound (fraction of w)
    MOUTH_X2_FRAC = 0.75   # mouth region right bound
    MOUTH_Y1_FRAC = 0.44   # mouth region top bound (fraction of h)
    MOUTH_Y2_FRAC = 0.54   # mouth region bottom bound
    TALK_CYCLE    = 0.38   # seconds per mouth open/close cycle (~2.6 Hz)
    # Two-sine model: primary amp + harmonic at TALK_HARMONIC_RATIO produce a
    # natural, aperiodic open/close cadence (≈ 2–3 syllables per second).
    TALK_PRIMARY_AMP    = 0.55   # amplitude of the primary sine wave
    TALK_SECONDARY_AMP  = 0.35   # amplitude of the secondary harmonic
    TALK_HARMONIC_RATIO = 1.9    # irrational ratio → avoids strict periodicity
    TALK_DC_BIAS        = 0.05   # positive offset keeps mouth open ~65 % of cycle
    TALK_OPEN_THRESHOLD = 0.04   # skip drawing if open_factor is below this
    TALK_SHADOW_ALPHA   = 115    # peak alpha of the mouth-shadow ellipse

    # Brow furrow overlay (impatient state)
    BROW_Y1_FRAC      = 0.16   # inner-brow shadow top (fraction of h)
    BROW_Y2_FRAC      = 0.21   # inner-brow shadow bottom
    LIP_PRESS_Y_FRAC  = 0.49   # tight-lip horizontal bar centre (fraction of h)
    # Brow furrow polygon geometry (in pixels from the image centre)
    BROW_FURROW_HALF_W = 22    # half-width of the inverted-V brow shadow
    BROW_FURROW_DEPTH  = 3     # how many px the apex rises above the brow top

    # Cheek flush (friendly / trusted states)
    CHEEK_L_X_FRAC  = 0.27   # left cheek centre (fraction of w)
    CHEEK_R_X_FRAC  = 0.73   # right cheek centre
    CHEEK_Y_FRAC    = 0.36   # cheek vertical centre (fraction of h)
    CHEEK_RX        = 26     # horizontal radius of cheek ellipse (px)
    CHEEK_RY        = 13     # vertical radius of cheek ellipse (px)
    CHEEK_CYCLE     = 4.2    # seconds per cheek-flush pulse
    # Warm face glow constants (trusted state only)
    GLOW_BASE_ALPHA  = 9     # minimum alpha of the amber overlay
    GLOW_VAR_ALPHA   = 4     # amplitude of the pulsing alpha variation
    GLOW_PHASE_MULT  = 0.65  # slows the glow pulse relative to the cheek cycle

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
        """Switch animation state: ``idle`` | ``talking`` | ``excited``
        | ``impatient`` | ``peaceful`` | ``friendly`` | ``trusted``."""
        if self._state == state:
            return
        self._state = state
        # Reset blink cadence to match the new emotional state.
        self._next_blink = self._rand_blink_interval()

    def start(self) -> None:
        """Begin (or restart) the animation loop."""
        if self._after_id is not None:
            self._canvas.after_cancel(self._after_id)
            self._after_id = None
        if _PIL and _IMAGETK and self._base is not None:
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
        if self._state == STATE_IMPATIENT:
            # Nervous / irritated — frequent blinking (~2–4 s).
            return random.randint(2 * self.FPS, 4 * self.FPS)
        if self._state == STATE_TRUSTED:
            # Very relaxed — unhurried blinking (~5–9 s).
            return random.randint(5 * self.FPS, 9 * self.FPS)
        return random.randint(self.BLINK_INTERVAL_MIN, self.BLINK_INTERVAL_MAX)

    def _tick(self) -> None:
        rendered    = self._render_frame()
        self._photo = ImageTk.PhotoImage(rendered.convert("RGB"))  # type: ignore[name-defined]
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
        """Compose all animation effects and return the frame as a PIL Image."""
        t = self._frame

        # State-dependent amplitude multipliers
        if self._state == STATE_EXCITED:
            breath_mult, float_mult = 1.8, 1.5
        elif self._state == STATE_TALKING:
            breath_mult, float_mult = 1.3, 0.7
        elif self._state == STATE_IMPATIENT:
            breath_mult, float_mult = 1.6, 0.5   # tense: jittery breath, suppressed float
        elif self._state == STATE_PEACEFUL:
            breath_mult, float_mult = 0.7, 1.3   # calm: slow breath, gentle drift
        elif self._state == STATE_FRIENDLY:
            breath_mult, float_mult = 1.0, 1.1   # warm and engaged
        elif self._state == STATE_TRUSTED:
            breath_mult, float_mult = 0.6, 1.4   # most relaxed
        else:
            breath_mult, float_mult = 1.0, 1.0

        w, h = self._w, self._h

        # 1. Breathing (subtle vertical zoom) ──────────────────────────────────
        bphase = 2 * math.pi * t / (self.FPS * self.BREATH_CYCLE)
        scale  = 1.0 + self.BREATH_AMP * breath_mult * math.sin(bphase)
        new_h  = int(h * scale)
        scaled = self._base.resize((w, new_h), _BILINEAR)
        crop_y = (new_h - h) // 2
        img    = scaled.crop((0, crop_y, w, crop_y + h))

        # 2. Gentle float (vertical sine drift) ────────────────────────────────
        fphase = 2 * math.pi * t / (self.FPS * self.FLOAT_CYCLE)
        dy     = int(self.FLOAT_AMP * float_mult * math.sin(fphase))
        if dy != 0:
            canvas_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            if dy > 0:
                canvas_img.paste(img.crop((0, 0, w, h - dy)), (0, dy))
            else:
                canvas_img.paste(img.crop((0, -dy, w, h)), (0, 0))
            img = canvas_img

        # 3. Hair sway (horizontal shift on top region, 3-band gradient) ───────
        sphase = 2 * math.pi * t / (self.FPS * self.HAIR_SWAY_CYCLE)
        dx     = int(self.HAIR_SWAY_AMP * math.sin(sphase))
        img    = self._apply_hair_sway(img, w, h, dx)

        # 4. Blinking ──────────────────────────────────────────────────────────
        self._next_blink -= 1
        if self._next_blink <= 0 and self._blink_phase == 0:
            self._blink_phase    = 1
            self._blink_subframe = 0
        if self._blink_phase > 0:
            img = self._apply_blink(img, w, h)

        # 5. Eye highlight — twinkling specular dot (idle, friendly, trusted)
        if self._state in (STATE_IDLE, STATE_FRIENDLY, STATE_TRUSTED):
            img = self._apply_eye_highlight(img, w, h, t)

        # 6. Talking mouth animation (talking / excited / friendly / trusted)
        if self._state in (STATE_TALKING, STATE_EXCITED, STATE_FRIENDLY, STATE_TRUSTED):
            img = self._apply_talking_anim(img, w, h, t)

        # 7. Trust-level expression overlays
        if self._state == STATE_IMPATIENT:
            img = self._apply_impatient_expression(img, w, h)
        elif self._state in (STATE_FRIENDLY, STATE_TRUSTED):
            img = self._apply_cheek_flush(img, w, h, t, self._state == STATE_TRUSTED)

        return img

    # ── effect helpers ─────────────────────────────────────────────────────────

    def _apply_hair_sway(self, img: object, w: int, h: int, dx: int) -> object:
        """Shift the hair region in three horizontal bands (tip → root gradient).

        Band 0 (topmost / tips) receives the full shift *dx*.
        Band 1 (mid) receives 67 % of *dx*.
        Band 2 (roots) receives 33 % of *dx*.
        Edge columns are repeated inward to avoid transparent gaps.
        """
        if dx == 0:
            return img
        hair_y2 = int(h * self.HAIR_Y2_FRAC)
        if hair_y2 <= 0:
            return img
        band_count = 3
        band_h     = max(1, hair_y2 // band_count)
        result     = img.copy()
        for band in range(band_count):
            frac = (band_count - band) / band_count   # 1.0 → 0.67 → 0.33
            bdx  = int(dx * frac)
            if bdx == 0:
                continue
            by1 = band * band_h
            by2 = min((band + 1) * band_h, hair_y2)
            bh  = by2 - by1
            if bh <= 0:
                continue
            strip    = img.crop((0, by1, w, by2))
            new_band = Image.new("RGBA", (w, bh), (0, 0, 0, 0))
            if bdx > 0:
                visible_w = max(0, w - bdx)
                if visible_w > 0:
                    new_band.paste(strip.crop((0, 0, visible_w, bh)), (bdx, 0))
                # Fill the revealed left gap with a repeated edge column.
                edge = strip.crop((0, 0, 1, bh)).resize((bdx, bh), _NEAREST)
                new_band.paste(edge, (0, 0))
            else:
                bdx_abs   = -bdx
                visible_w = max(0, w - bdx_abs)
                if visible_w > 0:
                    new_band.paste(strip.crop((bdx_abs, 0, w, bh)), (0, 0))
                # Fill the revealed right gap with a repeated edge column.
                edge = strip.crop((w - 1, 0, w, bh)).resize((bdx_abs, bh), _NEAREST)
                new_band.paste(edge, (visible_w, 0))
            result.paste(new_band, (0, by1))
        return result

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
        lid_strip  = lid_strip.resize((w, lid_h), _NEAREST)
        result     = img.copy()
        result.paste(lid_strip, (0, eye_y1))
        return result

    def _apply_eye_highlight(self, img: object, w: int, h: int, t: int) -> object:
        """Draw a twinkling specular dot in the eye area (idle state only).

        The alpha uses ``cos(phase) ** 4`` so the dot is briefly bright then
        fades, giving a natural sparkle rather than a uniform pulse.
        """
        phase = 2 * math.pi * t / (self.FPS * self.EYE_HL_CYCLE)
        raw   = math.cos(phase)
        alpha = int(max(0.0, raw) ** 4 * 190)
        if alpha < 4:
            return img
        hx = int(w * self.EYE_HL_X_FRAC)
        hy = int(h * self.EYE_HL_Y_FRAC)
        r  = self.EYE_HL_R
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw    = ImageDraw.Draw(overlay)
        draw.ellipse([hx - r, hy - r, hx + r, hy + r], fill=(255, 255, 255, alpha))
        # Small companion sparkle offset slightly to the upper-right.
        draw.ellipse(
            [hx + r + 1, hy - r - 1, hx + r + 3, hy - r + 1],
            fill=(255, 255, 255, alpha // 2),
        )
        return Image.alpha_composite(img, overlay)

    def _apply_talking_anim(self, img: object, w: int, h: int, t: int) -> object:
        """Pulse a mouth-shadow oval to suggest the lips parting when talking.

        Two sine waves at an irrational frequency ratio (1.0 : 1.9) produce an
        aperiodic, speech-like cadence.  Coefficients: 0.55 (primary amplitude),
        0.35 (secondary), +0.05 (DC bias) keep ``open_factor`` positive for
        roughly 65 % of the cycle so the mouth appears mostly active.
        The composite is done only on the small mouth crop for speed.
        """
        phase       = 2 * math.pi * t / (self.FPS * self.TALK_CYCLE)
        # Primary wave + harmonic at TALK_HARMONIC_RATIO with a small positive
        # bias keeps open_factor > 0 for ~65 % of the cycle (speech-like).
        open_factor = max(
            0.0,
            self.TALK_PRIMARY_AMP   * math.sin(phase)
            + self.TALK_SECONDARY_AMP * math.sin(phase * self.TALK_HARMONIC_RATIO)
            + self.TALK_DC_BIAS,
        )
        if open_factor < self.TALK_OPEN_THRESHOLD:
            return img
        mx1 = int(w * self.MOUTH_X1_FRAC)
        mx2 = int(w * self.MOUTH_X2_FRAC)
        my1 = int(h * self.MOUTH_Y1_FRAC)
        my2 = int(h * self.MOUTH_Y2_FRAC)
        mw  = mx2 - mx1
        mh  = max(1, my2 - my1)
        open_h = max(2, int(mh * 0.50 * open_factor))
        alpha  = int(self.TALK_SHADOW_ALPHA * open_factor)
        sy1    = (mh - open_h) // 2
        pad    = mw // 5
        # Work on a crop of the mouth region only to minimise composite cost.
        mouth_crop = img.crop((mx1, my1, mx2, my2)).convert("RGBA")
        overlay    = Image.new("RGBA", (mw, mh), (0, 0, 0, 0))
        draw       = ImageDraw.Draw(overlay)
        draw.ellipse([pad, sy1, mw - pad, sy1 + open_h], fill=(12, 4, 4, alpha))
        composited = Image.alpha_composite(mouth_crop, overlay)
        result     = img.copy()
        result.paste(composited, (mx1, my1))
        return result

    def _apply_impatient_expression(self, img: object, w: int, h: int) -> object:
        """Furrowed-brow shadow + tight lip-press bar for the *impatient* state.

        A subtle dark V-polygon is drawn over the inner-brow area to suggest a
        frown, and a short horizontal rectangle replaces the open mouth with a
        thin pressed line, conveying suppressed irritation.
        """
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw    = ImageDraw.Draw(overlay)
        # Inner-brow furrow: dark inverted-V shadow
        by1 = int(h * self.BROW_Y1_FRAC)
        by2 = int(h * self.BROW_Y2_FRAC)
        cx  = w // 2
        draw.polygon(
            [(cx - self.BROW_FURROW_HALF_W, by2),
             (cx, by1 + self.BROW_FURROW_DEPTH),
             (cx + self.BROW_FURROW_HALF_W, by2)],
            fill=(10, 4, 4, 52),
        )
        # Lip press: thin dark bar at mouth centre (pursed lips)
        ly  = int(h * self.LIP_PRESS_Y_FRAC)
        lx1 = int(w * self.MOUTH_X1_FRAC) + int(w * 0.09)
        lx2 = int(w * self.MOUTH_X2_FRAC) - int(w * 0.09)
        draw.rectangle([lx1, ly - 1, lx2, ly + 2], fill=(20, 7, 7, 65))
        return Image.alpha_composite(img, overlay)

    def _apply_cheek_flush(
        self, img: object, w: int, h: int, t: int, warm: bool
    ) -> object:
        """Rosy cheek ovals for the *friendly* and *trusted* states.

        *warm* = ``True`` (trusted) produces a deeper rose with a broad amber
        face glow; ``False`` (friendly) uses a softer, lighter pink.
        Both pulse gently via a slow sine wave so the flush feels alive rather
        than painted on.
        """
        phase      = 2 * math.pi * t / (self.FPS * self.CHEEK_CYCLE)
        base_alpha = 44 if warm else 30
        var_alpha  = 16 if warm else 12
        alpha      = int(base_alpha + var_alpha * math.sin(phase))
        colour     = (198, 78, 68, alpha) if warm else (215, 100, 88, alpha)
        rx         = self.CHEEK_RX + (4 if warm else 0)
        ry         = self.CHEEK_RY + (2 if warm else 0)
        cy         = int(h * self.CHEEK_Y_FRAC)
        overlay    = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw       = ImageDraw.Draw(overlay)
        for cx_frac in (self.CHEEK_L_X_FRAC, self.CHEEK_R_X_FRAC):
            cx = int(w * cx_frac)
            draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=colour)
        if warm:
            # Soft amber face glow — very subtle warmth for the trusted state.
            glow_a = int(self.GLOW_BASE_ALPHA + self.GLOW_VAR_ALPHA * math.sin(phase * self.GLOW_PHASE_MULT))
            draw.rectangle(
                [int(w * 0.16), int(h * 0.10),
                 int(w * 0.84), int(h * 0.58)],
                fill=(192, 142, 72, glow_a),
            )
        return Image.alpha_composite(img, overlay)
