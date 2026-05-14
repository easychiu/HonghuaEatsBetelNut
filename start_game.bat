@echo off
chcp 65001 >nul
title 紅花吃檳榔：圖書館夜談

echo ======================================
echo  紅花吃檳榔：圖書館夜談 — 深夜完全版
echo ======================================
echo.

:: 確認 Python 存在
where python >nul 2>&1
if errorlevel 1 (
    echo [錯誤] 找不到 Python。
    echo 請先安裝 Python 3.10 或以上版本：
    echo   https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 確認版本 >= 3.10
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo 偵測到 Python %PYVER%

:: 安裝相依套件
echo.
echo 正在安裝遊戲所需套件（Pillow、pygame）…
python -m pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo [警告] 套件安裝失敗，遊戲將以純文字模式執行（無圖像、無音樂）。
)

echo.
echo 正在啟動遊戲…
echo.
python game.py

if errorlevel 1 (
    echo.
    echo [錯誤] 遊戲異常退出。請確認 Python 3.10+ 已正確安裝。
    pause
)
