"""
紅花吃檳榔：圖書館夜談 — 深夜完全版
Enhanced visual novel · scene illustrations · BGM
"""
from __future__ import annotations

import os
import threading
from collections.abc import Callable
from typing import Optional

import tkinter as tk
from tkinter import messagebox

# ── optional dependencies ──────────────────────────────────────────────────────
try:
    from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageTk
    _PIL = True
except ImportError:
    _PIL = False

try:
    import pygame as _pygame
    _PYGAME = True
except ImportError:
    _PYGAME = False

# ── paths ──────────────────────────────────────────────────────────────────────
_DIR      = os.path.dirname(os.path.abspath(__file__))
INFO_JPG  = os.path.join(_DIR, "info.jpg")
ASSETS    = os.path.join(_DIR, "assets")
SCENES    = os.path.join(ASSETS, "scenes")
BGM_MAIN  = os.path.join(ASSETS, "bgm_main.mp3")
BGM_END   = os.path.join(ASSETS, "bgm_end.mp3")

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
    path = os.path.join(SCENES, f"{key}.png")
    if not os.path.exists(path):
        return None
    img = Image.open(path).convert("RGB")
    if img.size != (IW, IH):
        img = img.resize((IW, IH), Image.LANCZOS)
    return ImageTk.PhotoImage(img)


def _build(key: str) -> Optional[object]:
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
    }
    if key in PROC:
        base_rgb, lights = PROC[key]
        return _atmospheric(base_rgb, lights)

    return _atmospheric((7, 7, 11), [(IW // 2, IH // 2, 180, (28, 18, 38, 55))])


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


# ══════════════════════════════════════════════════════════════════════════════
#  HonghuaGame
# ══════════════════════════════════════════════════════════════════════════════
class HonghuaGame:
    # ── puzzle answers ─────────────────────────────────────────────────────────
    CODE_ANSWER      = "314"
    BOOKSHELF_ANSWER = "A"    # first choice = correct
    REQUIRED_CLUES   = 3
    REQUIRED_LORE    = 3
    PARTIAL_CLUES    = 2
    MAX_CODE_TRIES   = 3
    TRUST_THRESHOLD_SECRET   = 7  # minimum trust for the secret ending
    TRUST_THRESHOLD_TRUE     = 4  # minimum trust for the true ending path
    TRUST_THRESHOLD_ALLIANCE = 6  # minimum trust for the alliance ending
    TRUST_THRESHOLD_OBSERVE  = 1  # minimum trust to move past outright distrust
    WINDOW_TITLE     = "紅花吃檳榔：蔚藍學院秘案 - 深夜調查版"

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

        self.music = MusicPlayer()

        self._build_ui()
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
        img = scene_image(key)
        self._current_img = img
        self.img_canvas.delete("all")
        if img:
            self.img_canvas.create_image(0, 0, anchor="nw", image=img)
        else:
            self.img_canvas.configure(bg=C["panel"])

    def _set_story(self, text: str, typing: bool = True) -> None:
        if self._type_job:
            self.root.after_cancel(self._type_job)
            self._type_job = None
        self.story_text.configure(state="normal")
        self.story_text.delete("1.0", "end")
        self.story_text.configure(state="disabled")
        if typing:
            self._type_text(text, 0)
        else:
            self.story_text.configure(state="normal")
            self.story_text.insert("1.0", text)
            self.story_text.configure(state="disabled")

    def _type_text(self, text: str, idx: int) -> None:
        if idx >= len(text):
            # Ensure the full text is displayed on the last frame
            self.story_text.configure(state="normal")
            self.story_text.delete("1.0", "end")
            self.story_text.insert("1.0", text)
            self.story_text.configure(state="disabled")
            self._type_job = None
            return
        self.story_text.configure(state="normal")
        self.story_text.delete("1.0", "end")
        self.story_text.insert("1.0", text[:idx])
        self.story_text.configure(state="disabled")
        self.story_text.see("end")
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
        self.inventory.clear()
        self.clues.clear()
        self.lore.clear()
        self.trust = 0
        self._trust_events.clear()
        self.code_tries_left = self.MAX_CODE_TRIES
        self._refresh_status()

    def _trust_level(self) -> str:
        if self.trust >= self.TRUST_THRESHOLD_SECRET:
            return "高度信任"
        if self.trust >= self.TRUST_THRESHOLD_TRUE:
            return "逐步信任"
        if self.trust >= self.TRUST_THRESHOLD_OBSERVE:
            return "觀望中"
        return "不信任"

    def _gain_trust(self, event: str, points: int) -> None:
        if event in self._trust_events:
            return
        self._trust_events.add(event)
        self.trust += points

    def _format_status_text(
        self,
        items: str,
        clue_count: int,
        tries: int,
        lore_n: int,
    ) -> str:
        trust_label = self._trust_level()
        return (
            f"道具:{items} | 物證:{clue_count}/{self.REQUIRED_CLUES} | "
            f"密碼:{tries} | 線索:{lore_n}/{self.REQUIRED_LORE} | 信任:{self.trust}({trust_label})"
        )

    # ══════════════════════════════════════════════════════════════════════════
    #  Scenes
    # ══════════════════════════════════════════════════════════════════════════

    def show_intro(self) -> None:
        self._reset_state()
        self._show_image("intro")
        self._set_story(
            "===================================\n"
            "  紅花吃檳榔：蔚藍學院秘案  深夜調查版\n"
            "===================================\n\n"
            "17世紀英格蘭。\n\n"
            "蔚藍學院——曾是英倫最負盛名的貴族學院，\n"
            "如今大門緊閉，雜草叢生，廢棄整整兩年。\n\n"
            "兩年前，學院內發生了一場至今未破的謀殺案。\n"
            "受害者是校內受人愛戴的米糕店長。\n"
            "真兇至今逍遙法外，學院因此被迫關閉。\n\n"
            "「紅花綻放之處，是你尋找答案的起點。\n"
            " 但你能否離開，則是另一回事。」\n"
            "                              ——紅花\n\n"
            "廢棄圖書館深處，一盞燭火搖曳於幽暗之中。\n"
            "傳說中的紅花，就在那裡守候。",
            typing=False,
        )
        self._set_options([("進入故事", self.scene_prologue)])

    def scene_prologue(self) -> None:
        self._show_image("prologue")
        self._set_story(
            "你——英國皇家警察——踏入了蔚藍學院廢棄的圖書館。\n\n"
            "這是你的母校。也是你反覆做惡夢的地方。\n\n"
            "兩年前的那個傍晚，米糕店長倒在這裡。\n"
            "案件懸而未決，學院就此關閉。\n"
            "而你，曾是法國海軍，如今兼任英國皇家警察，\n"
            "今夜隻身來此，要終結這一切。\n\n"
            "你彎低身子穿過積滿灰塵的門廊——\n"
            "燭光映照著三個方向的書架，\n"
            "然後你看見了她。\n\n"
            "銀白色短髮，筆挺的水手服。\n"
            "她端坐於正中央的椅子上，\n"
            "嘴角含著一抹說不清是什麼顏色的紅。\n\n"
            "「英國皇家警察，」她緩緩開口，\n"
            "「真是個奇妙的名字——或者說，奇妙的稱號。」\n\n"
            "「你來這裡是為了什麼，我已經知道了。」\n"
            "她淡淡地說，「問題是……\n"
            " 你能找到答案嗎？」\n\n"
            "你掃視四周——生鏽的鎚子、不知從哪來的四葉草、\n"
            "一件疊得整齊的牛仔褲，以及一個密碼盒。\n\n"
            "天亮之前，必須找到真相。"
        )
        self._set_options([
            ("開始調查圖書館", self.scene_hall),
            ("直接上前與紅花說話", self.scene_confront),
        ])

    # ── main hall (hub) ───────────────────────────────────────────────────────
    def scene_hall(self) -> None:
        self._refresh_status()
        self._show_image("hall")
        has_key = "地下室鑰匙" in self.inventory
        basement_hint = "\n（口袋中有一把通往地下密室的鑰匙……）" if has_key else ""
        self._set_story(
            "蔚藍學院圖書館——廢棄兩年的舊址。\n"
            "灰塵、蛛網與腐舊的書香充滿了每一個角落。\n"
            "然而，燭光仍在搖曳。有人在守著這裡。\n\n"
            "你掃視四周，注意到幾件不尋常的物品：\n"
            "一把生鏽的鎚子、一片乾燥的四葉草，\n"
            "以及一件疊得整齊的牛仔褲——\n"
            "這些東西，不應該出現在廢棄的圖書館裡。\n\n"
            "書架深處還有謎題，研究桌上有筆記，\n"
            "窗台上似乎藏著什麼，\n"
            "而密碼盒就靜靜地立在書架旁。\n\n"
            "可以調查的地方：鎚子・四葉草・牛仔褲・書架深處・研究桌・窗邊"
            + basement_hint
        )
        opts: list[tuple[str, Callable]] = [
            ("調查鎚子", self.inspect_hammer),
            ("調查四葉草", self.inspect_clover),
            ("調查牛仔褲", self.inspect_jeans),
            ("前往書架深處", self.scene_bookshelves),
            ("前往研究桌", self.scene_desk),
            ("前往窗邊", self.scene_window),
        ]
        if has_key:
            opts.append(("打開地下密室", self.scene_basement))
        opts += [
            ("嘗試解鎖密碼盒", self.try_unlock),
            ("前去面對紅花", self.scene_confront),
        ]
        self._set_options(opts)

    # ── hammer ────────────────────────────────────────────────────────────────
    def inspect_hammer(self) -> None:
        self._gain_trust("inspect_hammer", 1)
        self.clues["鎚子"] = 3
        self._refresh_status()
        self._show_image("book")
        self._set_story(
            "書架角落，一把鏽跡斑斑的鎚子橫臥於塵埃之中。\n\n"
            "三十公分，沉甸甸——這是一件兇器嗎？\n\n"
            "鎚柄上有三道深刻的刻痕，像是刻意留下的記號。\n"
            "你在案卷中見過這個記號——\n"
            "案發現場的地面，留下過同樣的痕跡。\n\n"
            "鎚柄底端刻著羅馬數字「III」。\n\n"
            "【物證取得】第一碼是 3。\n"
            "【推斷】這把鎚子，極可能是米糕店長遇害的兇器。"
        )
        self._set_options([
            ("繼續調查", self.scene_hall),
            ("直接面對紅花", self.scene_confront),
        ])

    # ── four-leaf clover ──────────────────────────────────────────────────────
    def inspect_clover(self) -> None:
        self._gain_trust("inspect_clover", 1)
        self.clues["四葉草"] = 1
        self._refresh_status()
        self._show_image("feather")
        self._set_story(
            "一片乾燥的四葉草，夾在書架縫隙中，\n"
            "邊緣已泛黃，但保存得出奇完好。\n\n"
            "四葉草的葉片中央，用細筆寫著一個「壹」字。\n\n"
            "你記得蔚藍學院有一位出了名幸運的轉學生——\n"
            "她叫艾莉卡，「幸運的艾莉卡」。\n"
            "這片四葉草是她的標誌性飾品。\n\n"
            "她曾在案發前夕造訪學院。\n"
            "她說……她只是「順路帶來好運」。\n"
            "但案發當晚，她已不知去向。\n\n"
            "【物證取得】第二碼是 1。\n"
            "【推斷】艾莉卡可能是案發現場的目擊者。"
        )
        self._set_options([
            ("繼續調查", self.scene_hall),
            ("直接面對紅花", self.scene_confront),
        ])

    # ── YV jeans ──────────────────────────────────────────────────────────────
    def inspect_jeans(self) -> None:
        self._gain_trust("inspect_jeans", 1)
        self.clues["牛仔褲"] = 4
        self._refresh_status()
        self._show_image("box")
        self._set_story(
            "書架底層，一件疊得整整齊齊的牛仔褲。\n\n"
            "標籤上印著「YV」兩個字母——\n"
            "這是英倫近年流行的品牌，\n"
            "據說只有特定社交圈的人才會穿。\n\n"
            "褲腿內側縫著手寫的文字：\n"
            "「R.U. · 第四排 · 入場許可」\n\n"
            "R.U.——你腦海中浮現一個名字：\n"
            "天王星（Uranus）。退學生天王星，\n"
            "曾因家道中落憤恨離校，愛攀關係，\n"
            "卻也因此對某些人懷恨在心。\n\n"
            "而「第四排」，正是學院劇場的黑市座位……\n\n"
            "【物證取得】第三碼是 4。\n"
            "【推斷】天王星曾在案發前後秘密返回學院。"
        )
        self._set_options([
            ("繼續調查", self.scene_hall),
            ("嘗試解鎖密碼盒", self.try_unlock),
        ])

    # ── bookshelves area ──────────────────────────────────────────────────────
    def scene_bookshelves(self) -> None:
        self._refresh_status()
        self._show_image("bookshelves")
        self._set_story(
            "書架深處，光線幾乎不存在。\n\n"
            "你摸索前行，發現一排特殊的書架上，\n"
            "擺著四份封存的案件文件夾：\n\n"
            "   《失蹤案卷》  《退學檔案》  《死亡報告》  《停課公告》\n\n"
            "架下有一塊石板，刻著說明：\n\n"
            "「蔚藍學院的終結，並非始於最後那一聲哀鳴。\n"
            " 按事件發生的時間順序排列，\n"
            " 方可開啟封印。」\n\n"
            "石板旁有一個小鎖孔，排列正確才能打開。"
        )
        self._set_options([
            ("嘗試排列四份案卷（解謎）", self.puzzle_bookshelf),
            ("返回大廳", self.scene_hall),
        ])

    def puzzle_bookshelf(self) -> None:
        if "地下室鑰匙" in self.inventory:
            messagebox.showinfo("已解鎖", "地下密室的鑰匙已在你手中。")
            self.scene_hall()
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("案件時間線——事件排序")
        dialog.geometry("520x330")
        dialog.configure(bg=C["bg"])
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog,
            text="請根據蔚藍學院事件的發生順序，選出正確的時間排列：",
            font=_f(11),
            bg=C["bg"],
            fg=C["fg"],
            wraplength=480,
        ).pack(pady=14, padx=14)

        choices = [
            ("A", "失蹤案卷 → 退學檔案 → 死亡報告 → 停課公告（時間正序）"),
            ("B", "死亡報告 → 退學檔案 → 失蹤案卷 → 停課公告（倒序）"),
            ("C", "退學檔案 → 失蹤案卷 → 停課公告 → 死亡報告（混亂）"),
            ("D", "停課公告 → 死亡報告 → 退學檔案 → 失蹤案卷（完全逆序）"),
        ]
        selected = tk.StringVar(value="")

        for key, label in choices:
            tk.Radiobutton(
                dialog,
                text=f"{key}. {label}",
                variable=selected,
                value=key,
                font=_f(10),
                bg=C["bg"],
                fg=C["fg"],
                selectcolor=C["txt_sel"],
                activebackground=C["bg"],
                activeforeground=C["btn_hl"],
            ).pack(anchor="w", padx=22, pady=3)

        def confirm() -> None:
            ans = selected.get()
            if not ans:
                messagebox.showwarning("未選擇", "請選擇一個排列順序。", parent=dialog)
                return
            if ans == self.BOOKSHELF_ANSWER:
                self.inventory.add("地下室鑰匙")
                self._refresh_status()
                messagebox.showinfo(
                    "排序正確",
                    "書架底部傳來「喀噠」一聲，\n書架後方的牆壁微微滑動——\n\n"
                    "你取得了通往地下密室的鑰匙！",
                    parent=dialog,
                )
                dialog.destroy()
                self.scene_hall()
            else:
                messagebox.showerror(
                    "順序錯誤",
                    "案卷紋絲不動……仔細回想蔚藍學院的歷史，再試一次。",
                    parent=dialog,
                )

        tk.Button(
            dialog,
            text="確認排列",
            command=confirm,
            font=_f(11, True),
            bg=C["btn_bg"],
            fg=C["btn_fg"],
            relief="flat",
            padx=12,
            pady=6,
        ).pack(pady=14)

    # ── desk ──────────────────────────────────────────────────────────────────
    def scene_desk(self) -> None:
        self._refresh_status()
        self._show_image("desk")
        self._set_story(
            "圖書館一角有張破舊的研究桌。\n\n"
            "桌面散亂地鋪著手繪的案情分析圖，\n"
            "以及一份份逐漸發黃的筆記與文件。\n"
            "一根快燃盡的蠟燭在紙堆旁顫抖著。\n\n"
            "桌角有一本合上的筆記本，\n"
            "封面上縫著水手服的繡章——這是紅花的。"
        )
        self._set_options([
            ("閱讀紅花的案情筆記", self.read_case_notes),
            ("返回大廳", self.scene_hall),
        ])

    def read_case_notes(self) -> None:
        self._gain_trust("read_case_notes", 2)
        self.lore.add("紅花案情筆記")
        self._refresh_status()
        self._show_image("diary")
        self._set_story(
            "【紅花的案情紀錄 · 第七三頁】\n\n"
            "米糕的死絕非偶然。\n"
            "我看過那把鎚子，我看過現場的血跡。\n\n"
            "那個傍晚，我就在圖書館裡——\n"
            "我聽見了爭吵聲，聽見了倒地的聲音。\n"
            "但那道門在案發後自動上鎖，像是某種詛咒。\n\n"
            "我知道誰在那裡。\n"
            "但是沒有證據，沒有人會信我的話。\n\n"
            "我只能留在這裡，等一個真正懂得查案的人。\n"
            "等一個不只懂劍，也懂心的人。\n\n"
            "——紅花　謹記\n\n"
            "【人物線索】你了解了紅花所掌握的秘密。"
        )
        self._set_options([
            ("繼續探索桌面", self.scene_desk),
            ("返回大廳", self.scene_hall),
        ])

    # ── window ────────────────────────────────────────────────────────────────
    def scene_window(self) -> None:
        self._refresh_status()
        self._show_image("window")
        self._set_story(
            "大廳角落的窗戶，玻璃早已破碎，\n"
            "夜風從缺口灌入，搖晃著窗簾上的蛛網。\n\n"
            "窗台上的塵埃中，有一個橢圓形的輪廓——\n"
            "像是曾經放過一個相框。但相框已不在了。\n\n"
            "只剩下一縷乾燥的玫瑰花瓣，\n"
            "以及壓在花瓣下的一張折疊字條。"
        )
        self._set_options([
            ("仔細辨認字條", self.inspect_window_note),
            ("返回大廳", self.scene_hall),
        ])

    def inspect_window_note(self) -> None:
        self._gain_trust("inspect_window_note", 2)
        self.lore.add("艾蜜莉亞線索")
        self._refresh_status()
        self._show_image("window")
        self._set_story(
            "字條的字跡在燭光下若隱若現：\n\n"
            "「艾蜜莉亞，你知道他做了什麼。\n"
            " 你不得不消失。我明白。\n\n"
            " 但你留下的線索，\n"
            " 總有一天會讓真相浮現。\n\n"
            " 請——好好保重。\n\n"
            "                    ——你知道是誰的人」\n\n"
            "字跡……你認出了，這是紅花的筆跡。\n\n"
            "艾蜜莉亞——那個消失的學生聯誼會委員。\n"
            "她當時目睹了什麼，讓她必須逃離這裡？\n\n"
            "【人物線索】你了解了艾蜜莉亞消失的原因。"
        )
        self._set_options([
            ("返回大廳", self.scene_hall),
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
            self.scene_hall()
            return
        self._create_code_dialog()

    def _create_code_dialog(self) -> None:
        if "鎮魂歌譜" in self.inventory:
            messagebox.showinfo("已解鎖", "你已持有《鎮魂歌譜》。")
            self.scene_hall()
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
                self.scene_hall()
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
            self.scene_hall()
            return
        self._refresh_status()
        self._show_image("basement")
        self._set_story(
            "鑰匙插入暗格，書架後方的牆壁緩緩滑動。\n\n"
            "你踏上狹窄的石階，\n"
            "潮濕與腐舊紙張的氣味撲面而來。\n\n"
            "燭光在你身後搖曳，\n"
            "前方是一片深不見底的黑暗。\n"
            "你繼續下行……\n\n"
            "數十級石階之後，\n"
            "你看到一扇半開的石門，\n"
            "門縫中透出隱約的燭光。"
        )
        self._set_options([
            ("推開石門探索", self.scene_basement_deep),
            ("返回大廳", self.scene_hall),
        ])

    def scene_basement_deep(self) -> None:
        self._gain_trust("scene_basement_deep", 2)
        self.lore.add("天王星供詞")
        self._refresh_status()
        self._show_image("basement_deep")
        self._set_story(
            "石室中央，有一個塵封已久的小桌。\n\n"
            "桌上放著一封未完成的信，\n"
            "以及一本翻開的日記——\n"
            "日記的頁面上，你辨認出了熟悉的字體：\n"
            "「天王星（Uranus）」的親筆。\n\n"
            "翻開那一頁：\n\n"
            "「我做了不可挽回的事。\n"
            " 那一天，我衝進去找米糕，\n"
            " 是要他還我父親的錢——\n"
            " 他說沒有，我們起了衝突……\n\n"
            " 那把鎚子就在旁邊，\n"
            " 我只是想嚇嚇他。\n"
            " 我不是故意的。\n"
            " 上帝作證，我不是。\n\n"
            " 但艾莉卡在窗外看到了一切。\n"
            " 她……她沒有說話。她只是跑了。\n"
            " 艾蜜莉亞也知道了。\n"
            " 她選擇消失，不是因為膽怯——\n"
            " 是因為她不知道該告訴誰。」\n\n"
            "【人物線索】你掌握了天王星的親筆供詞，\n"
            "以及艾莉卡目睹事件的真相。"
        )
        self._set_options([
            ("帶著這個發現返回大廳", self.scene_hall),
        ])

    # ── confrontation ─────────────────────────────────────────────────────────
    def scene_confront(self) -> None:
        self._refresh_status()
        self._show_image("confront")

        has_talisman = "鎮魂歌譜" in self.inventory
        all_lore     = len(self.lore) >= self.REQUIRED_LORE
        clue_count   = len(self.clues)
        trust        = self.trust

        if has_talisman and all_lore and trust >= self.TRUST_THRESHOLD_SECRET:
            self._set_story(
                "你走向紅花，手中握著那份《鎮魂歌譜》。\n\n"
                "她的眼神微微一凝——\n"
                "「你……找到那首曲子了？」\n\n"
                "然後她看見你帶著的物證，\n"
                "看見你調查的眼神，\n"
                "眼中閃過一絲從未有過的動搖。\n\n"
                "「你不只知道那些數字。\n"
                " 你還知道……那個晚上發生了什麼。」\n\n"
                "紅花靜靜地望著你，許久沒有說話。\n"
                "最後，她緩緩開口：\n"
                "「說吧。你知道什麼，就說什麼。」"
            )
            self._set_options([("展示所有物證，陳述推論", self.ending_secret)])
        elif has_talisman and all_lore:
            self._set_story(
                "你走向紅花，展示了完整物證與供詞。\n\n"
                "紅花安靜地聽完，點了點頭。\n"
                "「你的推論成立，證據也完整。」\n\n"
                "她停頓片刻，視線卻沒有真正落在你身上：\n"
                "「但我還不確定，能不能把剩下的交給你。」\n\n"
                "「你破得了案，\n"
                " 卻還沒真正讓我相信你會善待這個真相。」"
            )
            self._set_options([("接受她的決定", self.ending_trust_coldtruth)])
        elif has_talisman and trust >= self.TRUST_THRESHOLD_TRUE:
            self._set_story(
                "你走向紅花，手中握著《鎮魂歌譜》。\n\n"
                "「你找到了，」她平靜地說，\n"
                "「密碼、歌譜——\n"
                " 你比大多數人走得更遠。」\n\n"
                "「那就說說你的推論吧。」\n"
                "她站起身，\n"
                "眼中有著你說不清楚的複雜情緒。"
            )
            self._set_options([("陳述目前的調查發現", self.ending_true)])
        elif has_talisman:
            self._set_story(
                "你拿出《鎮魂歌譜》與幾項物證。\n\n"
                "紅花看了一眼，神情冷了下來：\n"
                "「東西找得到，不代表你值得託付。」\n\n"
                "「你像是在解一個題目，\n"
                " 不是在面對一條人命。」\n\n"
                "她轉身走回書架陰影處：\n"
                "「今晚到此為止。你先學會『聽』，再來查案。」"
            )
            self._set_options([("沉默離開", self.ending_trust_rejected)])
        elif clue_count >= self.PARTIAL_CLUES and trust >= self.TRUST_THRESHOLD_ALLIANCE:
            self._set_story(
                "你走向紅花，帶著尚未完整的物證。\n\n"
                "她看著你，罕見地先開口：\n"
                "「證據還不夠，但你查案的方式，我認可。」\n\n"
                "她從袖中取出一枚舊徽章，放到你手中：\n"
                "「這是蔚藍學院舊館守備徽章。帶著它，\n"
                " 明晚你可以直接進地下密室最深處。」\n\n"
                "「我們不是朋友，」她淡淡說，\n"
                "「但從現在起，我們是同一邊的人。」"
            )
            self._set_options([("收下徽章，約定再查", self.ending_trust_alliance)])
        elif clue_count >= self.PARTIAL_CLUES:
            self._set_story(
                "你走向紅花，帶著你蒐集到的物證。\n\n"
                "「物證……你找到了一些，」她說，\n"
                "「但還不夠。」\n\n"
                "她嘆了口氣，放下手邊的書卷：\n"
                "「今晚就到這吧。\n"
                " 你不是最糟的那種調查員。\n"
                " 那把鎚子在書架角落，\n"
                " 如果你明晚再來，或許我可以多說幾句。」"
            )
            self._set_options([
                ("接受這個結果", self.ending_normal),
                ("我還沒放棄——返回調查", self.scene_hall),
            ])
        else:
            self._set_story(
                "你毫無準備地走向紅花。\n\n"
                "她抬起眼，眼神沒有溫度：\n"
                "「空手而來，你是警察，還是觀光客？」\n\n"
                "「你知道嗎，上一個這樣走進來的人，」\n"
                "她說，嘴角帶著一絲說不清的弧度，\n"
                "「現在就埋在學院的某個角落。」\n\n"
                "「不不不，我是開玩笑的。」她補充道，\n"
                "「……大概吧。」\n\n"
                "一陣沉默。"
            )
            self._set_options([("…", self.ending_bad_unprepared)])

    # ══════════════════════════════════════════════════════════════════════════
    #  Endings
    # ══════════════════════════════════════════════════════════════════════════

    def ending_secret(self) -> None:
        """Secret ending — all lore + talisman + full case solved."""
        end_bgm = BGM_END if os.path.exists(BGM_END) else BGM_MAIN
        self.music.switch(end_bgm)
        self._show_image("secret_end")
        self._set_story(
            "你將所有物證一一陳列——\n"
            "那把刻著「III」的鎚子，艾莉卡的四葉草，\n"
            "天王星留下的牛仔褲，以及地下室裡的親筆供詞。\n\n"
            "「天王星，」你緩緩說，\n"
            "「他因家道中落懷恨，\n"
            " 那一天衝進來找米糕理論，\n"
            " 失手——或者說，失控了。\n"
            " 艾莉卡目睹了一切，嚇到了，逃了。\n"
            " 艾蜜莉亞知道了，選擇消失。\n"
            " 而你——」\n\n"
            "「你也在圖書館裡，」你說，\n"
            "「你聽見了一切，但你被鎖在裡面。\n"
            " 兩年了，你守在這裡，等著有人來查清楚。」\n\n"
            "紅花的眼眶緩緩泛紅。\n\n"
            "「你……真的都知道了。」她低聲說，\n"
            "「兩年了。兩年來沒有任何人，\n"
            " 願意走進這裡，認真去查這件事。」\n\n"
            "「天王星已經逃到別處了，」她說，\n"
            "「但你現在有足夠的證據了。\n"
            " 去吧，英國皇家警察。\n"
            " 把真相帶回倫敦。」\n\n"
            "窗外，天邊出現了第一縷晨光。\n"
            "圖書館的燭火在晨風中搖曳——\n"
            "不是熄滅，而是向你致意。\n\n"
            "【秘密結局 · 真相大白】\n"
            "蔚藍學院的秘案，終於有了答案。\n"
            "天王星是兇手。紅花，一直在等這一刻。"
        )
        self._set_options([
            ("再玩一次", self.show_intro),
            ("離開", self.root.destroy),
        ])

    def ending_true(self) -> None:
        """True ending — talisman only."""
        end_bgm = BGM_END if os.path.exists(BGM_END) else BGM_MAIN
        self.music.switch(end_bgm)
        self._show_image("true_end")
        self._set_story(
            "你將蒐集到的物證一一陳列——\n"
            "鎚子、四葉草、牛仔褲，以及密碼盒裡的《鎮魂歌譜》。\n\n"
            "紅花靜靜聆聽，臉上看不出情緒。\n\n"
            "「不夠，」她最後說，\n"
            "「你知道案發的跡象，\n"
            " 但你還不知道完整的真相。\n"
            " 那個真正的秘密，\n"
            " 還藏在這圖書館的某處。」\n\n"
            "窗外傳來鳥鳴。天快亮了。\n\n"
            "「但你是我見過最認真的調查員了。」\n"
            "她微微點頭，「下次再來。我會在這裡。」\n\n"
            "【真結局 · 線索足夠】\n"
            "案件有了重要進展，但完整的真相尚未揭露。\n"
            "紅花依然守著圖書館，等待你的下一次造訪。"
        )
        self._set_options([
            ("再玩一次", self.show_intro),
            ("離開", self.root.destroy),
        ])

    def ending_trust_alliance(self) -> None:
        """Affinity ending — high trust without full evidence."""
        self._show_image("normal_end")
        self._set_story(
            "你收下了那枚舊徽章。\n\n"
            "紅花背對著你，聲音很輕：\n"
            "「別讓我後悔。」\n\n"
            "你走出圖書館時，天邊剛泛白。\n"
            "這一夜你沒有破案，\n"
            "卻換來了比答案更難得的東西——\n"
            "紅花的信任。\n\n"
            "【信任結局 · 共犯不是罪犯】\n"
            "你與紅花建立了調查同盟。\n"
            "真相尚未揭曉，但你們將並肩追到最後。"
        )
        self._set_options([
            ("再玩一次", self.show_intro),
            ("離開", self.root.destroy),
        ])

    def ending_trust_rejected(self) -> None:
        """Affinity ending — low trust with talisman."""
        self._show_image("bad_a")
        self._set_story(
            "你站在原地，手中的《鎮魂歌譜》忽然變得沉重。\n\n"
            "紅花沒有再看你，只說了一句：\n"
            "「會查案，不等於懂人。」\n\n"
            "門在你身後緩緩關上。\n"
            "你帶走了證據，卻帶不走她的配合。\n\n"
            "【信任結局 · 被拒於門外】\n"
            "你拿到關鍵物件，卻失去了紅花的信任。\n"
            "這起案件，變得更難了。"
        )
        self._set_options([
            ("重新開始", self.show_intro),
            ("離開", self.root.destroy),
        ])

    def ending_trust_coldtruth(self) -> None:
        """Affinity ending — case solved but relationship remains distant."""
        end_bgm = BGM_END if os.path.exists(BGM_END) else BGM_MAIN
        self.music.switch(end_bgm)
        self._show_image("true_end")
        self._set_story(
            "證據鏈完整，供詞清楚，真相已然浮現。\n\n"
            "你報出天王星的名字時，\n"
            "紅花沒有驚訝，也沒有喜悅。\n\n"
            "「你做到了，」她說，\n"
            "「但到這裡就好。」\n\n"
            "她把最後一份檔案留在桌上，\n"
            "卻沒有把目光留給你。\n\n"
            "【信任結局 · 冷真相】\n"
            "你解開了命案，卻沒有解開紅花心中的門。\n"
            "真相是對的，但你們仍然陌生。"
        )
        self._set_options([
            ("再玩一次", self.show_intro),
            ("離開", self.root.destroy),
        ])

    def ending_normal(self) -> None:
        """Normal ending — partial clues."""
        self._show_image("normal_end")
        self._set_story(
            "你以蒐集到的物證為依據，\n"
            "笨拙地說明著自己的推論。\n\n"
            "紅花靜靜地聽完，\n"
            "嘴角浮現一個難以形容的表情——\n"
            "不是滿意，也不是失望。\n\n"
            "「你努力過了，」她說，\n"
            "「今晚就到這裡吧。」\n\n"
            "她抬起眼，看向圖書館的角落——\n"
            "那裡有一把鏽跡斑斑的鎚子。\n"
            "「下次來，從那裡開始查。」\n\n"
            "你走出大門，回頭望去，\n"
            "黑暗中還有一點燭光，孤獨地燃著。\n\n"
            "【普通結局 · 物證不足】\n"
            "危機暫緩，但謎團仍在。\n"
            "紅花依舊守在廢棄的蔚藍學院圖書館，\n"
            "等待更完整的調查。"
        )
        self._set_options([
            ("再玩一次", self.show_intro),
            ("離開", self.root.destroy),
        ])

    def ending_bad_unprepared(self) -> None:
        """Bad ending A — confronted without preparation."""
        self._show_image("bad_a")
        self._set_story(
            "你毫無準備地走向紅花。\n\n"
            "一陣沉默，長到有些尷尬。\n\n"
            "「你知道嗎，」紅花緩緩開口，\n"
            "「蔚藍學院有個傳說——\n"
            " 每個空手走進這圖書館的人，\n"
            " 都會在某個書架後面找到自己的名字。」\n\n"
            "她停頓了一下。\n\n"
            "「我是說……刻在木頭上的那種名字。」\n\n"
            "你感覺到後背一陣發涼。\n\n"
            "「不過放心，」她補充道，\n"
            "「我最近沒有空間了。\n"
            " 你先回去，明天備好物證再來。」\n\n"
            "【壞結局 A · 準備不足】\n"
            "你被請出了圖書館。\n"
            "紅花依然守在那裡，優雅而神秘，\n"
            "傳說中的檳榔味，你沒能親身體驗到。"
        )
        self._set_options([
            ("重新開始", self.show_intro),
            ("離開", self.root.destroy),
        ])

    def ending_bad_codefail(self) -> None:
        """Bad ending B — too many code failures."""
        self._show_image("bad_b")
        self._set_story(
            "第三次輸入錯誤的瞬間——\n\n"
            "密碼盒劇烈震動。\n"
            "一股奇異的氣息從縫隙中湧出，\n"
            "帶著石灰、舊紙與……\n"
            "隱隱約約的，不知從何而來的檳榔味。\n\n"
            "你試圖後退，卻發現雙腿不聽使喚。\n\n"
            "黑暗中，你聽見紅花輕聲說：\n\n"
            "「猜不出密碼的人，\n"
            " 就留在這裡當書的護衛吧。」\n\n"
            "頓了頓，她補充：\n\n"
            "「放心，我會好好照顧你的。\n"
            " ……就像照顧這些書一樣。」\n\n"
            "【壞結局 B · 密碼失敗】\n"
            "你成為了圖書館的新住客。\n"
            "另外——傳說中的檳榔味，\n"
            "你終於親身體驗到了。"
        )
        self._set_options([
            ("重新開始", self.show_intro),
            ("離開", self.root.destroy),
        ])


# ══════════════════════════════════════════════════════════════════════════════
#  Entry point
# ══════════════════════════════════════════════════════════════════════════════
def main() -> None:
    root = tk.Tk()
    HonghuaGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
