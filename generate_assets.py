#!/usr/bin/env python3
"""
generate_assets.py — 開發者工具
================================
使用 Mureka.ai API 預先生成遊戲配樂，並儲存至 assets/ 目錄。
此腳本由開發者在本機執行一次即可，生成的 MP3 可隨遊戲一同發布。

使用方式：
    python generate_assets.py

環境需求：
    pip install requests
"""
import os
import sys
import time
import requests

MUREKA_KEY = "op_27fqd8alidss5kntoh3651wtos85jf0g2"
MUREKA_URL = "https://api.mureka.ai"

_DIR   = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(_DIR, "assets")

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

POLL_INTERVAL = 3   # seconds between status checks
TIMEOUT       = 420 # seconds total wait per track


def generate(track: dict) -> bool:
    name  = track["name"]
    path  = track["path"]
    prompt = track["prompt"]

    if os.path.exists(path):
        print(f"[{name}] 已存在，跳過。")
        return True

    os.makedirs(ASSETS, exist_ok=True)
    headers = {
        "Authorization": f"Bearer {MUREKA_KEY}",
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
    while time.time() - start < TIMEOUT:
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

        if status in ("failed", "cancelled", "timeouted"):
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

    print(f"[{name}] 等待逾時（>{TIMEOUT}s）。", file=sys.stderr)
    return False


def main() -> None:
    print("=== 紅花吃檳榔 — 配樂素材生成工具 ===")
    print(f"輸出目錄：{ASSETS}\n")

    success = all(generate(t) for t in TRACKS)

    print()
    if success:
        print("所有配樂生成完成！可將 assets/ 目錄隨遊戲一同發布。")
    else:
        print("部分配樂生成失敗，請檢查 API Key 與網路連線。", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
