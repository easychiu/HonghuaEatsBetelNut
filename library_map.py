"""Library map rendering and interaction flow."""
from __future__ import annotations

import os
from typing import TYPE_CHECKING, Protocol, Optional, TypeAlias

import story_texts as ST

if TYPE_CHECKING:
    from PIL.ImageTk import PhotoImage as MapImage
else:
    MapImage: TypeAlias = object

try:
    from PIL import Image, ImageDraw, ImageTk
    _PIL = True
    _RESAMPLING = getattr(Image, "Resampling", None)
    _LANCZOS = _RESAMPLING.LANCZOS if _RESAMPLING else Image.LANCZOS  # type: ignore[attr-defined]
except ImportError:
    _PIL = False
    _LANCZOS = 1  # unused when _PIL is False


MAP_SCENE_TITLES: dict[str, str] = {
    "map_f1": "圖書館地圖・一樓",
    "map_f2": "圖書館地圖・二樓",
    "map_f3": "圖書館地圖・三樓",
}

# Reference coordinate system for hotspot areas (matched to base canvas size).
# All room positions are estimated as proportional regions within the floor
# plan images (map_f1.png / map_f2.png / map_f3.png), using a 460×490 grid.
_MAP_BASE_W = 460
_MAP_BASE_H = 490
_MAP_CANVAS_W = 1462
_MAP_CANVAS_H = 1076
_DIR = os.path.dirname(os.path.abspath(__file__))

# ── 1F room areas (based on 1F floor plan image layout) ──────────────────────
# Rooms: ①正門大廳 ②中央書庫 ③閱覽室A ④閱覽室B ⑤會議廳I ⑥收藏室 ⑦管理室 ⑧守衛室
_1F_ROOMS = {
    "room_a":          (23,  34, 133, 162),   # ③ 閱覽室A     top-left
    "room_b":          (267,  34, 391, 162),   # ④ 閱覽室B     top-right
    "collection_room": (322, 186, 437, 294),   # ⑥ 收藏室（古籍庫）right-centre
    "meeting_room":    (5,   186,  83, 294),   # ⑤ 會議廳I     left-centre
    "corridor_1f":     (23,  294, 129, 367),   # ⑦ 管理室 / 走廊
    "guard_room":      (308, 294, 414, 367),   # ⑧ 守衛室
}

# ── 2F room areas (based on 2F floor plan image layout) ──────────────────────
# Rooms: ①二樓迴廊 ②中央挑空 ③研究室A ④研究室B ⑤會議廳II ⑥檔案室 ⑦修復工坊 ⑧隱藏樓梯
_2F_ROOMS = {
    "desk":         (32,  34, 143, 152),   # ③ 研究室A     top-left
    "window":       (290,  34, 400, 152),   # ④ 研究室B     top-right
    "archive_room": (322, 186, 451, 343),   # ⑥ 檔案室（禁書區）right
    "meeting_room": (5,   186, 106, 343),   # ⑤ 會議廳II    left
    "workshop":     (37,  353, 170, 446),   # ⑦ 修復工坊    bottom-left
    "corridor_2f":  (143,  34, 290, 186),   # ① 二樓迴廊    centre ring
}

# ── 3F room areas (based on 3F floor plan image layout) ──────────────────────
# Rooms: ①三樓迴廊 ②大房型書房（館長室）③私人研究室 ④廢棄閱覽室 ⑤封閉儲藏室 ⑥鐘塔通道
_3F_ROOMS = {
    "hall":           (23,  20, 212, 235),   # ② 大房型書房（館長室外調查區）
    "confront":       (23,  20, 212, 235),   # same area → leads to confront
    "corridor_3f":    (258,  20, 419, 216),  # ③ 私人研究室
    "abandoned_room": (23,  245, 184, 402),  # ④ 廢棄閱覽室  bottom-left
    "closed_storage": (253, 245, 423, 402),  # ⑤ 封閉儲藏室  bottom-right (danger)
}

# Floor-switch tab positions at the bottom of the canvas
_FLOOR_TABS = [
    ((20,  420, 130, 478), "一樓"),
    ((170, 420, 280, 478), "二樓"),
    ((320, 420, 430, 478), "三樓"),
]


class MapSceneGame(Protocol):
    _map_floor: int
    inventory: object  # supports __contains__ (e.g. Collection[str])

    def _refresh_status(self) -> None: ...
    def _show_image(self, key: str) -> None: ...
    def _set_story(self, text: str) -> None: ...
    def _set_options(self, options: list[tuple[str, object]]) -> None: ...
    def _set_image_actions(self, actions: list[dict[str, object]]) -> None: ...
    def scene_map_floor1(self) -> None: ...
    def scene_map_floor2(self) -> None: ...
    def scene_map_floor3(self) -> None: ...
    def scene_hall(self) -> None: ...
    def scene_confront(self) -> None: ...
    def scene_basement(self) -> None: ...
    # ── 1F scenes ─────────────────────────────────────────────────────────────
    def scene_room_a(self) -> None: ...
    def scene_room_b(self) -> None: ...
    def scene_collection_room(self) -> None: ...
    def scene_meeting_room(self) -> None: ...
    def scene_corridor_1f(self) -> None: ...
    def scene_guard_room(self) -> None: ...
    # ── 2F scenes ─────────────────────────────────────────────────────────────
    def scene_desk(self) -> None: ...
    def scene_window(self) -> None: ...
    def scene_archive_room(self) -> None: ...
    def scene_workshop(self) -> None: ...
    def scene_corridor_2f(self) -> None: ...
    # ── 3F scenes ─────────────────────────────────────────────────────────────
    def scene_corridor_3f(self) -> None: ...
    def scene_abandoned_room(self) -> None: ...
    def scene_basement_storage_room(self) -> None: ...


def _pixel_library_map(floor: int, iw: int, ih: int) -> Optional[MapImage]:
    if not _PIL:
        return None
    img = Image.new("RGBA", (iw, ih), (12, 12, 18, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    cell = 10
    for y in range(0, ih, cell):
        for x in range(0, iw, cell):
            shade = 18 + ((x // cell + y // cell) % 2) * 10
            draw.rectangle([x, y, x + cell, y + cell], fill=(shade, shade, shade + 8, 255))

    draw.rectangle([30, 20, iw - 30, ih - 20], outline=(220, 180, 120, 255), width=4)
    draw.rectangle([70, 60, iw - 70, ih - 60], outline=(130, 190, 255, 255), width=3)
    draw.rectangle([150, 150, iw - 150, ih - 150], fill=(30, 38, 58, 255), outline=(100, 140, 220, 255), width=3)
    draw.text((170, 220), "中央挑空", fill=(220, 230, 255, 255))

    draw.rectangle([90, 90, iw - 90, 125], fill=(126, 95, 52, 255))
    draw.rectangle([90, ih - 125, iw - 90, ih - 90], fill=(126, 95, 52, 255))
    draw.rectangle([90, 130, 125, ih - 130], fill=(126, 95, 52, 255))
    draw.rectangle([iw - 125, 130, iw - 90, ih - 130], fill=(126, 95, 52, 255))

    room_color = (66, 82, 110, 255)
    room_outline = (160, 196, 255, 255)
    # Per-floor room labels for top-left and top-right rooms
    floor_labels: dict[int, dict[str, str]] = {
        1: {"top_left": "閱覽室A", "top_right": "閱覽室B",    "bottom_left": "收藏室",  "bottom_right": "守衛室",  "mid_right": "會議廳I"},
        2: {"top_left": "研究室A", "top_right": "研究室B",    "bottom_left": "檔案室",  "bottom_right": "修復工坊", "mid_right": "會議廳II"},
        3: {"top_left": "私人研究室", "top_right": "廢棄閱覽室", "bottom_left": "封閉儲藏室", "bottom_right": "鐘塔通道", "mid_right": "館長室"},
    }
    labels = floor_labels.get(floor, floor_labels[1])
    rooms_def = [
        (36, 36, 126, 106, labels["top_left"]),
        (334, 36, 424, 106, labels["top_right"]),
        (36, 384, 126, 454, labels["bottom_left"]),
        (334, 384, 424, 454, labels["bottom_right"]),
        (334, 288, 424, 358, labels["mid_right"]),
    ]
    for x1, y1, x2, y2, label in rooms_def:
        draw.rectangle([x1, y1, x2, y2], fill=room_color, outline=room_outline, width=2)
        draw.text((x1 + 8, y1 + 24), label, fill=(230, 240, 255, 255))

    if floor == 1:
        draw.rectangle([36, 288, 126, 358], fill=(132, 40, 45, 255), outline=(255, 140, 130, 255), width=3)
        draw.text((42, 314), "收藏室", fill=(255, 220, 220, 255))
    if floor == 3:
        draw.rectangle([168, 24, 292, 84], fill=(42, 108, 88, 255), outline=(146, 255, 212, 255), width=3)
        draw.text((178, 48), "館長室(紅花)", fill=(220, 255, 240, 255))

    draw.rectangle([0, 0, iw, 28], fill=(48, 16, 28, 220))
    draw.text((10, 6), f"像素上帝視角地圖・第{floor}層", fill=(255, 220, 190, 255))
    return ImageTk.PhotoImage(img.convert("RGB"))


def _scale_area(
    area: tuple[int, int, int, int],
    iw: int = _MAP_CANVAS_W,
    ih: int = _MAP_CANVAS_H,
) -> tuple[int, int, int, int]:
    x1, y1, x2, y2 = area
    sx = iw / _MAP_BASE_W
    sy = ih / _MAP_BASE_H
    return (
        int(round(x1 * sx)),
        int(round(y1 * sy)),
        int(round(x2 * sx)),
        int(round(y2 * sy)),
    )


def _load_floor_image(floor: int, iw: int, ih: int) -> Optional[MapImage]:
    """Load the dedicated floor-plan image (map_f1/2/3.png) if it exists."""
    if not _PIL:
        return None
    path = os.path.join(_DIR, "assets", "scenes", f"map_f{floor}.png")
    if not os.path.exists(path):
        return None
    try:
        img = Image.open(path).convert("RGB")
        if img.size != (iw, ih):
            img = img.resize((iw, ih), _LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


def build_library_map_image(key: str, iw: int, ih: int) -> Optional[MapImage]:
    if key == "map_f1":
        return _load_floor_image(1, iw, ih) or _pixel_library_map(1, iw, ih)
    if key == "map_f2":
        return _load_floor_image(2, iw, ih) or _pixel_library_map(2, iw, ih)
    if key == "map_f3":
        return _load_floor_image(3, iw, ih) or _pixel_library_map(3, iw, ih)
    return None


def show_library_map_scene(game: MapSceneGame, floor: int) -> None:
    """Render the library map scene and bind interactive room hotspots."""
    game._refresh_status()
    game._map_floor = max(1, min(3, floor))
    game._show_image(f"map_f{game._map_floor}")
    map_texts = {
        1: ST.MAP_FLOOR_1,
        2: ST.MAP_FLOOR_2,
        3: ST.MAP_FLOOR_3,
    }
    game._set_story(map_texts[game._map_floor])

    has_key = "地下室鑰匙" in game.inventory

    # ── floor-switch button options ────────────────────────────────────────────
    opts: list[tuple[str, object]] = [
        ("查看一樓", game.scene_map_floor1),
        ("查看二樓", game.scene_map_floor2),
        ("查看三樓", game.scene_map_floor3),
    ]

    # ── floor-switch tabs (image hotspots at canvas bottom) ───────────────────
    actions: list[dict[str, object]] = [
        {"label": label, "area": _scale_area(area), "command": cmd}
        for area, label, cmd in [
            (_FLOOR_TABS[0][0], "一樓", game.scene_map_floor1),
            (_FLOOR_TABS[1][0], "二樓", game.scene_map_floor2),
            (_FLOOR_TABS[2][0], "三樓", game.scene_map_floor3),
        ]
    ]

    # ── per-floor room hotspots and button options ─────────────────────────────
    if game._map_floor == 1:
        room_actions = [
            ("閱覽室A",       _1F_ROOMS["room_a"],          game.scene_room_a),
            ("閱覽室B",       _1F_ROOMS["room_b"],          game.scene_room_b),
            ("收藏室（古籍庫）",  _1F_ROOMS["collection_room"], game.scene_collection_room),
            ("會議廳I",       _1F_ROOMS["meeting_room"],    game.scene_meeting_room),
            ("管理室走廊",    _1F_ROOMS["corridor_1f"],     game.scene_corridor_1f),
            ("守衛室",        _1F_ROOMS["guard_room"],      game.scene_guard_room),
        ]
        if has_key:
            room_actions.append(
                ("地下密室", (161, 294, 276, 353), game.scene_basement)
            )
    elif game._map_floor == 2:
        room_actions = [
            ("研究室A（研究桌）",  _2F_ROOMS["desk"],         game.scene_desk),
            ("研究室B（窗邊）",   _2F_ROOMS["window"],       game.scene_window),
            ("檔案室（禁書區）",  _2F_ROOMS["archive_room"], game.scene_archive_room),
            ("會議廳II",         _2F_ROOMS["meeting_room"], game.scene_meeting_room),
            ("修復工坊",          _2F_ROOMS["workshop"],     game.scene_workshop),
            ("二樓迴廊",         _2F_ROOMS["corridor_2f"],  game.scene_corridor_2f),
        ]
    else:  # 3F
        room_actions = [
            ("館長室外調查",         _3F_ROOMS["hall"],           game.scene_hall),
            ("進入館長室（面對紅花）", _3F_ROOMS["confront"],       game.scene_confront),
            ("私人研究室",           _3F_ROOMS["corridor_3f"],    game.scene_corridor_3f),
            ("廢棄閱覽室",           _3F_ROOMS["abandoned_room"], game.scene_abandoned_room),
            ("封閉儲藏室（危險）",    _3F_ROOMS["closed_storage"], game.scene_basement_storage_room),
        ]

    for label, area_base, cmd in room_actions:
        opts.append((f"前往{label}" if not label.startswith("進入") and not label.startswith("打開") else label, cmd))
        actions.append({"label": label, "area": _scale_area(area_base), "command": cmd})

    # Special case: hall and confront share the same area on 3F — keep only
    # one hotspot rect visible (hall investigation takes priority).
    if game._map_floor == 3:
        # Remove the duplicate confront hotspot (same coords as hall).
        actions = [a for a in actions if a.get("label") != "進入館長室（面對紅花）"]
        # Add confront as a slightly offset area so both remain clickable.
        actions.append({
            "label": "進入館長室（面對紅花）",
            "area": _scale_area((23, 235, 212, 304)),
            "command": game.scene_confront,
        })

    game._set_options(opts)
    game._set_image_actions(actions)

