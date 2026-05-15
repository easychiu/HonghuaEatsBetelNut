"""
紅花吃檳榔：圖書館夜談 — 深夜完全版
Enhanced visual novel · scene illustrations · BGM
"""
from __future__ import annotations

import os
import random
import threading
from collections.abc import Callable
from typing import Optional

import tkinter as tk
from tkinter import messagebox

import character_texts as CT
import library_map as LM
import story_texts as ST

# ── optional dependencies ──────────────────────────────────────────────────────
try:
    from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageTk
    _PIL = True
    _RESAMPLING = getattr(Image, "Resampling", None)
    _LANCZOS    = _RESAMPLING.LANCZOS if _RESAMPLING else Image.LANCZOS  # type: ignore[attr-defined]
except ImportError:
    _PIL = False
    _LANCZOS = 1  # unused when _PIL is False

try:
    import pygame as _pygame
    _PYGAME = True
except ImportError:
    _PYGAME = False

try:
    from character_animator import CharacterAnimator as _CharacterAnimator
    _ANIMATOR = True
except ImportError:
    _ANIMATOR = False

# ── paths ──────────────────────────────────────────────────────────────────────
_DIR      = os.path.dirname(os.path.abspath(__file__))
INFO_JPG  = os.path.join(_DIR, "info.jpg")
HONGHUA_READ_BOOK_JPG = os.path.join(_DIR, "HonghuaReadBook.jpg")
HONGHUA_IN_ENG_JPG = os.path.join(_DIR, "HonghuaInENG.jpg")
ASSETS    = os.path.join(_DIR, "assets")
SCENES    = os.path.join(ASSETS, "scenes")
CHARACTER_EMOTIONS = os.path.join(ASSETS, "character_emotions")
BGM_MAIN  = os.path.join(ASSETS, "bgm_main.mp3")
BGM_END   = os.path.join(ASSETS, "bgm_end.mp3")
DEFAULT_SCENE_PNG = os.path.join(SCENES, "default.png")
TRUST_EMOTION_ASSETS: dict[str, str] = {
    "impatient": os.path.join(CHARACTER_EMOTIONS, "honghua_readbook_impatient.png"),
    "peaceful": os.path.join(CHARACTER_EMOTIONS, "honghua_readbook_peaceful.png"),
    "friendly": os.path.join(CHARACTER_EMOTIONS, "honghua_readbook_friendly.png"),
    "trusted": os.path.join(CHARACTER_EMOTIONS, "honghua_readbook_trusted.png"),
}

# ── character animation: scene → animator state ────────────────────────────────
# Only scenes that show a character image (via SCENE_SOURCE_OVERRIDES) are listed.
_CHAR_ANIM_SCENES: dict[str, str] = {
    "intro":         "talking",
    "prologue":      "talking",   # Honghua is actively speaking in the prologue
    "hall":          "idle",
    "bookshelves":   "idle",
    "desk":          "idle",
    "diary":         "idle",
    "window":        "idle",
    "basement":      "talking",
    "basement_deep": "excited",
    "confront":      "excited",
}

# Scenes where Honghua is present and facing the player; her animation state
# should reflect the current trust level rather than a fixed value.
_CHAR_ANIM_TRUST_SCENES: frozenset[str] = frozenset({
    "prologue", "hall", "bookshelves", "desk", "diary", "window", "confront",
})

_char_pil_cache: dict[str, object] = {}


def _get_char_pil(path: str) -> Optional[object]:
    """Return a cached RGBA PIL Image sized to the canvas for the given path."""
    if not _PIL:
        return None
    if path not in _char_pil_cache:
        try:
            img = Image.open(path).convert("RGBA")
            if img.size != (IW, IH):
                img = img.resize((IW, IH), _LANCZOS)
            _char_pil_cache[path] = img
        except Exception:
            return None
    return _char_pil_cache.get(path)

SCENE_SOURCE_OVERRIDES: dict[str, str] = {
    "intro": HONGHUA_IN_ENG_JPG,
    "prologue": HONGHUA_READ_BOOK_JPG,
    "hall": HONGHUA_READ_BOOK_JPG,
    "bookshelves": HONGHUA_READ_BOOK_JPG,
    "desk": HONGHUA_READ_BOOK_JPG,
    "diary": HONGHUA_READ_BOOK_JPG,
    "window": HONGHUA_READ_BOOK_JPG,
    "basement": HONGHUA_IN_ENG_JPG,
    "basement_deep": HONGHUA_IN_ENG_JPG,
    "confront": HONGHUA_IN_ENG_JPG,
}

SCENE_TITLES: dict[str, str] = {
    "intro": "開場",
    "prologue": "序章",
    "hall": "圖書館大廳",
    "book": "鎚子線索",
    "feather": "四葉草線索",
    "box": "牛仔褲線索",
    "bookshelves": "書架深處",
    "desk": "研究桌",
    "diary": "紅花筆記",
    "window": "窗邊",
    "window_info": "窗台字條",
    "desk_info": "案情分析",
    "basement": "地下密室",
    "basement_deep": "地下深處",
    "confront": "面對紅花",
    **LM.MAP_SCENE_TITLES,
    "basement_storage": "地下儲藏室",
    # ── new explorable nodes ────────────────────────────────────────────────
    "corridor_1f":   "一樓走廊",
    "corridor_2f":   "二樓走廊",
    "corridor_3f":   "三樓走廊",
    "room_a":        "房間A・教師休息室",
    "room_b":        "房間B・舊社辦",
    "meeting_room":  "會議室",
    # ── time-danger ─────────────────────────────────────────────────────────
    "killer_map":    "大地圖遭遇",
    "true_end": "真結局",
    "secret_end": "秘密結局",
    "normal_end": "普通結局",
    "hidden_end": "隱藏結局",
    "bad_a": "壞結局",
    "bad_b": "密碼失敗",
}

# ── layout ─────────────────────────────────────────────────────────────────────
WIN_W, WIN_H = 1100, 700
IW, IH       = 460, 490        # scene image size
TITLE_H      = 52
STATUS_H     = 28
BTN_H        = 100

# ── gothic palette (extracted from info.jpg) ───────────────────────────────────
C = dict(
    bg        = "#08090d",
    panel     = "#0c0e14",
    title_bg  = "#0e0812",
    title_fg  = "#cc2020",
    border    = "#3a1e28",
    fg        = "#d4c4aa",
    dim       = "#6a5848",
    status_bg = "#0b0a0f",
    status_fg = "#8a7060",
    btn_bg    = "#170919",
    btn_fg    = "#b89068",
    btn_hl    = "#e07030",
    btn_brd   = "#4a2535",
    txt_bg    = "#0a0c12",
    txt_sel   = "#2a1520",
)


def _f(size: int, bold: bool = False) -> tuple:
    w = "bold" if bold else "normal"
    return ("TkDefaultFont", size, w)


# ══════════════════════════════════════════════════════════════════════════════
#  Scene image factory
# ══════════════════════════════════════════════════════════════════════════════
_img_cache: dict[str, object] = {}
_base_img: Optional[object]   = None


def _init_images() -> None:
    global _base_img
    if _PIL and os.path.exists(INFO_JPG):
        _base_img = Image.open(INFO_JPG).convert("RGBA")


def _tinted(
    darken: float = 0.75,
    tint: tuple = (0, 0, 0, 0),
    crop: Optional[tuple] = None,
) -> Optional[object]:
    """Return ImageTk.PhotoImage from info.jpg with tint/darken/crop."""
    if not _PIL or _base_img is None:
        return None
    img = _base_img.copy()
    if crop:
        img = img.crop(crop)
    img = img.resize((IW, IH), Image.LANCZOS)
    img = ImageEnhance.Brightness(img.convert("RGB")).enhance(darken).convert("RGBA")
    if any(tint):
        overlay = Image.new("RGBA", img.size, tint)
        img = Image.alpha_composite(img, overlay)
    return ImageTk.PhotoImage(img.convert("RGB"))


def _atmospheric(
    base_rgb: tuple,
    lights: list,
    blur: float = 2.5,
) -> Optional[object]:
    """Generate a procedural atmospheric scene image with Pillow."""
    if not _PIL:
        return None
    img = Image.new("RGBA", (IW, IH), base_rgb + (255,))
    draw = ImageDraw.Draw(img, "RGBA")
    for cx, cy, r, col in lights:
        rc, gc, bc, ma = col
        for rad in range(r, 0, -3):
            a = int(ma * (1 - rad / r) ** 0.65)
            draw.ellipse([cx - rad, cy - rad, cx + rad, cy + rad],
                         fill=(rc, gc, bc, a))
    if blur > 0:
        img = img.filter(ImageFilter.GaussianBlur(blur))
    # vignette
    v = Image.new("RGBA", (IW, IH), (0, 0, 0, 0))
    vd = ImageDraw.Draw(v, "RGBA")
    maxr = int((IW ** 2 + IH ** 2) ** 0.5) // 2 + 40
    for rad in range(maxr, 0, -5):
        a = int(130 * (rad / maxr) ** 1.5)
        vd.ellipse(
            [IW // 2 - rad, IH // 2 - rad, IW // 2 + rad, IH // 2 + rad],
            fill=(0, 0, 0, a),
        )
    img = Image.alpha_composite(img, v)
    return ImageTk.PhotoImage(img.convert("RGB"))


def scene_image(key: str) -> Optional[object]:
    if key not in _img_cache:
        _img_cache[key] = _build(key)
    return _img_cache[key]


def _load_scene_asset(key: str) -> Optional[object]:
    if not _PIL:
        return None
    path = SCENE_SOURCE_OVERRIDES.get(key)
    if path and os.path.exists(path):
        img = Image.open(path).convert("RGB")
        if img.size != (IW, IH):
            img = img.resize((IW, IH), Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    path = os.path.join(SCENES, f"{key}.png")
    if not os.path.exists(path):
        if os.path.exists(DEFAULT_SCENE_PNG):
            path = DEFAULT_SCENE_PNG
        else:
            return None
    img = Image.open(path).convert("RGB")
    if img.size != (IW, IH):
        img = img.resize((IW, IH), Image.LANCZOS)
    return ImageTk.PhotoImage(img)


def _default_scene_image(key: str) -> Optional[object]:
    if not _PIL:
        return None
    source = (
        SCENE_SOURCE_OVERRIDES.get(key)
        or (HONGHUA_READ_BOOK_JPG if os.path.exists(HONGHUA_READ_BOOK_JPG) else "")
        or (HONGHUA_IN_ENG_JPG if os.path.exists(HONGHUA_IN_ENG_JPG) else "")
        or (INFO_JPG if os.path.exists(INFO_JPG) else "")
    )
    if source:
        img = Image.open(source).convert("RGBA")
        img = img.resize((IW, IH), Image.LANCZOS)
        img = ImageEnhance.Brightness(img.convert("RGB")).enhance(0.68).convert("RGBA")
    else:
        img = Image.new("RGBA", (IW, IH), (12, 10, 18, 255))

    overlay = Image.new("RGBA", img.size, (16, 8, 14, 92))
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle([0, IH - 120, IW, IH], fill=(7, 5, 9, 214))
    draw.rectangle([18, 18, 138, 48], fill=(85, 20, 28, 180))
    draw.text((28, 25), "預設場景", fill=(255, 236, 220))
    draw.text((26, IH - 95), SCENE_TITLES.get(key, "紅花場景"), fill=(230, 214, 192))
    draw.text((26, IH - 63), "若缺少專屬圖像，先以紅花主視覺代替。", fill=(193, 163, 128))
    return ImageTk.PhotoImage(img.convert("RGB"))


def _build(key: str) -> Optional[object]:
    map_img = LM.build_library_map_image(key, IW, IH)
    if map_img is not None:
        return map_img

    prebuilt = _load_scene_asset(key)
    if prebuilt is not None:
        return prebuilt

    # info.jpg-derived scenes  (darken, tint_rgba, crop_box)
    INFO: dict[str, tuple] = {
        "intro":       (0.58, (30, 0, 0, 80),    None),
        "prologue":    (0.62, (0, 10, 20, 60),    None),
        "hall":        (0.52, (0, 15, 35, 70),    None),
        "book":        (0.68, (50, 30, 0, 90),    (0, 600, 800, 880)),
        "feather":     (0.65, (20, 35, 10, 85),   (0, 430, 500, 880)),
        "box":         (0.62, (0, 40, 10, 95),    (550, 580, 1196, 880)),
        "desk_info":   (0.65, (30, 20, 0, 80),    (0, 450, 950, 880)),
        "window_info": (0.55, (0, 10, 30, 90),    (0, 0, 500, 500)),
        "confront":    (0.72, (100, 0, 0, 110),   None),
        "true_end":    (0.82, (50, 25, 0, 55),    None),
        "secret_end":  (0.80, (20, 10, 35, 65),   None),
        "normal_end":  (0.45, (0, 5, 25, 90),     None),
        "hidden_end":  (0.60, (10, 20, 45, 100),  None),
    }
    if key in INFO:
        d, t, c = INFO[key]
        return _tinted(d, t, c)

    # procedural scenes
    PROC: dict[str, tuple] = {
        "bookshelves": (
            (6, 4, 3),
            [(70, IH // 2, 130, (180, 95, 25, 75)),
             (IW - 60, IH // 2 + 40, 95, (120, 60, 15, 55))],
        ),
        "puzzle_book": (
            (5, 5, 8),
            [(IW // 2, IH // 2, 220, (160, 110, 40, 85)),
             (IW // 2, IH // 2, 75, (220, 170, 80, 90))],
        ),
        "desk": (
            (5, 7, 4),
            [(IW // 2, IH - 80, 220, (210, 125, 40, 100)),
             (IW // 2, IH - 80, 75, (255, 185, 85, 110))],
        ),
        "diary": (
            (11, 7, 4),
            [(IW // 2, IH // 2, 185, (200, 155, 75, 90)),
             (IW // 2 - 70, IH // 2 + 30, 65, (255, 200, 115, 75))],
        ),
        "window": (
            (4, 7, 12),
            [(IW // 2, 75, 170, (30, 55, 85, 95)),
             (IW // 2, 75, 55, (60, 95, 145, 75))],
        ),
        "basement": (
            (3, 3, 7),
            [(IW // 2, IH, 210, (18, 25, 58, 80)),
             (IW // 2, IH // 2, 38, (38, 48, 88, 55))],
        ),
        "basement_deep": (
            (2, 2, 5),
            [(IW // 2, IH // 2, 160, (65, 0, 20, 105)),
             (IW // 2, IH // 2, 48, (105, 0, 28, 80))],
        ),
        "bad_a": (
            (5, 0, 0),
            [(IW // 2, IH // 2, 190, (155, 0, 0, 120)),
             (IW // 2, IH // 2, 58, (200, 20, 20, 95))],
        ),
        "bad_b": (
            (7, 1, 1),
            [(IW // 2, IH // 2, 225, (185, 0, 18, 130)),
             (IW // 4, IH // 3, 105, (225, 45, 0, 100)),
             (3 * IW // 4, 2 * IH // 3, 82, (205, 28, 8, 88))],
        ),
        "corridor_1f": (
            (4, 4, 3),
            [(IW // 2, IH // 2, 200, (110, 75, 30, 65)),
             (IW - 80, IH // 2, 90, (90, 55, 18, 50))],
        ),
        "corridor_2f": (
            (3, 3, 4),
            [(80, IH // 2, 140, (80, 55, 20, 70)),
             (IW // 2, IH - 100, 170, (60, 40, 15, 55))],
        ),
        "corridor_3f": (
            (5, 5, 4),
            [(IW // 2, 100, 190, (140, 100, 50, 70)),
             (IW // 2, IH // 2, 80, (180, 140, 70, 60))],
        ),
        "room_a": (
            (6, 5, 4),
            [(IW // 2, IH // 2, 190, (120, 80, 35, 75)),
             (IW // 2, IH // 2, 60, (170, 120, 55, 60))],
        ),
        "room_b": (
            (4, 5, 5),
            [(60, IH // 3, 120, (90, 65, 30, 65)),
             (IW // 2, 2 * IH // 3, 160, (70, 50, 20, 55))],
        ),
        "meeting_room": (
            (5, 4, 3),
            [(IW // 2, IH // 3, 200, (100, 65, 25, 70)),
             (IW // 2, 2 * IH // 3, 70, (140, 90, 35, 55))],
        ),
    }
    if key in PROC:
        base_rgb, lights = PROC[key]
        return _atmospheric(base_rgb, lights)

    return _default_scene_image(key)


class MusicPlayer:
    """Thin wrapper around pygame.mixer for looping BGM."""

    def __init__(self) -> None:
        self._ready = False
        if _PYGAME:
            try:
                _pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
                _pygame.mixer.init()
                self._ready = True
            except Exception:
                pass

    def play(self, path: str, loops: int = -1) -> None:
        if not self._ready or not os.path.exists(path):
            return
        try:
            _pygame.mixer.music.load(path)
            _pygame.mixer.music.set_volume(0.50)
            _pygame.mixer.music.play(loops)
        except Exception:
            pass

    def switch(self, path: str) -> None:
        if not self._ready:
            return
        try:
            _pygame.mixer.music.fadeout(2500)
        except Exception:
            pass
        threading.Timer(2.6, lambda: self.play(path)).start()

    def stop(self) -> None:
        if self._ready:
            try:
                _pygame.mixer.music.stop()
            except Exception:
                pass


class _NullAnimator:
    """No-op animator used when character_animator is unavailable."""

    def load_image(self, _: object) -> None: ...
    def set_state(self, _: str) -> None: ...
    def set_focus_point(self, _x: int, _y: int) -> None: ...
    def clear_focus(self) -> None: ...
    def set_lip_sync_intensity(self, _intensity: float) -> None: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...


# ══════════════════════════════════════════════════════════════════════════════
#  HonghuaGame
# ══════════════════════════════════════════════════════════════════════════════
class HonghuaGame:
    # ── puzzle answers ─────────────────────────────────────────────────────────
    CODE_ANSWER      = "314"

    # ── Honghua click OS lines (cycle on every click) ──────────────────────────
    # "怎麼點擊都是表現優雅，但旁邊台詞會有主角OS"
    _HONGHUA_OS_LINES = CT.HONGHUA_OS_LINES
    BOOKSHELF_CORRECT_ORDER = CT.BOOKSHELF_CORRECT_ORDER
    REQUIRED_CLUES   = 3
    REQUIRED_LORE    = 3
    PARTIAL_CLUES    = 2
    MAX_CODE_TRIES   = 3
    HAMMER_LENGTH_CM = 30
    TRUST_THRESHOLD_SECRET   = 7  # minimum trust for the secret ending
    TRUST_THRESHOLD_TRUE     = 4  # minimum trust for the true ending path
    TRUST_THRESHOLD_ALLIANCE = 6  # minimum trust for the alliance ending
    TRUST_THRESHOLD_OBSERVE  = 1  # minimum trust to move past outright distrust
    WINDOW_TITLE     = "紅花吃檳榔：蔚藍學院秘案 - 深夜調查版"
    STORAGE_AMBUSH_CHANCE = 0.20          # generalised 1F/2F backstab chance
    STORAGE_AMBUSH_CHANCE_HIGH = 0.65    # near the killer's hideout (basement storage room)
    # ── time & killer system ─────────────────────────────────────────────────
    GAME_START_HOUR    = 23              # game clock starts at 23:00
    KILLER_EMERGE_ELAPSED = 180          # minutes of game-time before 2AM (23:00 + 3h)
    KILLER_MAP_AMBUSH_CHANCE = 0.30      # per floor-map visit after 2AM
    KILLER_MAP_AMBUSH_CHANCE_3F = 0.05   # 3F is much safer (away from killer's basement lair)
    KILLER_PATROL_INTERVAL_MS = 90_000   # ms between killer floor changes
    MIN_FLOOR = 1                        # lowest library floor accessible to player
    MAX_FLOOR = 3                        # highest library floor (safe zone)
    TYPEWRITER_PAUSE_CHARS = "，。！？、 \n\t"

    # ── init ───────────────────────────────────────────────────────────────────
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(self.WINDOW_TITLE)
        self.root.geometry(f"{WIN_W}x{WIN_H}")
        self.root.minsize(900, 600)
        self.root.configure(bg=C["bg"])

        _init_images()

        self.inventory: set[str] = set()
        self.clues: dict[str, int] = {}
        self.lore: set[str] = set()
        self.trust = 0
        self._trust_events: set[str] = set()
        self.code_tries_left = self.MAX_CODE_TRIES
        self._type_job: Optional[str] = None
        self._current_img: Optional[object] = None
        self._current_scene: str = ""
        self._image_actions: list[dict[str, object]] = []
        self._hover_action: Optional[int] = None
        self._honghua_click_count: int = 0
        self._map_floor: int = 3
        self._ambush_job: Optional[str] = None
        # ── time & killer state ─────────────────────────────────────────────
        self._game_elapsed: int = 0          # minutes elapsed since game start (23:00)
        self._killer_emerged: bool = False
        self._killer_floor: int = 1          # current floor killer is patrolling (1-3)
        self._killer_patrol_job: Optional[str] = None

        self.music = MusicPlayer()

        self._build_ui()
        self.animator: object = (
            _CharacterAnimator(self.img_canvas, IW, IH) if _ANIMATOR else _NullAnimator()
        )
        self.music.play(BGM_MAIN)
        self.show_intro()

    # ── UI construction ────────────────────────────────────────────────────────
    def _build_ui(self) -> None:
        # title bar
        title_bar = tk.Frame(self.root, bg=C["title_bg"], height=TITLE_H, bd=0)
        title_bar.pack(fill="x", side="top")
        title_bar.pack_propagate(False)
        tk.Label(
            title_bar,
            text="✦  " + self.WINDOW_TITLE + "  ✦",
            font=_f(13, True),
            bg=C["title_bg"],
            fg=C["title_fg"],
        ).pack(side="left", padx=16, pady=10)

        # main content row
        content = tk.Frame(self.root, bg=C["bg"])
        content.pack(fill="both", expand=True, padx=8, pady=(6, 0))

        # left: scene image canvas
        left = tk.Frame(
            content, bg=C["panel"], bd=0,
            highlightbackground=C["border"], highlightthickness=1,
        )
        left.pack(side="left", fill="y", padx=(0, 6))
        self.img_canvas = tk.Canvas(
            left, width=IW, height=IH,
            bg=C["panel"], bd=0, highlightthickness=0,
        )
        self.img_canvas.pack()
        self.img_canvas.bind("<Button-1>", self._on_image_click)
        self.img_canvas.bind("<Motion>", self._on_image_motion)
        self.img_canvas.bind("<Leave>", self._on_image_leave)

        # right: story + status + buttons
        right = tk.Frame(content, bg=C["bg"])
        right.pack(side="left", fill="both", expand=True)

        # story text
        txt_frame = tk.Frame(
            right, bg=C["border"], bd=0,
            highlightbackground=C["border"], highlightthickness=1,
        )
        txt_frame.pack(fill="both", expand=True)
        self.story_text = tk.Text(
            txt_frame,
            wrap="word",
            font=_f(12),
            bg=C["txt_bg"],
            fg=C["fg"],
            insertbackground=C["fg"],
            selectbackground=C["txt_sel"],
            relief="flat",
            bd=0,
            padx=14,
            pady=12,
            spacing1=3,
            spacing2=2,
            spacing3=3,
        )
        self.story_text.pack(fill="both", expand=True)
        self.story_text.configure(state="disabled")

        # status bar
        self.status_var = tk.StringVar(value="準備中...")
        status_bar = tk.Frame(right, bg=C["status_bg"], height=STATUS_H)
        status_bar.pack(fill="x", pady=(4, 0))
        status_bar.pack_propagate(False)
        tk.Label(
            status_bar,
            textvariable=self.status_var,
            font=_f(9),
            bg=C["status_bg"],
            fg=C["status_fg"],
            anchor="w",
            padx=8,
        ).pack(fill="x", expand=True)

        # button bar
        self.btn_frame = tk.Frame(right, bg=C["bg"], height=BTN_H)
        self.btn_frame.pack(fill="x", pady=(5, 4))

    # ── helpers ────────────────────────────────────────────────────────────────
    def _show_image(self, key: str) -> None:
        # Cancel any pending backstab ambush from the previous scene.
        if self._ambush_job:
            self.root.after_cancel(self._ambush_job)
            self._ambush_job = None
        self._current_scene = key
        self.animator.stop()
        self.img_canvas.delete("all")
        self._image_actions = []
        self._hover_action  = None

        # Use the character animator for scenes that show a character image.
        anim_state = _CHAR_ANIM_SCENES.get(key)
        src_path   = SCENE_SOURCE_OVERRIDES.get(key)
        if key in _CHAR_ANIM_TRUST_SCENES:
            trust_state = self._trust_anim_state()
            anim_state = trust_state
            trust_path = TRUST_EMOTION_ASSETS.get(trust_state, "")
            if trust_path and os.path.exists(trust_path):
                src_path = trust_path
        if anim_state and src_path and _PIL and os.path.exists(src_path):
            base = _get_char_pil(src_path)
            if base is not None:
                self.animator.load_image(base)
                self.animator.set_state(anim_state)
                self.animator.clear_focus()
                self.animator.set_lip_sync_intensity(0.0)
                self.animator.start()
                self._current_img = None
                return

        # Fall back to the static scene image.
        img = scene_image(key)
        self._current_img = img
        if img:
            self.img_canvas.create_image(0, 0, anchor="nw", image=img)
        else:
            self.img_canvas.configure(bg=C["panel"])

    def _set_image_actions(self, actions: list[dict[str, object]]) -> None:
        self._image_actions = actions
        self._hover_action = None
        self._render_image_actions()

    def _render_image_actions(self) -> None:
        self.img_canvas.delete("hotspot")
        for idx, action in enumerate(self._image_actions):
            x1, y1, x2, y2 = action["area"]
            active = idx == self._hover_action
            outline = C["btn_hl"] if active else C["btn_brd"]
            width = 3 if active else 2
            self.img_canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                outline=outline,
                width=width,
                dash=(6, 3),
                tags=("hotspot",),
            )
            # Use a custom hover hint when provided; otherwise fall back to the
            # default "點擊：{label}" format.
            hint = action.get("hint", f"點擊：{action['label']}")
            self.img_canvas.create_text(
                x1 + 8,
                y1 + 10,
                anchor="nw",
                text=hint,
                fill=C["btn_hl"] if active else C["fg"],
                font=_f(10, True),
                tags=("hotspot",),
            )
        self.img_canvas.configure(cursor="hand2" if self._hover_action is not None else "")

    def _image_action_at(self, x: int, y: int) -> Optional[int]:
        for idx, action in enumerate(self._image_actions):
            x1, y1, x2, y2 = action["area"]
            if x1 <= x <= x2 and y1 <= y <= y2:
                return idx
        return None

    def _on_image_click(self, event: tk.Event) -> None:
        idx = self._image_action_at(event.x, event.y)
        if idx is None:
            return
        cb = self._image_actions[idx]["command"]
        cb()

    def _on_image_motion(self, event: tk.Event) -> None:
        idx = self._image_action_at(event.x, event.y)
        if idx == self._hover_action:
            if self._current_scene in _CHAR_ANIM_SCENES:
                self.animator.set_focus_point(event.x, event.y)
            return
        self._hover_action = idx
        self._render_image_actions()
        if self._current_scene in _CHAR_ANIM_SCENES:
            self.animator.set_focus_point(event.x, event.y)

    def _on_image_leave(self, _event: tk.Event) -> None:
        if self._current_scene in _CHAR_ANIM_SCENES:
            self.animator.clear_focus()
        if self._hover_action is None:
            return
        self._hover_action = None
        self._render_image_actions()

    def _set_story(self, text: str, typing: bool = True) -> None:
        if self._type_job:
            self.root.after_cancel(self._type_job)
            self._type_job = None
        self.story_text.configure(state="normal")
        self.story_text.delete("1.0", "end")
        self.story_text.configure(state="disabled")
        if typing:
            if self._current_scene in _CHAR_ANIM_SCENES:
                self.animator.set_lip_sync_intensity(0.55)
            self._type_text(text, 0)
        else:
            self.story_text.configure(state="normal")
            self.story_text.insert("1.0", text)
            self.story_text.configure(state="disabled")
            self.animator.set_lip_sync_intensity(0.0)

    def _type_text(self, text: str, idx: int) -> None:
        if idx >= len(text):
            # Ensure the full text is displayed on the last frame
            self.story_text.configure(state="normal")
            self.story_text.delete("1.0", "end")
            self.story_text.insert("1.0", text)
            self.story_text.configure(state="disabled")
            self.animator.set_lip_sync_intensity(0.0)
            self._type_job = None
            return
        self.story_text.configure(state="normal")
        self.story_text.delete("1.0", "end")
        self.story_text.insert("1.0", text[:idx])
        self.story_text.configure(state="disabled")
        self.story_text.see("end")
        if self._current_scene in _CHAR_ANIM_SCENES:
            prev_char = text[idx - 1] if idx > 0 else ""
            intensity = 0.65 if prev_char not in self.TYPEWRITER_PAUSE_CHARS else 0.35
            self.animator.set_lip_sync_intensity(intensity)
        self._type_job = self.root.after(16, self._type_text, text, idx + 1)

    def _clear_buttons(self) -> None:
        for w in self.btn_frame.winfo_children():
            w.destroy()

    def _set_options(self, options: list[tuple[str, Callable]]) -> None:
        self._clear_buttons()
        for label, cb in options:
            btn = tk.Button(
                self.btn_frame,
                text=label,
                command=cb,
                font=_f(11, True),
                bg=C["btn_bg"],
                fg=C["btn_fg"],
                activebackground=C["btn_hl"],
                activeforeground="#ffffff",
                relief="flat",
                bd=0,
                padx=14,
                pady=8,
                cursor="hand2",
            )
            btn.pack(side="left", padx=5, pady=6)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#2e1030"))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=C["btn_bg"]))

    def _refresh_status(self) -> None:
        items  = "、".join(sorted(self.inventory)) or "無"
        lore_n = len(self.lore)
        tries  = self.code_tries_left
        self.status_var.set(self._format_status_text(items, len(self.clues), tries, lore_n))

    def _reset_state(self) -> None:
        if self._ambush_job:
            self.root.after_cancel(self._ambush_job)
            self._ambush_job = None
        if self._killer_patrol_job:
            self.root.after_cancel(self._killer_patrol_job)
            self._killer_patrol_job = None
        self.inventory.clear()
        self.clues.clear()
        self.lore.clear()
        self.trust = 0
        self._trust_events.clear()
        self.code_tries_left = self.MAX_CODE_TRIES
        self._honghua_click_count = 0
        self._map_floor = 3
        self._game_elapsed = 0
        self._killer_emerged = False
        self._killer_floor = 1
        self._killer_patrol_job = None
        self._refresh_status()

    def _schedule_ambush_check(self, chance: Optional[float] = None) -> None:
        """Schedule a backstab check 800 ms after a risky scene loads.

        Used by 1F/2F and basement scenes.
        The delay lets the player read the scene before the ambush fires.
        Navigating away cancels the check via _show_image().
        """
        if chance is None:
            chance = self.STORAGE_AMBUSH_CHANCE
        if self._ambush_job:
            self.root.after_cancel(self._ambush_job)
        self._ambush_job = self.root.after(
            800,
            lambda: self._resolve_ambush(chance),
        )

    def _resolve_ambush(self, chance: float) -> None:
        self._ambush_job = None
        if random.random() < chance:
            self.ending_storage_ambush()

    def _trust_level(self) -> str:
        if self.trust >= self.TRUST_THRESHOLD_SECRET:
            return "高度信任"
        if self.trust >= self.TRUST_THRESHOLD_TRUE:
            return "逐步信任"
        if self.trust >= self.TRUST_THRESHOLD_OBSERVE:
            return "觀望中"
        return "不信任"

    def _trust_anim_state(self) -> str:
        """Return the animator state string matching the current trust tier."""
        if self.trust >= self.TRUST_THRESHOLD_SECRET:
            return "trusted"
        if self.trust >= self.TRUST_THRESHOLD_TRUE:
            return "friendly"
        if self.trust >= self.TRUST_THRESHOLD_OBSERVE:
            return "peaceful"
        return "impatient"

    # ── time & killer mechanics ────────────────────────────────────────────────

    def _format_time(self) -> str:
        """Return current in-game time as HH:MM (24-hour)."""
        total = (self.GAME_START_HOUR * 60 + self._game_elapsed) % (24 * 60)
        return f"{total // 60:02d}:{total % 60:02d}"

    def _advance_time(self, minutes: int = 5) -> None:
        """Advance the in-game clock and trigger 2AM killer emergence if threshold reached."""
        self._game_elapsed += minutes
        self._refresh_status()
        if not self._killer_emerged and self._game_elapsed >= self.KILLER_EMERGE_ELAPSED:
            self._trigger_killer_emergence()

    def _trigger_killer_emergence(self) -> None:
        """Mark killer as emerged, show warning, and start patrol loop."""
        self._killer_emerged = True
        self._killer_floor = random.randint(self.MIN_FLOOR, self.MAX_FLOOR)
        # Start patrol tick loop.
        self._killer_patrol_job = self.root.after(
            self.KILLER_PATROL_INTERVAL_MS, self._killer_patrol_tick
        )
        messagebox.showwarning("凌晨兩點警告", ST.DANGER_2AM)

    def _killer_patrol_tick(self) -> None:
        """Periodically move killer to a random floor."""
        if not self._killer_emerged:
            return
        self._killer_floor = random.randint(self.MIN_FLOOR, self.MAX_FLOOR)
        self._killer_patrol_job = self.root.after(
            self.KILLER_PATROL_INTERVAL_MS, self._killer_patrol_tick
        )

    def _check_map_killer(self, floor: int) -> bool:
        """Return True (and go to bad ending D) if killer encounters player on this floor.

        Only active after 2AM.  3F has a much lower encounter rate since the
        killer's territory is the basement / lower floors.
        """
        if not self._killer_emerged:
            return False
        chance = (
            self.KILLER_MAP_AMBUSH_CHANCE_3F
            if floor == 3
            else self.KILLER_MAP_AMBUSH_CHANCE
        )
        if self._killer_floor == floor and random.random() < chance:
            self.ending_killer_map()
            return True
        return False

    def _gain_trust(self, event: str, points: int) -> None:
        if event in self._trust_events:
            return
        self._trust_events.add(event)
        self.trust += points
        # If Honghua is currently visible, update her expression immediately.
        if self._current_scene in _CHAR_ANIM_TRUST_SCENES:
            self.animator.set_state(self._trust_anim_state())

    def _format_status_text(
        self,
        items: str,
        clue_count: int,
        tries: int,
        lore_n: int,
    ) -> str:
        trust_label = self._trust_level()
        time_str = self._format_time()
        danger_flag = "  ⚠兇手出沒中" if self._killer_emerged else ""
        return (
            f"現在 {time_str}{danger_flag} | 道具:{items} | 物證:{clue_count}/{self.REQUIRED_CLUES} | "
            f"密碼:{tries} | 線索:{lore_n}/{self.REQUIRED_LORE} | 信任:{self.trust}({trust_label})"
        )

    # ── interactive OS helpers ─────────────────────────────────────────────────

    def _append_os(self, text: str) -> None:
        """Append a protagonist inner-monologue (OS) line to the story box.

        Unlike ``_set_story``, this does *not* clear the existing text or
        trigger a page navigation — it just appends to whatever is currently
        visible, giving the feel of a live thought bubble.
        """
        if self._type_job:
            self.root.after_cancel(self._type_job)
            self._type_job = None
        self.story_text.configure(state="normal")
        self.story_text.insert("end", f"\n\n【主角OS】{text}")
        self.story_text.see("end")
        self.story_text.configure(state="disabled")
        if self._current_scene in _CHAR_ANIM_SCENES:
            self.animator.set_lip_sync_intensity(0.7)

    def _on_honghua_click(self) -> None:
        """Cycle through the protagonist's inner thoughts when clicking Honghua.

        Honghua herself stays graceful (animation state unchanged); only the
        story text gains a new OS line.  Lines rotate every 3 clicks.
        """
        line = self._HONGHUA_OS_LINES[
            self._honghua_click_count % len(self._HONGHUA_OS_LINES)
        ]
        self._honghua_click_count += 1
        self._append_os(line)

    def _on_book_regular_click(self) -> None:
        """Protagonist notices an unremarkable book on the shelf."""
        self._append_os("就是一本書……")

    def _on_book_bl_click(self) -> None:
        """Easter-egg: protagonist spots the suspicious title on a spine."""
        self._append_os(
            "等等這書名是啥……\n"
            "《傑克森與伍茲的冬夜》……\n"
            "居然還有這種一看書名就是BL的書。"
        )

    def _on_book_clue_click(self) -> None:
        """Game-relevant clue hidden in an old annual report on the shelf.

        First interaction gives +1 trust (the player is being thorough) and
        adds the clue to ``lore``; subsequent clicks just remind the player.
        """
        if "圖書館年報" not in self.lore:
            self.lore.add("圖書館年報")
            self._gain_trust("book_annual", 1)
            self._refresh_status()
            self._append_os(
                "《蔚藍學院圖書館・年度登記冊》……\n"
                "翻到案發當夜那一頁——\n"
                "入館紀錄第三欄：T.S.（天王星）　23:14 入館。\n"
                "【線索】天王星案發當晚確實在場。"
            )
        else:
            self._append_os("（已記下年度登記冊的入館紀錄。）")

    # ══════════════════════════════════════════════════════════════════════════
    #  Scenes
    # ══════════════════════════════════════════════════════════════════════════

    def show_intro(self) -> None:
        self._reset_state()
        self._show_image("intro")
        self._set_story(ST.INTRO, typing=False)
        self._set_options([("進入故事", self.scene_prologue)])

    def scene_prologue(self) -> None:
        self._show_image("prologue")
        self._set_story(ST.PROLOGUE.format(hammer_length=self.HAMMER_LENGTH_CM))
        self._set_options([
            ("查看地圖", self.scene_map_floor3),
            ("直接前往管理室外調查", self.scene_hall),
            ("直接上前與紅花說話", self.scene_confront),
        ])
        # Prologue: Honghua is front-and-centre — add her click hotspot.
        # Coordinates are (x1, y1, x2, y2) measured from the top-left corner
        # of the 460×490 canvas in pixels.  To adjust: open HonghuaReadBook.jpg
        # in any image editor, hover over the character boundary and read off
        # the pixel coordinates shown in the status bar.
        self._set_image_actions([
            {
                "label": "紅花",
                "area": (70, 30, 360, 280),
                "command": self._on_honghua_click,
                "hint": "……",
            },
        ])

    # ── main hall (hub) ───────────────────────────────────────────────────────
    def scene_hall(self) -> None:
        self._refresh_status()
        self._show_image("hall")
        has_key = "地下室鑰匙" in self.inventory
        basement_hint = "\n（口袋中有一把通往地下密室的鑰匙……）" if has_key else ""

        trust_remark = CT.TRUST_REMARKS.get(self._trust_level(), "")
        self._set_story(
            ST.HALL.format(
                trust_remark=trust_remark,
                hammer_length=self.HAMMER_LENGTH_CM,
                basement_hint=basement_hint,
            )
        )
        opts: list[tuple[str, Callable]] = [
            ("回到上帝視角地圖", self.scene_map_floor3),
            ("前往書架深處", self.scene_bookshelves),
            ("前往研究桌", self.scene_desk),
            ("前往窗邊", self.scene_window),
        ]
        if has_key:
            opts.append(("打開地下密室", self.scene_basement))
        opts += [
            ("前去面對紅花", self.scene_confront),
        ]
        self._set_options(opts)
        # ── image hotspots ────────────────────────────────────────────────────
        # All coordinates are (x1, y1, x2, y2) from the top-left of the
        # 460×490 canvas in pixels.  To calibrate: open HonghuaReadBook.jpg
        # in an image editor and read pixel coordinates from its status bar.
        # More-specific (smaller) areas are listed BEFORE the larger Honghua
        # area so they take priority when both overlap at the same pixel.
        hall_actions: list[dict[str, object]] = [
            # ── existing investigation items ─────────────────────────────────
            {"label": "鎚子",  "area": (24, 316, 126, 470), "command": self.inspect_hammer},
            {"label": "四葉草", "area": (152, 266, 246, 386), "command": self.inspect_clover},
            {"label": "牛仔褲", "area": (286, 316, 426, 468), "command": self.inspect_jeans},
            {"label": "密碼盒", "area": (316, 146, 448, 278), "command": self.try_unlock},
            # ── book hotspots (upper-left bookshelf area) ────────────────────
            {
                "label": "書架上的書",
                "area": (14, 44, 118, 152),
                "command": self._on_book_regular_click,
                "hint": "點擊：書架上的書",
            },
            {
                "label": "角落的舊書",
                "area": (126, 44, 256, 152),
                "command": self._on_book_bl_click,
                "hint": "點擊：角落的舊書",
            },
            {
                "label": "封面泛黃的年報",
                "area": (14, 158, 160, 258),
                "command": self._on_book_clue_click,
                "hint": "點擊：封面泛黃的年報",
            },
            # ── Honghua (centre of image; listed last so books take priority
            #    where areas overlap) ──────────────────────────────────────────
            {
                "label": "紅花",
                "area": (70, 30, 310, 260),
                "command": self._on_honghua_click,
                "hint": "……",
            },
        ]
        self._set_image_actions(hall_actions)

    def scene_map_floor1(self) -> None:
        self._advance_time(2)
        if not self._check_map_killer(1):
            self.scene_library_map(1)

    def scene_map_floor2(self) -> None:
        self._advance_time(2)
        if not self._check_map_killer(2):
            self.scene_library_map(2)

    def scene_map_floor3(self) -> None:
        self._advance_time(2)
        if not self._check_map_killer(3):
            self.scene_library_map(3)

    def scene_library_map(self, floor: int) -> None:
        LM.show_library_map_scene(self, floor)

    # ── hammer ────────────────────────────────────────────────────────────────
    def inspect_hammer(self) -> None:
        self._advance_time(5)
        self._gain_trust("inspect_hammer", 1)
        self.clues["鎚子"] = 3
        self._refresh_status()
        self._show_image("book")
        trust_reaction = CT.TRUST_REACTIONS["inspect_hammer"].get(self._trust_level(), "")
        self._set_story(
            ST.INSPECT_HAMMER.format(hammer_length=self.HAMMER_LENGTH_CM)
            + trust_reaction
        )
        self._set_options([
            ("繼續調查", self.scene_map_floor3),
            ("直接面對紅花", self.scene_confront),
        ])

    # ── four-leaf clover ──────────────────────────────────────────────────────
    def inspect_clover(self) -> None:
        self._advance_time(5)
        self._gain_trust("inspect_clover", 1)
        self.clues["四葉草"] = 1
        self._refresh_status()
        self._show_image("feather")
        trust_reaction = CT.TRUST_REACTIONS["inspect_clover"].get(self._trust_level(), "")
        self._set_story(
            ST.INSPECT_CLOVER
            + trust_reaction
        )
        self._set_options([
            ("繼續調查", self.scene_map_floor3),
            ("直接面對紅花", self.scene_confront),
        ])

    # ── YV jeans ──────────────────────────────────────────────────────────────
    def inspect_jeans(self) -> None:
        self._advance_time(5)
        self._gain_trust("inspect_jeans", 1)
        self.clues["牛仔褲"] = 4
        self._refresh_status()
        self._show_image("box")
        trust_reaction = CT.TRUST_REACTIONS["inspect_jeans"].get(self._trust_level(), "")
        self._set_story(
            ST.INSPECT_JEANS
            + trust_reaction
        )
        self._set_options([
            ("繼續調查", self.scene_map_floor3),
        ])

    # ── bookshelves area ──────────────────────────────────────────────────────
    def scene_bookshelves(self) -> None:
        self._advance_time(8)
        self._refresh_status()
        self._show_image("bookshelves")
        self._set_story(ST.SCENE_BOOKSHELVES)
        self._set_options([
            ("離開書架，返回走廊", self.scene_map_floor1),
        ])
        self._set_image_actions([
            {"label": "案卷謎題", "area": (82, 108, 380, 360), "command": self.puzzle_bookshelf},
        ])
        self._schedule_ambush_check()  # 1F – backstab risk

    def puzzle_bookshelf(self) -> None:
        if "地下室鑰匙" in self.inventory:
            messagebox.showinfo("已解鎖", "地下密室的鑰匙已在你手中。")
            self.scene_map_floor1()
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("案件時間線——事件排序")
        dialog.geometry("620x500")
        dialog.configure(bg=C["bg"])
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog,
            text="請依事件發生順序，點擊下方四份案卷完成時間線：",
            font=_f(11),
            bg=C["bg"],
            fg=C["fg"],
            wraplength=560,
        ).pack(pady=14, padx=14)

        docs = list(self.BOOKSHELF_CORRECT_ORDER)
        selected_order: list[str] = []
        order_var = tk.StringVar(value="目前順序：尚未選擇")
        canvas = tk.Canvas(
            dialog,
            width=560,
            height=250,
            bg=C["panel"],
            highlightbackground=C["border"],
            highlightthickness=1,
            bd=0,
        )
        canvas.pack(padx=18, pady=(0, 10))
        boxes = [
            (30, 24, 260, 108),
            (300, 24, 530, 108),
            (30, 142, 260, 226),
            (300, 142, 530, 226),
        ]

        def redraw_docs() -> None:
            canvas.delete("all")
            for doc, box in zip(docs, boxes, strict=True):
                x1, y1, x2, y2 = box
                chosen_idx = selected_order.index(doc) + 1 if doc in selected_order else None
                outline = C["btn_hl"] if chosen_idx else C["btn_brd"]
                canvas.create_rectangle(
                    x1, y1, x2, y2,
                    outline=outline,
                    width=3 if chosen_idx else 2,
                    fill=C["txt_bg"],
                )
                if chosen_idx:
                    canvas.create_text(
                        x1 + 18,
                        y1 + 18,
                        anchor="nw",
                        text=f"{chosen_idx}.",
                        fill=C["btn_hl"],
                        font=_f(12, True),
                    )
                canvas.create_text(
                    (x1 + x2) // 2,
                    (y1 + y2) // 2,
                    text=doc,
                    fill=C["fg"],
                    width=max(120, x2 - x1 - 40),
                    font=_f(11, True),
                )

        def update_order_text() -> None:
            if selected_order:
                order_var.set("目前順序：" + " → ".join(selected_order))
            else:
                order_var.set("目前順序：尚未選擇")

        def select_doc(event: tk.Event) -> None:
            for doc, box in zip(docs, boxes, strict=True):
                x1, y1, x2, y2 = box
                if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                    if doc in selected_order:
                        order_var.set(f"「{doc}」已經選過了，若要重排請按「重新排列」。")
                    else:
                        selected_order.append(doc)
                        update_order_text()
                        redraw_docs()
                    return

        canvas.bind("<Button-1>", select_doc)
        redraw_docs()

        tk.Label(
            dialog,
            textvariable=order_var,
            font=_f(10),
            bg=C["bg"],
            fg=C["fg"],
            wraplength=560,
            justify="left",
        ).pack(fill="x", padx=24)

        def confirm() -> None:
            if len(selected_order) != len(docs):
                messagebox.showwarning("尚未完成", "請依序點完四份案卷。", parent=dialog)
                return
            if selected_order == self.BOOKSHELF_CORRECT_ORDER:
                self._advance_time(15)
                self.inventory.add("地下室鑰匙")
                self._refresh_status()
                messagebox.showinfo(
                    "排序正確",
                    "書架底部傳來「喀噠」一聲，\n書架後方的牆壁微微滑動——\n\n"
                    "你取得了通往地下密室的鑰匙！",
                    parent=dialog,
                )
                dialog.destroy()
                self.scene_map_floor1()
            else:
                messagebox.showerror(
                    "順序錯誤",
                    "案卷紋絲不動……仔細回想蔚藍學院的歷史，再試一次。",
                    parent=dialog,
                )

        def reset_selection() -> None:
            selected_order.clear()
            update_order_text()
            redraw_docs()

        btns = tk.Frame(dialog, bg=C["bg"])
        btns.pack(pady=14)
        tk.Button(
            btns,
            text="重新排列",
            command=reset_selection,
            font=_f(11, True),
            bg=C["btn_bg"],
            fg=C["btn_fg"],
            relief="flat",
            padx=12,
            pady=6,
        ).pack(side="left", padx=6)
        tk.Button(
            btns,
            text="確認排列",
            command=confirm,
            font=_f(11, True),
            bg=C["btn_bg"],
            fg=C["btn_fg"],
            relief="flat",
            padx=12,
            pady=6,
        ).pack(side="left", padx=6)

    # ── desk ──────────────────────────────────────────────────────────────────
    def scene_desk(self) -> None:
        self._advance_time(8)
        self._refresh_status()
        self._show_image("desk")
        self._set_story(ST.SCENE_DESK)
        self._set_options([
            ("離開研究桌，返回走廊", self.scene_map_floor2),
        ])
        self._set_image_actions([
            {"label": "紅花的案情筆記", "area": (92, 218, 364, 430), "command": self.read_case_notes},
        ])
        self._schedule_ambush_check()  # 2F – backstab risk

    def read_case_notes(self) -> None:
        self._advance_time(5)
        self._gain_trust("read_case_notes", 2)
        self.lore.add("紅花案情筆記")
        self._refresh_status()
        self._show_image("diary")
        trust_reaction = CT.TRUST_REACTIONS["read_case_notes"].get(self._trust_level(), "")
        self._set_story(ST.READ_CASE_NOTES + trust_reaction)
        self._set_options([
            ("繼續探索桌面", self.scene_desk),
            ("返回走廊", self.scene_map_floor2),
        ])

    # ── window ────────────────────────────────────────────────────────────────
    def scene_window(self) -> None:
        self._advance_time(8)
        self._refresh_status()
        self._show_image("window")
        self._set_story(ST.SCENE_WINDOW)
        self._set_options([
            ("離開窗邊，返回走廊", self.scene_map_floor2),
        ])
        self._set_image_actions([
            {"label": "折疊字條", "area": (142, 174, 334, 388), "command": self.inspect_window_note},
        ])
        self._schedule_ambush_check()  # 2F – backstab risk

    def inspect_window_note(self) -> None:
        self._advance_time(5)
        self._gain_trust("inspect_window_note", 2)
        self.lore.add("艾蜜莉亞線索")
        self._refresh_status()
        self._show_image("window")
        trust_reaction = CT.TRUST_REACTIONS["inspect_window_note"].get(self._trust_level(), "")
        self._set_story(ST.INSPECT_WINDOW_NOTE + trust_reaction)
        self._set_options([
            ("返回走廊", self.scene_map_floor2),
            ("直接去找紅花", self.scene_confront),
        ])

    # ── code lock puzzle ──────────────────────────────────────────────────────
    def try_unlock(self) -> None:
        if len(self.clues) < self.REQUIRED_CLUES:
            messagebox.showinfo(
                "物證不足",
                f"你只找到了 {len(self.clues)}/{self.REQUIRED_CLUES} 件物證，\n"
                "尚不足以推算密碼。",
            )
            self.scene_map_floor3()
            return
        self._create_code_dialog()

    def _create_code_dialog(self) -> None:
        if "鎮魂歌譜" in self.inventory:
            messagebox.showinfo("已解鎖", "你已持有《鎮魂歌譜》。")
            self.scene_map_floor3()
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("輸入三位密碼")
        dialog.geometry("340x180")
        dialog.configure(bg=C["bg"])
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog,
            text="根據三件物證推算案件密碼，輸入三位數：",
            font=_f(11),
            bg=C["bg"],
            fg=C["fg"],
            wraplength=300,
        ).pack(pady=12)
        entry = tk.Entry(
            dialog,
            justify="center",
            font=_f(16, True),
            bg=C["txt_bg"],
            fg=C["btn_hl"],
            insertbackground=C["btn_hl"],
            relief="flat",
            bd=4,
        )
        entry.pack(pady=4, ipady=4, ipadx=20)
        entry.focus_set()

        def submit() -> None:
            code = entry.get().strip()
            if code == self.CODE_ANSWER:
                self._advance_time(10)
                self._gain_trust("unlock_code", 1)
                self.inventory.add("鎮魂歌譜")
                self._refresh_status()
                messagebox.showinfo(
                    "解鎖成功！",
                    "密碼盒緩緩打開，裡面有一份泛黃的音樂手稿——\n"
                    "《鎮魂歌譜》入手！\n\n"
                    "這份樂譜似乎對紅花有特殊的意義……",
                    parent=dialog,
                )
                dialog.destroy()
                self.scene_map_floor3()
            else:
                self.code_tries_left -= 1
                self._refresh_status()
                if self.code_tries_left <= 0:
                    dialog.destroy()
                    self.ending_bad_codefail()
                else:
                    messagebox.showwarning(
                        "密碼錯誤",
                        f"盒身微微震動……還剩 {self.code_tries_left} 次機會。",
                        parent=dialog,
                    )

        btn = tk.Button(
            dialog,
            text="確認",
            command=submit,
            font=_f(11, True),
            bg=C["btn_bg"],
            fg=C["btn_fg"],
            relief="flat",
            padx=14,
            pady=6,
        )
        btn.pack(pady=10)
        dialog.bind("<Return>", lambda _: btn.invoke())

    # ── basement ──────────────────────────────────────────────────────────────
    def scene_basement(self) -> None:
        if "地下室鑰匙" not in self.inventory:
            messagebox.showinfo("門緊閉", "地下密室的門紋絲不動，需要某種鑰匙。")
            self.scene_map_floor1()
            return
        self._advance_time(10)
        self._refresh_status()
        self._show_image("basement")
        self._set_story(ST.SCENE_BASEMENT)
        self._set_options([
            ("推開左側石門，進入倉庫", self.scene_basement_deep),
            ("靠近右側石門（儲藏室）", self.scene_basement_storage_room),
            ("離開地下室，返回走廊", self.scene_map_floor1),
        ])
        self._schedule_ambush_check()  # underground – backstab risk

    def scene_basement_deep(self) -> None:
        self._advance_time(8)
        self._gain_trust("scene_basement_deep", 2)
        self.lore.add("天王星供詞")
        self._refresh_status()
        self._show_image("basement_deep")
        self._set_story(ST.SCENE_BASEMENT_DEEP)
        self._set_options([
            ("帶著這個發現返回走廊", self.scene_map_floor1),
        ])
        self._schedule_ambush_check()  # underground – backstab risk

    def scene_basement_storage_room(self) -> None:
        """The sealed storage room where the killer has been hiding."""
        self._refresh_status()
        self._show_image("basement")
        self._set_story(ST.SCENE_BASEMENT_STORAGE_ROOM)
        self._set_options([
            ("退開，返回地下入口", self.scene_basement),
            ("離開地下室，返回走廊", self.scene_map_floor1),
        ])
        # Very close to the killer's hideout – much higher ambush probability.
        self._schedule_ambush_check(chance=self.STORAGE_AMBUSH_CHANCE_HIGH)

    # ── confrontation ─────────────────────────────────────────────────────────
    def scene_confront(self) -> None:
        self._refresh_status()
        self._show_image("confront")

        has_talisman = "鎮魂歌譜" in self.inventory
        all_lore     = len(self.lore) >= self.REQUIRED_LORE
        clue_count   = len(self.clues)
        trust        = self.trust

        if has_talisman and all_lore and trust >= self.TRUST_THRESHOLD_SECRET:
            self._set_story(ST.CONFRONT_SECRET_PATH)
            self._set_options([("展示所有物證，陳述推論", self.ending_secret)])
        elif has_talisman and all_lore:
            self._set_story(ST.CONFRONT_COLDTRUTH_PATH)
            self._set_options([("接受她的決定", self.ending_trust_coldtruth)])
        elif has_talisman and trust >= self.TRUST_THRESHOLD_TRUE:
            self._set_story(ST.CONFRONT_TRUE_PATH)
            self._set_options([("陳述目前的調查發現", self.ending_true)])
        elif has_talisman:
            self._set_story(ST.CONFRONT_REJECTED_PATH)
            self._set_options([("沉默離開", self.ending_trust_rejected)])
        elif clue_count >= self.PARTIAL_CLUES and trust >= self.TRUST_THRESHOLD_ALLIANCE:
            self._set_story(ST.CONFRONT_ALLIANCE_PATH)
            self._set_options([("收下徽章，約定再查", self.ending_trust_alliance)])
        elif clue_count >= self.PARTIAL_CLUES:
            self._set_story(ST.CONFRONT_NORMAL_PATH)
            self._set_options([
                ("接受這個結果", self.ending_normal),
                ("我還沒放棄——返回地圖", self.scene_map_floor3),
            ])
        else:
            self._set_story(ST.CONFRONT_UNPREPARED_PATH)
            self._set_options([("…", self.ending_bad_unprepared)])

    # ══════════════════════════════════════════════════════════════════════════
    #  Endings
    # ══════════════════════════════════════════════════════════════════════════

    def ending_secret(self) -> None:
        """Secret ending — all lore + talisman + full case solved."""
        end_bgm = BGM_END if os.path.exists(BGM_END) else BGM_MAIN
        self.music.switch(end_bgm)
        self._show_image("secret_end")
        self._set_story(ST.ENDING_SECRET)
        self._set_options([
            ("再玩一次", self.show_intro),
            ("離開", self.root.destroy),
        ])

    def ending_true(self) -> None:
        """True ending — talisman only."""
        end_bgm = BGM_END if os.path.exists(BGM_END) else BGM_MAIN
        self.music.switch(end_bgm)
        self._show_image("true_end")
        self._set_story(ST.ENDING_TRUE)
        self._set_options([
            ("再玩一次", self.show_intro),
            ("離開", self.root.destroy),
        ])

    def ending_trust_alliance(self) -> None:
        """Affinity ending — high trust without full evidence."""
        self._show_image("normal_end")
        self._set_story(ST.ENDING_TRUST_ALLIANCE)
        self._set_options([
            ("再玩一次", self.show_intro),
            ("離開", self.root.destroy),
        ])

    def ending_trust_rejected(self) -> None:
        """Affinity ending — low trust with talisman."""
        self._show_image("bad_a")
        self._set_story(ST.ENDING_TRUST_REJECTED)
        self._set_options([
            ("重新開始", self.show_intro),
            ("離開", self.root.destroy),
        ])

    def ending_trust_coldtruth(self) -> None:
        """Affinity ending — case solved but relationship remains distant."""
        end_bgm = BGM_END if os.path.exists(BGM_END) else BGM_MAIN
        self.music.switch(end_bgm)
        self._show_image("true_end")
        self._set_story(ST.ENDING_TRUST_COLDTRUTH)
        self._set_options([
            ("再玩一次", self.show_intro),
            ("離開", self.root.destroy),
        ])

    def ending_normal(self) -> None:
        """Normal ending — partial clues."""
        self._show_image("normal_end")
        self._set_story(ST.ENDING_NORMAL)
        self._set_options([
            ("再玩一次", self.show_intro),
            ("離開", self.root.destroy),
        ])

    def ending_bad_unprepared(self) -> None:
        """Bad ending A — confronted without preparation."""
        self._show_image("bad_a")
        self._set_story(ST.ENDING_BAD_UNPREPARED)
        self._set_options([
            ("疲憊地離去，沉沉睡去", self.ending_hidden),
            ("重新開始", self.show_intro),
            ("離開", self.root.destroy),
        ])

    def ending_bad_codefail(self) -> None:
        """Bad ending B — too many code failures."""
        self._show_image("bad_b")
        self._set_story(ST.ENDING_BAD_CODEFAIL)
        self._set_options([
            ("重新開始", self.show_intro),
            ("離開", self.root.destroy),
        ])

    def ending_storage_ambush(self) -> None:
        self._show_image("bad_a")
        self._set_story(ST.ENDING_STORAGE_AMBUSH)
        self._set_options([
            ("重新開始", self.show_intro),
            ("離開", self.root.destroy),
        ])

    def ending_killer_map(self) -> None:
        """Bad ending D — killer encounters player on the floor map after 2AM."""
        self._show_image("bad_a")
        self._set_story(ST.ENDING_KILLER_MAP)
        self._set_options([
            ("重新開始", self.show_intro),
            ("離開", self.root.destroy),
        ])

    def inspect_meeting_docs(self) -> None:
        already_found = "董事會封鎖紀錄" in self.lore
        if not already_found:
            self._advance_time(5)
            self.lore.add("董事會封鎖紀錄")
            self._gain_trust("meeting_docs", 2)
            self._refresh_status()
        self._show_image("meeting_room")
        text = ST.INSPECT_MEETING_DOCS if not already_found else (
            "（你已記下董事會議紀錄：\n案件被校方組織性地掩蓋。）"
        )
        self._set_story(text)
        self._set_options([
            ("繼續調查會議室", self.scene_meeting_room),
            ("返回一樓地圖", self.scene_map_floor1),
            ("返回二樓地圖", self.scene_map_floor2),
        ])

    def ending_hidden(self) -> None:
        """Hidden ending — dream revelation."""
        self.music.switch(BGM_END)
        self._show_image("hidden_end")
        self._set_story(ST.ENDING_HIDDEN)
        self._set_options([
            ("再玩一次", self.show_intro),
            ("離開", self.root.destroy),
        ])

    # ══════════════════════════════════════════════════════════════════════════
    #  New explorable nodes — corridors / rooms / meeting rooms
    # ══════════════════════════════════════════════════════════════════════════

    # ── 1F corridor ───────────────────────────────────────────────────────────
    def scene_corridor_1f(self) -> None:
        self._advance_time(8)
        self._refresh_status()
        self._show_image("corridor_1f")
        self._set_story(ST.SCENE_CORRIDOR_1F)
        self._set_options([
            ("離開走廊，返回一樓地圖", self.scene_map_floor1),
        ])
        self._set_image_actions([
            {
                "label": "相框背後的紙張",
                "area": (60, 60, 280, 360),
                "command": self.inspect_corridor_photo,
            },
        ])
        self._schedule_ambush_check()  # 1F – backstab risk

    def inspect_corridor_photo(self) -> None:
        already_found = "艾蜜莉亞走廊字條" in self.lore
        if not already_found:
            self._advance_time(5)
            self.lore.add("艾蜜莉亞走廊字條")
            self._gain_trust("corridor_photo", 1)
            self._refresh_status()
        self._show_image("corridor_1f")
        text = ST.INSPECT_CORRIDOR_PHOTO if not already_found else (
            "（你已記下相框背後艾蜜莉亞的字條。）"
        )
        self._set_story(text)
        self._set_options([
            ("繼續調查走廊", self.scene_corridor_1f),
            ("返回一樓地圖", self.scene_map_floor1),
        ])

    # ── 2F corridor ───────────────────────────────────────────────────────────
    def scene_corridor_2f(self) -> None:
        self._advance_time(8)
        self._refresh_status()
        self._show_image("corridor_2f")
        self._set_story(ST.SCENE_CORRIDOR_2F)
        self._set_options([
            ("離開走廊，返回二樓地圖", self.scene_map_floor2),
        ])
        self._set_image_actions([
            {
                "label": "被撕過的公告欄",
                "area": (100, 80, 380, 340),
                "command": self.inspect_corridor_noticeboard,
            },
        ])
        self._schedule_ambush_check()  # 2F – backstab risk

    def inspect_corridor_noticeboard(self) -> None:
        already_found = "公告欄天王星紀錄" in self.lore
        if not already_found:
            self._advance_time(5)
            self.lore.add("公告欄天王星紀錄")
            self._gain_trust("corridor_noticeboard", 1)
            self._refresh_status()
        self._show_image("corridor_2f")
        text = ST.INSPECT_CORRIDOR_NOTICEBOARD if not already_found else (
            "（你已記下公告欄上天王星返校的目擊紀錄。）"
        )
        self._set_story(text)
        self._set_options([
            ("繼續調查走廊", self.scene_corridor_2f),
            ("返回二樓地圖", self.scene_map_floor2),
        ])

    # ── 3F corridor ───────────────────────────────────────────────────────────
    def scene_corridor_3f(self) -> None:
        self._advance_time(8)
        self._refresh_status()
        self._show_image("corridor_3f")
        self._set_story(ST.SCENE_CORRIDOR_3F)
        self._set_options([
            ("離開走廊，返回三樓地圖", self.scene_map_floor3),
        ])
        self._set_image_actions([
            {
                "label": "機密存查資料夾",
                "area": (80, 100, 360, 380),
                "command": self.inspect_corridor_3f_file,
            },
        ])
        # 3F is the safe zone — no ambush check

    def inspect_corridor_3f_file(self) -> None:
        already_found = "校方封鎖備忘錄" in self.lore
        if not already_found:
            self._advance_time(5)
            self.lore.add("校方封鎖備忘錄")
            self._gain_trust("corridor_3f_file", 2)
            self._refresh_status()
        self._show_image("corridor_3f")
        text = ST.INSPECT_CORRIDOR_3F_FILE if not already_found else (
            "（你已記下校方封鎖案件的備忘錄內容。）"
        )
        self._set_story(text)
        self._set_options([
            ("繼續調查走廊", self.scene_corridor_3f),
            ("返回三樓地圖", self.scene_map_floor3),
        ])

    # ── Room A ────────────────────────────────────────────────────────────────
    def scene_room_a(self) -> None:
        self._advance_time(8)
        self._refresh_status()
        self._show_image("room_a")
        self._set_story(ST.SCENE_ROOM_A)
        self._set_options([
            ("離開房間，返回一樓地圖", self.scene_map_floor1),
        ])
        self._set_image_actions([
            {
                "label": "書桌抽屜",
                "area": (80, 200, 360, 420),
                "command": self.inspect_room_a_drawer,
            },
        ])
        self._schedule_ambush_check()  # 1F – backstab risk

    def inspect_room_a_drawer(self) -> None:
        already_found = "米糕的遺信" in self.lore
        if not already_found:
            self._advance_time(5)
            self.lore.add("米糕的遺信")
            self._gain_trust("room_a_drawer", 1)
            self._refresh_status()
        self._show_image("room_a")
        text = ST.INSPECT_ROOM_A_DRAWER if not already_found else (
            "（你已記下米糕留下的遺信，\n指引前往地下室倉庫的第三個木箱。）"
        )
        self._set_story(text)
        self._set_options([
            ("繼續調查房間", self.scene_room_a),
            ("返回一樓地圖", self.scene_map_floor1),
        ])

    # ── Room B ────────────────────────────────────────────────────────────────
    def scene_room_b(self) -> None:
        self._advance_time(8)
        self._refresh_status()
        self._show_image("room_b")
        self._set_story(ST.SCENE_ROOM_B)
        self._set_options([
            ("離開房間，返回一樓地圖", self.scene_map_floor1),
        ])
        self._set_image_actions([
            {
                "label": "窗台上的手套",
                "area": (120, 60, 380, 260),
                "command": self.inspect_room_b_gloves,
            },
        ])
        self._schedule_ambush_check()  # 1F – backstab risk

    def inspect_room_b_gloves(self) -> None:
        already_found = "天王星手套" in self.lore
        if not already_found:
            self._advance_time(5)
            self.lore.add("天王星手套")
            self._gain_trust("room_b_gloves", 1)
            self._refresh_status()
        self._show_image("room_b")
        text = ST.INSPECT_ROOM_B_GLOVES if not already_found else (
            "（你已記下手套上「T.S.」的縫線與鏽跡，\n與鎚子相符。）"
        )
        self._set_story(text)
        self._set_options([
            ("繼續調查房間", self.scene_room_b),
            ("返回一樓地圖", self.scene_map_floor1),
        ])

    # ── Meeting room ──────────────────────────────────────────────────────────
    def scene_meeting_room(self) -> None:
        self._advance_time(8)
        self._refresh_status()
        self._show_image("meeting_room")
        self._set_story(ST.SCENE_MEETING_ROOM)
        self._set_options([
            ("離開會議室，返回一樓地圖", self.scene_map_floor1),
            ("離開會議室，返回二樓地圖", self.scene_map_floor2),
        ])
        self._set_image_actions([
            {
                "label": "桌上公文",
                "area": (60, 160, 400, 420),
                "command": self.inspect_meeting_docs,
            },
        ])
        self._schedule_ambush_check()  # ambush risk wherever killer may roam


# ══════════════════════════════════════════════════════════════════════════════
#  Entry point
# ══════════════════════════════════════════════════════════════════════════════
def main() -> None:
    root = tk.Tk()
    HonghuaGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
