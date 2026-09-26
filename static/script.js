/* ==========================================================
   ԿիբեռՎահան — Ինտերակտիվ Սկրիպտներ
   ========================================================== */

const T = window.TRANSLATIONS || {};
let soundEnabled = localStorage.getItem('sound') !== 'off';

// ---------- ԹԵՄԱ ----------
const themeBtn = document.getElementById('theme-toggle');
if (themeBtn) {
    if (localStorage.getItem('theme') === 'light') {
        document.body.classList.add('light-mode');
        themeBtn.textContent = '☀️';
    }
    themeBtn.addEventListener('click', () => {
        document.body.classList.toggle('light-mode');
        const isLight = document.body.classList.contains('light-mode');
        localStorage.setItem('theme', isLight ? 'light' : 'dark');
        themeBtn.textContent = isLight ? '☀️' : '🌙';
    });
}

// ---------- ՁԱՅՆ ----------
const soundBtn = document.getElementById('sound-toggle');
if (soundBtn) {
    soundBtn.textContent = soundEnabled ? '🔊' : '🔇';
    soundBtn.addEventListener('click', () => {
        soundEnabled = !soundEnabled;
        localStorage.setItem('sound', soundEnabled ? 'on' : 'off');
        soundBtn.textContent = soundEnabled ? '🔊' : '🔇';
        if (soundEnabled) playSound('tick');
    });
}

// Web Audio API-ով ձայներ
let audioCtx = null;
function playSound(type) {
    if (!soundEnabled) return;
    try {
        if (!audioCtx) {
            const AC = window.AudioContext || window.webkitAudioContext;
            audioCtx = new AC();
        }
        if (audioCtx.state === 'suspended') audioCtx.resume();

        if (type === 'correct') {
            // Երկու բարձր նոտա՝ ուրախ
            [659, 880].forEach((freq, i) => {
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.connect(gain); gain.connect(audioCtx.destination);
                osc.frequency.value = freq;
                osc.type = 'sine';
                const t = audioCtx.currentTime + i * 0.1;
                gain.gain.setValueAtTime(0.15, t);
                gain.gain.exponentialRampToValueAtTime(0.001, t + 0.25);
                osc.start(t); osc.stop(t + 0.25);
            });
        } else if (type === 'wrong') {
            // Ցածր բզզոց
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain); gain.connect(audioCtx.destination);
            osc.frequency.setValueAtTime(220, audioCtx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(110, audioCtx.currentTime + 0.3);
            osc.type = 'sawtooth';
            gain.gain.setValueAtTime(0.15, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.4);
            osc.start(); osc.stop(audioCtx.currentTime + 0.4);
        } else if (type === 'tick') {
            // Կարճ կտտոց
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain); gain.connect(audioCtx.destination);
            osc.frequency.value = 1200;
            osc.type = 'square';
            gain.gain.setValueAtTime(0.06, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.06);
            osc.start(); osc.stop(audioCtx.currentTime + 0.06);
        } else if (type === 'complete') {
            // Երեք նոտաների մեղեդի
            [523, 659, 784].forEach((freq, i) => {
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.connect(gain); gain.connect(audioCtx.destination);
                osc.frequency.value = freq;
                osc.type = 'sine';
                const t = audioCtx.currentTime + i * 0.15;
                gain.gain.setValueAtTime(0.15, t);
                gain.gain.exponentialRampToValueAtTime(0.001, t + 0.25);
                osc.start(t); osc.stop(t + 0.25);
            });
        } else if (type === 'hover') {
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain); gain.connect(audioCtx.destination);
            osc.frequency.value = 800;
            osc.type = 'sine';
            gain.gain.setValueAtTime(0.03, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.04);
            osc.start(); osc.stop(audioCtx.currentTime + 0.04);
        }
    } catch (e) {
        console.warn('Ձայնի սխալ:', e);
    }
}

// ---------- Բջջային ՄԵՆՅՈՒ ----------
const hamburger = document.getElementById('hamburger');
const navMenu = document.getElementById('navMenu');
if (hamburger && navMenu) {
    hamburger.addEventListener('click', () => navMenu.classList.toggle('active'));
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => navMenu.classList.remove('active'));
    });
}

// ==========================================================
//   ՎԻԿՏՈՐԻՆԱՅԻ ՀԱՄԱԿԱՐԳ
// ==========================================================
const startScreen = document.getElementById('start-screen');
if (startScreen) {
    let selectedDifficulty = null;
    let playerName = '';
    let questions = [];
    let currentIndex = 0;
    let score = 0;
    let correctCount = 0;
    let totalTimeSpent = 0;
    let questionStartTime = 0;
    let timerInterval = null;
    let timeRemaining = 0;
    let levelConfig = {};

    const gameScreen = document.getElementById('game-screen');
    const resultScreen = document.getElementById('result-screen');
    const playerNameInput = document.getElementById('player-name');
    const startBtn = document.getElementById('start-btn');
    const displayName = document.getElementById('display-name');
    const playerAvatar = document.getElementById('player-avatar');
    const currentDiffBadge = document.getElementById('current-difficulty');
    const questionCard = document.getElementById('question-card');
    const questionText = document.getElementById('question-text');
    const optionsContainer = document.getElementById('options-container');
    const inlineResult = document.getElementById('quiz-result');
    const progressFill = document.getElementById('progressFill');
    const progressPercent = document.getElementById('progress-percent');
    const timerDisplay = document.getElementById('timer-display');
    const timerNumber = document.getElementById('timer-number');
    const timerCircle = document.getElementById('timer-circle');
    const liveScore = document.getElementById('live-score');
    const liveCorrect = document.getElementById('live-correct');
    const resultEmoji = document.getElementById('result-emoji');
    const resultTitle = document.getElementById('result-title');
    const resultSubtitle = document.getElementById('result-subtitle');
    const statScore = document.getElementById('stat-score');
    const statCorrect = document.getElementById('stat-correct');
    const statTime = document.getElementById('stat-time');
    const statRank = document.getElementById('stat-rank');
    const restartBtn = document.getElementById('restart-btn');

    const CIRCLE_LENGTH = 2 * Math.PI * 19;

    // ---------- Բարդության ընտրություն ----------
    document.querySelectorAll('.difficulty-card').forEach(card => {
        card.addEventListener('click', () => {
            document.querySelectorAll('.difficulty-card').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            selectedDifficulty = card.dataset.difficulty;
            playSound('tick');
            checkStartReady();
        });
    });

    playerNameInput.addEventListener('input', () => {
        playerName = playerNameInput.value.trim();
        checkStartReady();
    });

    function checkStartReady() {
        startBtn.disabled = !(selectedDifficulty && playerName.length >= 2);
    }

    startBtn.addEventListener('click', () => {
        playSound('tick');
        fetch(`/api/questions/${selectedDifficulty}`)
            .then(res => res.json())
            .then(data => {
                if (data.error) { alert(data.error); return; }
                questions = data.questions;
                levelConfig = {
                    difficulty: data.difficulty,
                    label: data.label,
                    time: data.time,
                    points: data.points
                };
                startQuiz();
            })
            .catch(err => console.error(err));
    });

    function startQuiz() {
        startScreen.classList.add('hidden');
        gameScreen.classList.remove('hidden');
        displayName.textContent = playerName;
        playerAvatar.textContent = playerName.charAt(0).toUpperCase();
        playerAvatar.style.background = getAvatarColor(playerName);

        currentDiffBadge.textContent = levelConfig.label;
        currentDiffBadge.className = 'quiz-badge diff-' + levelConfig.difficulty;

        currentIndex = 0; score = 0; correctCount = 0; totalTimeSpent = 0;
        loadQuestion();
    }

    function getAvatarColor(name) {
        const colors = ['#00f0ff', '#7000ff', '#00ff66', '#ff9900', '#ff0055', '#ec4899', '#3b82f6', '#a855f7'];
        const idx = (name.charCodeAt(0) || 0) % colors.length;
        return colors[idx];
    }

    function loadQuestion() {
        clearInterval(timerInterval);

        // Անիմացիա — Fade out հին պարունակությունը
        questionCard.classList.add('slide-out');
        optionsContainer.classList.add('slide-out');

        setTimeout(() => {
            optionsContainer.innerHTML = '';
            inlineResult.textContent = '';
            inlineResult.className = 'answer-feedback';
            updateLiveStats();

            const q = questions[currentIndex];
            questionText.textContent = q.question;

            q.options.forEach((opt, i) => {
                const btn = document.createElement('button');
                btn.className = 'option-item';
                btn.innerHTML = `
                    <span class="option-letter">${String.fromCharCode(65 + i)}</span>
                    <span class="option-text">${opt}</span>
                    <span class="option-check"></span>
                `;
                btn.onclick = () => selectAnswer(i, btn);
                optionsContainer.appendChild(btn);
            });

            // Անիմացիա — Fade in նոր պարունակությունը
            questionCard.classList.remove('slide-out');
            optionsContainer.classList.remove('slide-out');
            questionCard.classList.add('slide-in');
            optionsContainer.classList.add('slide-in');

            setTimeout(() => {
                questionCard.classList.remove('slide-in');
                optionsContainer.classList.remove('slide-in');
            }, 500);

            const pct = (currentIndex / questions.length) * 100;
            progressFill.style.width = (currentIndex / questions.length) * 100 + '%';
            if (progressPercent) {
                progressPercent.textContent = Math.round((currentIndex / questions.length) * 100) + '%';
            }

            timeRemaining = levelConfig.time;
            questionStartTime = Date.now();
            updateTimer();
            timerInterval = setInterval(() => {
                timeRemaining--;
                updateTimer();
                if (timeRemaining <= 0) {
                    clearInterval(timerInterval);
                    timeUp();
                }
            }, 1000);
        }, 250);
    }

    function updateTimer() {
        timerNumber.textContent = timeRemaining;
        const pct = timeRemaining / levelConfig.time;
        timerCircle.style.strokeDasharray = CIRCLE_LENGTH;
        timerCircle.style.strokeDashoffset = CIRCLE_LENGTH * (1 - pct);

        if (timeRemaining <= 5) {
            timerDisplay.classList.add('danger');
            timerDisplay.classList.remove('warning');
            if (timeRemaining > 0 && timeRemaining <= 5) playSound('tick');
        } else if (timeRemaining <= levelConfig.time * 0.4) {
            timerDisplay.classList.add('warning');
            timerDisplay.classList.remove('danger');
        } else {
            timerDisplay.classList.remove('warning', 'danger');
        }
    }

    function updateLiveStats() {
        liveScore.textContent = score;
        liveCorrect.textContent = correctCount;
    }

    function timeUp() {
        playSound('wrong');
        const allBtns = optionsContainer.querySelectorAll('.option-item');
        allBtns.forEach(b => b.style.pointerEvents = 'none');
        totalTimeSpent += levelConfig.time;

        fetch('/api/check', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                difficulty: levelConfig.difficulty,
                question_id: questions[currentIndex].id,
                selected: -1
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.correct_index !== undefined) {
                allBtns[data.correct_index].classList.add('correct');
            }
            inlineResult.className = 'answer-feedback error';
            inlineResult.innerHTML = '⏰ ' + (T.quiz_time_up || 'Ժամանակը սպառվեց');
        })
        .finally(() => setTimeout(nextQuestion, 1600));
    }

    function selectAnswer(selected, btnEl) {
        clearInterval(timerInterval);
        const timeSpent = Math.min(levelConfig.time, (Date.now() - questionStartTime) / 1000);
        totalTimeSpent += timeSpent;

        const allBtns = optionsContainer.querySelectorAll('.option-item');
        allBtns.forEach(b => b.style.pointerEvents = 'none');

        fetch('/api/check', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                difficulty: levelConfig.difficulty,
                question_id: questions[currentIndex].id,
                selected: selected
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.correct) {
                btnEl.classList.add('correct');
                score += levelConfig.points;
                correctCount++;
                playSound('correct');
                inlineResult.className = 'answer-feedback success';
                inlineResult.innerHTML = `✅ ${T.quiz_correct_msg || 'Ճիշտ է։'} <strong>+${levelConfig.points} ${T.quiz_points_added || 'միավոր'}</strong>`;
            } else {
                btnEl.classList.add('wrong');
                allBtns[data.correct_index].classList.add('correct');
                playSound('wrong');
                inlineResult.className = 'answer-feedback error';
                inlineResult.innerHTML = '❌ ' + (T.quiz_wrong_msg || 'Սխալ է։');
            }
            updateLiveStats();
        })
        .finally(() => setTimeout(nextQuestion, 1600));
    }

    function nextQuestion() {
        currentIndex++;
        if (currentIndex < questions.length) {
            loadQuestion();
        } else {
            showResults();
        }
    }

    function showResults() {
        gameScreen.classList.add('hidden');
        resultScreen.classList.remove('hidden');
        progressFill.style.width = '100%';
        playSound('complete');

        statScore.textContent = score;
        statCorrect.textContent = `${correctCount} / ${questions.length}`;
        statTime.textContent = Math.round(totalTimeSpent) + (T.seconds_short || 'վ');

        const pct = (correctCount / questions.length) * 100;
        if (pct >= 90) {
            resultEmoji.textContent = '🏆';
            resultTitle.textContent = T.quiz_excellent || 'Հիանալի է։';
            resultSubtitle.textContent = T.quiz_excellent_sub || '';
        } else if (pct >= 70) {
            resultEmoji.textContent = '🎉';
            resultTitle.textContent = T.quiz_great || 'Շատ լավ է։';
            resultSubtitle.textContent = T.quiz_great_sub || '';
        } else if (pct >= 50) {
            resultEmoji.textContent = '👍';
            resultTitle.textContent = T.quiz_good || 'Լավ է։';
            resultSubtitle.textContent = T.quiz_good_sub || '';
        } else {
            resultEmoji.textContent = '📚';
            resultTitle.textContent = T.quiz_learn || 'Շարունակիր Սովորել։';
            resultSubtitle.textContent = T.quiz_learn_sub || '';
        }

        fetch('/api/leaderboard', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: playerName,
                score: score,
                difficulty: levelConfig.difficulty,
                correct: correctCount,
                total: questions.length,
                time: totalTimeSpent
            })
        })
        .then(res => res.json())
        .then(data => {
            statRank.textContent = data.position ? '#' + data.position : '—';
        })
        .catch(err => { console.error(err); statRank.textContent = '—'; });
    }

    restartBtn.addEventListener('click', () => {
        playSound('tick');
        resultScreen.classList.add('hidden');
        startScreen.classList.remove('hidden');
        selectedDifficulty = null;
        document.querySelectorAll('.difficulty-card').forEach(c => c.classList.remove('selected'));
        checkStartReady();
    });
}

// ==========================================================
//   ԼԻԴԵՐԲՈՐԴԻ ԷՋ
// ==========================================================
const lbTable = document.getElementById('leaderboard-table');
if (lbTable) {
    document.querySelectorAll('.lb-filter').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.lb-filter').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            playSound('tick');
            loadLeaderboard(btn.dataset.filter);
        });
    });
    loadLeaderboard('all');
}

function loadLeaderboard(filter) {
    const body = document.getElementById('leaderboard-body');
    const loading = document.getElementById('leaderboard-loading');
    const table = document.getElementById('leaderboard-table');
    const empty = document.getElementById('leaderboard-empty');
    const podium = document.getElementById('podium');

    loading.classList.remove('hidden');
    table.classList.add('hidden');
    empty.classList.add('hidden');
    podium.classList.add('hidden');

    fetch('/api/leaderboard')
        .then(res => res.json())
        .then(data => {
            loading.classList.add('hidden');
            let filtered = data;
            if (filter !== 'all') filtered = data.filter(e => e.difficulty === filter);

            if (filtered.length === 0) {
                empty.classList.remove('hidden');
                return;
            }

            if (filtered.length >= 1) {
                podium.classList.remove('hidden');
                renderPodium(filtered);
            }

            table.classList.remove('hidden');
            body.innerHTML = filtered.map((e, i) => {
                const rankClass = i < 3 ? `rank-${i+1}` : '';
                const medal = i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : (i + 1);
                return `
                    <tr class="${rankClass}">
                        <td class="td-rank"><span class="rank-circle">${medal}</span></td>
                        <td class="td-name">
                            <div class="name-cell">
                                <span class="mini-avatar" style="background: ${getAvatarColor(e.name)}">${escapeHtml(e.name.charAt(0).toUpperCase())}</span>
                                <strong>${escapeHtml(e.name)}</strong>
                            </div>
                        </td>
                        <td><span class="diff-pill diff-${e.difficulty}">${e.difficulty_label}</span></td>
                        <td class="td-score"><strong>${e.score}</strong></td>
                        <td class="td-correct">${e.correct}/${e.total}</td>
                        <td class="td-time">${e.time}${T.seconds_short || 'վ'}</td>
                        <td class="td-date">${formatDate(e.date)}</td>
                    </tr>
                `;
            }).join('');
        })
        .catch(err => {
            console.error(err);
            loading.classList.add('hidden');
            empty.classList.remove('hidden');
        });
}

function renderPodium(list) {
    const top3 = list.slice(0, 3);
    if (top3[0]) {
        const p1 = document.getElementById('podium-1');
        p1.querySelector('.podium-avatar').textContent = top3[0].name.charAt(0).toUpperCase();
        p1.querySelector('.podium-avatar').style.background = getAvatarColor(top3[0].name);
        p1.querySelector('.podium-name').textContent = top3[0].name;
        p1.querySelector('.podium-score').textContent = top3[0].score + ' ' + (T.quiz_score_unit || 'միավոր');
    }
    if (top3[1]) {
        const p2 = document.getElementById('podium-2');
        p2.querySelector('.podium-avatar').textContent = top3[1].name.charAt(0).toUpperCase();
        p2.querySelector('.podium-avatar').style.background = getAvatarColor(top3[1].name);
        p2.querySelector('.podium-name').textContent = top3[1].name;
        p2.querySelector('.podium-score').textContent = top3[1].score + ' ' + (T.quiz_score_unit || 'միավոր');
    } else {
        document.getElementById('podium-2').style.visibility = 'hidden';
    }
    if (top3[2]) {
        const p3 = document.getElementById('podium-3');
        p3.querySelector('.podium-avatar').textContent = top3[2].name.charAt(0).toUpperCase();
        p3.querySelector('.podium-avatar').style.background = getAvatarColor(top3[2].name);
        p3.querySelector('.podium-name').textContent = top3[2].name;
        p3.querySelector('.podium-score').textContent = top3[2].score + ' ' + (T.quiz_score_unit || 'միավոր');
    } else {
        document.getElementById('podium-3').style.visibility = 'hidden';
    }
}

function getAvatarColor(name) {
    const colors = ['#00f0ff', '#7000ff', '#00ff66', '#ff9900', '#ff0055', '#ec4899', '#3b82f6', '#a855f7'];
    const idx = (name.charCodeAt(0) || 0) % colors.length;
    return colors[idx];
}

function formatDate(dateStr) {
    try {
        const [d] = dateStr.split(' ');
        const [y, m, day] = d.split('-');
        return `${day}.${m}.${y.slice(2)}`;
    } catch (e) { return dateStr; }
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}


/* ==========================================================
   🎨 ԱՆԻՄԱՑԻՈՆ ՖՈՆ — Matrix Rain + Particles
   ========================================================== */

// ==========================================================
// 🌧️ MATRIX RAIN
// ==========================================================
(function initMatrixRain() {
    const canvas = document.getElementById('matrix-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    // Կիբեռանվտանգությանը համապատասխան սիմվոլներ
    const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノ01010101ABCDEF#$%&@!';
    const charsArray = chars.split('');

    const fontSize = 16;
    let columns = Math.floor(canvas.width / fontSize);
    let drops = Array(columns).fill(1);

    function getColor() {
        // Մութ ռեժիմում՝ cyan, լուսավորում՝ կապույտ
        return document.body.classList.contains('light-mode')
            ? 'rgba(37, 99, 235, 0.7)'
            : 'rgba(0, 240, 255, 0.7)';
    }

    function draw() {
        // Անհրաժեշտության դեպքում թարմացնում ենք սյուների քանակը
        const newColumns = Math.floor(canvas.width / fontSize);
        if (newColumns !== columns) {
            columns = newColumns;
            drops = Array(columns).fill(1);
        }

        // Կիսաթափանց սև ֆոն հետքի համար
        ctx.fillStyle = document.body.classList.contains('light-mode')
            ? 'rgba(248, 250, 252, 0.08)'
            : 'rgba(10, 14, 23, 0.08)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = getColor();
        ctx.font = fontSize + 'px monospace';

        for (let i = 0; i < drops.length; i++) {
            const text = charsArray[Math.floor(Math.random() * charsArray.length)];
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);

            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }
            drops[i]++;
        }
    }

    setInterval(draw, 55);
})();


// ==========================================================
// ✨ ԼՈՂԱՑՈՂ ՄԱՍՆԻԿՆԵՐ
// ==========================================================
(function initParticles() {
    const container = document.getElementById('bg-particles');
    if (!container) return;

    const PARTICLE_COUNT = window.innerWidth < 768 ? 20 : 45;
    const colors = ['', 'purple', 'green', 'pink'];

    for (let i = 0; i < PARTICLE_COUNT; i++) {
        const dot = document.createElement('div');
        dot.className = 'particle-dot ' + colors[Math.floor(Math.random() * colors.length)];
        dot.style.left = Math.random() * 100 + '%';
        dot.style.animationDuration = (8 + Math.random() * 12) + 's';
        dot.style.animationDelay = (Math.random() * 15) + 's';
        dot.style.width = dot.style.height = (2 + Math.random() * 3) + 'px';
        container.appendChild(dot);
    }
})();


// ==========================================================
// 💫 ՖՈՆԻ ՇԱՐԺՈՒՄ ՄՈՒԿԻ ՀԵՏ (Parallax Effect)
// ==========================================================
(function initParallax() {
    // Միայն desktop-ի համար
    if (window.innerWidth < 1024) return;

    const orbs = document.querySelectorAll('.orb');
    let ticking = false;

    window.addEventListener('mousemove', (e) => {
        if (ticking) return;
        ticking = true;

        requestAnimationFrame(() => {
            const x = (e.clientX / window.innerWidth - 0.5) * 2;
            const y = (e.clientY / window.innerHeight - 0.5) * 2;

            orbs.forEach((orb, i) => {
                const depth = (i + 1) * 15;
                orb.style.transform = `translate(${x * depth}px, ${y * depth}px)`;
            });

            ticking = false;
        });
    });
})();
