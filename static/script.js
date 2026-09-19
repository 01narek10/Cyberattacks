/* ==========================================================
   ԿիբեռՎահան — Ինտերակտիվ Սկրիպտներ
   ========================================================== */

// ---------- Թեմայի Փոխարկում ----------
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

// ---------- Բջջային Մենյու ----------
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

    // DOM
    const gameScreen = document.getElementById('game-screen');
    const resultScreen = document.getElementById('result-screen');
    const playerNameInput = document.getElementById('player-name');
    const startBtn = document.getElementById('start-btn');
    const displayName = document.getElementById('display-name');
    const playerAvatar = document.getElementById('player-avatar');
    const currentDiffBadge = document.getElementById('current-difficulty');
    const questionText = document.getElementById('question-text');
    const optionsContainer = document.getElementById('options-container');
    const inlineResult = document.getElementById('quiz-result');
    const progressFill = document.getElementById('progressFill');
    const progressCurrent = document.getElementById('progress-current');
    const progressTotal = document.getElementById('progress-total');
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

    const CIRCLE_LENGTH = 2 * Math.PI * 19; // շրջանագծի երկարությունը

    // ---------- Բարդության քարտի ընտրություն ----------
    document.querySelectorAll('.difficulty-card').forEach(card => {
        card.addEventListener('click', () => {
            document.querySelectorAll('.difficulty-card').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            selectedDifficulty = card.dataset.difficulty;
            checkStartReady();
        });
    });

    // ---------- Անունի մուտքագրում ----------
    playerNameInput.addEventListener('input', () => {
        playerName = playerNameInput.value.trim();
        checkStartReady();
    });

    function checkStartReady() {
        startBtn.disabled = !(selectedDifficulty && playerName.length >= 2);
    }

    // ---------- Սկսել Թեստը ----------
    startBtn.addEventListener('click', () => {
        fetch(`/api/questions/${selectedDifficulty}`)
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    alert('Սխալ. ' + data.error);
                    return;
                }
                questions = data.questions;
                levelConfig = {
                    difficulty: data.difficulty,
                    label: data.label,
                    time: data.time,
                    points: data.points
                };
                startQuiz();
            })
            .catch(err => {
                console.error('Սխալ:', err);
                alert('Չհաջողվեց բեռնել հարցերը։');
            });
    });

    // ---------- Սկսել Խաղը ----------
    function startQuiz() {
        startScreen.classList.add('hidden');
        gameScreen.classList.remove('hidden');
        displayName.textContent = playerName;
        playerAvatar.textContent = playerName.charAt(0).toUpperCase();
        playerAvatar.style.background = getAvatarColor(playerName);

        currentDiffBadge.textContent = levelConfig.label;
        currentDiffBadge.className = 'quiz-badge diff-' + levelConfig.difficulty;

        progressTotal.textContent = questions.length;
        currentIndex = 0;
        score = 0;
        correctCount = 0;
        totalTimeSpent = 0;

        // Թաքցնում ենք ավատարի գույնը
        loadQuestion();
    }

    function getAvatarColor(name) {
        const colors = ['#00f0ff', '#7000ff', '#00ff66', '#ff9900', '#ff0055', '#ec4899', '#3b82f6', '#a855f7'];
        const idx = (name.charCodeAt(0) || 0) % colors.length;
        return colors[idx];
    }

    // ---------- Հարցի բեռնում ----------
    function loadQuestion() {
        clearInterval(timerInterval);
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

        progressCurrent.textContent = currentIndex + 1;
        const pct = ((currentIndex) / questions.length) * 100;
        progressFill.style.width = pct + '%';
        progressPercent.textContent = Math.round(pct) + '%';

        // Ժամաչափ
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
    }

    function updateTimer() {
        timerNumber.textContent = timeRemaining;

        // Շրջանագծի անիմացիա
        const pct = timeRemaining / levelConfig.time;
        timerCircle.style.strokeDasharray = CIRCLE_LENGTH;
        timerCircle.style.strokeDashoffset = CIRCLE_LENGTH * (1 - pct);

        // Գույների փոփոխում
        if (timeRemaining <= 5) {
            timerDisplay.classList.add('danger');
            timerDisplay.classList.remove('warning');
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

    // ---------- Ժամանակը Սպառվել է ----------
    function timeUp() {
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
            inlineResult.innerHTML = '⏰ Ժամանակը սպառվեց';
        })
        .finally(() => {
            setTimeout(nextQuestion, 1600);
        });
    }

    // ---------- Պատասխանի Ընտրություն ----------
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
                inlineResult.className = 'answer-feedback success';
                inlineResult.innerHTML = `✅ Ճիշտ է։ <strong>+${levelConfig.points} միավոր</strong>`;
            } else {
                btnEl.classList.add('wrong');
                allBtns[data.correct_index].classList.add('correct');
                inlineResult.className = 'answer-feedback error';
                inlineResult.innerHTML = '❌ Սխալ է։';
            }
            updateLiveStats();
        })
        .finally(() => {
            setTimeout(nextQuestion, 1600);
        });
    }

    // ---------- Հաջորդ Հարց ----------
    function nextQuestion() {
        currentIndex++;
        if (currentIndex < questions.length) {
            loadQuestion();
        } else {
            showResults();
        }
    }

    // ---------- Արդյունքներ ----------
    function showResults() {
        gameScreen.classList.add('hidden');
        resultScreen.classList.remove('hidden');
        progressFill.style.width = '100%';

        statScore.textContent = score;
        statCorrect.textContent = `${correctCount} / ${questions.length}`;
        statTime.textContent = Math.round(totalTimeSpent) + 'վ';

        const pct = (correctCount / questions.length) * 100;
        if (pct >= 90) {
            resultEmoji.textContent = '🏆';
            resultTitle.textContent = 'Հիանալի է։';
            resultSubtitle.textContent = 'Դու իսկական մասնագետ ես։';
        } else if (pct >= 70) {
            resultEmoji.textContent = '🎉';
            resultTitle.textContent = 'Շատ լավ է։';
            resultSubtitle.textContent = 'Մի փոքր էլ ջանք ու դու կհասնես գագաթին։';
        } else if (pct >= 50) {
            resultEmoji.textContent = '👍';
            resultTitle.textContent = 'Լավ է։';
            resultSubtitle.textContent = 'Կարող ես ավելի լավ։ Փորձիր նորից։';
        } else {
            resultEmoji.textContent = '📚';
            resultTitle.textContent = 'Շարունակիր Սովորել։';
            resultSubtitle.textContent = 'Նայիր մյուս բաժինները և փորձիր նորից։';
        }

        // Ուղարկում ենք լիդերբորդին
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
            if (data.position) {
                statRank.textContent = '#' + data.position;
            } else {
                statRank.textContent = '—';
            }
        })
        .catch(err => {
            console.error('Լիդերբորդի սխալ:', err);
            statRank.textContent = '—';
        });
    }

    // ---------- Կրկին Փորձել ----------
    restartBtn.addEventListener('click', () => {
        resultScreen.classList.add('hidden');
        startScreen.classList.remove('hidden');
        selectedDifficulty = null;
        document.querySelectorAll('.difficulty-card').forEach(c => c.classList.remove('selected'));
        checkStartReady();
    });
}
