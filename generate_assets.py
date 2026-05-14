#!/usr/bin/env python3
"""
generate_assets.py — 開發者工具
================================
可預先生成遊戲配樂與場景圖素材，並儲存至 assets/ 目錄。
"""
import argparse
import os
import sys
import time

try:
    import requests
except ImportError:
    requests = None

try:
    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
except ImportError:
    Image = ImageDraw = ImageEnhance = ImageFilter = None

MUREKA_URL = "https://api.mureka.ai"

_DIR   = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(_DIR, "assets")
SCENES = os.path.join(ASSETS, "scenes")
INFO_JPG = os.path.join(_DIR, "info.jpg")
HONGHUA_READ_BOOK_JPG = os.path.join(_DIR, "HonghuaReadBook.jpg")
HONGHUA_IN_ENG_JPG = os.path.join(_DIR, "HonghuaInENG.jpg")
IMAGE_WIDTH, IMAGE_HEIGHT = 460, 490
DEFAULT_SCENE_PNG = os.path.join(SCENES, "default.png")

TRACKS = [
    {
        "name": "bgm_main",
        "path": os.path.join(ASSETS, "bgm_main.mp3"),
        "prompt": (
            "dark gothic horror atmosphere, mysterious ancient library at night, "
            "haunting orchestral strings, candlelight ambiance, slow tension, "
            "Chinese folklore horror, piano and cello, ominous, 80 bpm"
        ),
    },
    {
        "name": "bgm_end",
        "path": os.path.join(ASSETS, "bgm_end.mp3"),
        "prompt": (
            "bittersweet emotional release, gothic piano solo, melancholic hope, "
            "gentle resolution, Chinese folklore inspired, 70 bpm"
        ),
    },
]

POLL_INTERVAL = 3         # seconds between status checks
TIMEOUT_PER_TRACK = 420   # max seconds to wait per track

INFO_SCENES = {
    "intro":       (0.58, (30, 0, 0, 80),    None),
    "prologue":    (0.62, (0, 10, 20, 60),   None),
    "hall":        (0.52, (0, 15, 35, 70),   None),
    "book":        (0.68, (50, 30, 0, 90),   (0, 600, 800, 880)),
    "feather":     (0.65, (20, 35, 10, 85),  (0, 430, 500, 880)),
    "box":         (0.62, (0, 40, 10, 95),   (550, 580, 1196, 880)),
    "desk_info":   (0.65, (30, 20, 0, 80),   (0, 450, 950, 880)),
    "window_info": (0.55, (0, 10, 30, 90),   (0, 0, 500, 500)),
    "confront":    (0.72, (100, 0, 0, 110),  None),
    "true_end":    (0.82, (50, 25, 0, 55),   None),
    "secret_end":  (0.80, (20, 10, 35, 65),  None),
    "normal_end":  (0.45, (0, 5, 25, 90),    None),
}

PROC_SCENES = {
    "bookshelves": (
        (6, 4, 3),
        [(70, IMAGE_HEIGHT // 2, 130, (180, 95, 25, 75)),
         (IMAGE_WIDTH - 60, IMAGE_HEIGHT // 2 + 40, 95, (120, 60, 15, 55))],
    ),
    "puzzle_book": (
        (5, 5, 8),
        [(IMAGE_WIDTH // 2, IMAGE_HEIGHT // 2, 220, (160, 110, 40, 85)),
         (IMAGE_WIDTH // 2, IMAGE_HEIGHT // 2, 75, (220, 170, 80, 90))],
    ),
    "desk": (
        (5, 7, 4),
        [(IMAGE_WIDTH // 2, IMAGE_HEIGHT - 80, 220, (210, 125, 40, 100)),
         (IMAGE_WIDTH // 2, IMAGE_HEIGHT - 80, 75, (255, 185, 85, 110))],
    ),
    "diary": (
        (11, 7, 4),
        [(IMAGE_WIDTH // 2, IMAGE_HEIGHT // 2, 185, (200, 155, 75, 90)),
         (IMAGE_WIDTH // 2 - 70, IMAGE_HEIGHT // 2 + 30, 65, (255, 200, 115, 75))],
    ),
    "window": (
        (4, 7, 12),
        [(IMAGE_WIDTH // 2, 75, 170, (30, 55, 85, 95)),
         (IMAGE_WIDTH // 2, 75, 55, (60, 95, 145, 75))],
    ),
    "basement": (
        (3, 3, 7),
        [(IMAGE_WIDTH // 2, IMAGE_HEIGHT, 210, (18, 25, 58, 80)),
         (IMAGE_WIDTH // 2, IMAGE_HEIGHT // 2, 38, (38, 48, 88, 55))],
    ),
    "basement_deep": (
        (2, 2, 5),
        [(IMAGE_WIDTH // 2, IMAGE_HEIGHT // 2, 160, (65, 0, 20, 105)),
         (IMAGE_WIDTH // 2, IMAGE_HEIGHT // 2, 48, (105, 0, 28, 80))],
    ),
    "bad_a": (
        (5, 0, 0),
        [(IMAGE_WIDTH // 2, IMAGE_HEIGHT // 2, 190, (155, 0, 0, 120)),
         (IMAGE_WIDTH // 2, IMAGE_HEIGHT // 2, 58, (200, 20, 20, 95))],
    ),
    "bad_b": (
        (7, 1, 1),
        [(IMAGE_WIDTH // 2, IMAGE_HEIGHT // 2, 225, (185, 0, 18, 130)),
         (IMAGE_WIDTH // 4, IMAGE_HEIGHT // 3, 105, (225, 45, 0, 100)),
         (3 * IMAGE_WIDTH // 4, 2 * IMAGE_HEIGHT // 3, 82, (205, 28, 8, 88))],
    ),
}

SCENE_SOURCE_OVERRIDES = {
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

SCENE_TITLES = {
    "default": "紅花預設場景",
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
    "true_end": "真結局",
    "secret_end": "秘密結局",
    "normal_end": "普通結局",
    "bad_a": "壞結局",
    "bad_b": "密碼失敗",
}


def _tinted(
    base_img,
    darken: float = 0.75,
    tint: tuple = (0, 0, 0, 0),
    crop: tuple | None = None,
):
    img = base_img.copy()
    if crop:
        img = img.crop(crop)
    img = img.resize((IMAGE_WIDTH, IMAGE_HEIGHT), Image.LANCZOS)
    img = ImageEnhance.Brightness(img.convert("RGB")).enhance(darken).convert("RGBA")
    if any(tint):
        overlay = Image.new("RGBA", img.size, tint)
        img = Image.alpha_composite(img, overlay)
    return img.convert("RGB")


def _atmospheric(base_rgb: tuple, lights: list, blur: float = 2.5):
    img = Image.new("RGBA", (IMAGE_WIDTH, IMAGE_HEIGHT), base_rgb + (255,))
    draw = ImageDraw.Draw(img, "RGBA")
    for cx, cy, r, col in lights:
        rc, gc, bc, ma = col
        for rad in range(r, 0, -3):
            alpha = int(ma * (1 - rad / r) ** 0.65)
            draw.ellipse([cx - rad, cy - rad, cx + rad, cy + rad],
                         fill=(rc, gc, bc, alpha))
    if blur > 0:
        img = img.filter(ImageFilter.GaussianBlur(blur))
    vignette = Image.new("RGBA", (IMAGE_WIDTH, IMAGE_HEIGHT), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette, "RGBA")
    maxr = int((IMAGE_WIDTH ** 2 + IMAGE_HEIGHT ** 2) ** 0.5) // 2 + 40
    for rad in range(maxr, 0, -5):
        alpha = int(130 * (rad / maxr) ** 1.5)
        vd.ellipse(
            [
                IMAGE_WIDTH // 2 - rad,
                IMAGE_HEIGHT // 2 - rad,
                IMAGE_WIDTH // 2 + rad,
                IMAGE_HEIGHT // 2 + rad,
            ],
            fill=(0, 0, 0, alpha),
        )
    return Image.alpha_composite(img, vignette).convert("RGB")


def _default_scene_image(key: str):
    source = (
        SCENE_SOURCE_OVERRIDES.get(key)
        or (HONGHUA_READ_BOOK_JPG if os.path.exists(HONGHUA_READ_BOOK_JPG) else "")
        or (HONGHUA_IN_ENG_JPG if os.path.exists(HONGHUA_IN_ENG_JPG) else "")
        or (INFO_JPG if os.path.exists(INFO_JPG) else "")
    )
    if source:
        img = Image.open(source).convert("RGBA").resize(
            (IMAGE_WIDTH, IMAGE_HEIGHT), Image.LANCZOS
        )
        img = ImageEnhance.Brightness(img.convert("RGB")).enhance(0.68).convert("RGBA")
    else:
        img = Image.new("RGBA", (IMAGE_WIDTH, IMAGE_HEIGHT), (12, 10, 18, 255))

    img = Image.alpha_composite(
        img,
        Image.new("RGBA", img.size, (16, 8, 14, 92)),
    )
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle([0, IMAGE_HEIGHT - 120, IMAGE_WIDTH, IMAGE_HEIGHT], fill=(7, 5, 9, 214))
    draw.rectangle([18, 18, 138, 48], fill=(85, 20, 28, 180))
    draw.text((28, 25), "預設場景", fill=(255, 236, 220))
    draw.text((26, IMAGE_HEIGHT - 95), SCENE_TITLES.get(key, SCENE_TITLES["default"]), fill=(230, 214, 192))
    draw.text((26, IMAGE_HEIGHT - 63), "若缺少專屬圖像，先以紅花主視覺代替。", fill=(193, 163, 128))
    return img.convert("RGB")


def build_scene_image(key: str):
    if Image is None:
        return None
    if key == "default":
        return _default_scene_image(key)
    source = SCENE_SOURCE_OVERRIDES.get(key)
    if source and os.path.exists(source):
        return Image.open(source).convert("RGB").resize(
            (IMAGE_WIDTH, IMAGE_HEIGHT), Image.LANCZOS
        )
    if key in INFO_SCENES:
        if not os.path.exists(INFO_JPG):
            return None
        base_img = Image.open(INFO_JPG).convert("RGBA")
        darken, tint, crop = INFO_SCENES[key]
        return _tinted(base_img, darken, tint, crop)
    if key in PROC_SCENES:
        base_rgb, lights = PROC_SCENES[key]
        return _atmospheric(base_rgb, lights)
    return _default_scene_image(key)


def generate_scene_images(force: bool = False) -> bool:
    if Image is None:
        print("缺少 Pillow，無法生成場景圖。請先安裝：pip install Pillow", file=sys.stderr)
        return False

    os.makedirs(SCENES, exist_ok=True)
    success = True
    for key in ["default", *INFO_SCENES.keys(), *PROC_SCENES.keys()]:
        path = os.path.join(SCENES, f"{key}.png")
        if os.path.exists(path) and not force:
            print(f"[scene:{key}] 已存在，跳過。")
            continue
        img = build_scene_image(key)
        if img is None:
            print(f"[scene:{key}] 生成失敗。", file=sys.stderr)
            success = False
            continue
        img.save(path, "PNG")
        print(f"[scene:{key}] 已輸出：{path}")
    return success


def generate(track: dict) -> bool:
    name  = track["name"]
    path  = track["path"]
    prompt = track["prompt"]

    if os.path.exists(path):
        print(f"[{name}] 已存在，跳過。")
        return True

    os.makedirs(ASSETS, exist_ok=True)
    if requests is None:
        print(f"[{name}] 缺少 requests，無法呼叫 Mureka API。", file=sys.stderr)
        return False
    mureka_key = os.getenv("MUREKA_API_KEY", "").strip()
    if not mureka_key:
        print(
            f"[{name}] 缺少 MUREKA_API_KEY 環境變數，無法呼叫 API。",
            file=sys.stderr,
        )
        return False
    headers = {
        "Authorization": f"Bearer {mureka_key}",
        "Content-Type": "application/json",
    }

    print(f"[{name}] 提交生成請求…")
    try:
        resp = requests.post(
            f"{MUREKA_URL}/v1/instrumental/generate",
            json={"model": "auto", "prompt": prompt},
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()
    except Exception as e:
        print(f"[{name}] 提交失敗：{e}", file=sys.stderr)
        return False

    task_id = resp.json().get("id", "")
    if not task_id:
        print(f"[{name}] 未取得 task_id，回應：{resp.json()}", file=sys.stderr)
        return False

    print(f"[{name}] 任務 ID：{task_id}，等待生成完成…")
    start = time.time()
    while time.time() - start < TIMEOUT_PER_TRACK:
        time.sleep(POLL_INTERVAL)
        try:
            q = requests.get(
                f"{MUREKA_URL}/v1/instrumental/query/{task_id}",
                headers=headers,
                timeout=20,
            )
            q.raise_for_status()
        except Exception as e:
            print(f"[{name}] 查詢失敗：{e}", file=sys.stderr)
            continue

        data   = q.json()
        status = data.get("status", "failed")
        elapsed = int(time.time() - start)
        print(f"[{name}] {elapsed}s — 狀態：{status}")

        if status in ("failed", "cancelled", "timeouted", "timed_out"):
            print(f"[{name}] 生成失敗：{status}", file=sys.stderr)
            return False

        if status == "succeeded":
            choices = data.get("choices", [])
            if not choices:
                print(f"[{name}] 無可用音檔。", file=sys.stderr)
                return False
            url = choices[0].get("url", "")
            if not url:
                print(f"[{name}] 音檔 URL 為空。", file=sys.stderr)
                return False
            print(f"[{name}] 下載中…")
            try:
                dl = requests.get(url, timeout=60)
                with open(path, "wb") as f:
                    f.write(dl.content)
                size_kb = os.path.getsize(path) // 1024
                print(f"[{name}] 儲存完成：{path} ({size_kb} KB)")
                return True
            except Exception as e:
                print(f"[{name}] 下載失敗：{e}", file=sys.stderr)
                return False

    print(f"[{name}] 等待逾時（>{TIMEOUT_PER_TRACK}s）。", file=sys.stderr)
    return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成遊戲配樂與場景圖素材")
    parser.add_argument("--scenes-only", action="store_true", help="只生成場景圖")
    parser.add_argument("--bgm-only", action="store_true", help="只生成 BGM")
    parser.add_argument("--force-scenes", action="store_true", help="覆寫既有場景圖")
    args = parser.parse_args()
    if args.scenes_only and args.bgm_only:
        parser.error("--scenes-only 與 --bgm-only 不能同時使用")
    return args


def main() -> None:
    args = parse_args()
    print("=== 紅花吃檳榔 — 素材生成工具 ===")
    print(f"輸出目錄：{ASSETS}\n")

    scene_success = True
    bgm_success = True

    if not args.bgm_only:
        scene_success = generate_scene_images(force=args.force_scenes)

    if not args.scenes_only:
        bgm_success = all(generate(t) for t in TRACKS)

    print()
    if scene_success and bgm_success:
        print("素材生成完成！可將 assets/ 目錄隨遊戲一同發布。")
        return

    if not scene_success:
        print("場景圖生成失敗，請確認 Pillow 與來源圖片是否存在。", file=sys.stderr)
    if not bgm_success:
        print("部分配樂生成失敗，請檢查 requests、API Key 與網路連線。", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
