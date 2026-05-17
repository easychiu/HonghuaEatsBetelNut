// --- Meta UI Function ---
    function applyMetaTheme(isMeta) {
      const root = document.documentElement;
      if (isMeta) {
        // 現代診間 / MMO 白光主題
        root.style.setProperty('--bg', '#f0f4f8');
        root.style.setProperty('--panel', '#ffffff');
        root.style.setProperty('--panel-2', '#e2e8f0');
        root.style.setProperty('--text', '#1a202c');
        root.style.setProperty('--muted', '#718096');
        root.style.setProperty('--line', '#cbd5e0');
        document.body.style.background = '#f0f4f8';
      } else {
        // 恢復 17 世紀古堡黑暗主題
        root.style.setProperty('--bg', '#0e0a12');
        root.style.setProperty('--panel', '#171121');
        root.style.setProperty('--panel-2', '#221a2f');
        root.style.setProperty('--text', '#d9d0c6');
        root.style.setProperty('--muted', '#9b8ead');
        root.style.setProperty('--line', '#3e3054');
        document.body.style.background = 'radial-gradient(1200px 600px at 10% -20%, #2a1f3b, transparent), var(--bg)';
      }
    }

    function archiveKeys(group) {
      return Object.keys(TEXT_ARCHIVE[group] || {}).sort();
    }

    function ensureArchiveState() {
      if (!S.archive || !TEXT_ARCHIVE[S.archive.group]) {
        S.archive = { group: "story_texts.py", key: null };
      }
      if (S.archive.key && !(S.archive.key in (TEXT_ARCHIVE[S.archive.group] || {}))) {
        S.archive.key = null;
      }
    }

    function formatTemplateText(raw) {
      if (typeof raw !== "string") {
        return JSON.stringify(raw, null, 2);
      }
      return raw.replaceAll("{hammer_length}", "30").replaceAll("{meeting_room_name}", "會議室");
    }

function openArchive() {
      ensureArchiveState();
      goto("archive_index");
    }

    let currentSceneOptionButtons = [];

    let S = initialState();
    document.documentElement.style.setProperty("--player-marker-duration", `${MARKER_MOVE_DURATION_MS}ms`);
    let hotspotMoveTimeoutId = null;
    let hotspotMoveToken = 0;

    function deepClone(obj) {
      if (typeof structuredClone === "function") return structuredClone(obj);
      return JSON.parse(JSON.stringify(obj));
    }

    function nowClock() {
      const total = GAME_START_HOUR * 60 + S.elapsed;
      const h = Math.floor((total % (24 * 60)) / 60);
      const m = total % 60;
      return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
    }

    function dangerOn() { return S.elapsed >= KILLER_EMERGE_ELAPSED; }

    function trustTier() {
      if (S.trust >= 60) return "high";
      if (S.trust >= 25) return "mid";
      return "low";
    }

    function isEndingOrHiddenScene(scene) {
      return scene.startsWith("ending_") || scene.startsWith("python_hidden_") || scene.startsWith("amelia_");
    }

    function clampCandle(value) {
      return Math.max(0, Math.min(MAX_CANDLE, Math.floor(value)));
    }

    function shouldTriggerDarknessEnding() {
      return S.candle === 0 && !isEndingOrHiddenScene(S.scene);
    }

    function scene1TimeOfDay() {
      const total = (GAME_START_HOUR * 60 + S.elapsed) % (24 * 60);
      const hour = Math.floor(total / 60);
      if (hour >= 6 && hour < 17) return "day";
      if (hour >= 17 && hour < 18) return "dusk";
      return "night";
    }

    const bgm = new Audio(BGM_MAIN);
    bgm.loop = true;
    bgm.volume = 0.45;

    const bgmEnd = new Audio(BGM_END);
    bgmEnd.loop = true;
    bgmEnd.volume = 0.45;

    const bgmBattle = new Audio(BGM_BATTLE);
    bgmBattle.loop = true;
    bgmBattle.volume = 0.45;
    const bgmBoss = new Audio(BGM_BOSS);
    bgmBoss.loop = true;
    bgmBoss.volume = 0.45;

    const sfxAttack = new Audio("assets/sfx_attack.mp3");
    const sfxHeal = new Audio("assets/sfx_heal.mp3");
    const sfxMonsterHit = new Audio("assets/sfx_monster.mp3");
    const victoryCueAudio = new Audio(BGM_END);
    victoryCueAudio.loop = false;
    victoryCueAudio.volume = 0.6;

    const ALL_BGMS = {
      [BGM_MAIN]: bgm,
      [BGM_END]: bgmEnd,
      [BGM_BATTLE]: bgmBattle,
      [BGM_BOSS]: bgmBoss,
    };

    let audioEnabled = false;
    let audioGestureBound = false;
    let monsterHitEffectTimer = null;
    let lastRenderedScene = null;

    function getMonsterImageSrc() {
      if (S.scene === "battle_starscream") return "assets/boss_starscream.png";

      const mName = S.lastVictory ? S.lastVictory.enemyName : S.monsterName;
      if (!mName) return "assets/mob_shadow.png";

      if (mName.includes("幽魂")) return "assets/mob_ghost.png";
      if (mName.includes("鎧甲")) return "assets/mob_armor.png";
      if (mName.includes("深淵守衛")) return "assets/mob_guard.png";
      if (mName.includes("米糕")) return "assets/boss_migao.png";
      if (mName.includes("艾莉卡")) return "assets/boss_erica.png";

      return "assets/mob_shadow.png";
    }

    function targetBgmForScene() {
      if (S.scene === "victory") return null; // Mute background music during victory fanfare
      if (S.scene.startsWith("battle_")) {
        const imgSrc = getMonsterImageSrc();
        if (imgSrc.includes("boss_")) return BGM_BOSS;
        return BGM_BATTLE;
      }
      return isEndingOrHiddenScene(S.scene) ? BGM_END : BGM_MAIN;
    }

    function updateAudioButton() {
      const btn = document.getElementById("audioBtn");
      btn.textContent = audioEnabled ? "🔊 音樂：開" : "🔈 音樂：關";
    }

    function triggerMonsterHitEffect() {
      const monsterEl = document.getElementById("monsterImg");
      const sceneEl = document.getElementById("sceneImg");
      const imgEl = monsterEl && monsterEl.style.display !== "none" ? monsterEl : sceneEl;
      
      if (!imgEl || imgEl.style.display === "none") return;
      
      if (audioEnabled && typeof sfxMonsterHit !== 'undefined') {
        sfxMonsterHit.currentTime = 0;
        sfxMonsterHit.play().catch(() => {});
      }
      
      imgEl.classList.remove("monster-hurt");
      void imgEl.offsetWidth;
      imgEl.classList.add("monster-hurt");
      
      if (monsterHitEffectTimer) clearTimeout(monsterHitEffectTimer);
      monsterHitEffectTimer = setTimeout(() => {
        if(imgEl) imgEl.classList.remove("monster-hurt");
        monsterHitEffectTimer = null;
      }, 300);
    }

    // Trigger player's attack effect (slash)
    function triggerPlayerAttackVisual() {
      const effectEl = document.getElementById("effectLayer");
      if (effectEl) {
        effectEl.src = "assets/slash_effect.gif?t=" + new Date().getTime();
        effectEl.style.maxWidth = "150px"; // Reset to slash size
        effectEl.style.height = "auto";
        effectEl.style.display = "block";
        setTimeout(() => { effectEl.style.display = "none"; }, 500);
      }
    }

    // Trigger monster's attack animation (GIF or Phantom Fallback)
    function triggerMonsterAttackVisual(attackImgSrc, durationMs = 800) {
      const monsterImgEl = document.getElementById("monsterImg");
      const mainCard = document.querySelector(".main");
      const effectEl = document.getElementById("effectLayer");

      // 1. Screen Shake
      if (mainCard) {
        mainCard.style.transform = "translateX(10px)";
        setTimeout(() => mainCard.style.transform = "translateX(-10px)", 50);
        setTimeout(() => mainCard.style.transform = "translateX(10px)", 100);
        setTimeout(() => mainCard.style.transform = "translateX(0)", 150);
      }

      // 2. Play GIF if provided
      if (attackImgSrc && attackImgSrc.endsWith(".gif")) {
        if (monsterImgEl && monsterImgEl.style.display !== "none") {
          const originalSrc = monsterImgEl.src;
          const cacheBuster = "?t=" + new Date().getTime();
          monsterImgEl.src = attackImgSrc + cacheBuster;

          setTimeout(() => {
            if (monsterImgEl.src.includes(attackImgSrc)) {
               monsterImgEl.src = originalSrc;
            }
          }, durationMs);
        }
      } else {
        // 3. Phantom Red Strike Fallback (If no GIF)
        if (monsterImgEl && effectEl && monsterImgEl.style.display !== "none") {
          effectEl.src = monsterImgEl.src; // Copy monster image
          effectEl.style.maxWidth = "none";
          effectEl.style.height = monsterImgEl.clientHeight + "px"; 
          effectEl.style.display = "block";
          
          effectEl.classList.add("phantom-strike-anim");
          
          setTimeout(() => {
            effectEl.classList.remove("phantom-strike-anim");
            effectEl.style.display = "none";
            effectEl.style.maxWidth = "150px"; // Restore slash size
            effectEl.style.height = "auto";
          }, 400);
        }
      }
    }

    function battleMonsterAltText() {
      if (S.scene === "victory") return `勝利演出角色：${S.lastVictory?.enemyName || "敵人"}`;
      if (S.scene === "battle_farm") return `戰鬥敵人：${S.monsterName || "敵人"}`;
      return `戰鬥敵人：${BATTLE_ENEMY_CONFIG[S.scene]?.name || "敵人"}`;
    }

    function playVictoryCue() {
      if (!audioEnabled) return;
      victoryCueAudio.currentTime = 0;
      victoryCueAudio.play().catch(() => {});
    }

    function tryPlayBgm() {
      if (!audioEnabled) return;
      const target = targetBgmForScene();
      const targetAudio = ALL_BGMS[target];
      if (!targetAudio) return;
      const playPromise = targetAudio.play();
      if (playPromise && typeof playPromise.catch === "function") {
        playPromise.catch(() => {});
      }
    }

    function syncBgmTrack() {
      const target = targetBgmForScene();

      Object.entries(ALL_BGMS).forEach(([src, audio]) => {
        if (src !== target && !audio.paused) {
          audio.pause();
          audio.currentTime = 0;
        }
      });

      if (target && audioEnabled) {
        const targetAudio = ALL_BGMS[target];
        if (targetAudio && targetAudio.paused) {
          targetAudio.play().catch(() => {});
        }
      }
    }

    function bindAudioGesture() {
      if (audioGestureBound) return;
      audioGestureBound = true;
      const resume = () => {
        if (audioEnabled) tryPlayBgm();
      };
      window.addEventListener("pointerdown", resume, { once: true });
      window.addEventListener("keydown", resume, { once: true });
    }

    function toggleAudio() {
      audioEnabled = !audioEnabled;
      if (audioEnabled) {
        syncBgmTrack();
        bindAudioGesture();
        tryPlayBgm();
        pushLog("🔊 背景音樂已開啟");
      } else {
        victoryCueAudio.pause();
        victoryCueAudio.currentTime = 0;
        Object.values(ALL_BGMS).forEach(audio => audio.pause());
        pushLog("🔈 背景音樂已關閉");
      }
      updateAudioButton();
      render();
    }

    function scene1TrustState() {
      if (S.trust >= 75) return "trusted";
      if (S.trust >= 50) return "friendly";
      if (S.trust >= 25) return "peaceful";
      return "impatient";
    }

    function scene1ImageCandidates() {
      const tod = scene1TimeOfDay();
      const trust = scene1TrustState();
      return [
        `${SCENE1_ASSETS}honghua_look_${tod}_${trust}.png`,
        `${SCENE1_ASSETS}honghua_look_${tod}.png`,
        `${SCENE1_ASSETS}honghua_look_day.png`,
        "assets/scenes/prologue.png",   
      ];
    }

    function tryImageFallbacks(imgEl, candidates, idx) {
      if (idx >= candidates.length) return;
      imgEl.onerror = () => tryImageFallbacks(imgEl, candidates, idx + 1);
      imgEl.src = candidates[idx];
    }

    function evidenceCount() {
      return Object.values(S.evidence).filter(Boolean).length;
    }

    function clueCount() {
      return Object.values(S.clues).filter(Boolean).length;
    }

    function pushLog(text) {
      S.log.push(text);
      if (S.log.length > MAX_LOG_ENTRIES) S.log = S.log.slice(-MAX_LOG_ENTRIES);
    }

    function advance(minutes, reason) {
      S.elapsed += minutes;
      
      // 紅花隨行會使燭火消耗減半
      let drain = Math.floor(minutes * CANDLE_DRAIN_PER_MINUTE);
      if (S.flags.honghuaJoined) drain = Math.floor(drain / 2);
      
      S.candle = clampCandle(S.candle - drain);
      if (reason) pushLog(`⏱ +${minutes} 分鐘：${reason}`);
      if (shouldTriggerDarknessEnding()) {
        goto("ending_bad_darkness");
        pushLog("🕯️ 燭火熄滅，黑暗吞噬了你。");
      }
    }

    function addTrust(v, reason) {
      const next = Math.max(0, Math.min(100, S.trust + v));
      const diff = next - S.trust;
      S.trust = next;
      if (diff !== 0 && reason) pushLog(`💫 信任度 ${diff > 0 ? "+" : ""}${diff}：${reason}`);
    }

    function goto(scene) {
      if (
        S.candle === 0 &&
        S.scene === "ending_bad_darkness" &&
        !isEndingOrHiddenScene(scene)
      ) {
        render();
        return;
      }
      S.scene = scene;
      if (scene === "map1") S.currentFloor = 1;
      if (scene === "map2") S.currentFloor = 2;
      if (scene === "map3") S.currentFloor = 3;
      render();
    }

    function getPlayerAtk() {
      let atk = S.playerBaseAtk;
      if (S.evidence.hammer) atk += 15; // 30cm 生鏽鐵鎚的加成
      return atk;
    }

    function applyExpAndLevel(expGain) {
      const gain = Math.max(0, Math.floor(expGain || 0));
      S.exp += gain;
      let levelUps = 0;
      while (S.exp >= S.expNext) {
        S.exp -= S.expNext;
        S.level += 1;
        levelUps += 1;
        S.maxHp += LEVEL_UP_HP_GAIN;
        S.playerBaseAtk += LEVEL_UP_ATK_GAIN;
        S.playerHp = S.maxHp;
        S.expNext = Math.floor(S.expNext * EXP_NEXT_MULTIPLIER);
      }
      return { gain, levelUps };
    }

    function startVictoryPhase({ enemyName, expGain, waxGain, candleGain, potionGain }) {
      const safeWaxGain = Math.max(0, Math.floor(waxGain || 0));
      const safeCandleGain = Math.max(0, Math.floor(candleGain || 0));
      const safePotionGain = Math.max(0, Math.floor(potionGain || 0));
      const levelResult = applyExpAndLevel(expGain);
      S.wax += safeWaxGain;
      S.candle = Math.min(MAX_CANDLE, S.candle + safeCandleGain);
      S.potions += safePotionGain;
      S.lastVictory = {
        enemyName: enemyName || "敵人",
        expGain: levelResult.gain,
        waxGain: safeWaxGain,
        candleGain: safeCandleGain,
        potionGain: safePotionGain,
        levelUps: levelResult.levelUps,
      };
      goto("victory");
    }

    function processVictory(expGain, waxGain, potionGain, candleGain) {
      S.farmZone = "";
      startVictoryPhase({
        enemyName: S.monsterName,
        expGain,
        waxGain,
        candleGain,
        potionGain,
      });
    }

    function tryFloorTransition(targetFloor, minutes, reason) {
      advance(minutes, reason);
      S.currentFloor = targetFloor;

      // 1. Check for Stalker (original logic)
      if (S.elapsed > STALKER_ENCOUNTER_ELAPSED && Math.random() < STALKER_ENCOUNTER_CHANCE) {
        goto("killer_encounter");
        return;
      }

      // 2. 20% chance for random encounter (shadow monster)
      if (Math.random() < 0.20 && !isEndingOrHiddenScene(S.scene)) {
        S.monsterHp = 40;
        S.monsterMaxHp = 40;
        pushLog("⚠️ 感覺到黑暗中有東西靠近... 進入戰鬥！");
        goto("battle_random");
        return;
      }

      goto(`map${targetFloor}`);
    }

    function normalizeAnswer(ans) {
      return String(ans || "").trim().replace(/\s+/g, "");
    }

    function startDeductionQuiz() {
      for (let i = 0; i < DEDUCTION_QUESTIONS.length; i += 1) {
        const { question, answer } = DEDUCTION_QUESTIONS[i];
        const input = prompt(question);
        if (input === null) {
          pushLog("📝 你暫停了推理。");
          goto("map3");
          return;
        }
        if (normalizeAnswer(input) !== normalizeAnswer(answer)) {
          pushLog(`❌ 推理中斷：第 ${i + 1} 題答案不正確。`);
          goto("map3");
          return;
        }
      }
      S.flags.deductionComplete = true;
      pushLog("🧠 推理完成：你整理出完整案件邏輯。");
      goto("confront");
    }

    function clickOptionByMatch(match) {
      const buttons = currentSceneOptionButtons;
      const normalize = (text) => (text || "").trim();
      const exact = buttons.find((b) => normalize(b.textContent) === match);
      if (exact) {
        exact.click();
        return true;
      }
      const starts = buttons.filter((b) => normalize(b.textContent).startsWith(match));
      if (starts.length === 1) {
        starts[0].click();
        return true;
      }
      const includes = buttons.filter((b) => normalize(b.textContent).includes(match));
      if (includes.length === 1) {
        includes[0].click();
        return true;
      }
      return false;
    }

    function setSceneUiInteractivity(enabled) {
      const pointerEvents = enabled ? "auto" : "none";
      document.getElementById("sceneHotspots").style.pointerEvents = pointerEvents;
      document.getElementById("options").style.pointerEvents = pointerEvents;
    }

    function renderHotspots() {
      const wrap = document.getElementById("sceneHotspots");
      wrap.innerHTML = "";
      const imgSrc = SCENE_IMAGES[S.scene] || "";
      const defs = SCENE_HOTSPOTS[S.scene] || [];
      if (!imgSrc || !defs.length) {
        wrap.style.display = "none";
        return;
      }
      wrap.style.display = "block";
      defs.forEach((hotspot) => {
        if (typeof hotspot.visibleWhen === "function" && !hotspot.visibleWhen(S)) return;
        const [left, top, width, height] = hotspot.rect;
        const hotspotBtn = document.createElement("button");
        hotspotBtn.type = "button";
        hotspotBtn.className = "scene-hotspot";
        hotspotBtn.textContent = hotspot.label;
        hotspotBtn.title = hotspot.label;
        hotspotBtn.setAttribute("aria-label", `互動：${hotspot.label}`);
        hotspotBtn.style.left = `${left}%`;
        hotspotBtn.style.top = `${top}%`;
        hotspotBtn.style.width = `${width}%`;
        hotspotBtn.style.height = `${height}%`;
        hotspotBtn.onclick = () => {
          // Calculate the center of the clicked hotspot (percentage coordinates)
          const centerX = left + (width / 2);
          const centerY = top + (height / 2);
          const previousPlayerX = S.playerX;
          const previousPlayerY = S.playerY;

          if (S.flags.honghuaJoined) {
            S.honghuaX = previousPlayerX;
            S.honghuaY = previousPlayerY;
            const honghuaMarker = document.getElementById("honghuaMarker");
            honghuaMarker.style.left = `${S.honghuaX}%`;
            honghuaMarker.style.top = `${S.honghuaY}%`;
          }

          // Update state and marker position
          // We store target coordinates immediately so save/load reflects the player's intended destination.
          S.playerX = centerX;
          S.playerY = centerY;
          const marker = document.getElementById("playerMarker");
          marker.style.left = `${centerX}%`;
          marker.style.top = `${centerY}%`;
          const sceneAtClick = S.scene;
          const moveToken = ++hotspotMoveToken;

          // Disable UI during movement to prevent double-clicking
          setSceneUiInteractivity(false);
          if (hotspotMoveTimeoutId !== null) {
            clearTimeout(hotspotMoveTimeoutId);
          }

          // Wait for the CSS transition to finish before triggering the scene logic
          hotspotMoveTimeoutId = setTimeout(() => {
            hotspotMoveTimeoutId = null;
            if (moveToken !== hotspotMoveToken || S.scene !== sceneAtClick) {
              return;
            }
            setSceneUiInteractivity(true);
            if (!clickOptionByMatch(hotspot.match)) {
              pushLog(`⚠ 互動區「${hotspot.label}」暫時無法使用，請改用按鈕選項。`);
              render();
            }
          }, MARKER_MOVE_DURATION_MS);
        };
        wrap.appendChild(hotspotBtn);
      });
    }

    function render() {
      // --- 套用 Meta UI 視覺主題 ---
      applyMetaTheme(isEndingOrHiddenScene(S.scene) && !S.scene.includes("darkness") && !S.scene.includes("killer"));

      // --- 網路不穩 / PING 999 視覺特效 ---
      const clockEl = document.getElementById("clock");
      if (S.scene === "ending_bad" || S.scene === "ending_normal" || S.scene === "ending_bad_codefail") {
        clockEl.textContent = Math.random() > 0.5 ? "PING: 999ms" : "伺服器連線不穩";
        clockEl.style.color = "#d77777";
      } else {
        clockEl.textContent = nowClock();
        clockEl.style.color = "";
      }

      document.getElementById("dangerState").innerHTML = dangerOn()
        ? '<span class="danger">危險（2AM 後）</span>'
        : "一般";
      document.getElementById("candleText").textContent = `${S.candle}/${MAX_CANDLE}`;
      document.getElementById("candleBar").style.width = `${S.candle}%`;
      document.getElementById("candleBar").setAttribute("aria-valuenow", String(S.candle));
      document.getElementById("trustText").textContent = `${S.trust}/100`;
      document.getElementById("trustBar").style.width = `${S.trust}%`;
      document.getElementById("evidenceText").textContent = `${evidenceCount()}/3`;
      document.getElementById("clueText").textContent = `${clueCount()}/3`;

      const evidenceNames = [["hammer", "生鏽鎚子"], ["clover", "四葉草"], ["jeans", "YV 牛仔褲"]];
      const clueNames = [["honghua", "紅花筆記"], ["amelia", "艾蜜莉亞字條"], ["starscream", "天王星供詞"]];
      document.getElementById("evidenceChips").innerHTML =
        evidenceNames.filter(([k]) => S.evidence[k]).map(([, n]) => `<span class="chip">${n}</span>`).join("") || '<span class="chip">尚未取得</span>';
      document.getElementById("clueChips").innerHTML =
        clueNames.filter(([k]) => S.clues[k]).map(([, n]) => `<span class="chip">${n}</span>`).join("") || '<span class="chip">尚未取得</span>';

      const isEnding = S.scene.startsWith("ending_");
      const inArchive = S.scene.startsWith("archive_");
      const isAmelia = S.scene.startsWith("amelia_");
      const isHidden = S.scene.startsWith("python_hidden_") || isAmelia;
      const isBattle = S.scene.startsWith("battle_");
      const mainEl = document.querySelector(".main");
      if (mainEl) mainEl.classList.toggle("battle-mode", isBattle);
      if (mainEl) mainEl.classList.toggle("victory-mode", S.scene === "victory");

      document.getElementById("sceneName").textContent =
        (isEnding || isHidden) ? "ENDING" : (inArchive ? "TEXT ARCHIVE" : (SCENE_DISPLAY_NAMES[S.scene] || S.scene.toUpperCase()));

      const imgEl = document.getElementById("sceneImg");
      const monsterEl = document.getElementById("monsterImg");
      if (SCENE1_SCENES.has(S.scene)) {
        imgEl.style.display = "block";
        tryImageFallbacks(imgEl, scene1ImageCandidates(), 0);
      } else {
        imgEl.onerror = null;
        const imgSrc = SCENE_IMAGES[S.scene] || "";
        imgEl.src = imgSrc;
        imgEl.style.display = imgSrc ? "block" : "none";
      }
      imgEl.alt = SCENE_ALT_TEXTS[S.scene] || `${S.scene.toUpperCase()} 場景`;
      const mapViewport = MAP_SCENE_VIEWPORTS[S.scene];
      if (mapViewport) {
        imgEl.style.objectPosition = mapViewport.objectPosition;
        imgEl.style.transform = `scale(${mapViewport.scale})`;
      } else {
        imgEl.style.objectPosition = "50% 50%";
        imgEl.style.transform = "scale(1)";
      }
      if (monsterEl) {
        const showMonsterLayer = isBattle || S.scene === "victory";
        if (showMonsterLayer) {
          monsterEl.onerror = () => {
            monsterEl.onerror = null;
            monsterEl.src = "assets/mob_shadow.png";
          };
          monsterEl.style.display = "block";
          imgEl.style.filter = `brightness(${BATTLE_BACKGROUND_BRIGHTNESS})`;
          monsterEl.src = getMonsterImageSrc();
          monsterEl.alt = battleMonsterAltText();
        } else {
          monsterEl.style.display = "none";
          imgEl.style.filter = "none";
          monsterEl.removeAttribute("src");
          monsterEl.alt = "";
        }
      }
      const effectEl = document.getElementById("effectLayer");
      if (effectEl) {
        if (!isBattle) {
          effectEl.classList.remove("active");
          effectEl.classList.remove("phantom-strike-anim");
          effectEl.style.display = "none";
          effectEl.removeAttribute("src");
        }
      }
      const sceneEl = document.getElementById("sceneText");
      if (isEnding) {
        sceneEl.innerHTML = `<span class="ending">${endingText()}</span>`;
      } else if (isHidden) {
        sceneEl.innerHTML = `<span class="ending" style="color: #1a202c; font-weight: bold;">${sceneText(S.scene)}</span>`;
      } else {
        sceneEl.textContent = sceneText(S.scene);
      }
      const safeHp = Number.isFinite(S.playerHp) ? S.playerHp : 0;
      const safeMaxHp = Number.isFinite(S.maxHp) ? S.maxHp : 100;
      const safeWax = Number.isFinite(S.wax) ? S.wax : 0;
      const safePotions = Number.isFinite(S.potions) ? S.potions : 0;
      const safeBossHp = Number.isFinite(S.bossHp) ? Math.max(0, S.bossHp) : 0;
      const safeBossMaxHp = Number.isFinite(S.bossMaxHp) ? S.bossMaxHp : 150;
      const safeMonsterHp = Number.isFinite(S.monsterHp) ? Math.max(0, S.monsterHp) : 0;
      const safeMonsterMaxHp = Number.isFinite(S.monsterMaxHp) ? S.monsterMaxHp : 0;
      const safeLevel = Number.isFinite(S.level) ? Math.max(1, Math.floor(S.level)) : 1;
      const safeExp = Number.isFinite(S.exp) ? Math.max(0, Math.floor(S.exp)) : 0;
      const safeExpNext = Number.isFinite(S.expNext) ? Math.max(1, Math.floor(S.expNext)) : 50;
      document.getElementById("statusLine").innerHTML = inArchive
        ? "完整文本檔案庫：已將 story_texts.py / character_texts.py 內嵌到單一 HTML（可離線瀏覽）"
        : `<strong>🎖️ Lv: ${safeLevel} (EXP: ${safeExp}/${safeExpNext}) &nbsp;|&nbsp; ❤️ HP: ${safeHp} / ${safeMaxHp} &nbsp;|&nbsp; 🕯️ 殘蠟: ${safeWax} &nbsp;|&nbsp; 💊 檳榔: ${safePotions}</strong>`;
      const battleStatusWindowEl = document.getElementById("battleStatusWindow");
      if (isBattle) {
        const enemyHpPools = {
          boss: { hp: safeBossHp, maxHp: safeBossMaxHp },
          monster: { hp: safeMonsterHp, maxHp: safeMonsterMaxHp },
        };
        const enemyConfig = BATTLE_ENEMY_CONFIG[S.scene] || DEFAULT_BATTLE_ENEMY_CONFIG;
        const enemyPool = enemyHpPools[enemyConfig.hpPool] || enemyHpPools.monster;
        const enemyName = S.scene === "battle_farm" ? (S.monsterName || enemyConfig.name) : enemyConfig.name;
        const enemyStatus = `👹 ${enemyName} HP: ${enemyPool.hp} / ${enemyPool.maxHp}`;
        battleStatusWindowEl.replaceChildren();
        [`❤️ HP ${safeHp}/${safeMaxHp}`, `💊 檳榔 ${safePotions}`, enemyStatus].forEach((line) => {
          const lineEl = document.createElement("div");
          lineEl.textContent = line;
          battleStatusWindowEl.appendChild(lineEl);
        });
        battleStatusWindowEl.style.display = "block";
      } else {
        battleStatusWindowEl.style.display = "none";
        battleStatusWindowEl.replaceChildren();
      }

      const optionsEl = document.getElementById("options");
      optionsEl.innerHTML = "";
      const opts = makeOptions();
      opts.forEach(([label, fn]) => {
        const b = document.createElement("button");
        b.textContent = label;
        b.onclick = fn;
        optionsEl.appendChild(b);
      });
      if (isEnding) {
        const restart = document.createElement("button");
        restart.textContent = "重新開始";
        restart.onclick = () => { S = initialState(); render(); };
        optionsEl.appendChild(restart);
      }
      setSceneUiInteractivity(true);
      currentSceneOptionButtons = [...optionsEl.querySelectorAll("button")];
      renderHotspots();
      syncBgmTrack();
      if (S.scene === "victory" && lastRenderedScene !== "victory" && audioEnabled) {
        playVictoryCue();
      }
      lastRenderedScene = S.scene;
      updateAudioButton();
      const marker = document.getElementById("playerMarker");
      const honghuaMarker = document.getElementById("honghuaMarker");
      marker.classList.toggle("is-amelia", isAmelia);
      if (MAP_SCENES.has(S.scene)) {
        marker.style.display = "block";
        marker.style.left = `${S.playerX}%`;
        marker.style.top = `${S.playerY}%`;
        if (S.flags.honghuaJoined) {
          honghuaMarker.style.display = "block";
          honghuaMarker.style.left = `${S.honghuaX}%`;
          honghuaMarker.style.top = `${S.honghuaY}%`;
        } else {
          honghuaMarker.style.display = "none";
        }
      } else {
        marker.style.display = "none";
        honghuaMarker.style.display = "none";
      }

      document.getElementById("log").innerHTML = S.log.map(x => `<div>${x}</div>`).join("");
    }

    function normalizeLoadedState(state) {
      const merged = deepClone(initialState());
      Object.assign(merged, state || {});
      merged.evidence = Object.assign({}, DEFAULT_EVIDENCE, state?.evidence || {});
      merged.clues = Object.assign({}, DEFAULT_CLUES, state?.clues || {});
      merged.flags = Object.assign({}, DEFAULT_FLAGS, state?.flags || {});
      merged.archive = Object.assign({}, DEFAULT_ARCHIVE, state?.archive || {});
      if (typeof merged.candle !== "number" || Number.isNaN(merged.candle)) merged.candle = MAX_CANDLE;
      merged.candle = clampCandle(merged.candle);
      if (!Array.isArray(merged.log)) merged.log = [DEFAULT_LOG_MESSAGE];
      if (!Array.isArray(merged.booksOrder)) merged.booksOrder = [];
      if (typeof merged.passwordFails !== "number") merged.passwordFails = 0;
      if (!VALID_FLOORS.includes(merged.currentFloor)) merged.currentFloor = 3;
      if (!Number.isFinite(merged.playerX)) merged.playerX = DEFAULT_PLAYER_X;
      if (!Number.isFinite(merged.playerY)) merged.playerY = DEFAULT_PLAYER_Y;
      if (!Number.isFinite(merged.honghuaX)) merged.honghuaX = DEFAULT_HONGHUA_X;
      if (!Number.isFinite(merged.honghuaY)) merged.honghuaY = DEFAULT_HONGHUA_Y;
      if (!Number.isFinite(merged.playerHp)) merged.playerHp = 100;
      if (!Number.isFinite(merged.maxHp)) merged.maxHp = 100;
      if (!Number.isFinite(merged.playerBaseAtk)) merged.playerBaseAtk = 10;
      if (!Number.isFinite(merged.potions)) merged.potions = 3;
      if (!Number.isFinite(merged.wax)) merged.wax = 0;
      if (!Number.isFinite(merged.bossHp)) merged.bossHp = 150;
      if (!Number.isFinite(merged.bossMaxHp)) merged.bossMaxHp = 150;
      if (typeof merged.isDefending !== "boolean") merged.isDefending = false;
      if (!Number.isFinite(merged.monsterHp)) merged.monsterHp = 0;
      if (!Number.isFinite(merged.monsterMaxHp)) merged.monsterMaxHp = 0;
      if (!Number.isFinite(merged.monsterAtk)) merged.monsterAtk = 0;
      if (typeof merged.monsterName !== "string") merged.monsterName = "敵人";
      if (typeof merged.farmZone !== "string") merged.farmZone = "";
      if (!Number.isFinite(merged.lowZoneKills)) merged.lowZoneKills = 0;
      if (!Number.isFinite(merged.highZoneKills)) merged.highZoneKills = 0;
      if (!Number.isFinite(merged.level)) merged.level = 1;
      if (!Number.isFinite(merged.exp)) merged.exp = 0;
      if (!Number.isFinite(merged.expNext)) merged.expNext = 50;
      merged.level = Math.max(1, Math.floor(merged.level));
      merged.exp = Math.max(0, Math.floor(merged.exp));
      merged.expNext = Math.max(1, Math.floor(merged.expNext));
      if (merged.lastVictory && typeof merged.lastVictory !== "object") merged.lastVictory = null;
      return merged;
    }

    function saveGame() {
      const data = { version: SAVE_VERSION, state: S };
      localStorage.setItem(SAVE_KEY, JSON.stringify(data));
      pushLog("💾 已儲存至瀏覽器 localStorage");
      render();
    }

    function loadGame() {
      const raw = localStorage.getItem(SAVE_KEY);
      if (!raw) {
        pushLog("⚠ 找不到存檔");
        render();
        return;
      }
      try {
        const data = JSON.parse(raw);
        if (!data || typeof data !== "object") {
          pushLog("⚠ 存檔格式錯誤，已忽略");
          render();
          return;
        }
        if (data.version !== SAVE_VERSION) {
          pushLog(`⚠ 存檔版本不相容（存檔:${data.version}｜當前:${SAVE_VERSION}），已忽略`);
          render();
          return;
        }
        if (!data.state || typeof data.state !== "object") {
          pushLog("⚠ 存檔缺少遊戲狀態資料，已忽略");
          render();
          return;
        }
        S = normalizeLoadedState(data.state);
        pushLog("📂 已載入存檔");
      } catch (err) {
        pushLog(`⚠ 存檔損毀，無法載入（${err?.message || "未知錯誤"}）`);
      }
      render();
    }

    document.getElementById("saveBtn").onclick = saveGame;
    document.getElementById("loadBtn").onclick = loadGame;
    document.getElementById("archiveBtn").onclick = () => {
      pushLog("📚 開啟全內容文字庫");
      openArchive();
    };
    document.getElementById("audioBtn").onclick = toggleAudio;
    document.getElementById("resetBtn").onclick = () => {
      S = initialState();
      pushLog("♻ 已重新開始");
      render();
    };

    render();
