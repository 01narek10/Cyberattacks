/* ==========================================================
   CyberShield — Interactive Scripts
   ========================================================== */

// ---------- Theme Toggle (Dark / Light) ----------
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

// ---------- Mobile Menu ----------
const hamburger = document.getElementById('hamburger');
const navMenu = document.getElementById('navMenu');
if (hamburger && navMenu) {
    hamburger.addEventListener('click', () => navMenu.classList.toggle('active'));
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => navMenu.classList.remove('active'));
    });
}

// ---------- Quiz Logic (Multi-question) ----------
const quizContainer = document.getElementById('quizContainer');
if (quizContainer) {
    let questions = [];
    let currentIndex = 0;
    let score = 0;

    const questionText = document.getElementById('question-text');
    const optionsContainer = document.getElementById('options-container');
    const quizUi = document.getElementById('quiz-ui');
    const resultUi = document.getElementById('result-ui');
    const scoreText = document.getElementById('score-text');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const inlineResult = document.getElementById('quiz-result');

    fetch('/api/questions')
        .then(res => res.json())
        .then(data => {
            questions = data;
            loadQuestion();
        })
        .catch(err => console.error('Quiz load error:', err));

    function loadQuestion() {
        optionsContainer.innerHTML = '';
        inlineResult.textContent = '';
        const q = questions[currentIndex];
        questionText.textContent = `${currentIndex + 1}. ${q.question}`;

        q.options.forEach((opt, i) => {
            const btn = document.createElement('button');
            btn.className = 'option-btn';
            btn.textContent = opt;
            btn.onclick = () => checkAnswer(i, q.answer, btn);
            optionsContainer.appendChild(btn);
        });

        progressFill.style.width = ((currentIndex) / questions.length) * 100 + '%';
        progressText.textContent = `${currentIndex + 1} / ${questions.length}`;
    }

    function checkAnswer(selected, correct, btnEl) {
        const allBtns = optionsContainer.querySelectorAll('.option-btn');
        allBtns.forEach(b => b.disabled = true);

        if (selected === correct) {
            btnEl.classList.add('correct');
            score++;
            inlineResult.textContent = '✅ Ճիշտ է։';
            inlineResult.style.color = 'var(--accent-green)';
        } else {
            btnEl.classList.add('wrong');
            allBtns[correct].classList.add('correct');
            inlineResult.textContent = '❌ Սխալ է։';
            inlineResult.style.color = 'var(--accent-red)';
        }

        setTimeout(() => {
            currentIndex++;
            if (currentIndex < questions.length) {
                loadQuestion();
            } else {
                showResults();
            }
        }, 1300);
    }

    function showResults() {
        quizUi.classList.add('hidden');
        resultUi.classList.remove('hidden');
        progressFill.style.width = '100%';
        scoreText.textContent = `Դուք ճիշտ պատասխանեցիք ${score} հարցի ${questions.length}-ից։ (${Math.round((score / questions.length) * 100)}%)`;
    }
}
