// Dark Mode Logic
const themeBtn = document.getElementById('theme-toggle');
const body = document.body;

if (localStorage.getItem('theme') === 'dark') {
    body.classList.add('dark-mode');
}

themeBtn.addEventListener('click', () => {
    body.classList.toggle('dark-mode');
    localStorage.setItem('theme', body.classList.contains('dark-mode') ? 'dark' : 'light');
});

// Quiz Logic
const quizContainer = document.getElementById('quiz-container');
if (quizContainer) {
    let questions = [];
    let currentQuestionIndex = 0;
    let score = 0;

    const questionText = document.getElementById('question-text');
    const optionsContainer = document.getElementById('options-container');
    const quizUi = document.getElementById('quiz-ui');
    const resultUi = document.getElementById('result-ui');
    const scoreText = document.getElementById('score-text');

    // Fetch questions from Flask API
    fetch('/api/questions')
        .then(response => response.json())
        .then(data => {
            questions = data;
            loadQuestion();
        })
        .catch(err => console.error("Error loading questions:", err));

    function loadQuestion() {
        optionsContainer.innerHTML = '';
        const currentQ = questions[currentQuestionIndex];
        questionText.textContent = `${currentQuestionIndex + 1}. ${currentQ.question}`;

        currentQ.options.forEach((opt, index) => {
            const btn = document.createElement('button');
            btn.classList.add('option-btn');
            btn.textContent = opt;
            btn.onclick = () => checkAnswer(index, currentQ.answer, btn);
            optionsContainer.appendChild(btn);
        });
    }

    function checkAnswer(selectedIndex, correctIndex, btnElement) {
        // Disable all buttons after choice
        const allBtns = optionsContainer.querySelectorAll('.option-btn');
        allBtns.forEach(b => b.style.pointerEvents = 'none');

        if (selectedIndex === correctIndex) {
            btnElement.classList.add('correct');
            score++;
        } else {
            btnElement.classList.add('wrong');
            allBtns[correctIndex].classList.add('correct');
        }

        setTimeout(() => {
            currentQuestionIndex++;
            if (currentQuestionIndex < questions.length) {
                loadQuestion();
            } else {
                showResults();
            }
        }, 1500);
    }

    function showResults() {
        quizUi.classList.add('hidden');
        resultUi.classList.remove('hidden');
        scoreText.textContent = `Դուք ճիշտ պատասխանեցիք ${score} հարցի ${questions.length}-ից:`;
    }
}
