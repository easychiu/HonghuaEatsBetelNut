"""Library map rendering and interaction flow."""
from __future__ import annotations

import os
from collections import deque
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

_MAP_BASE_W = 460
_MAP_BASE_H = 490
_MAP_CANVAS_W = 1462
_MAP_CANVAS_H = 1076
_DIR = os.path.dirname(os.path.abspath(__file__))
_TOP_MAP_PATH = os.path.join(_DIR, "assets", "scenes", "TopMap.png")
_TOP_MAP_SCAN_HEIGHT_RATIO = 0.62
# Grayscale cutoff used to separate dark background from brighter floor-plan strokes.
_TOP_MAP_BRIGHTNESS_THRESHOLD = 24
_TOP_MAP_FLOOR_ROW_GROUP_RATIO = 0.12
_TOP_MAP_MIN_COMPONENT_AREA_RATIO = 0.01
_TOP_MAP_MIN_COMPONENT_AREA_ABS = 2500
_TOP_MAP_MIN_COMPONENT_W_RATIO = 0.12
_TOP_MAP_MIN_COMPONENT_H_RATIO = 0.20
_TOP_MAP_MIN_COMPONENT_DIM_ABS = 90
_TOP_MAP_MAX_CANDIDATES = 8
_top_map_floor_regions_cache: dict[tuple[int, int], list[tuple[int, int, int, int]]] = {}


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
    def scene_bookshelves(self) -> None: ...
    def scene_desk(self) -> None: ...
    def scene_window(self) -> None: ...
    def scene_hall(self) -> None: ...
    def scene_basement(self) -> None: ...
    def scene_confront(self) -> None: ...
    # ── new explorable nodes ─────────────────────────────────────────────────
    def scene_corridor_1f(self) -> None: ...
    def scene_corridor_2f(self) -> None: ...
    def scene_corridor_3f(self) -> None: ...
    def scene_room_a(self) -> None: ...
    def scene_room_b(self) -> None: ...
    def scene_meeting_room(self) -> None: ...


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
    _top_left_label  = {1: "房間A", 2: "研究桌", 3: "房間A"}
    _top_right_label = {1: "房間B", 2: "窗邊",   3: "房間B"}
    rooms = [
        (36, 36, 126, 106, _top_left_label.get(floor, "房間A")),
        (334, 36, 424, 106, _top_right_label.get(floor, "房間B")),
        (36, 384, 126, 454, "房間C"),
        (334, 384, 424, 454, "會議1"),
        (334, 288, 424, 358, "會議2"),
    ]
    for x1, y1, x2, y2, label in rooms:
        draw.rectangle([x1, y1, x2, y2], fill=room_color, outline=room_outline, width=2)
        draw.text((x1 + 8, y1 + 24), label, fill=(230, 240, 255, 255))

    if floor == 1:
        draw.rectangle([36, 288, 126, 358], fill=(132, 40, 45, 255), outline=(255, 140, 130, 255), width=3)
        draw.text((42, 314), "儲物間", fill=(255, 220, 220, 255))
    if floor == 3:
        draw.rectangle([168, 24, 292, 84], fill=(42, 108, 88, 255), outline=(146, 255, 212, 255), width=3)
        draw.text((178, 48), "管理室(紅花)", fill=(220, 255, 240, 255))

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


def _fallback_floor_regions(w: int, h: int) -> list[tuple[int, int, int, int]]:
    top = int(h * 0.14)
    bottom = int(h * 0.55)
    left = int(w * 0.06)
    right = int(w * 0.94)
    span = max(3, right - left)
    panel = span // 3
    regions: list[tuple[int, int, int, int]] = []
    for idx in range(3):
        x1 = left + idx * panel
        x2 = left + (idx + 1) * panel - 1 if idx < 2 else right
        regions.append((x1, top, x2, bottom))
    return regions


def _detect_top_map_floor_regions(img: Image.Image) -> list[tuple[int, int, int, int]]:
    size_key = img.size
    cached = _top_map_floor_regions_cache.get(size_key)
    if cached:
        return cached

    gray = img.convert("L")
    w, h = gray.size
    if w < (_TOP_MAP_MIN_COMPONENT_DIM_ABS * 2) or h < (_TOP_MAP_MIN_COMPONENT_DIM_ABS * 2):
        regions = _fallback_floor_regions(w, h)
        _top_map_floor_regions_cache[size_key] = regions
        return regions
    y_limit = max(1, int(h * _TOP_MAP_SCAN_HEIGHT_RATIO))
    pix = gray.load()
    mask = [bytearray(w) for _ in range(y_limit)]
    for y in range(y_limit):
        row = mask[y]
        for x in range(w):
            row[x] = 1 if pix[x, y] >= _TOP_MAP_BRIGHTNESS_THRESHOLD else 0

    visited = [bytearray(w) for _ in range(y_limit)]
    min_area = max(_TOP_MAP_MIN_COMPONENT_AREA_ABS, int(w * y_limit * _TOP_MAP_MIN_COMPONENT_AREA_RATIO))
    min_w = max(_TOP_MAP_MIN_COMPONENT_DIM_ABS, int(w * _TOP_MAP_MIN_COMPONENT_W_RATIO))
    min_h = max(_TOP_MAP_MIN_COMPONENT_DIM_ABS, int(h * _TOP_MAP_MIN_COMPONENT_H_RATIO))
    components: list[tuple[int, int, int, int, int]] = []

    for y in range(y_limit):
        for x in range(w):
            if not mask[y][x] or visited[y][x]:
                continue
            q = deque([(x, y)])
            visited[y][x] = 1
            area = 0
            x1 = x2 = x
            y1 = y2 = y
            while q:
                cx, cy = q.popleft()
                area += 1
                x1 = min(x1, cx)
                x2 = max(x2, cx)
                y1 = min(y1, cy)
                y2 = max(y2, cy)
                if cx > 0 and mask[cy][cx - 1] and not visited[cy][cx - 1]:
                    visited[cy][cx - 1] = 1
                    q.append((cx - 1, cy))
                if cx + 1 < w and mask[cy][cx + 1] and not visited[cy][cx + 1]:
                    visited[cy][cx + 1] = 1
                    q.append((cx + 1, cy))
                if cy > 0 and mask[cy - 1][cx] and not visited[cy - 1][cx]:
                    visited[cy - 1][cx] = 1
                    q.append((cx, cy - 1))
                if cy + 1 < y_limit and mask[cy + 1][cx] and not visited[cy + 1][cx]:
                    visited[cy + 1][cx] = 1
                    q.append((cx, cy + 1))
            if area < min_area:
                continue
            if (x2 - x1 + 1) < min_w or (y2 - y1 + 1) < min_h:
                continue
            components.append((area, x1, y1, x2, y2))

    if not components:
        regions = _fallback_floor_regions(w, h)
        _top_map_floor_regions_cache[size_key] = regions
        return regions

    components.sort(key=lambda c: (-c[0], c[2], c[1]))
    candidates = components[:_TOP_MAP_MAX_CANDIDATES]
    top_y = min(c[2] for c in candidates)
    row_cutoff = top_y + int(h * _TOP_MAP_FLOOR_ROW_GROUP_RATIO)
    row = [c for c in candidates if c[2] <= row_cutoff]
    if len(row) < 3:
        row = candidates
    row.sort(key=lambda c: c[1])
    regions = [(x1, y1, x2, y2) for _area, x1, y1, x2, y2 in row[:3]]

    if len(regions) < 3:
        regions = _fallback_floor_regions(w, h)

    _top_map_floor_regions_cache[size_key] = regions
    return regions


def _top_map_floor_image(floor: int, iw: int, ih: int) -> Optional[MapImage]:
    if not _PIL or not os.path.exists(_TOP_MAP_PATH):
        return None
    try:
        img = Image.open(_TOP_MAP_PATH).convert("RGB")
    except Exception:
        return None
    regions = _detect_top_map_floor_regions(img)
    idx = min(len(regions) - 1, max(0, floor - 1))
    x1, y1, x2, y2 = regions[idx]
    crop = img.crop((x1, y1, x2 + 1, y2 + 1))
    if crop.size != (iw, ih):
        crop = crop.resize((iw, ih), _LANCZOS)
    return ImageTk.PhotoImage(crop)


def build_library_map_image(key: str, iw: int, ih: int) -> Optional[MapImage]:
    if key == "map_f1":
        return _top_map_floor_image(1, iw, ih) or _pixel_library_map(1, iw, ih)
    if key == "map_f2":
        return _top_map_floor_image(2, iw, ih) or _pixel_library_map(2, iw, ih)
    if key == "map_f3":
        return _top_map_floor_image(3, iw, ih) or _pixel_library_map(3, iw, ih)
    return None


def show_library_map_scene(game: MapSceneGame, floor: int) -> None:
    """Render the library map scene and bind interactive actions."""
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

    opts = [
        ("查看一樓", game.scene_map_floor1),
        ("查看二樓", game.scene_map_floor2),
        ("查看三樓", game.scene_map_floor3),
    ]
    if game._map_floor == 1:
        opts.extend([
            ("前往書架深處（一樓）", game.scene_bookshelves),
            ("探索一樓走廊", game.scene_corridor_1f),
            ("前往房間A", game.scene_room_a),
            ("前往房間B", game.scene_room_b),
            ("前往會議室", game.scene_meeting_room),
        ])
        if has_key:
            opts.append(("打開地下密室", game.scene_basement))
    elif game._map_floor == 2:
        opts.extend([
            ("前往二樓研究桌區", game.scene_desk),
            ("前往二樓窗邊區", game.scene_window),
            ("探索二樓走廊", game.scene_corridor_2f),
            ("前往二樓會議室", game.scene_meeting_room),
        ])
    else:
        opts.extend([
            ("前往三樓管理室外調查", game.scene_hall),
            ("直接進管理室找紅花", game.scene_confront),
            ("探索三樓走廊", game.scene_corridor_3f),
        ])
    game._set_options(opts)

    # ── floor-switch tabs at the bottom edge of the canvas ────────────────────
    actions: list[dict[str, object]] = [
        {"label": "一樓", "area": _scale_area((20, 420, 130, 478)), "command": game.scene_map_floor1},
        {"label": "二樓", "area": _scale_area((170, 420, 280, 478)), "command": game.scene_map_floor2},
        {"label": "三樓", "area": _scale_area((320, 420, 430, 478)), "command": game.scene_map_floor3},
    ]

    # Top corridor strip — shared click target for corridor scenes
    _CORRIDOR_AREA = _scale_area((130, 93, 295, 122))

    if game._map_floor == 1:
        actions.extend([
            {
                "label": "書架深處",
                "area": _scale_area((36, 288, 126, 358)),
                "command": game.scene_bookshelves,
            },
            {
                "label": "一樓走廊",
                "area": _CORRIDOR_AREA,
                "command": game.scene_corridor_1f,
            },
            {
                "label": "房間A",
                "area": _scale_area((36, 36, 126, 106)),
                "command": game.scene_room_a,
            },
            {
                "label": "房間B",
                "area": _scale_area((334, 36, 424, 106)),
                "command": game.scene_room_b,
            },
            {
                "label": "會議室",
                "area": _scale_area((334, 288, 424, 454)),
                "command": game.scene_meeting_room,
            },
        ])
        if has_key:
            actions.append({
                "label": "地下密室",
                "area": _scale_area((36, 384, 126, 454)),
                "command": game.scene_basement,
            })
    elif game._map_floor == 2:
        actions.extend([
            {
                "label": "研究桌",
                "area": _scale_area((36, 36, 126, 106)),
                "command": game.scene_desk,
            },
            {
                "label": "窗邊",
                "area": _scale_area((334, 36, 424, 106)),
                "command": game.scene_window,
            },
            {
                "label": "二樓走廊",
                "area": _CORRIDOR_AREA,
                "command": game.scene_corridor_2f,
            },
            {
                "label": "二樓會議室",
                "area": _scale_area((334, 288, 424, 454)),
                "command": game.scene_meeting_room,
            },
        ])
    else:  # 3F
        actions.extend([
            {
                "label": "管理室外",
                "area": _scale_area((168, 24, 292, 84)),
                "command": game.scene_hall,
            },
            {
                "label": "進管理室（紅花）",
                "area": _scale_area((168, 84, 292, 150)),
                "command": game.scene_confront,
            },
            {
                "label": "三樓走廊",
                "area": _CORRIDOR_AREA,
                "command": game.scene_corridor_3f,
            },
        ])

    game._set_image_actions(actions)
