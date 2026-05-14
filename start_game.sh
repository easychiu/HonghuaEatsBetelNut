#!/usr/bin/env bash
# 紅花吃檳榔：圖書館夜談 — 啟動腳本（macOS / Linux）

echo "======================================"
echo " 紅花吃檳榔：圖書館夜談 — 深夜完全版"
echo "======================================"
echo

# 尋找合適的 Python 直譯器（優先 python3，其次 python）
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        ver=$("$cmd" -c "import sys; print(sys.version_info[:2] >= (3,10))" 2>/dev/null)
        if [ "$ver" = "True" ]; then
            PYTHON="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "[錯誤] 找不到 Python 3.10 或以上版本。"
    echo "請先安裝 Python：https://www.python.org/downloads/"
    exit 1
fi

echo "使用直譯器：$($PYTHON --version)"
echo

# 安裝相依套件
echo "正在安裝遊戲所需套件（Pillow、pygame）…"
"$PYTHON" -m pip install --quiet -r requirements.txt || \
    echo "[警告] 套件安裝失敗，遊戲將以純文字模式執行（無圖像、無音樂）。"

echo
echo "正在啟動遊戲…"
echo
"$PYTHON" game.py
