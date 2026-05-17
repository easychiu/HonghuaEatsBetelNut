    const SAVE_KEY = "honghua-single-html-mvp-save";
    const SAVE_VERSION = 1;
    const GAME_START_HOUR = 15;
    const KILLER_EMERGE_ELAPSED = 660; // 由 15:00 起算 660 分鐘（跨日到翌日 02:00）
    const STALKER_ENCOUNTER_ELAPSED = 480; // 由 15:00 起算 480 分鐘（23:00）
    const STALKER_ENCOUNTER_CHANCE = 0.3;
    const MAX_LOG_ENTRIES = 60;
    const MAX_CANDLE = 100;
    const DEFAULT_PLAYER_X = 50;
    const DEFAULT_PLAYER_Y = 86;
    const DEFAULT_HONGHUA_X = DEFAULT_PLAYER_X;
    const DEFAULT_HONGHUA_Y = DEFAULT_PLAYER_Y;
    const MARKER_MOVE_DURATION_MS = 600;
    const CANDLE_DRAIN_PER_MINUTE = 0.5;
    const BATTLE_EFFECT_DURATION_MS = 350;
    const MATCHES_CANDLE_BONUS = 30;
    const DEFAULT_LOG_MESSAGE = "── 進入蔚藍學院 ──";
    const ARCHIVE_PREVIEW_LIMIT = 12;
    const VALID_FLOORS = [1, 2, 3];
    const LEVEL_UP_HP_GAIN = 10;
    const LEVEL_UP_ATK_GAIN = 2;
    const EXP_NEXT_MULTIPLIER = 1.4;
    const PASSWORD_CODE = "314";
    const PASSWORD_DIGITS = { hammer: "3", clover: "1", jeans: "4" };
    const BOOKSHELF_CORRECT_ORDER = ["失蹤案卷", "退學檔案", "死亡報告", "停課公告"];
    const BOOKSHELF_REQUIRED_COUNT = BOOKSHELF_CORRECT_ORDER.length;
    const DEFAULT_BATTLE_ENEMY_CONFIG = { name: "敵人", hpPool: "monster" };
    const BATTLE_ENEMY_CONFIG = {
      battle_starscream: { name: "天王星", hpPool: "boss" },
      battle_random: { name: "黑影", hpPool: "monster" },
    };
    const DEDUCTION_QUESTIONS = [
      { question: "兇器鎚子真正的主人是誰？", answer: "天王星" },
      { question: "案發當晚的目擊者是誰？", answer: "艾莉卡" },
      { question: "這起案件為何被封鎖？", answer: "校方掩蓋" },
    ];
    const DEFAULT_EVIDENCE = { hammer: false, clover: false, jeans: false };
    const DEFAULT_CLUES = { honghua: false, amelia: false, starscream: false };
    const DEFAULT_FLAGS = {
      basementOpen: false,
      trueSong: false,
      deductionComplete: false,
      guardLogbookFound: false,
      workshopCardFound: false,
      foundMatches: false,
      cloverUsed: false,
      ameliaTalkedClover: false,
      ameliaTalkedErica: false,
      ameliaTalkedShanshan: false,
      ameliaTalkedJackson: false,
      ameliaTalkedSeth: false,
      ameliaEricaFollowup: false,
      ameliaInsulinUnlocked: false,
      honghuaJoined: false // <--- 新增的紅花入隊標記
    };
    const DEFAULT_ARCHIVE = { group: "story_texts.py", key: null };

    const SCENE1_ASSETS = "assets/scene1/";
    const SCENE1_SCENES = new Set(["prologue", "hall"]);
    const MAP_SCENES = new Set(["map1", "map2", "map3"]);
    const BGM_MAIN = "assets/bgm_main.mp3";
    const BGM_END = "assets/bgm_end.mp3";
    const BGM_BATTLE = "assets/bgm_battle.mp3";
    const BGM_BOSS = "assets/bgm_boss.mp3";
    const BATTLE_BACKGROUND_BRIGHTNESS = 0.4;

    const SCENE_IMAGES = {
      intro:          "assets/scenes/outside.png",
      map3:           "assets/scenes/map_f3.png",
      map2:           "assets/scenes/map_f2.png",
      map1:           "assets/scenes/map_f1.png",
      hall:           "assets/scenes/hall.png",
      desk:           "assets/scenes/desk.png",
      window:         "assets/scenes/window.png",
      bookshelves:    "assets/scenes/bookshelves.png",
      basement:       "assets/scenes/basement.png",
      basementDeep:   "assets/scenes/basement_deep.png",
      collectionRoom: "assets/scenes/collection_room.png",
      toolbox:        "assets/scenes/collection_room.png",
      archiveRoom:    "assets/scenes/archive_room.png",
      guardRoom:      "assets/scenes/guard_room.png",
      workshop:       "assets/scenes/workshop.png",
      abandonedRoom:  "assets/scenes/abandoned_room.png",
      alliance_followup: "assets/scenes/confront.png",
      ending_secret:  "assets/scenes/secret_end.png",
      ending_true:    "assets/scenes/true_end.png",
      ending_trust:   "assets/scenes/normal_end.png",
      ending_normal:  "assets/scenes/normal_end.png",
      ending_bad:     "assets/scenes/bad_a.png",
      ending_alliance_capture: "assets/scenes/secret_end.png",
      ending_alliance_solo_bad: "assets/scenes/bad_a.png",
      ending_bad_codefail: "assets/scenes/bad_a.png",
      ending_bad_darkness: "assets/scenes/bad_a.png",
      ending_killer_map: "assets/scenes/bad_a.png",
      killer_encounter: "assets/scenes/hall.png",
      battle_starscream: "assets/scenes/basement_deep.png",
      battle_random: "assets/scenes/basement.png",
      battle_farm:   "assets/scenes/basement.png",
      victory: "assets/scenes/secret_end.png",
      deduction: "assets/scenes/desk.png",
      python_hidden_start: "assets/scenes/true_end.png",
      python_hidden_london: "assets/scenes/true_end.png",
      amelia_hub:           "assets/scenes/map_f1.png",
      amelia_reading_room:  "assets/scenes/collection_room.png",
      amelia_archive_room:  "assets/scenes/archive_room.png",
      amelia_workshop:      "assets/scenes/workshop.png",
      amelia_meeting_room:  "assets/scenes/guard_room.png",
      amelia_guild_office:  "assets/scenes/desk.png",
      amelia_wakeup:        "assets/scenes/outside.png",
    };

const TEXT_ARCHIVE = {
  "story_texts.py": {
    "INTRO": "===================================\n  紅花吃檳榔：蔚藍學院秘案  深夜調查版\n===================================\n\n17世紀英格蘭。\n\n蔚藍學院——曾是英倫最負盛名的貴族學院，\n如今大門緊閉，雜草叢生，廢棄整整兩年。\n\n兩年前，學院內發生了一場至今未破的謀殺案。\n受害者是校內受人愛戴的米糕店長。\n真兇至今逍遙法外，學院因此被迫關閉。\n\n「紅花綻放之處，是你尋找答案的起點。\n 但你能否離開，則是另一回事。」\n                              ——紅花\n\n廢棄圖書館深處，一盞燭火搖曳於幽暗之中。\n傳說中的紅花，就在那裡守候。",
    "PROLOGUE": "你——英國皇家警察——踏入了蔚藍學院廢棄的圖書館。\n\n這是你的母校。也是你反覆做惡夢的地方。\n\n兩年前的那個傍晚，米糕店長倒在這裡。\n案件懸而未決，學院就此關閉。\n而你，曾是法國海軍，如今兼任英國皇家警察，\n今夜隻身來此，要終結這一切。\n\n你彎低身子穿過積滿灰塵的門廊，沿著旋梯一路上行。\n三樓管理室的門半掩著，燭光映照著牆上的上帝視角地圖。\n然後你看見了她。\n\n銀白色短髮，筆挺的水手服。\n她端坐於正中央的椅子上，\n嘴角含著一抹說不清是什麼顏色的紅，\n空氣裡漂著一絲隱約的石灰與生澀草腥的氣息——\n你說不上來那是從哪裡來的。\n\n「英國皇家警察，」她緩緩開口，\n「真是個奇妙的名字——或者說，奇妙的稱號。」\n\n「你來這裡是為了什麼，我已經知道了。」\n她淡淡地說，「問題是……\n 你能找到答案嗎？」\n\n天亮之前，必須找到真相。",
    "HALL": "你站在三樓館長室外的展示區。\n灰塵、蛛網與腐舊的書香充滿了每一個角落。\n\n密碼盒就立在書架旁，等待正確的三位數。\n\n【鎚子→一樓收藏室 / 四葉草→二樓檔案室 / 牛仔褲→三樓廢棄閱覽室】",
    "MAP_FLOOR_1": "【圖書館平面圖｜一樓】\n\n本層可探索：閱覽室A、閱覽室B、收藏室（古籍庫）、會議廳I、管理室走廊、守衛室。\n整層被標紅：『此層任何角落，背後隨時可能有人。』",
    "MAP_FLOOR_2": "【圖書館平面圖｜二樓】\n\n本層可探索：研究室A（研究桌）、研究室B（窗邊）、檔案室（禁書區）、會議廳II、修復工坊、二樓迴廊。\n整層同樣被標紅：『此層任何角落，背後隨時可能有人。』",
    "MAP_FLOOR_3": "【圖書館平面圖｜三樓】\n\n本層可探索：館長室外（密碼盒）、館長室（面對紅花）、私人研究室、廢棄閱覽室、封閉儲藏室（危險）。\n三樓相對安全，但封閉儲藏室有危機。",
    "INSPECT_HAMMER": "收藏室書架的深處角落，一把鏽跡斑斑、長約{hammer_length}公分的鎚子橫臥於塵埃之中。\n\n鎚柄上有三道深刻的刻痕，鎚柄底端刻著羅馬數字「III」。\n\n【物證取得】第一碼是 3。",
    "INSPECT_CLOVER": "一片乾燥的四葉草，四葉草的葉片中央，用細筆寫著一個「壹」字。\n這是「幸運的艾莉卡」的標誌性飾品。\n\n【物證取得】第二碼是 1。",
    "INSPECT_JEANS": "一件疊得整整齊齊的牛仔褲。標籤上印著「YV」兩個字母。\n褲腿內側縫著手寫的文字：「R.U. · 第四排 · 入場許可」\nR.U.——退學生天王星（Starscream）。\n\n【物證取得】第三碼是 4。",
    "SCENE_BOOKSHELVES": "書架深處，擺著四份封存的案件文件夾：\n   《失蹤案卷》  《退學檔案》  《死亡報告》  《停課公告》\n\n石板旁有一個小鎖孔，排列正確才能打開。",
    "SCENE_DESK": "桌角有一本合上的筆記本，封面上縫著水手服的繡章——這是紅花的。",
    "READ_CASE_NOTES": "【紅花的案情紀錄】\n米糕的死絕非偶然。\n我看過那把鎚子，我看過現場的血跡。\n那個傍晚，我就在圖書館裡——我聽見了爭吵聲，聽見了倒地的聲音。\n我知道誰在那裡。但是我沒有證據。\n\n【人物線索】你了解了紅花所掌握的秘密。",
    "SCENE_WINDOW": "窗台上的塵埃中，只剩下一縷乾燥的玫瑰花瓣，以及壓在花瓣下的一張折疊字條。",
    "INSPECT_WINDOW_NOTE": "字條的字跡在燭光下若隱若現：\n「艾蜜莉亞，你知道他做了什麼。你不得不消失。我明白。請——好好保重。」\n\n【人物線索】你了解了艾蜜莉亞消失的原因。",
    "SCENE_BASEMENT": "鑰匙插入暗格，書架後方的牆壁緩緩滑動。\n你看到兩扇分岔的石門。左邊是倉庫，右邊是儲藏室。",
    "SCENE_BASEMENT_STORAGE_ROOM": "冷氣從門縫滲出。裡面有極低沉的呼吸聲。門鎖從裡頭扣住，你打不開它。",
    "SCENE_BASEMENT_DEEP": "日記的頁面上，你辨認出了熟悉的字體：「天王星（Starscream）」的親筆。\n「那一天，我衝進去找米糕，是要他還我父親的錢——我們起了衝突……那把鎚子就在旁邊，我只是想嚇嚇他。我不是故意的。但艾莉卡在窗外看到了一切。」\n\n【人物線索】你掌握了天王星的親筆供詞。",
    "SCENE_TOOLBOX": "書架深處的角落有一個積滿灰塵的木製工具箱，裡面散落著幾把工具。你必須選出真正的兇器。\n\n1. 一把 15 公分的乾淨鐵鎚，木柄很新。\n2. 一把 30 公分的生鏽鐵鎚，拿起來沉甸甸的。\n3. 一把 50 公分的雙手大木槌，通常用來敲擊木樁。",
    "ENDING_SECRET": "【秘密結局 · 真相大白】\n蔚藍學院的秘案，終於有了答案。天王星是兇手。紅花，一直在等這一刻。",
    "ENDING_TRUE": "【真結局 · 線索足夠】\n案件有了重要進展，但完整的真相尚未揭露。紅花依然守著圖書館，等待你的下一次造訪。",
    "ENDING_TRUST_ALLIANCE": "【信任結局 · 共犯不是罪犯】\n你與紅花建立了調查同盟。真相尚未揭曉，但你們將並肩追到最後。",
    "ENDING_TRUST_REJECTED": "【信任結局 · 被拒於門外】\n你拿到關鍵物件，卻失去了紅花的信任。這起案件，變得更難了。",
    "ENDING_TRUST_COLDTRUTH": "【信任結局 · 冷真相】\n你解開了命案，卻沒有解開紅花心中的門。真相是對的，但你們仍然陌生。",
    "ENDING_NORMAL": "【普通結局 · 物證不足】\n危機暫緩，但謎團仍在。紅花依舊守在廢棄的蔚藍學院圖書館，等待更完整的調查。",
    "ENDING_BAD_UNPREPARED": "【壞結局 A · 準備不足】\n你被請出了圖書館。紅花依然守在那裡，優雅而神秘。",
    "ENDING_BAD_CODEFAIL": "【壞結局 B · 密碼失敗】\n第三次輸入錯誤的瞬間——密碼盒劇烈震動。你成為了圖書館的新住客。",
    "ENDING_BAD_DARKNESS": "【壞結局 E · 迷失黑暗】\n最後一絲燭火發出微弱的『嘶嘶』聲，隨後徹底熄滅。\n伸手不見五指的絕對黑暗瞬間湧入，將你吞沒。你試圖摸索牆壁前進，卻在廢棄的走廊中迷失了方向。\n不久後，你聽見了某種沉重的腳步聲，正在黑暗中慢慢向你靠近……",
    "ENDING_STORAGE_AMBUSH": "【壞結局 C · 背後偷襲】\n黑暗中，你沒有意識到腳步聲正悄悄從背後逼近。下一秒，冰冷的呼吸落在你頸後，刀光一閃。",
    "ENDING_KILLER_MAP": "【壞結局 D · 凌晨的獵殺】\n凌晨兩點後，兇手從地下室走出，在圖書館各層巡邏。燭光一口氣全滅。黑暗如潮水湧入。",
    "ENDING_HIDDEN": "「等等——妳要不要打胰島素？」\n\n話一出口，你自己都愣了。辦案辦到絕路的你，腦袋突然閃過這句毫不相干的話。\n\n紅花愣住了。燭火劇烈搖曳。整座17世紀的蔚藍學院圖書館開始剝落，像過期的伺服器貼圖一層層崩解。\n\n你眨了眨眼。\n\n舊書的氣味，被酒精棉片與消毒水的刺鼻味取代。\n你坐在一間亮得刺眼的診間裡。對面的病人用一種困惑到不知如何是好的眼神望著你：\n\n「Yv醫生……我只是來拿胃藥。妳為什麼突然問我要不要打胰島素？」\n\n你揉了揉太陽穴。是夢。\n英國皇家警察、蔚藍學院、那樁命案——只是你值大夜班打盹時，腦袋裡《大航海時代》的遊戲記憶跟現實混亂產生的夢境。\n\n你請病人離開後，走向診間外的洗手台，對著鏡子潑了點冷水。\n但當你抬起頭，你看著鏡子裡的臉，卻久久無法移開視線。\n\n鏡子裡的人，是艾蜜莉亞（Amelia）。\n\n艾蜜莉亞兩年前就不玩了。她的靈魂早就不在了。\n但你——Yv——為了不讓公會的人傷心，借用她的帳號代開太久，久到你已經習慣用她的名字登入，用她的口吻說話。\n世界以為艾蜜莉亞還在。而你，也漸漸忘記了自己到底是誰。",
    "LONDON_HIDDEN_PROLOGUE": "下班後，你回到家坐在電腦前。\n\n既然夢到了蔚藍學院，也許該去『那個地方』看看。\n你以艾蜜莉亞的身份登入遊戲，操控著角色前往倫敦。泰晤士河畔，Harbour Lane 17號。\n\n外觀是一棟灰褐色砂岩建築，門楣上掛著系統預設的銅製牌匾：\n【海員行會堂 MARINERS' GUILD HALL】\n\n但你和所有還在線的老成員都知道，這裡真正的名字是——\n★ 水手服同好會工會據點 ★",
    "LONDON_HIDDEN_CH1_ARRIVE": "你推門走進去。\n\n沒有人攔你。沒有人問你是誰。\n他們看著你的臉——艾蜜莉亞的臉——\n\n某個角落傳來一聲低低的：\n「……艾蜜莉亞回來了。」\n\n你停了一下，沒有糾正任何人。\n\n因為在這個地方，在這群人眼前，\n你本來就是艾蜜莉亞。\n你的內心也這麼告訴你。\n\n【隱藏結局 · 靈魂不在的代開帳號】\n歡迎回來，艾蜜莉亞。"
  },
  "character_texts.py": {
    "BOOKSHELF_CORRECT_ORDER": [
      "失蹤案卷",
      "退學檔案",
      "死亡報告",
      "停課公告"
    ],
    "TRUST_REMARKS": {
      "不信任": "\n紅花的目光像刀，冷冷地釘在你身上。沒有歡迎，沒有客套。",
      "觀望中": "\n她側過臉，用眼角餘光確認了你的位置——沒有說話，卻也沒有移開視線。",
      "逐步信任": "\n「……隨便你，」她輕聲說，目光重新落回書頁，但翻頁的動作慢了許多。",
      "高度信任": "\n「慢慢來，」她輕聲說，挪了挪燭台，讓光線照進了更多的角落。"
    }
  }
};

    const STORY = {
      intro:
`17世紀英格蘭，蔚藍學院已荒廢兩年。
你是英國皇家警察，也是這所學院的舊校友。

廢棄圖書館深處，銀髮少女紅花正等著你。
「你能找到答案嗎？」`,
      prologue:
`你踏入三樓管理室內，燭光在黑暗中搖曳。
紅花望向你，語氣平靜：
「三樓以外，背後隨時可能有人。」`,
      map3:
`【3F 平面圖】
可探索：館長室外（密碼盒）、館長室（面對紅花）、私人研究室、廢棄閱覽室、封閉儲藏室。
點擊房間區域或下方按鈕移動。`,
      map2:
`【2F 平面圖】
可探索：研究室A（研究桌）、研究室B（窗邊）、檔案室（四葉草在此）、會議廳II、修復工坊、二樓迴廊。
點擊房間區域或下方按鈕移動。`,
      map1:
`【1F 平面圖】
可探索：閱覽室A/B、收藏室（鎚子在此）、會議廳I、管理室走廊、守衛室。
點擊房間區域或下方按鈕移動。`,
      hall:
`你在三樓館長室外展示區，空氣中瀰漫灰塵與潮濕紙張味。
密碼盒就立在旁邊等待作答。`,
      bookshelves:
`書架深處有四份案卷。
請依序點選「失蹤案卷→退學檔案→死亡報告→停課公告」啟動機關。`,
      desk:
`你翻開紅花筆記。
她曾聽見案發當晚爭吵與倒地聲，但一直等不到能查清真相的人。`,
      window:
`窗台字條提到艾蜜莉亞被迫消失，且留下能指向真相的線索。`,
      basement:
`你抵達地下區域，左側倉庫有供詞，右側儲藏室門鎖從內扣住。`,
      basementDeep:
`你找到天王星親筆供詞：衝突中失手，艾莉卡目睹全程，艾蜜莉亞因此消失。`,
      confront:
`你回到紅花面前。
她看著你手中的證據，靜靜等你給出結論。`,
      killer_encounter:
`走廊盡頭出現一道黑影，正緩緩轉過頭來……`,
      deduction:
`你深呼吸，開始整理今晚所有線索。
若推論有誤，你將無法說服紅花。`,
      alliance_followup:
`紅花收下你遞出的證據後，終於站到你身旁。
「你說得對，兇手沒有離開圖書館。」
她用指尖點了點你剛整理出的線索：
地下儲藏室的門從內反鎖、呼吸聲持續、補給痕跡沒中斷——
那個人一直躲在裡面。

「帶路吧，」紅花說，
「這次我跟你一起下去。」`,

      python_hidden_london:
`你打開電腦，《大航海時代：傳說》的載入畫面緩緩展開。

右上角，工會圖示亮了起來──水手服同好會。
成員們都在線上，今天的工會據點應該很熱鬧。

你輸入了密碼。
以艾蜜莉亞的身份，登入這個你最熟悉的世界。`,

      amelia_hub:
`你以艾蜜莉亞的身份登入《大航海時代：傳說》。

工會據點──圖書館──熟悉的書香與幾分虛擬的海風交錯。
身穿淺咖啡色雙馬尾水手服的你，環顧著這個稱為「水手服同好會」的工會據點。

成員們分散在各個角落，談論著航海與冒險。
新賽季剛剛開始，今天的據點比平日更熱鬧。`,

      amelia_reading_room:
`閱覽室內，暗金色雙馬尾的幸運四葉草正盯著筆記本，眉飛色舞地圈圈畫畫。

「艾蜜莉亞！」她一看到你立刻揚起笑容，水手服隨動作輕輕飄動。
「你有沒有試過新賽季的香料群島路線？
 那裡有隱藏的海圖碎片，我找了三天才拼出一半──
 但據說完整的海圖能換限定稱號『群島探索者』！
 而且……」她壓低聲音，「最後一片在馬六甲的隱藏海盜港，
 說不定傑克森馬吉斯知道詳細位置！」`,

      amelia_reading_room_visited:
`幸運四葉草依然埋頭在她的航線計算裡，見你過來歡快地揮手。

「艾蜜莉亞！我跟傑克森確認了──
 香料群島最後那片海圖碎片就在馬六甲海峽的隱藏海盜港！
 我已經把路線記好了，等你有空，我們一起去拿！」`,

      amelia_archive_room:
`檔案室的書桌旁，銀白色雙馬尾的艾莉卡正翻閱著一份航海紀錄。

她抬起頭，平靜地點點頭：「艾蜜莉亞。」

「你知道嗎，這個工會最初只有三個人。
 紅花、我、還有一個後來轉去其他伺服器的隊員。
 我們在《大航海時代》裡找到彼此，只因為都穿水手服。
 就這樣。沒有什麼遠大的理由──
 同一個審美，就成了夥伴。」

她停頓，看向窗外：「說起來，這比現實裡的很多緣分都單純。」`,

      amelia_archive_room_followup:
`艾莉卡把桌上的紀錄往旁邊推，看著你進來。

「艾蜜莉亞，你來了。」語氣比平時多了一分認真。

「幸運四葉草告訴我香料群島的最後路線，
 傑克森也確認了海盜港的位置。
 也就是說──我們可以組成最完整的艦隊了。
 水手 × 海盜 × 探索者，三種職業，一個工會。」

她微微笑：「《大航海時代》的設計者很厲害──
 他們讓不同性格的人，在同一片海上找到各自的位置。
 就像我們。」`,

      amelia_workshop:
`修復工坊的桌上擺滿了航線圖和攻略筆記。
戴著眼鏡、黑色中短髮的珊珊正皺眉對著一份任務說明。

「艾蜜莉亞，」她調整眼鏡，語氣一如既往地直接，「你來得正好。
 塞特說倫敦教堂有一條隱藏任務鏈，
 需要水手和海盜玩家同時在場才能觸發。

 我試過三次了，一個人不夠。」

她把任務說明推到你面前：
「你去跟塞特確認觸發條件吧──他在會議室。」`,

      amelia_meeting_room:
`會議室的長桌旁，粉紅色短髮的傑克森馬吉斯正試算航海戰術表格。

「哦，艾蜜莉亞，」她抬頭，帶著一貫的爽利笑容。
「我有個好消息──馬六甲的海盜港位置確認了，
 就是幸運四葉草要找的那個碎片所在地。
 在《大航海時代》裡，情報才是海盜的核心。」

她把一份手寫地圖甩給你：「拿好，說不定我們哪天組隊去。」

她頓了頓，笑意輕輕收了收：
「說真的，艾蜜莉亞……你最近狀態怎麼樣？現實裡，我是說。」

────
角落的窗邊，金髮的塞特正看著窗外出神。
他正在等什麼……你還不清楚。`,

      amelia_meeting_room_seth_avail:
`會議室的長桌旁，傑克森馬吉斯依然在研究她的戰術表格，偶爾抬頭和你點個頭。

────
金髮的塞特靠在窗邊，露胸海盜裝在圖書館燈光下格外不羈。

他看到你走近，溫柔地笑了笑：
「艾蜜莉亞，珊珊說你要來。
 倫敦教堂的隱藏任務──我找到觸發條件了。
 必須在午夜時分，帶著聖水和一枚舊錢幣，
 在地下教堂的彩繪玻璃前等待。
 那幅聖喬治屠龍畫後面，藏著古老海圖的第一頁。」

他推開窗，外面是圖書館庭院的夜色：
「倫敦教堂最高管理員的稱號……其實不重要。
 我更喜歡和你們一起探索這件事本身。加油，艾蜜莉亞。」`,

      amelia_meeting_room_seth_done:
`會議室裡，傑克森馬吉斯和塞特都在，氣氛平靜而熱鬧。

傑克森回頭看了你一眼：「怎樣，塞特說的聽懂了嗎？」
塞特笑了笑：「她聽懂了。」

《大航海時代》的新賽季，讓這個工會比以往都更有活力。`,

      amelia_guild_office:
`工會辦公室裡，銀色短髮的紅花端坐於會長椅上，
翻閱著工會航線統計報告。

「艾蜜莉亞，」她不抬頭，「你今天又在這裡待了很久了。」

她放下報告，看著你：
「《大航海時代》是個好遊戲，我設立這個工會，
 是希望大家能在這裡找到屬於自己的海洋。
 但記住──」眼神認真起來，
「哪些是遊戲裡的風浪，哪些是現實的，要分清楚。」`,

      amelia_guild_office_final:
`紅花放下報告，罕見地直接盯著你。

「艾蜜莉亞，我直說了。
 大家都跟我說你今天的狀態不對──
 傑克森說你眼神有點渙散，珊珊說你在線時間太長，
 幸運四葉草說你打字比平時慢。
 我知道你喜歡待在這裡，」她停頓，
「但有些事，遊戲替代不了。
 你的胰島素──」她直視著你，語氣放輕，像是穿透螢幕在說話：
「你有記得用嗎？」

那個詞在你心裡迴響。胰島素。
書頁聲、鍵盤聲、遠處傑克森馬吉斯的笑聲──
在那一刻，全部變得遙遠。

你……應該回去了。`,

      amelia_wakeup:
`你睜開眼睛。

臥室的天花板，熟悉而真實。
窗外的光線平穩，時鐘的秒針一格格地走。
手機螢幕上，《大航海時代：傳說》的登入畫面靜靜等著。

你的水手服同好會夥伴們，應該還在那片海上。

但現在，有一件事需要先做。
你翻身起床，從床頭取出胰島素筆。
刺點、注射、記錄──這個過程你早就做得熟練。

做完之後，你坐回床邊，看著窗外的光。
有些人在遊戲裡等你，
但你先得好好照顧現實裡的自己，
才能繼續和他們一起航行。

【隱藏線真結局：醒來】`,
    };

    const CHARACTER = {
      trustRemarks: {
        low: "紅花的目光像刀，冷冷地釘在你身上。",
        mid: "她沒有移開視線，似乎願意再聽你多說一點。",
        high: "「慢慢來。」她把燭台往前推了些，讓光照進更多角落。"
      }
    };

    const SCENE_HOTSPOTS = {
      map3: [
        { label: "館長室外調查",       rect: [5,   4, 46, 47], match: "前往館長室外調查" },
        { label: "面對紅花", rect: [5,  48, 46, 14], match: "面對紅花" },
        { label: "私人研究室",         rect: [56,  4, 35, 43], match: "前往私人研究室" },
        { label: "廢棄閱覽室",         rect: [5,  50, 37, 33], match: "前往廢棄閱覽室" },
        { label: "封閉儲藏室（危險）",  rect: [55, 50, 38, 33], match: "前往封閉儲藏室（危險）" },
        { label: "查看一樓",           rect: [4,  86, 24,  9], match: "查看一樓" },
        { label: "查看二樓",           rect: [37, 86, 24,  9], match: "查看二樓" },
      ],
      map2: [
        { label: "研究室A（研究桌）",  rect: [7,   7, 24, 29], match: "前往研究室A（研究桌）" },
        { label: "研究室B（窗邊）",   rect: [63,  7, 24, 29], match: "前往研究室B（窗邊）" },
        { label: "檔案室（禁書區）",  rect: [70, 38, 28, 32], match: "前往檔案室（禁書區）" },
        { label: "會議廳II",          rect: [1,  38, 23, 32], match: "前往會議廳II" },
        { label: "修復工坊",           rect: [8,  72, 29, 20], match: "前往修復工坊" },
        { label: "二樓迴廊",           rect: [31,  7, 31, 36], match: "前往二樓迴廊" },
        { label: "查看一樓",           rect: [4,  86, 24,  9], match: "查看一樓" },
        { label: "查看三樓",           rect: [69, 86, 24,  9], match: "查看三樓" },
      ],
      map1: [
        { label: "閱覽室A",            rect: [5,   7, 24, 31], match: "前往閱覽室A" },
        { label: "閱覽室B",            rect: [58,  7, 27, 31], match: "前往閱覽室B" },
        { label: "收藏室（古籍庫）",   rect: [70, 38, 25, 22], match: "前往收藏室（古籍庫）" },
        { label: "會議廳I",            rect: [1,  38, 17, 22], match: "前往會議廳I" },
        { label: "管理室走廊",         rect: [5,  60, 24, 16], match: "前往管理室走廊" },
        { label: "守衛室",             rect: [67, 60, 24, 16], match: "前往守衛室" },
        { label: "地下密室",           rect: [35, 60, 24, 16], match: "地下密室",
          visibleWhen: (state) => state.flags.basementOpen },
        { label: "查看二樓",           rect: [4,  86, 24,  9], match: "查看二樓" },
        { label: "查看三樓",           rect: [69, 86, 24,  9], match: "查看三樓" },
      ],
      hall: [
        { label: "密碼盒", rect: [69, 30, 28, 27], match: "密碼盒" },
        { label: "回地圖", rect: [73, 86, 24,  9], match: "回到三樓地圖" },
      ],
      abandonedRoom: [
        { label: "牛仔褲", rect: [53, 58, 34, 30], match: "調查閱讀台下的牛仔褲（第四排）" },
        { label: "回地圖", rect: [73, 86, 24,  9], match: "離開廢棄閱覽室，返回三樓地圖" },
      ],
    };

    const ARCHIVE_LABELS = {
      "story_texts.py": "主劇情文本",
      "character_texts.py": "角色文本",
    };
    const SCENE_ALT_TEXTS = {
      intro: "學院外觀",
      python_hidden_start: "Python 隱藏線起點：診所",
      python_hidden_london: "Python 隱藏線：倫敦",
    };
    const MAP_SCENE_VIEWPORTS = {};  

    const SCENE_DISPLAY_NAMES = {
      intro:        "學院外觀",
      prologue:     "序章",
      hall:         "館長室外展示區",
      deduction:    "推理盤",
      killer_encounter: "走廊遭遇",
      map3:         "3F 平面圖",
      map2:         "2F 平面圖",
      map1:         "1F 平面圖",
      collectionRoom: "收藏室（古籍庫）",
      toolbox:      "舊工具箱",
      archiveRoom:  "檔案室（禁書區）",
      guardRoom:    "守衛室",
      workshop:     "修復工坊",
      abandonedRoom:"廢棄閱覽室",
      confront:     "面對紅花",
      alliance_followup:"同盟追兇",
      battle_starscream: "地下儲藏室 · 死鬥",
      battle_random: "突發遭遇戰",
      battle_farm:   "刷怪房",
      victory:      "戰鬥勝利",
      python_hidden_start:"隱藏線：夢醒時分",
      python_hidden_london:"隱藏線：航向倫敦",
      amelia_hub:          "水手服同好會工會據點",
      amelia_reading_room: "閱覽室",
      amelia_archive_room: "檔案室",
      amelia_workshop:     "修復工坊",
      amelia_meeting_room: "會議室",
      amelia_guild_office: "工會辦公室",
      amelia_wakeup:       "醒來",
    };

const initialState = () => ({
      scene: "intro",
      elapsed: 0,
      trust: 0,
      candle: MAX_CANDLE,
      playerX: DEFAULT_PLAYER_X,
      playerY: DEFAULT_PLAYER_Y,
      honghuaX: DEFAULT_HONGHUA_X,
      honghuaY: DEFAULT_HONGHUA_Y,
      evidence: { ...DEFAULT_EVIDENCE },
      clues: { ...DEFAULT_CLUES },
      flags: { ...DEFAULT_FLAGS },
      archive: { ...DEFAULT_ARCHIVE },
      log: [DEFAULT_LOG_MESSAGE],
      passwordFails: 0,
      booksOrder: [],
      currentFloor: 3,
      // RPG 戰鬥屬性
      playerHp: 100,
      maxHp: 100,
      playerBaseAtk: 10,
      potions: 3,
      wax: 0,
      bossHp: 150,
      bossMaxHp: 150,
      isDefending: false,
      monsterHp: 0,
      monsterMaxHp: 0,
      monsterAtk: 0,
      monsterName: "敵人",
      farmZone: "",
      lowZoneKills: 0,
      highZoneKills: 0,
      level: 1,
      exp: 0,
      expNext: 50,
      lastVictory: null,
    });
