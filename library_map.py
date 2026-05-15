"""Library map rendering and interaction flow."""
from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, Optional, TypeAlias

import story_texts as ST

if TYPE_CHECKING:
    from PIL.ImageTk import PhotoImage as MapImage
else:
    MapImage: TypeAlias = object

try:
    from PIL import Image, ImageDraw, ImageTk
    _PIL = True
except ImportError:
    _PIL = False


MAP_SCENE_TITLES: dict[str, str] = {
    "map_f1": "圖書館地圖・一樓",
    "map_f2": "圖書館地圖・二樓",
    "map_f3": "圖書館地圖・三樓",
}


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


def build_library_map_image(key: str, iw: int, ih: int) -> Optional[MapImage]:
    if key == "map_f1":
        return _pixel_library_map(1, iw, ih)
    if key == "map_f2":
        return _pixel_library_map(2, iw, ih)
    if key == "map_f3":
        return _pixel_library_map(3, iw, ih)
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
        {"label": "一樓", "area": (20, 420, 130, 478), "command": game.scene_map_floor1},
        {"label": "二樓", "area": (170, 420, 280, 478), "command": game.scene_map_floor2},
        {"label": "三樓", "area": (320, 420, 430, 478), "command": game.scene_map_floor3},
    ]

    # Top corridor strip — shared click target for corridor scenes
    _CORRIDOR_AREA = (130, 93, 295, 122)

    if game._map_floor == 1:
        actions.extend([
            {
                "label": "書架深處",
                "area": (36, 288, 126, 358),
                "command": game.scene_bookshelves,
            },
            {
                "label": "一樓走廊",
                "area": _CORRIDOR_AREA,
                "command": game.scene_corridor_1f,
            },
            {
                "label": "房間A",
                "area": (36, 36, 126, 106),
                "command": game.scene_room_a,
            },
            {
                "label": "房間B",
                "area": (334, 36, 424, 106),
                "command": game.scene_room_b,
            },
            {
                "label": "會議室",
                "area": (334, 288, 424, 454),
                "command": game.scene_meeting_room,
            },
        ])
        if has_key:
            actions.append({
                "label": "地下密室",
                "area": (36, 384, 126, 454),
                "command": game.scene_basement,
            })
    elif game._map_floor == 2:
        actions.extend([
            {
                "label": "研究桌",
                "area": (36, 36, 126, 106),
                "command": game.scene_desk,
            },
            {
                "label": "窗邊",
                "area": (334, 36, 424, 106),
                "command": game.scene_window,
            },
            {
                "label": "二樓走廊",
                "area": _CORRIDOR_AREA,
                "command": game.scene_corridor_2f,
            },
            {
                "label": "二樓會議室",
                "area": (334, 288, 424, 454),
                "command": game.scene_meeting_room,
            },
        ])
    else:  # 3F
        actions.extend([
            {
                "label": "管理室外",
                "area": (168, 24, 292, 84),
                "command": game.scene_hall,
            },
            {
                "label": "進管理室（紅花）",
                "area": (168, 84, 292, 150),
                "command": game.scene_confront,
            },
            {
                "label": "三樓走廊",
                "area": _CORRIDOR_AREA,
                "command": game.scene_corridor_3f,
            },
        ])

    game._set_image_actions(actions)
