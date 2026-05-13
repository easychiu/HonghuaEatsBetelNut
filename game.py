"""
紅花吃檳榔：圖書館夜談 — 深夜完全版
Enhanced visual novel · scene illustrations · Mureka.ai BGM
"""
from __future__ import annotations

import os
import threading
import time
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

try:
    import requests as _requests
    _REQUESTS = True
except ImportError:
    _REQUESTS = False

# ── paths ──────────────────────────────────────────────────────────────────────
_DIR      = os.path.dirname(os.path.abspath(__file__))
INFO_JPG  = os.path.join(_DIR, "info.jpg")
ASSETS    = os.path.join(_DIR, "assets")
BGM_MAIN  = os.path.join(ASSETS, "bgm_main.mp3")
BGM_END   = os.path.join(ASSETS, "bgm_end.mp3")

MUREKA_KEY = "op_27fqd8alidss5kntoh3651wtos85jf0g2"
MUREKA_URL = "https://api.mureka.ai"

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


def _build(key: str) -> Optional[object]:
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


# ══════════════════════════════════════════════════════════════════════════════
#  Mureka.ai BGM generation
# ══════════════════════════════════════════════════════════════════════════════
def _mureka_generate_bgm(prompt: str, save_path: str, timeout: float = 360) -> bool:
    """Generate instrumental BGM via Mureka.ai and save to disk. Blocking."""
    if not _REQUESTS:
        return False
    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        headers = {
            "Authorization": f"Bearer {MUREKA_KEY}",
            "Content-Type": "application/json",
        }
        resp = _requests.post(
            f"{MUREKA_URL}/v1/instrumental/generate",
            json={"model": "auto", "prompt": prompt},
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()
        task_id = resp.json().get("id", "")
        if not task_id:
            return False

        start = time.time()
        while time.time() - start < timeout:
            q = _requests.get(
                f"{MUREKA_URL}/v1/instrumental/query/{task_id}",
                headers=headers,
                timeout=20,
            )
            q.raise_for_status()
            data = q.json()
            status = data.get("status", "failed")
            if status in ("failed", "cancelled", "timeouted"):
                return False
            if status == "succeeded":
                choices = data.get("choices", [])
                if not choices:
                    return False
                url = choices[0].get("url", "")
                if not url:
                    return False
                dl = _requests.get(url, timeout=60)
                with open(save_path, "wb") as f:
                    f.write(dl.content)
                return True
            time.sleep(2)
        return False
    except Exception:
        return False


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
    PARTIAL_CLUES    = 2
    MAX_CODE_TRIES   = 3
    WINDOW_TITLE     = "紅花吃檳榔：圖書館夜談 — 深夜完全版"

    BGM_MAIN_PROMPT = (
        "dark gothic horror atmosphere, mysterious ancient library at night, "
        "haunting orchestral strings, candlelight ambiance, slow tension, "
        "Chinese folklore horror, piano and cello, ominous, 80 bpm"
    )
    BGM_END_PROMPT = (
        "bittersweet emotional release, gothic piano solo, melancholic hope, "
        "gentle resolution, Chinese folklore inspired, 70 bpm"
    )

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
        self.code_tries_left = self.MAX_CODE_TRIES
        self._type_job: Optional[str] = None
        self._current_img: Optional[object] = None

        self.music = MusicPlayer()

        self._build_ui()
        threading.Thread(target=self._prepare_bgm, daemon=True).start()
        self.show_intro()

    # ── BGM background task ───────────────────────────────────────────────────
    def _prepare_bgm(self) -> None:
        if not os.path.exists(BGM_MAIN):
            _mureka_generate_bgm(self.BGM_MAIN_PROMPT, BGM_MAIN)
        if os.path.exists(BGM_MAIN):
            self.root.after(0, lambda: self.music.play(BGM_MAIN))

        if not os.path.exists(BGM_END):
            _mureka_generate_bgm(self.BGM_END_PROMPT, BGM_END)

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
        clues  = " | ".join(f"{k}:{v}" for k, v in sorted(self.clues.items())) or "尚未蒐集"
        lore_n = len(self.lore)
        tries  = self.code_tries_left
        self.status_var.set(
            f"道具：{items}　　線索：{clues}　　密碼剩餘 {tries} 次　　典故：{lore_n}/3"
        )

    def _reset_state(self) -> None:
        self.inventory.clear()
        self.clues.clear()
        self.lore.clear()
        self.code_tries_left = self.MAX_CODE_TRIES
        self._refresh_status()

    # ══════════════════════════════════════════════════════════════════════════
    #  Scenes
    # ══════════════════════════════════════════════════════════════════════════

    def show_intro(self) -> None:
        self._reset_state()
        self._show_image("intro")
        self._set_story(
            "===================================\n"
            "  紅花吃檳榔：圖書館夜談  深夜完全版\n"
            "===================================\n\n"
            "「紅花綻放之處，便是你的葬身之地。\n"
            " 惹我？那就用你的血，來餵這口鮮紅。」\n"
            "                              ——紅花\n\n"
            "深夜的圖書館，一盞燭火搖曳於幽暗之中。\n"
            "傳說中的紅花，就在那裡。",
            typing=False,
        )
        self._set_options([("進入故事", self.scene_prologue)])

    def scene_prologue(self) -> None:
        self._show_image("prologue")
        self._set_story(
            "你是受雇的調查員，接到一份奇怪的委託：\n"
            "進入城外那座廢棄圖書館，記錄其中的「異象」。\n\n"
            "踏入大門，你看見燭光搖曳的書架間，有人端坐其中。\n\n"
            "銀白色頭髮，水手服，嘴角帶著一抹血色——\n"
            "她將一片檳榔塞入口中，緩緩抬起眼眸看著你。\n\n"
            "「終於又有人來了，」她低聲說，\n"
            "「這座圖書館藏著你想知道的一切。\n"
            " 但在你找到答案之前——你哪兒也別想去。」\n\n"
            "你掃視四周：三根紫色燭臺，佈滿灰塵的書架，\n"
            "古舊的羽毛筆，還有一只神秘的檳榔盒。\n\n"
            "天亮之前，必須找到出路。"
        )
        self._set_options([
            ("開始調查圖書館", self.scene_hall),
            ("直接上前與紅花說話", self.scene_confront),
        ])

    # ── main hall (hub) ───────────────────────────────────────────────────────
    def scene_hall(self) -> None:
        self._refresh_status()
        self._show_image("hall")
        has_key = "書架鑰匙" in self.inventory
        basement_hint = "\n（口袋中有一把生鏽的書架鑰匙……）" if has_key else ""
        self._set_story(
            "圖書館大廳。\n"
            "燭光映照著三個方向的書架，\n"
            "桌上散落著古書、羽毛筆、以及那只密碼盒。\n"
            "紅花靜靜坐在遠處，目光如炬，看著你的一舉一動。\n\n"
            "可以調查的地方：古書・羽毛筆・檳榔盒・書架深處・研究桌・窗邊"
            + basement_hint
        )
        opts: list[tuple[str, Callable]] = [
            ("查看古書", self.inspect_book),
            ("查看羽毛筆", self.inspect_feather),
            ("查看檳榔盒", self.inspect_box),
            ("前往書架深處", self.scene_bookshelves),
            ("前往研究桌", self.scene_desk),
            ("前往窗邊", self.scene_window),
        ]
        if has_key:
            opts.append(("打開地下室", self.scene_basement))
        opts += [
            ("嘗試解鎖密碼盒", self.try_unlock),
            ("前去面對紅花", self.scene_confront),
        ]
        self._set_options(opts)

    # ── book ──────────────────────────────────────────────────────────────────
    def inspect_book(self) -> None:
        self.clues["古書"] = 3
        self.lore.add("古書典故")
        self._refresh_status()
        self._show_image("book")
        self._set_story(
            "《圓周率秘錄》——書脊上的金字已褪去大半。\n\n"
            "翻開扉頁，有人用紅墨水寫道：\n"
            "「答案始於圓，圓始於 3。」\n\n"
            "書中夾著一張泛黃的紙條：\n"
            "「紅花曾在此苦讀三年，企圖以數學破解命運之鎖。\n"
            " 她找到了——卻也因此失去了離開的能力。」\n\n"
            "【線索取得】第一碼是 3。\n"
            "【典故】古書記載了紅花與數字命運的淵源。"
        )
        self._set_options([
            ("繼續調查", self.scene_hall),
            ("直接面對紅花", self.scene_confront),
        ])

    # ── feather ───────────────────────────────────────────────────────────────
    def inspect_feather(self) -> None:
        self.clues["羽毛筆"] = 1
        self._refresh_status()
        self._show_image("feather")
        self._set_story(
            "一根墨汁未乾的白色羽毛筆，\n"
            "筆尖點著未完成的算式。\n\n"
            "壓在筆下的字條寫著：\n"
            "「一筆定心，心正則路正。第二碼藏於此。」\n\n"
            "你仔細辨認墨漬的形狀——\n"
            "那是一個未被圈起的數字「1」。\n\n"
            "【線索取得】第二碼是 1。"
        )
        self._set_options([
            ("繼續調查", self.scene_hall),
            ("直接面對紅花", self.scene_confront),
        ])

    # ── box ───────────────────────────────────────────────────────────────────
    def inspect_box(self) -> None:
        self.clues["檳榔盒"] = 4
        self._refresh_status()
        self._show_image("box")
        self._set_story(
            "金牌正宗檳榔——外包裝的文字已模糊，\n"
            "但底部用刀刻著四個字：「四季花開」。\n\n"
            "「四季」——你默數：春夏秋冬，共四季。\n\n"
            "盒蓋內側還有一行小字：\n"
            "「此盒由紅花親手封印。欲開者，需知三數之和。」\n\n"
            "【線索取得】第三碼是 4。"
        )
        self._set_options([
            ("繼續調查", self.scene_hall),
            ("嘗試解鎖", self.try_unlock),
        ])

    # ── bookshelves area ──────────────────────────────────────────────────────
    def scene_bookshelves(self) -> None:
        self._refresh_status()
        self._show_image("bookshelves")
        self._set_story(
            "書架深處，光線幾乎不存在。\n\n"
            "你摸索前行，發現一排陳舊的書架上，\n"
            "有四本書被刻意排列在同一層：\n\n"
            "   《晨曦錄》  《暮色卷》  《星辰賦》  《隱月頌》\n\n"
            "架下有一塊石板，刻著謎語：\n\n"
            "「太陽初升，書見曙光。\n"
            " 日落西山，紙墨留香。\n"
            " 繁星閃耀，筆走龍蛇。\n"
            " 月隱無蹤，秘密封藏。」\n\n"
            "石板旁有一個小鎖孔，按照正確的書序才能打開。"
        )
        self._set_options([
            ("嘗試排列四書（解謎）", self.puzzle_bookshelf),
            ("返回大廳", self.scene_hall),
        ])

    def puzzle_bookshelf(self) -> None:
        if "書架鑰匙" in self.inventory:
            messagebox.showinfo("已解鎖", "書架鑰匙已在你手中。")
            self.scene_hall()
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("書架謎題——四書排序")
        dialog.geometry("520x330")
        dialog.configure(bg=C["bg"])
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog,
            text="請根據謎語「日升→日落→繁星→月隱」選出正確排列順序：",
            font=_f(11),
            bg=C["bg"],
            fg=C["fg"],
            wraplength=480,
        ).pack(pady=14, padx=14)

        choices = [
            ("A", "晨曦錄 → 暮色卷 → 星辰賦 → 隱月頌（黎明→黃昏→深夜→新月）"),
            ("B", "隱月頌 → 星辰賦 → 暮色卷 → 晨曦錄（逆序）"),
            ("C", "暮色卷 → 晨曦錄 → 隱月頌 → 星辰賦（混亂）"),
            ("D", "星辰賦 → 晨曦錄 → 暮色卷 → 隱月頌（亂序）"),
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
                self.inventory.add("書架鑰匙")
                self._refresh_status()
                messagebox.showinfo(
                    "解謎成功",
                    "書架底部傳來「喀噠」一聲，\n你取得了一把生鏽的書架鑰匙！\n\n"
                    "（可用來打開大廳的地下室入口）",
                    parent=dialog,
                )
                dialog.destroy()
                self.scene_hall()
            else:
                messagebox.showerror(
                    "順序錯誤",
                    "書架紋絲不動……仔細重讀謎語，再試一次。",
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
            "桌面散亂地鋪著筆記與殘破的文件，\n"
            "一根快燃盡的蠟燭在紙堆旁顫抖著。\n\n"
            "桌角有一本合上的日記，\n"
            "封面上縫著一片乾枯的紅色花瓣。"
        )
        self._set_options([
            ("閱讀日記", self.read_diary),
            ("返回大廳", self.scene_hall),
        ])

    def read_diary(self) -> None:
        self.lore.add("日記頁")
        self._refresh_status()
        self._show_image("diary")
        self._set_story(
            "【日記　第七三頁】\n\n"
            "今夜我終於明白了那個詛咒的本質。\n"
            "那本古書所藏的不是知識——是一道枷鎖。\n"
            "誰解開了它，誰就必須永遠守護它。\n\n"
            "我以為我能承受。我以為我夠強大。\n\n"
            "但當我第一次翻開那頁，我的腳步就再也\n"
            "無法邁出這座圖書館的門檻。\n\n"
            "若有人能找到「安魂符」，\n"
            "以它驅散書中的怨念，\n"
            "或許……或許那道枷鎖就能解開。\n\n"
            "                              ——紅花　謹記\n\n"
            "【典故】你理解了紅花被困此處的真相。"
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
            "窗沿上有一張被雨水打濕、幾乎辨認不了的紙條。\n\n"
            "你努力辨認……"
        )
        self._set_options([
            ("仔細辨認紙條", self.inspect_window_note),
            ("返回大廳", self.scene_hall),
        ])

    def inspect_window_note(self) -> None:
        self.lore.add("窗邊記憶")
        self._refresh_status()
        self._show_image("window")
        self._set_story(
            "紙條的字跡在燭光下若隱若現：\n\n"
            "「我恨你們。你們說要救我。\n"
            " 你們說會回來。\n"
            " 但沒有人……沒有人回來過。\n\n"
            " 所以我選擇留下。\n"
            " 留在這裡，等待一個\n"
            " 真正能讀懂我的人。\n\n"
            " 如果你在讀這張紙——\n"
            " 你就是那個人。\n"
            " 請……不要讓我白等了。」\n\n"
            "【典故】你感受到紅花深藏的孤獨與等待。"
        )
        self._set_options([
            ("返回大廳", self.scene_hall),
            ("直接去找紅花", self.scene_confront),
        ])

    # ── code lock puzzle ──────────────────────────────────────────────────────
    def try_unlock(self) -> None:
        if len(self.clues) < self.REQUIRED_CLUES:
            messagebox.showinfo(
                "線索不足",
                f"你只蒐集了 {len(self.clues)}/{self.REQUIRED_CLUES} 個線索，\n"
                "尚不足以推算密碼。",
            )
            self.scene_hall()
            return
        self._create_code_dialog()

    def _create_code_dialog(self) -> None:
        if "安魂符" in self.inventory:
            messagebox.showinfo("已解鎖", "你已持有安魂符。")
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
            text="根據三個線索推算密碼，輸入三位數：",
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
                self.inventory.add("安魂符")
                self._refresh_status()
                messagebox.showinfo(
                    "解鎖成功！",
                    "密碼盒緩緩打開，裡面有一張泛黃的符紙——\n「安魂符」入手！",
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
        if "書架鑰匙" not in self.inventory:
            messagebox.showinfo("門緊閉", "地下室的門紋絲不動，需要某種鑰匙。")
            self.scene_hall()
            return
        self._refresh_status()
        self._show_image("basement")
        self._set_story(
            "鑰匙插入門縫，鏽跡斑斑的鎖機發出一聲沉悶的聲響。\n\n"
            "你踏上狹窄的石階，潮濕與腐敗的氣味撲面而來。\n\n"
            "燭光在你身後搖曳，前方是一片深不見底的黑暗。\n"
            "你繼續下行……\n\n"
            "數十級石階之後，你看到一扇半開的石門，\n"
            "門縫中透出隱約的紅光。"
        )
        self._set_options([
            ("推開石門探索", self.scene_basement_deep),
            ("返回大廳", self.scene_hall),
        ])

    def scene_basement_deep(self) -> None:
        self.lore.add("地下真相")
        self._refresh_status()
        self._show_image("basement_deep")
        self._set_story(
            "石室中央，有一個刻滿符文的石台。\n\n"
            "台上擺著一本血紅色封面的典籍——\n"
            "《縛靈典·圖書館章》\n\n"
            "你翻開：\n\n"
            "「凡觸碰『真理之封』者，\n"
            " 其靈魂將與封印共存，\n"
            " 直至有人以『安魂符』和『真情告解』\n"
            " 同時破解封印，方可得解脫。\n\n"
            " 安魂符破其形，\n"
            " 真情告解破其心。」\n\n"
            "「真情告解」——你想起窗邊的那張紙條，\n"
            "還有日記裡紅花傾訴的那段孤獨。\n\n"
            "【典故】你掌握了解開紅花封印的完整方式。"
        )
        self._set_options([
            ("帶著這個發現返回大廳", self.scene_hall),
        ])

    # ── confrontation ─────────────────────────────────────────────────────────
    def scene_confront(self) -> None:
        self._refresh_status()
        self._show_image("confront")

        has_talisman = "安魂符" in self.inventory
        all_lore     = len(self.lore) >= 3
        clue_count   = len(self.clues)

        if has_talisman and all_lore:
            self._set_story(
                "你走向紅花，手中握著安魂符。\n\n"
                "「你……找到了那裡。」她低聲說，\n"
                "眼神中第一次出現了動搖。\n\n"
                "「你不只知道那個數字。\n"
                " 你還知道我的故事……為什麼你要知道？」\n\n"
                "你注視著她，緩緩說出你在日記和窗台上讀到的一切——\n"
                "她三年的苦讀，那道詛咒，以及那張「不要讓我白等了」的紙條。\n\n"
                "紅花怔住了。"
            )
            self._set_options([("舉起安魂符，說出真情", self.ending_secret)])
        elif has_talisman:
            self._set_story(
                "你走向紅花，手中握著安魂符。\n\n"
                "「你找到了，」她平靜地說，\n"
                "「解開密碼——找到符紙。」\n\n"
                "「那就試試吧。」她站起身，\n"
                "眼中有著你說不清楚的複雜情緒。"
            )
            self._set_options([("使用安魂符", self.ending_true)])
        elif clue_count >= self.PARTIAL_CLUES:
            self._set_story(
                "你走向紅花，帶著你蒐集到的線索。\n\n"
                "「線索……你找到了一些，」她說，\n"
                "「但還不夠。」\n\n"
                "她嘆了口氣，放下手中的檳榔：\n"
                "「今晚就到這吧。你不是最差的那種人。」"
            )
            self._set_options([
                ("接受這個結果", self.ending_normal),
                ("我還沒放棄——返回調查", self.scene_hall),
            ])
        else:
            self._set_story(
                "你毫無準備地走向紅花。\n\n"
                "她抬起眼，眼神沒有溫度：\n"
                "「空手而來。你是在嘲弄我嗎？」\n\n"
                "一陣檳榔的辛辣氣味彌漫開來——\n"
                "你感到眩暈，意識開始渙散。"
            )
            self._set_options([("…", self.ending_bad_unprepared)])

    # ══════════════════════════════════════════════════════════════════════════
    #  Endings
    # ══════════════════════════════════════════════════════════════════════════

    def ending_secret(self) -> None:
        """Secret ending — all lore + talisman + emotional confession."""
        end_bgm = BGM_END if os.path.exists(BGM_END) else BGM_MAIN
        self.music.switch(end_bgm)
        self._show_image("secret_end")
        self._set_story(
            "你舉起安魂符，緩緩念出古書上的句子。\n\n"
            "但同時——你開口說話了：\n\n"
            "「我看了你的日記。我讀了你窗台上的字條。\n"
            " 我去了地下室，我知道了一切。\n\n"
            " 你等了很久了。\n"
            " 你一個人，在這裡，等了那麼久。\n\n"
            " 我回來了。」\n\n"
            "紅花的眼眶紅了。\n\n"
            "符文從書架上一一熄滅，封印在光芒中消散。\n"
            "窗外，天邊出現了第一縷晨光。\n\n"
            "她輕輕落下一滴淚，\n"
            "然後微笑著，慢慢消失在你眼前——\n"
            "不是死去，而是……終於自由了。\n\n"
            "圖書館的燭火一盞一盞熄滅，只剩清晨的陽光。\n\n"
            "【秘密結局 · 真情告解】\n"
            "你解開了紅花的詛咒，也解開了她內心的枷鎖。\n"
            "她等的，就是這一刻。"
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
            "你舉起安魂符，低聲念出古書上的字句。\n\n"
            "符紙燃起紅色的火光，書架上的符文一一暗去。\n\n"
            "紅花怔怔地望著那片光，\n"
            "慢慢地，慢慢地，放下了手中的檳榔盒。\n\n"
            "「三年了，」她低聲說，\n"
            "「我以為沒有人能找到那個答案。」\n\n"
            "窗外傳來鳥鳴。天快亮了。\n\n"
            "封印消散，詛咒解除。\n"
            "紅花的身影在晨光中逐漸透明。\n\n"
            "「謝謝你……」她的聲音遠去。\n\n"
            "【真結局 · 安魂符解封】\n"
            "你成功化解了圖書館的異變，紅花重獲自由。"
        )
        self._set_options([
            ("再玩一次", self.show_intro),
            ("離開", self.root.destroy),
        ])

    def ending_normal(self) -> None:
        """Normal ending — partial clues."""
        self._show_image("normal_end")
        self._set_story(
            "你以蒐集到的線索為依據，笨拙地說明著自己的推論。\n\n"
            "紅花靜靜地聽完，\n"
            "嘴角浮現一個難以形容的表情——\n"
            "不是滿意，也不是失望。\n\n"
            "「你努力過了，」她說，\n"
            "「今晚就到這裡吧。」\n\n"
            "她拾起桌上的檳榔，重新咀嚼起來。\n"
            "圖書館的燭火一如往常地搖曳，沒有任何改變。\n\n"
            "你走出大門，回頭望去，\n"
            "黑暗中還有一點燭光，孤獨地燃著。\n\n"
            "【普通結局 · 線索不足】\n"
            "危機暫緩，但謎團仍在。\n"
            "紅花依舊守在那座圖書館中，等待著更完整的解答。"
        )
        self._set_options([
            ("再玩一次", self.show_intro),
            ("離開", self.root.destroy),
        ])

    def ending_bad_unprepared(self) -> None:
        """Bad ending A — confronted without preparation."""
        self._show_image("bad_a")
        self._set_story(
            "意識一片混亂。\n\n"
            "你聽見遠處紅花緩慢說著什麼，\n"
            "但你已無力分辨。\n\n"
            "最後一個清晰的畫面，是她嘴角的那抹紅——\n"
            "不知是唇色，還是那口鮮紅的汁液。\n\n"
            "「不怕，」她的聲音像從水底傳來，\n"
            "「你就留下來陪我吧。\n"
            " 圖書館最不缺的，就是時間。」\n\n"
            "【壞結局 A · 準備不足】\n"
            "你失去了主導權，成為了圖書館的另一個守夜人。"
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
            "紅色的霧氣從縫隙中噴湧而出，\n"
            "帶著一股刺鼻的石灰與檳榔混合的氣味。\n\n"
            "你試圖後退，卻發現雙腿不聽使喚。\n\n"
            "紅霧蔓延，燭火一一熄滅。\n"
            "黑暗中，你聽見紅花輕聲說：\n\n"
            "「猜不出答案的人，就留在這裡成為謎題吧。」\n\n"
            "【壞結局 B · 密碼失敗】\n"
            "紅霧侵蝕了你的理智。圖書館獲得了新的守護者。"
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
