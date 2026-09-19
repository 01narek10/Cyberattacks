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
    // Փոփոխականներ
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

    // DOM տարրեր
    const gameScreen = document.getElementById('game-screen');
    const resultScreen = document.getElementById('result-screen');
    const playerNameInput = document.getElementById('player-name');
    const startBtn = document.getElementById('start-btn');
    const displayName = document.getElementById('display-name');
    const currentDiffBadge = document.getElementById('current-difficulty');
    const questionText = document.getElementById('question-text');
    const optionsContainer = document.getElementById('options-container');
    const inlineResult = document.getElementById('quiz-result');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const timerDisplay = document.getElementById('timer-display');
    const liveScore = document.getElementById('live-score');
    const liveCorrect = document.getElementById('live-correct');
    const scoreText = document.getElementById('score-text');
    const resultEmoji = document.getElementById('result-emoji');
    const resultTitle = document.getElementById('result-title');
    const statScore = document.getElementById('stat-score');
    const statCorrect = document.getElementById('stat-correct');
    const statTime = document.getElementById('stat-time');
    const statRank = document.getElementById('stat-rank');
    const restartBtn = document.getElementById('restart-btn');

    // ---------- Բարդության ընտրություն ----------
    document.querySelectorAll('.difficulty-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.difficulty-btn').forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            selectedDifficulty = btn.dataset.difficulty;
            checkStartReady();
        });
    });

    // ---------- Անուն գրելը ----------
    playerNameInput.addEventListener('input', () => {
        playerName = playerNameInput.value.trim();
        checkStartReady();
    });

    function checkStartReady() {
        startBtn.disabled = !(selectedDifficulty && playerName.length >= 2);
    }

    // ---------- Սկսել թեստը ----------
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

    // ---------- Սկսել խաղը ----------
    function startQuiz() {
        startScreen.classList.add('hidden');
        gameScreen.classList.remove('hidden');
        displayName.textContent = playerName;
        currentDiffBadge.textContent = levelConfig.label;
        currentDiffBadge.className = 'quiz-badge diff-' + levelConfig.difficulty;

        currentIndex = 0;
        score = 0;
        correctCount = 0;
        totalTimeSpent = 0;
        loadQuestion();
    }

    // ---------- Հարցի բեռնում ----------
    function loadQuestion() {
        clearInterval(timerInterval);
        optionsContainer.innerHTML = '';
        inlineResult.textContent = '';
        updateLiveStats();

        const q = questions[currentIndex];
        questionText.textContent = `${currentIndex + 1}. ${q.question}`;

        q.options.forEach((opt, i) => {
            const btn = document.createElement('button');
            btn.className = 'option-btn';
            btn.textContent = opt;
            btn.onclick = () => selectAnswer(i, btn);
            optionsContainer.appendChild(btn);
        });

        progressFill.style.width = ((currentIndex) / questions.length) * 100 + '%';
        progressText.textContent = `${currentIndex + 1} / ${questions.length}`;

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
        timerDisplay.textContent = `⏱ ${timeRemaining}`;
        timerDisplay.classList.toggle('warning', timeRemaining <= 5);
    }

    function updateLiveStats() {
        liveScore.textContent = score;
        liveCorrect.textContent = correctCount;
    }

    // ---------- Ժամանակը սպառվել է ----------
    function timeUp() {
        const allBtns = optionsContainer.querySelectorAll('.option-btn');
        allBtns.forEach(b => b.disabled = true);
        inlineResult.textContent = '⏰ Ժամանակը սպառվեց։';
        inlineResult.style.color = 'var(--accent-orange)';
        totalTimeSpent += levelConfig.time;

        // Ցույց ենք տալիս ճիշտ պատասխանը
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
        })
        .finally(() => {
            setTimeout(nextQuestion, 1400);
        });
    }

    // ---------- Պատասխանի ընտրություն ----------
    function selectAnswer(selected, btnEl) {
        clearInterval(timerInterval);
        const timeSpent = Math.min(levelConfig.time, (Date.now() - questionStartTime) / 1000);
        totalTimeSpent += timeSpent;

        const allBtns = optionsContainer.querySelectorAll('.option-btn');
        allBtns.forEach(b => b.disabled = true);

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
                inlineResult.textContent = '✅ Ճիշտ է։ +' + levelConfig.points + ' միավոր';
                inlineResult.style.color = 'var(--accent-green)';
            } else {
                btnEl.classList.add('wrong');
                allBtns[data.correct_index].classList.add('correct');
                inlineResult.textContent = '❌ Սխալ է։';
                inlineResult.style.color = 'var(--accent-red)';
            }
            updateLiveStats();
        })
        .finally(() => {
            setTimeout(nextQuestion, 1400);
        });
    }

    // ---------- Հաջորդ հարց ----------
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
        statTime.textContent = Math.round(totalTimeSpent) + ' վրկ';

        // Գնահատական
        const pct = (correctCount / questions.length) * 100;
        if (pct >= 90) {
            resultEmoji.textContent = '🏆';
            resultTitle.textContent = 'Հիանալի է, դու մասնագետ ես։';
        } else if (pct >= 70) {
            resultEmoji.textContent = '🎉';
            resultTitle.textContent = 'Շատ լավ է։';
        } else if (pct >= 50) {
            resultEmoji.textContent = '👍';
            resultTitle.textContent = 'Լավ է, բայց կարող ես ավելի լավ։';
        } else {
            resultEmoji.textContent = '📚';
            resultTitle.textContent = 'Փորձիր նորից, սովորիր ավելին։';
        }

        scoreText.textContent = `Դուք հավաքեցիք ${score} միավոր։`;

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

    // ---------- Կրկին փորձել ----------
    restartBtn.addEventListener('click', () => {
        resultScreen.classList.add('hidden');
        startScreen.classList.remove('hidden');
        selectedDifficulty = null;
        playerName = playerNameInput.value.trim();
        document.querySelectorAll('.difficulty-btn').forEach(b => b.classList.remove('selected'));
        checkStartReady();
    });
}
