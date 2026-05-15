# HonghuaEatsBetelNut — 蔚藍學院秘案 深夜調查版

以 `info.jpg` 哥德式暗黑美學為基礎的視覺小說遊戲 Demo，深化版新增：

- 17世紀英格蘭背景與完整謀殺懸案劇情
- 哥德式場景插圖（已隨專案附帶於 `assets/scenes/`）
- 哥德式管弦樂 BGM（已隨專案附帶）
- 豐富的多分支劇情與人物線索系統
- 新增「紅花信任度」好感度系統
- 純圖片角色演出（內建微動態與嘴型同步效果）
- 兩種謎題類型與 8 種結局
- 新增圖書館三層「上帝視角」2D 像素風地圖與樓層切換

## 🚀 快速開始（下載即玩）

> **所有場景圖與配樂均已內附，無需自行生成任何素材。**

### 前置需求

- [Python 3.10 或以上版本](https://www.python.org/downloads/)（必要）
- Pillow + pygame（選用；缺少時以純文字模式執行，無圖像、無音樂）

### Windows 玩家

1. 下載此專案（ZIP 解壓縮 或 `git clone`）
2. 雙擊 `start_game.bat`

腳本會自動安裝套件並啟動遊戲。

### macOS / Linux 玩家

```bash
# 1. 進入專案目錄
cd HonghuaEatsBetelNut

# 2. 給啟動腳本執行權限（只需一次）
chmod +x start_game.sh

# 3. 啟動遊戲
./start_game.sh
```

### 手動啟動（任何平台）

```bash
pip install -r requirements.txt   # 安裝圖像與音樂套件
python game.py                     # 啟動遊戲
```

## 🌐 完整單一 HTML 分享（完整文本版）

專案根目錄提供 `index.html`，可直接分享單一檔案給他人，並以瀏覽器離線開啟：

- 產物：`index.html`（單一檔案、無外部請求）
- 使用方式：雙擊開啟，或拖曳到 Chrome / Edge / Safari / Firefox
- 存檔：使用瀏覽器 `localStorage`（含版本欄位，避免舊存檔不相容）

### 目前單檔 HTML 已包含

- 核心劇情流程與場景狀態機切換
- 對話選項與主要分支
- 信任度、物證/人物線索進度
- 遊戲時間推進與 2AM 後危險旗標
- 結局分支判定（壞結局 / 普通 / 信任 / 真 / 秘密）
- 內建「全內容文字庫」：`story_texts.py` / `character_texts.py` 常數文字已內嵌，可離線完整瀏覽

### 後續階段（仍待補齊）

- 更多場景熱區精修（目前已支援主流程地圖與館長室外物證區點擊）
- 完整伏擊機制
- 音效與完整 UI 動畫
- 與 Python 版所有場景細節逐項對齊

## 素材說明

- 專案已附帶可直接使用的場景圖、紅花信任度情緒圖與配樂：
  - `assets/scenes/*.png`
  - `assets/character_emotions/honghua_readbook_{impatient|peaceful|friendly|trusted}.png`
  - `assets/bgm_main.mp3`
  - `assets/bgm_end.mp3`
- 一般使用者只需要執行 `python game.py`，**不需要**自行生成任何圖像或音樂。

## 維護者選用：重新生成素材

只有在需要重做內附素材時，才需要使用下列指令。

先安裝：

```bash
pip install Pillow requests
```

重新生成場景圖（會同時重做紅花信任度情緒圖）：

```bash
python generate_assets.py --scenes-only --force-scenes
```

重新生成 BGM：

> 僅限維護者使用；一般使用者不需要此步驟。

```bash
export MUREKA_API_KEY='你的 Mureka API Key'
python generate_assets.py --bgm-only
```

`generate_assets.py` 會依 `info.jpg` 的整體哥德式暗色風格生成場景圖，並可透過 Mureka.ai API 重做配樂；但這些素材目前都已先行附帶在專案中。

## 遊戲簡介

17世紀英格蘭。蔚藍學院因兩年前一場懸而未決的謀殺案而關閉。  
你是英國皇家警察，也是這所學院的舊校友，今夜隻身來到廢棄的圖書館調查舊案。

銀髮少女紅花端坐其中，水手服筆挺，表情神秘：  
「你來這裡是為了什麼，我已經知道了。問題是……你能找到答案嗎？」

你必須在天亮前蒐集物證、破解謎題，揭開米糕店長死亡的真相。

### 主要登場人物

| 人物 | 說明 |
|------|------|
| 紅花 | 銀色短髮，水手服，水手服同好會會長，圖書館的守護者 |
| 英國皇家警察（你） | 舊校友，曾任法國海軍，如今兼任皇家警察，來此查案 |
| 消失的艾蜜莉亞 | 前學生聯誼會委員，目睹某事後神秘失蹤 |
| 退學生天王星（Starscream） | 因家道中落憤而退學，案件關鍵嫌疑人 |
| 幸運的艾莉卡 | 轉學生，極度幸運，案發現場目擊者 |
| 米糕店長 | 命案受害者 |

### 可探索場景

| 場景 | 說明 |
|------|------|
| 三樓管理室外展示區 | 遊戲起始區域，紅花位於三樓管理室 |
| 圖書館上帝視角地圖（1F/2F/3F） | 三層平面圖，會依 `TopMap.png` 下方圖說顯示各層實際房間名稱（如閱覽室、研究室、館長室、禁書檔案室等） |
| 一樓書架深處 | 案件時間線排序謎題，解開可得地下密室鑰匙；1F/2F 任何場景均有背刺風險 |
| 研究桌（二樓） | 紅花的案情筆記，揭露她所掌握的秘密；2F 有背刺風險 |
| 窗邊（二樓） | 艾蜜莉亞失蹤的線索；2F 有背刺風險 |
| 地下密室・倉庫 | 天王星的親筆供詞，解鎖「秘密結局」的關鍵；地下區有背刺風險 |
| 地下密室・儲藏室 | 兇手長期藏身之處（門鎖從內扣，無法進入）；接近時背刺機率大幅提升 |

### 場景圖素材

- 遊戲會優先讀取 `assets/scenes/*.png`
- 若場景圖不存在，會先回退到 `assets/scenes/default.png`
- 場景一（`prologue` / `hall`）支援日夜素材切換，資源可放在 `assets/scene1/`：
  - 進場看書圖：`honghua_readbook_{day|dusk|night}.{png|jpg|jpeg}`
  - 對話看向你（一般）：`honghua_look_{day|dusk|night}.{png|jpg|jpeg}`
  - 對話看向你（依信任度）：`honghua_look_{day|dusk|night}_{impatient|peaceful|friendly|trusted}.{png|jpg|jpeg}`
  - 紅花看向窗外（回訪時偶爾觸發，夜晚不觸發）：`honghua_window_{day|dusk}.{png|jpg|jpeg}`
  - 也可用環境變數 `SCENE1_TIME_OF_DAY=day|dusk|night` 強制指定時段
- `hall` 對話期間若缺少上述信任度圖，會回退到 `assets/character_emotions/honghua_readbook_{impatient|peaceful|friendly|trusted}.png`
- 若缺少上述素材，會回退至 `HonghuaReadBook.jpg`（紅花在圖書館看書）
- `intro` 開場畫面會優先使用 `assets/scenes/outside.png`
- 大地圖模式（`map_f1` / `map_f2` / `map_f3`）會優先使用 `assets/scenes/TopMap.png`，並依樓層顯示對應區域
- 若有 `HonghuaInENG.jpg`，`confront` / `basement` / `basement_deep` 會優先使用該圖（紅花人物形象）
- 專案已先行附帶開場、大廳、對峙、地下室、各調查節點與結局場景圖（包含 `assets/scenes/default.png`）
- 維護者重新生成場景圖時，會一併輸出 `assets/scenes/default.png` 作為紅花主視覺預設場景

### 物證與謎題

**三件關鍵物證**（各藏一位密碼數字）：
1. **陳舊生鏽的鎚子**：一把約 **30公分** 的生鏽鎚子，鎚柄刻有「III」→ 第一碼
2. **幸運四葉草**：葉片上寫著「壹」→ 第二碼
3. **YV牛仔褲**：內側縫有「第四排」→ 第三碼

**案件時間線謎題**：按正確順序排列四份案卷 → 取得地下密室鑰匙

### 操作方式

- 物證與場景內互動改為點擊左側場景圖上的互動區域
- 紅花角色圖支援滑鼠跟隨與打字口型（由遊戲狀態即時驅動）
- 離開目前畫面或切換到其他場景時，仍使用右下方按鈕

### 紅花信任度

- 信任度代表紅花對你「查案態度與判斷力」的評價
- 透過關鍵調查行為（讀筆記、整理供詞、追查失蹤線索）提升
- 同樣的事件只會計分一次，避免重複刷分
- 信任度高低會影響面對紅花時的分支與結局

### 結局

| 結局 | 達成條件 |
|------|---------|
| 秘密結局 | 鎮魂歌譜 + 全部 3 條人物線索 + 高信任度 |
| 真結局 | 鎮魂歌譜 + 基本信任度 |
| 信任結局：共犯不是罪犯 | 物證達標 + 高信任度（即使證據未全） |
| 信任結局：被拒於門外 | 持有鎮魂歌譜但信任度過低 |
| 信任結局：冷真相 | 全證據達成但信任度不足 |
| 普通結局 | 蒐集 2 件以上物證後直接面對 |
| 壞結局 A | 毫無準備就面對紅花 |
| 壞結局 B | 密碼盒輸錯三次 |

### 配樂

遊戲啟動後直接播放專案內附的配樂素材（`assets/bgm_main.mp3`）。  
結局場景會淡出切換至 `assets/bgm_end.mp3`。
