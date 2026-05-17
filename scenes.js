function sceneText(key) {
      if (key === "hall") {
        return STORY.hall + "\n\n" + CHARACTER.trustRemarks[trustTier()];
      }
      if (key === "bookshelves") {
        const picked = S.booksOrder.length ? S.booksOrder.join(" → ") : "（尚未選擇）";
        return `${STORY.bookshelves}\n\n目前排序：${picked}`;
      }
      if (key === "deduction") {
        return STORY.deduction + (S.flags.deductionComplete ? "\n\n✅ 已完成推理，可直接面對紅花。" : "");
      }
      if (key === "collectionRoom") return STORY.SCENE_COLLECTION_ROOM || "【收藏室（古籍庫）】\n\n厚重的書架深處有什麼東西靜靜躺著……";
      if (key === "toolbox") return STORY.SCENE_TOOLBOX || "書架深處的角落有一個積滿灰塵的木製工具箱，裡面散落著幾把工具。";
      if (key === "archiveRoom") return STORY.SCENE_ARCHIVE_ROOM || "【檔案室（禁書區）】\n\n封閉多年的禁書區，有人留下了足跡……";
      if (key === "guardRoom") {
        if (S.flags.guardLogbookFound) {
          return STORY.INSPECT_GUARD_LOGBOOK || "你翻開守衛記錄本，記下了案發夜的異常巡邏紀錄。";
        }
        return STORY.SCENE_GUARD_ROOM || "【守衛室】\n\n守衛室已人去樓空，桌角有一本記錄本……";
      }
      if (key === "workshop") {
        if (S.flags.workshopCardFound) {
          return STORY.INSPECT_WORKSHOP_CARD || "你翻閱工作記錄卡，確認案發前三天有人委託秘密修復文書。";
        }
        return STORY.SCENE_WORKSHOP || "【修復工坊】\n\n工作台上有一本工作記錄……";
      }
      if (key === "abandonedRoom") return STORY.SCENE_ABANDONED_ROOM || "【廢棄閱覽室】\n\n積灰的閱讀台下藏著某些東西……";
      if (key === "alliance_followup") return STORY.alliance_followup;
      if (key === "battle_starscream") {
        return `【地下儲藏室 · 死鬥】\n黑暗中，天王星像一頭野獸般轉過身來。\n\n[皇家警察 Yv]\n❤️ HP: ${S.playerHp} / ${S.maxHp}\n⚔️ 攻擊力: ${getPlayerAtk()} (武器裝備中)\n\n[退學生 天王星]\n❤️ HP: ${S.bossHp} / ${S.bossMaxHp}\n\n請選擇你的行動：`;
      }
      if (key === "battle_random") {
        return `【突發戰鬥】\n走廊的陰影中，一具『徘徊的黑影』朝你撲來！\n\n[皇家警察 Yv]\n❤️ HP: ${S.playerHp} / ${S.maxHp}\n\n[徘徊的黑影]\n❤️ HP: ${S.monsterHp} / ${S.monsterMaxHp}\n\n請選擇行動：`;
      }
      if (key === "battle_farm") {
        return `【戰鬥】\n你遭遇了『${S.monsterName}』！\n\n[皇家警察 Yv]\n❤️ HP: ${S.playerHp} / ${S.maxHp}\n\n[${S.monsterName}]\n❤️ HP: ${S.monsterHp} / ${S.monsterMaxHp}\n\n請選擇行動：`;
      }
      if (key === "victory") {
        const V = S.lastVictory;
        if (!V) return "【Victory】\n戰鬥結束，你暫時安全了。";
        const potionText = V.potionGain > 0 ? `\n• 急救檳榔 +${V.potionGain}` : "";
        const levelText = V.levelUps > 0
          ? `\n🎖️ 升級！你提升了 ${V.levelUps} 級，現在是 Lv.${S.level}。`
          : "\n📘 尚未升級，繼續戰鬥累積經驗。";
        return `【Victory】\n你擊敗了「${V.enemyName}」！\n\n✨ 戰利品結算\n• EXP +${V.expGain}\n• 殘蠟 +${V.waxGain}\n• 燭火 +${V.candleGain}${potionText}${levelText}\n\n你擺出勝利姿勢，準備繼續調查。`;
      }
      if (key === "python_hidden_start") {
        return formatTemplateText(TEXT_ARCHIVE["story_texts.py"]?.ENDING_HIDDEN || "【隱藏結局】夢醒時分。");
      }
      if (key === "python_hidden_london") {
        return STORY.python_hidden_london || formatTemplateText(TEXT_ARCHIVE["story_texts.py"]?.LONDON_HIDDEN_PROLOGUE || "【隱藏分支】航向倫敦。");
      }
      // ── Amelia mode scenes ─────────────────────────────────────────────────
      if (key === "amelia_reading_room") {
        return S.flags.ameliaTalkedClover ? STORY.amelia_reading_room_visited : STORY.amelia_reading_room;
      }
      if (key === "amelia_archive_room") {
        return S.flags.ameliaEricaFollowup ? STORY.amelia_archive_room_followup : STORY.amelia_archive_room;
      }
      if (key === "amelia_meeting_room") {
        if (!S.flags.ameliaTalkedShanshan) return STORY.amelia_meeting_room;
        if (!S.flags.ameliaTalkedSeth)    return STORY.amelia_meeting_room_seth_avail;
        return STORY.amelia_meeting_room_seth_done;
      }
      if (key === "amelia_guild_office") {
        const allTalked = S.flags.ameliaTalkedClover && S.flags.ameliaTalkedErica &&
                          S.flags.ameliaTalkedShanshan && S.flags.ameliaTalkedJackson &&
                          S.flags.ameliaTalkedSeth;
        return allTalked ? STORY.amelia_guild_office_final : STORY.amelia_guild_office;
      }
      if (key === "archive_index") {
        const storyCount = archiveKeys("story_texts.py").length;
        const characterCount = archiveKeys("character_texts.py").length;
        return [
          "【全內容文字庫】",
          "這裡已將 Python 版文本常數 HTML 化並內嵌到單一 index.html。",
          `可瀏覽：主劇情 ${storyCount} 筆、角色文本 ${characterCount} 筆。`,
          "請選擇要瀏覽的文本群組。",
        ].join("\n\n");
      }
      if (key === "archive_group") {
        ensureArchiveState();
        const keys = archiveKeys(S.archive.group);
        const sample = keys.slice(0, ARCHIVE_PREVIEW_LIMIT).join("、");
        return [
          `【${ARCHIVE_LABELS[S.archive.group] || S.archive.group}】`,
          `共 ${keys.length} 筆常數。`,
          sample ? `部分條目：${sample}` : "（無資料）",
          "請從下方按鈕選擇要查看的條目。",
        ].join("\n\n");
      }
      if (key === "archive_entry") {
        ensureArchiveState();
        const val = (TEXT_ARCHIVE[S.archive.group] || {})[S.archive.key];
        return [
          `【${S.archive.key || "未選擇條目"}】`,
          "",
          formatTemplateText(val ?? "（此條目不存在）"),
        ].join("\n");
      }
      return STORY[key] || "（場景資料不存在）";
    }

function makeOptions() {
      const opts = [];
      switch (S.scene) {
        case "archive_index":
          opts.push([ARCHIVE_LABELS["story_texts.py"], () => { S.archive.group = "story_texts.py"; S.archive.key = null; goto("archive_group"); }]);
          opts.push([ARCHIVE_LABELS["character_texts.py"], () => { S.archive.group = "character_texts.py"; S.archive.key = null; goto("archive_group"); }]);
          opts.push(["返回遊戲", () => goto("map3")]);
          break;
        case "archive_group": {
          ensureArchiveState();
          for (const key of archiveKeys(S.archive.group)) {
            opts.push([key, () => { S.archive.key = key; goto("archive_entry"); }]);
          }
          opts.push(["← 回到文字庫首頁", () => goto("archive_index")]);
          opts.push(["返回遊戲", () => goto("map3")]);
          break;
        }
        case "archive_entry":
          opts.push(["← 回到條目列表", () => goto("archive_group")]);
          opts.push(["返回遊戲", () => goto("map3")]);
          break;
        case "intro":
          opts.push(["開始調查", () => { advance(10, "抵達圖書館"); goto("prologue"); }]);
          break;
        case "prologue":
          opts.push(["[強硬] 皇家警察辦案，請妳配合交出所有線索。", () => { addTrust(-15, "態度強硬"); goto("map3"); }]);
          opts.push(["[溫和] 我知道妳在保護某個秘密，我們目的一致。", () => { addTrust(20, "釋出善意"); goto("map3"); }]);
          break;
        case "map3":
          opts.push(["前往館長室外調查", () => { advance(20, "進入館長室外展示區"); goto("hall"); }]);
          opts.push(["開始整理線索 (推理)", () => goto("deduction")]);
          opts.push(["面對紅花", () => {
            if (!S.flags.deductionComplete) {
              pushLog("⚠ 你還沒完成推理盤，無法直接提出結論。");
              render();
              return;
            }
            goto("confront");
          }]);
          opts.push(["前往私人研究室 (高難度刷怪區)", () => {
            advance(20, "進入私人研究室");
            S.farmZone = "high";
            if (S.highZoneKills >= 10) {
              S.monsterHp = 350; S.monsterMaxHp = 350; S.monsterAtk = 38;
              S.monsterName = "【隱藏超魔王】狂暴艾莉卡";
              pushLog("🚨 警告：空間結構嚴重扭曲！雙馬尾被血色染紅的恐怖存在降臨──狂暴艾莉卡擋住了去路！");
            } else {
              S.monsterHp = 100; S.monsterMaxHp = 100; S.monsterAtk = 20;
              S.monsterName = "深淵守衛";
            }
            goto("battle_farm");
          }]);
          opts.push(["前往廢棄閱覽室", () => { advance(20, "進入廢棄閱覽室"); goto("abandonedRoom"); }]);
          opts.push(["前往封閉儲藏室（危險）", () => { advance(20, "靠近封閉儲藏室"); goto("basement"); }]);
          opts.push(["查看一樓", () => { tryFloorTransition(1, 30, "前往 1F"); }]);
          opts.push(["查看二樓", () => { tryFloorTransition(2, 20, "前往 2F"); }]);
          break;
        case "map2":
          opts.push(["前往研究室A（研究桌）", () => { advance(20, "閱讀案情筆記"); goto("desk"); }]);
          opts.push(["前往研究室B（窗邊）", () => { advance(20, "查看窗台字條"); goto("window"); }]);
          opts.push(["前往檔案室（禁書區）", () => { advance(15, "進入禁書區"); goto("archiveRoom"); }]);
          opts.push(["前往會議廳II (中難度刷怪區)", () => {
            advance(15, "進入會議廳II");
            S.farmZone = "";
            S.monsterHp = 60; S.monsterMaxHp = 60; S.monsterAtk = 12; S.monsterName = "殘破的鎧甲";
            goto("battle_farm");
          }]);
          opts.push(["前往修復工坊", () => { advance(20, "進入修復工坊"); goto("workshop"); }]);
          opts.push(["前往二樓迴廊 (中難度刷怪區)", () => {
            advance(15, "探索二樓迴廊");
            S.farmZone = "";
            S.monsterHp = 60; S.monsterMaxHp = 60; S.monsterAtk = 12; S.monsterName = "殘破的鎧甲";
            goto("battle_farm");
          }]);
          opts.push(["查看一樓", () => { tryFloorTransition(1, 20, "前往 1F"); }]);
          opts.push(["查看三樓", () => { tryFloorTransition(3, 20, "前往 3F"); }]);
          break;
        case "map1":
          opts.push(["前往閱覽室A (低難度刷怪區)", () => {
            advance(10, "進入閱覽室A尋找物資");
            S.farmZone = "low";
            if (S.lowZoneKills >= 10) {
              S.monsterHp = 130; S.monsterMaxHp = 130; S.monsterAtk = 15;
              S.monsterName = "受害者的怨靈 米糕";
              pushLog("🛑 突然間四周溫度驟降！書架間飄出巨大的黑影──那是米糕因不甘而凝聚的怨靈！");
            } else {
              S.monsterHp = 30; S.monsterMaxHp = 30; S.monsterAtk = 5;
              S.monsterName = "迷惘的幽魂";
            }
            goto("battle_farm");
          }]);
          opts.push(["前往閱覽室B (低難度刷怪區)", () => {
            advance(10, "進入閱覽室B尋找物資");
            S.farmZone = "";
            S.monsterHp = 30; S.monsterMaxHp = 30; S.monsterAtk = 5; S.monsterName = "迷惘的幽魂";
            goto("battle_farm");
          }]);
          opts.push(["前往收藏室（古籍庫）", () => { advance(20, "進入收藏室"); goto("collectionRoom"); }]);
          opts.push(["前往會議廳I", () => { advance(20, "進入會議廳I"); goto("map1"); }]);
          opts.push(["前往管理室走廊", () => { advance(15, "巡查管理室走廊"); goto("map1"); }]);
          opts.push(["前往守衛室", () => { advance(20, "進入守衛室"); goto("guardRoom"); }]);
          if (S.flags.basementOpen) {
            opts.push(["地下密室", () => { advance(20, "下到地下密室"); goto("basement"); }]);
          }
          opts.push(["查看二樓", () => { tryFloorTransition(2, 20, "前往 2F"); }]);
          opts.push(["查看三樓", () => { tryFloorTransition(3, 30, "前往 3F"); }]);
          break;
        case "hall":
          opts.push(["密碼盒", () => {
            const ans = prompt("請輸入三位數密碼：");
            if (ans === PASSWORD_CODE) {
              S.flags.trueSong = true;
              advance(5, "解開密碼盒");
              pushLog("🔓 密碼正確！取得關鍵道具《鎮魂歌譜》");
            } else {
              S.passwordFails += 1;
              pushLog(`❌ 密碼錯誤（${S.passwordFails}/3）`);
              if (S.passwordFails >= 3) {
                goto("ending_bad_codefail");
                return;
              }
            }
            render();
          }]);
          opts.push(["前往書架深處（取得密碼盒線索）", () => { advance(20, "排列案卷"); goto("bookshelves"); }]);
          
          if (S.trust >= 60 && !S.flags.honghuaJoined) {
            opts.push(["(信任) 邀請紅花一起行動", () => { 
              S.flags.honghuaJoined = true; 
              advance(5, "說服紅花"); 
              pushLog("🤝 紅花點了點頭，拿起了她的燭台與你同行。"); 
              render(); 
            }]);
          }

          // --- Firekeeper Rest Mechanic ---
          if (S.wax >= 2) {
            opts.push([`🔥 [休息] 交出 2 塊殘蠟 (恢復 40 HP 與 全部燭火)`, () => {
              S.wax -= 2;
              S.playerHp = Math.min(S.maxHp, S.playerHp + 40);
              advance(30, "在紅花的守護下休息");
              
              // 確保在 advance 扣除時間後，燭火依然補滿
              S.candle = MAX_CANDLE; 
              
              addTrust(2, "依賴與陪伴");
              pushLog("❤️ 紅花接過殘蠟添入燭台，火光重新明亮起來。你恢復了 40 點 HP，燭火值已補滿！");
              render();
            }]);
          } else {
            opts.push([`🔥 [休息] (需要 2 塊殘蠟) 目前殘蠟不足`, () => {
              pushLog("💡 提示：在圖書館各樓層探索遭遇『黑影』並擊敗它們，可以取得殘蠟。");
              render();
            }]);
          }
          // -------------------------------------
          opts.push(["回到三樓地圖", () => { advance(15, "返回地圖"); goto("map3"); }]);
          break;
        case "collectionRoom":
          opts.push(["調查書架角落的舊工具箱", () => goto("toolbox")]);
          opts.push(["離開收藏室，返回一樓地圖", () => { advance(15, "返回 1F"); goto("map1"); }]);
          break;
        case "toolbox":
          opts.push(["拿走 15 公分的乾淨鐵鎚", () => {
            advance(10, "拿錯證物");
            pushLog("❌ 這把鎚子太輕，且沒有任何使用痕跡，顯然不是兇器。");
            render();
          }]);
          opts.push(["拿走 30 公分的生鏽鐵鎚", () => {
            if (!S.evidence.hammer) {
              S.evidence.hammer = true;
              addTrust(8, "你以精準的眼光挑出了正確兇器");
              pushLog("📌 物證：30公分生鏽鐵鎚。你在底部刮開血污，發現了羅馬數字『III』（第一碼 3）");
            }
            advance(15, "找到關鍵證物");
            goto("collectionRoom");
          }]);
          opts.push(["拿走 50 公分的雙手大木槌", () => {
            advance(10, "拿錯證物");
            pushLog("❌ 這把木槌太巨大了，兇手不可能把它藏在衣服裡帶進圖書館。");
            render();
          }]);
          opts.push(["放棄調查，退回收藏室", () => goto("collectionRoom")]);
          break;
        case "archiveRoom":
          opts.push([S.evidence.clover ? "✓ 已調查四葉草" : "書縫中的四葉草", () => {
            if (!S.evidence.clover) {
              S.evidence.clover = true;
              pushLog(`📌 物證：幸運四葉草（第二碼 ${PASSWORD_DIGITS.clover}）`);
            }
            advance(15, "調查四葉草");
            render();
          }]);
          if (S.evidence.clover && !S.flags.cloverUsed) {
            opts.push(["(使用四葉草) 將四葉草作為書籤，放入桌上的無字天書", () => {
              advance(10, "破解天書密碼");
              S.flags.cloverUsed = true;
              pushLog("📖 書頁浮現了隱藏的字跡！");
              if (!S.clues.amelia) {
                S.clues.amelia = true;
                addTrust(10, "你透過四葉草解讀出艾蜜莉亞線索");
                pushLog("🧩 人物線索：艾蜜莉亞失蹤原因（無字天書顯現）");
              }
              render();
            }]);
          }
          opts.push(["離開檔案室，返回二樓地圖", () => { advance(15, "返回 2F"); goto("map2"); }]);
          break;
        case "guardRoom":
          opts.push([S.flags.guardLogbookFound ? "✓ 已調查守衛記錄本" : "調查桌角的守衛記錄本", () => {
            if (!S.flags.guardLogbookFound) {
              S.flags.guardLogbookFound = true;
              addTrust(5, "你記下守衛記錄本異常內容");
              pushLog("🧩 線索：守衛記錄本（案發夜異常巡邏紀錄）");
            }
            advance(15, "翻閱守衛記錄本");
            render();
          }]);
          if (!S.flags.foundMatches) {
            opts.push(["尋找抽屜裡的火柴盒 (+30 燭火)", () => {
              S.candle = Math.min(MAX_CANDLE, S.candle + MATCHES_CANDLE_BONUS);
              advance(5, "點燃新火柴");
              pushLog("🕯️ 補充光源");
              S.flags.foundMatches = true;
              render();
            }]);
          }
          opts.push(["離開守衛室，返回一樓地圖", () => { advance(15, "返回 1F"); goto("map1"); }]);
          break;
        case "workshop":
          opts.push([S.flags.workshopCardFound ? "✓ 已調查工作記錄卡" : "調查工具箱旁的工作記錄卡", () => {
            if (!S.flags.workshopCardFound) {
              S.flags.workshopCardFound = true;
              addTrust(5, "你找到秘密修復委託記錄");
              pushLog("🧩 線索：修復工作卡（T.S. 案發前三天秘密委託）");
            }
            advance(15, "翻閱工作記錄卡");
            render();
          }]);
          opts.push(["離開修復工坊，返回二樓地圖", () => { advance(15, "返回 2F"); goto("map2"); }]);
          break;
        case "abandonedRoom":
          if (S.flags.honghuaJoined && !S.clues.starscream) {
            opts.push(["讓紅花幫忙搜索廢棄手冊", () => { 
              S.clues.starscream = true; 
              addTrust(10, "並肩作戰"); 
              advance(5, "紅花的協助"); 
              pushLog("🧩 紅花憑藉對圖書館的熟悉，從角落翻出了廢棄相框。"); 
              render(); 
            }]);
          }

          if (!S.clues.starscream) {
            S.clues.starscream = true;
            addTrust(5, "你找到廢棄手冊");
            pushLog("🧩 人物線索：廢棄相框（艾莉卡的監視行程）");
          }
          opts.push([S.evidence.jeans ? "✓ 已調查牛仔褲" : "調查閱讀台下的牛仔褲（第四排）", () => {
            if (!S.evidence.jeans) {
              S.evidence.jeans = true;
              pushLog(`📌 物證：YV 牛仔褲（第三碼 ${PASSWORD_DIGITS.jeans}）`);
            }
            advance(15, "調查牛仔褲");
            render();
          }]);
          opts.push(["離開廢棄閱覽室，返回三樓地圖", () => { advance(15, "返回 3F"); goto("map3"); }]);
          break;
        case "killer_encounter":
          opts.push(["(躲進旁邊的櫃子) 屏住呼吸", () => {
            advance(30, "躲避殺手");
            goto(`map${S.currentFloor}`);
          }]);
          opts.push(["(直接衝過去) 試圖硬闖", () => { goto("ending_killer_map"); }]);
          break;
        case "deduction":
          opts.push(["開始回答三題推理", () => startDeductionQuiz()]);
          if (S.flags.deductionComplete) {
            opts.push(["面對紅花", () => goto("confront")]);
          }
          opts.push(["先回 3F 地圖", () => goto("map3")]);
          break;
        case "confront":
          opts.push(["提出推論與證據", () => endingCheck()]);
          opts.push(["返回 3F 地圖", () => goto("map3")]);
          break;
        case "alliance_followup":
          opts.push(["帶紅花前往地下儲藏室", () => {
            advance(15, "與紅花前往地下儲藏室");
            if (S.scene === "ending_bad_darkness") return;
            if (S.clues.starscream) {
              pushLog("⚔️ 遭遇了躲在儲藏室深處的天王星！戰鬥開始！");
              S.bossHp = S.bossMaxHp;
              goto("battle_starscream");
            } else {
              pushLog("⚠ 線索不足，無法鎖定兇手藏匿點。");
              goto("map1");
            }
          }]);
          opts.push(["我自己先去地下室確認", () => {
            advance(12, "單獨前往地下儲藏室");
            if (S.scene === "ending_bad_darkness") return;
            if (S.clues.starscream) {
              S.scene = "ending_alliance_solo_bad";
              pushLog("☠ 達成：單獨追兇失敗");
              render();
              return;
            }
            goto("basement");
          }]);
          opts.push(["先補齊線索再行動", () => goto("map3")]);
          break;

        case "battle_starscream":
          // 1. Attack Option
          opts.push(["🗡️ 全力攻擊", () => {
            S.isDefending = false;

            // Player Attack
            let dmg = getPlayerAtk() + Math.floor(Math.random() * 6) - 3;
            S.bossHp -= dmg;
            pushLog(`💥 你揮舞武器，對天王星造成了 ${dmg} 點傷害！`);

            // Honghua Assist
            if (S.flags.honghuaJoined && S.bossHp > 0) {
              let hDmg = 8;
              S.bossHp -= hDmg;
              pushLog(`✨ 紅花在後方擲出燭台干擾，造成了 ${hDmg} 點追加傷害！`);
            }

            // Check Boss Death
            if (S.bossHp <= 0) {
              pushLog("🎉 天王星倒下了！");
              S.scene = "ending_alliance_capture";
              render();
              return;
            }

            render();
            setSceneUiInteractivity(false);
            setTimeout(() => {
              if (S.scene !== "battle_starscream") {
                setSceneUiInteractivity(true);
                return;
              }

              triggerMonsterAttackVisual("assets/boss_starscream_attack.gif", 1000);
              if (audioEnabled) {
                sfxMonsterHit.currentTime = 0;
                sfxMonsterHit.play().catch(() => {});
              }

              let bossDmg = 20 + Math.floor(Math.random() * 10);
              S.playerHp -= bossDmg;
              pushLog(`🩸 天王星瘋狂反撲，你受到了 ${bossDmg} 點傷害。`);

              if (S.playerHp <= 0) {
                S.scene = "ending_alliance_solo_bad";
                pushLog("☠ 你在戰鬥中力竭倒下了...");
              }
              setSceneUiInteractivity(true);
              render();
            }, 300);
            return;
          }]);

          // 2. Defend Option
          opts.push(["🛡️ 舉起物品防禦", () => {
            S.isDefending = true;
            let bossDmg = Math.floor((20 + Math.floor(Math.random() * 10)) * 0.3);
            S.playerHp -= bossDmg;
            pushLog(`🛡️ 你採取守勢，完美格擋！只受到了 ${bossDmg} 點傷害。`);

            if (S.playerHp <= 0) S.scene = "ending_alliance_solo_bad";
            render();
          }]);

          // 3. Heal Option
          if (S.potions > 0) {
            opts.push([`💊 嚼一口急救檳榔 (剩餘: ${S.potions})`, () => {
              S.isDefending = false;
              S.potions--;
              let heal = 40;
              S.playerHp = Math.min(S.maxHp, S.playerHp + heal);
              pushLog(`💚 你嚼了一口檳榔，恢復了 ${heal} 點 HP！精神百倍！`);

              // Boss still attacks while you heal
              let bossDmg = 20 + Math.floor(Math.random() * 10);
              S.playerHp -= bossDmg;
              pushLog(`🩸 天王星趁隙攻擊，你受到了 ${bossDmg} 點傷害。`);

              if (S.playerHp <= 0) S.scene = "ending_alliance_solo_bad";
              render();
            }]);
          }
          break;

        case "battle_random":
          opts.push(["🗡️ 攻擊", () => {
            // Player hits monster
            let dmg = getPlayerAtk() + Math.floor(Math.random() * 4);
            S.monsterHp -= dmg;
            pushLog(`⚔️ 你擊中黑影，造成 ${dmg} 點傷害！`);
            triggerMonsterHitEffect();

            // Monster dies -> Reward and go back to map
            if (S.monsterHp <= 0) {
              let waxDrop = Math.floor(Math.random() * 2) + 1;
              let candleRestore = 15;
              let potionDrop = Math.random() < 0.2 ? 1 : 0;
              startVictoryPhase({
                enemyName: "徘徊的黑影",
                expGain: 20,
                waxGain: waxDrop,
                candleGain: candleRestore,
                potionGain: potionDrop,
              });
              return;
            }

            // Monster hits player
            let mDmg = Math.floor(Math.random() * 8) + 2;
            S.playerHp -= mDmg;
            pushLog(`🩸 黑影抓傷了你，受到 ${mDmg} 點傷害。`);

            if (S.playerHp <= 0) S.scene = "ending_alliance_solo_bad";
            render();
          }]);

          opts.push(["🏃 逃跑", () => {
            if (Math.random() < 0.6) {
              pushLog("💨 你成功甩開了黑影！");
              goto(`map${S.currentFloor}`);
            } else {
              let mDmg = Math.floor(Math.random() * 8) + 2;
              S.playerHp -= mDmg;
              pushLog(`🩸 逃跑失敗！黑影趁機攻擊，受到 ${mDmg} 點傷害。`);
              if (S.playerHp <= 0) S.scene = "ending_alliance_solo_bad";
              render();
            }
          }]);

          // Heal Option in Random Battle
          if (S.potions > 0) {
            opts.push([`💊 嚼一口急救檳榔 (剩餘: ${S.potions})`, () => {
              S.potions--;
              let heal = 40;
              S.playerHp = Math.min(S.maxHp, S.playerHp + heal);
              pushLog(`💚 你嚼了一口檳榔，恢復了 ${heal} 點 HP！`);
              if (audioEnabled) sfxHeal.play().catch(() => {});

              let mDmg = Math.floor(Math.random() * 8) + 2;
              S.playerHp -= mDmg;
              pushLog(`🩸 黑影趁隙攻擊，受到 ${mDmg} 點傷害。`);

              if (S.playerHp <= 0) S.scene = "ending_alliance_solo_bad";
              render();
            }]);
          }
          break;

        case "battle_farm":
          opts.push(["🗡️ 攻擊", () => {
            if (audioEnabled) sfxAttack.play().catch(() => {});

            let dmg = getPlayerAtk() + Math.floor(Math.random() * 5);
            S.monsterHp -= dmg;
            pushLog(`⚔️ 你擊中 ${S.monsterName}，造成 ${dmg} 點傷害！`);
            triggerMonsterHitEffect();

            if (S.monsterHp <= 0) {
              if (S.monsterName === "受害者的怨靈 米糕") {
                S.lowZoneKills = 0;
                pushLog("💀 你揮舞重鎚擊散了核心怨念，終於成功超渡了米糕的亡魂... 現場留下了大量遺物。");
                processVictory(100, 6, 2, 50);
                return;
              }

              if (S.monsterName === "【隱藏超魔王】狂暴艾莉卡") {
                S.highZoneKills = 0;
                pushLog("👑 奇蹟！你竟然憑藉驚人的毅力與戰術，擊敗了本遊戲的最強傳說──狂暴艾莉卡！");
                processVictory(400, 20, 5, 100);
                return;
              }

              if (S.farmZone === "low") {
                S.lowZoneKills++;
                pushLog(`📊 閱覽室淨化進度：${S.lowZoneKills}/10`);
              } else if (S.farmZone === "high") {
                S.highZoneKills++;
                pushLog(`📊 研究室淨化進度：${S.highZoneKills}/10`);
              }

              let exp = S.monsterMaxHp > 50 ? 30 : 10;
              let waxDrop = S.monsterMaxHp > 50 ? (Math.floor(Math.random() * 3) + 2) : 1;
              let candleRestore = S.monsterMaxHp > 50 ? 25 : 10;
              let potionDrop = (Math.random() < (S.monsterMaxHp / 200)) ? 1 : 0;

              pushLog(`🎉 戰鬥勝利！擊敗了 ${S.monsterName}。`);
              processVictory(exp, waxDrop, potionDrop, candleRestore);
              return;
            }

            render();
            setSceneUiInteractivity(false);
            setTimeout(() => {
              if (S.scene !== "battle_farm") {
                setSceneUiInteractivity(true);
                return;
              }

              let attackGif = "assets/mob_shadow.png";
              let animDuration = 800;

              if (S.monsterName.includes("米糕")) {
                attackGif = "assets/boss_migao_attack.gif";
                animDuration = 1000;
              } else if (S.monsterName.includes("艾莉卡")) {
                attackGif = "assets/boss_erica_attack.gif";
                animDuration = 1800;
              } else {
                attackGif = "assets/mob_attack.gif";
              }

              triggerMonsterAttackVisual(attackGif, animDuration);
              if (audioEnabled) {
                sfxMonsterHit.currentTime = 0;
                sfxMonsterHit.play().catch(() => {});
              }

              let mDmg = Math.floor(Math.random() * S.monsterAtk) + Math.floor(S.monsterAtk / 2);
              S.playerHp -= mDmg;
              pushLog(`🩸 ${S.monsterName} 反擊，你受到 ${mDmg} 點傷害。`);

              if (S.playerHp <= 0) S.scene = "ending_alliance_solo_bad";
              setSceneUiInteractivity(true);
              render();
            }, 300);
            return;
          }]);

          opts.push(["🏃 逃跑", () => {
            if (Math.random() < 0.7) {
              pushLog("💨 你趁隙逃出了房間！");
              S.farmZone = "";
              goto(`map${S.currentFloor}`);
            } else {
              let mDmg = S.monsterAtk;
              S.playerHp -= mDmg;
              pushLog(`🩸 逃跑失敗！被 ${S.monsterName} 追擊，受到 ${mDmg} 點傷害。`);
              if (S.playerHp <= 0) S.scene = "ending_alliance_solo_bad";
              render();
            }
          }]);

          // Heal Option in Farm Battle
          if (S.potions > 0) {
            opts.push([`💊 嚼一口急救檳榔 (剩餘: ${S.potions})`, () => {
              S.potions--;
              let heal = 40;
              S.playerHp = Math.min(S.maxHp, S.playerHp + heal);
              pushLog(`💚 你嚼了一口檳榔，恢復了 ${heal} 點 HP！精神百倍！`);
              if (audioEnabled) sfxHeal.play().catch(() => {});

              // Monster still attacks while you heal
              let mDmg = Math.floor(Math.random() * S.monsterAtk) + Math.floor(S.monsterAtk / 2);
              S.playerHp -= mDmg;
              pushLog(`🩸 ${S.monsterName} 趁隙攻擊，你受到了 ${mDmg} 點傷害。`);

              if (S.playerHp <= 0) S.scene = "ending_alliance_solo_bad";
              render();
            }]);
          }
          break;

        case "victory":
          opts.push(["✅ 繼續前進", () => {
            const returnScene = `map${S.currentFloor}`;
            S.lastVictory = null;
            goto(returnScene);
          }]);
          break;

        case "ending_bad":
        case "ending_bad_codefail":
        case "ending_bad_darkness":
        case "ending_normal":
          opts.push(["(察覺違和感) 等等……妳要不要打胰島素？", () => {
            pushLog("👁️ 脫口而出的一句話，打破了夢境的邏輯。");
            goto("python_hidden_start");
          }]);
          opts.push(["重新開始", () => {
            S = initialState();
            pushLog("♻ 已重新開始");
            render();
          }]);
          break;

        case "python_hidden_start":
          opts.push(["登入遊戲，前往倫敦尋找過去", () => {
            pushLog("🖥️ 你打開了《大航海時代Online》。");
            goto("python_hidden_london");
          }]);
          opts.push(["關閉遊戲，接受現實", () => {
            S = initialState();
            pushLog("♻ 遊戲已關閉。");
            render();
          }]);
          break;

        case "python_hidden_london":
          opts.push(["(進入工會據點) 接受艾蜜莉亞的身份", () => {
            pushLog("📜 你以艾蜜莉亞的身份進入了公會據點。");
            goto("amelia_hub");
          }]);
          opts.push(["(登出) 關閉客戶端", () => {
            S = initialState();
            pushLog("♻ 一切重新開始。");
            render();
          }]);
          break;

        // ── Amelia mode scenes ───────────────────────────────────────────────
        case "amelia_hub":
          opts.push(["前往閱覽室（幸運四葉草）", () => { advance(5, "進入閱覽室"); goto("amelia_reading_room"); }]);
          opts.push(["前往檔案室（艾莉卡）", () => { advance(5, "進入檔案室"); goto("amelia_archive_room"); }]);
          opts.push(["前往修復工坊（珊珊）", () => { advance(5, "進入修復工坊"); goto("amelia_workshop"); }]);
          opts.push(["前往會議室（塞特・傑克森馬吉斯）", () => { advance(5, "進入會議室"); goto("amelia_meeting_room"); }]);
          opts.push(["前往工會辦公室（紅花）", () => { advance(5, "前往工會辦公室"); goto("amelia_guild_office"); }]);
          opts.push(["（登出）關閉客戶端", () => { S = initialState(); pushLog("♻ 已登出。"); render(); }]);
          break;

        case "amelia_reading_room":
          if (!S.flags.ameliaTalkedClover) {
            opts.push(["和幸運四葉草聊香料群島路線", () => {
              S.flags.ameliaTalkedClover = true;
              addTrust(5, "和幸運四葉草聊了新賽季路線");
              pushLog("💬 幸運四葉草：香料群島海圖碎片線索，最後一片在馬六甲！");
              advance(10, "閒聊");
              render();
            }]);
          } else {
            opts.push(["✓ 幸運四葉草（已對話）繼續聊", () => { advance(5, "續聊"); render(); }]);
          }
          opts.push(["返回工會據點", () => goto("amelia_hub")]);
          break;

        case "amelia_archive_room": {
          const ericaFollowupReady = S.flags.ameliaTalkedClover && S.flags.ameliaTalkedJackson && !S.flags.ameliaEricaFollowup;
          if (!S.flags.ameliaTalkedErica) {
            opts.push(["聽艾莉卡說工會的故事", () => {
              S.flags.ameliaTalkedErica = true;
              addTrust(5, "了解工會的起源");
              pushLog("💬 艾莉卡：工會起源——三個水手服同好，就這樣成了夥伴");
              advance(10, "傾聽");
              render();
            }]);
          } else if (ericaFollowupReady) {
            opts.push(["艾莉卡有新話題（幸運＋傑克森資訊帶來的感觸）", () => {
              S.flags.ameliaEricaFollowup = true;
              addTrust(8, "艾莉卡說出了艦隊完整後的感觸");
              pushLog("💬 艾莉卡（後續）：三種職業、一個工會——完整的艦隊");
              advance(10, "傾聽");
              render();
            }]);
          } else {
            opts.push(["✓ 艾莉卡（已對話）繼續在書架旁坐一會", () => { advance(5, "靜坐"); render(); }]);
          }
          opts.push(["返回工會據點", () => goto("amelia_hub")]);
          break;
        }

        case "amelia_workshop":
          if (!S.flags.ameliaTalkedShanshan) {
            opts.push(["聽珊珊說倫敦教堂任務的事", () => {
              S.flags.ameliaTalkedShanshan = true;
              addTrust(5, "了解倫敦教堂隱藏任務鏈");
              pushLog("💬 珊珊：倫敦教堂隱藏任務需要水手＋海盜同時在場才能觸發");
              advance(10, "傾聽");
              render();
            }]);
          } else {
            opts.push(["✓ 珊珊（已對話）繼續整理攻略", () => { advance(5, "觀看"); render(); }]);
          }
          opts.push(["返回工會據點", () => goto("amelia_hub")]);
          break;

        case "amelia_meeting_room":
          if (!S.flags.ameliaTalkedJackson) {
            opts.push(["和傑克森馬吉斯聊航海戰術與情報", () => {
              S.flags.ameliaTalkedJackson = true;
              addTrust(5, "和傑克森聊了情報與海盜戰術");
              pushLog("💬 傑克森馬吉斯：情報才是海盜的核心；馬六甲海盜港位置確認");
              advance(10, "閒聊");
              render();
            }]);
          } else {
            opts.push(["✓ 傑克森（已對話）繼續聊航線", () => { advance(5, "續聊"); render(); }]);
          }
          if (!S.flags.ameliaTalkedShanshan) {
            opts.push(["塞特（🔒 先去修復工坊找珊珊才能解鎖）", () => {
              pushLog("💡 提示：先去修復工坊找珊珊聊聊，再回來找塞特。");
              render();
            }]);
          } else if (!S.flags.ameliaTalkedSeth) {
            opts.push(["向塞特詢問倫敦教堂任務的觸發條件", () => {
              S.flags.ameliaTalkedSeth = true;
              addTrust(8, "塞特分享了倫敦任務的秘密");
              pushLog("💬 塞特：午夜＋聖水＋舊錢幣→聖喬治畫後的古老海圖第一頁");
              advance(10, "傾聽");
              render();
            }]);
          } else {
            opts.push(["✓ 塞特（已對話）倫敦任務細節確認完畢", () => { advance(5, "閒聊"); render(); }]);
          }
          opts.push(["返回工會據點", () => goto("amelia_hub")]);
          break;

        case "amelia_guild_office": {
          const allTalked = S.flags.ameliaTalkedClover && S.flags.ameliaTalkedErica &&
                            S.flags.ameliaTalkedShanshan && S.flags.ameliaTalkedJackson &&
                            S.flags.ameliaTalkedSeth;
          if (S.flags.ameliaInsulinUnlocked) {
            opts.push(["💊 醒來", () => {
              pushLog("☀️ 你回到了現實。");
              goto("amelia_wakeup");
            }]);
          } else if (allTalked) {
            opts.push(["聽紅花說最後一句話……", () => {
              S.flags.ameliaInsulinUnlocked = true;
              addTrust(20, "紅花說出了那個詞");
              pushLog("💊 紅花提到「胰島素」——你應該醒來了");
              advance(5, "凝神");
              render();
            }]);
          } else {
            opts.push(["和紅花說說今天工會的狀況", () => { advance(5, "閒聊"); render(); }]);
          }
          opts.push(["返回工會據點", () => goto("amelia_hub")]);
          break;
        }

        case "amelia_wakeup":
          opts.push(["重新開始（回到序章）", () => { S = initialState(); pushLog("♻ 已重新開始"); render(); }]);
          opts.push(["回到工會據點（繼續遊戲）", () => goto("amelia_hub")]);
          break;

        case "desk":
          if (!S.clues.honghua) {
            S.clues.honghua = true;
            addTrust(12, "你認真讀完紅花筆記");
            pushLog("🧩 人物線索：紅花的案情紀錄");
          }
          opts.push(["返回 2F 地圖", () => goto("map2")]);
          break;
        case "window":
          if (!S.clues.amelia) {
            S.clues.amelia = true;
            addTrust(12, "你找到艾蜜莉亞字條");
            pushLog("🧩 人物線索：艾蜜莉亞失蹤原因");
          }
          opts.push(["返回 2F 地圖", () => goto("map2")]);
          break;
        case "bookshelves":
          BOOKSHELF_CORRECT_ORDER.forEach((book) => {
            opts.push([book, () => {
              if (S.booksOrder.length >= BOOKSHELF_REQUIRED_COUNT) {
                pushLog("ℹ️ 目前排序已滿，請清除後重新嘗試。");
                render();
                return;
              }
              S.booksOrder.push(book);
              if (S.booksOrder.length === BOOKSHELF_REQUIRED_COUNT) {
                const correct = BOOKSHELF_CORRECT_ORDER.every((v, idx) => S.booksOrder[idx] === v);
                if (correct) {
                  S.flags.basementOpen = true;
                  pushLog("🔑 取得地下密室鑰匙");
                } else {
                  S.booksOrder = [];
                  pushLog("❌ 順序錯誤，機關毫無反應。");
                }
              }
              render();
            }]);
          });
          if (S.booksOrder.length > 0) {
            opts.push(["清除目前排序", () => { S.booksOrder = []; render(); }]);
          }
          opts.push(["返回 1F 地圖", () => goto("map1")]);
          break;
        case "basement":
          if (S.evidence.hammer) {
            opts.push(["(使用生鏽鎚子) 暴力砸開儲藏室的暗鎖", () => {
              advance(15, "砸開鎖頭");
              goto("basementDeep");
            }]);
          } else {
            opts.push(["嘗試推開儲藏室的門", () => {
              advance(5, "推門");
              pushLog("🔒 門從裡面被鎖死了，需要某種堅硬的工具才能破壞。");
              render();
            }]);
          }
          opts.push(["離開地下區", () => { advance(8, "返回 1F"); goto("map1"); }]);
          break;
        case "basementDeep":
          if (!S.clues.starscream) {
            S.clues.starscream = true;
            S.flags.trueSong = true;
            addTrust(18, "你掌握天王星供詞與關鍵真相");
            pushLog("🧩 人物線索：天王星親筆供詞");
            pushLog("🎼 取得鎮魂歌譜");
          }
          opts.push(["返回 3F 面對紅花", () => { advance(20, "回到 3F"); goto("map3"); }]);
          break;
        default:
          opts.push(["重新開始", () => {
            S = initialState();
            pushLog("♻ 已重新開始");
            render();
          }]);
          break;
      }

      // --- GLOBAL MAP OPTIONS: Allow healing outside of battle ---
      if (MAP_SCENES.has(S.scene) && S.potions > 0 && S.playerHp < S.maxHp) {
        // Use unshift to place the heal button at the TOP of the options list
        opts.unshift([`💊 停下腳步吃一顆檳榔 (剩餘: ${S.potions}, 恢復 40 HP)`, () => {
          S.potions--;
          S.playerHp = Math.min(S.maxHp, S.playerHp + 40);
          pushLog(`💚 你在走廊上稍作休息，嚼了一口檳榔，恢復了 40 點 HP。`);
          if (audioEnabled && typeof sfxHeal !== "undefined") sfxHeal.play().catch(() => {});
          render();
        }]);
      }

      return opts;
    }

function endingCheck() {
      const e = evidenceCount();
      const c = clueCount();
      const t = S.trust;
      advance(5, "面對紅花");
      if (S.scene === "ending_bad_darkness") return;
      if (S.flags.trueSong && c === 3 && t >= 70) {
        S.scene = "ending_secret";
        pushLog("✅ 達成：秘密結局");
      } else if (S.flags.trueSong && t >= 45) {
        S.scene = "ending_true";
        pushLog("✅ 達成：真結局");
      } else if (e >= 2 && t >= 60) {
        S.scene = "alliance_followup";
        pushLog("🤝 紅花加入：解鎖同盟追兇分支");
      } else if (e >= 2) {
        S.scene = "ending_normal";
        pushLog("✅ 達成：普通結局");
      } else {
        S.scene = "ending_bad";
        pushLog("☠ 達成：壞結局");
      }
      render();
    }

function endingText() {
      switch (S.scene) {
        case "ending_secret":
          return "【秘密結局】\n你遞出鎮魂歌譜與完整人物線索。紅花第一次真正笑了。";
        case "ending_true":
          return "【真結局】\n你證明了案件的關鍵脈絡，紅花終於願意與你並肩作證。";
        case "ending_trust":
          return "【信任結局】\n證據未齊，但紅花選擇相信你的判斷。";
        case "ending_normal":
          return "【普通結局】\n你帶著部分物證離開，真相仍有缺口。";
        case "ending_bad":
          return "【壞結局】\n準備不足就面對紅花，對話在沉默中結束。";
        case "ending_bad_codefail":
          return "【壞結局 B】\n你在密碼盒前連續輸錯三次，暗鎖警報響起，調查被迫中止。";
        case "ending_bad_darkness":
          return formatTemplateText(TEXT_ARCHIVE["story_texts.py"].ENDING_BAD_DARKNESS);
        case "ending_killer_map":
          return "【壞結局】\n你試圖硬闖黑影，下一秒只剩走廊裡急促的腳步與熄滅的燭光。";
        case "ending_alliance_capture":
          return "【同盟追兇結局】\n你依線索帶紅花下到地下儲藏室，兇手果然仍在。\n紅花一拳擊倒對方，嫌犯供出：封閉房內有暗門直通館外，\n過往失蹤調查員都是被他誘入地下後殺害。\n收尾後你騎上 GP125，準時下班離開。";
        case "ending_alliance_solo_bad":
          return "【壞結局 · 單獨追兇】\n你帶著線索獨自闖入地下儲藏室。\n門後黑影早已等著你——下一秒，刀光落下。\n你終於明白，這條路本該和紅花一起走。";
        default:
          return "";
      }
    }
