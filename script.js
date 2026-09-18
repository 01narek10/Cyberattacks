// Dark Mode -ի միացում/անջատում
const themeToggleBtn = document.getElementById('theme-toggle');
const body = document.body;

// Ստուգել, արդյոք օգտատերը նախկինում ընտրել է մութ ռեժիմ
if (localStorage.getItem('theme') === 'dark') {
    body.classList.add('dark-mode');
}

themeToggleBtn.addEventListener('click', () => {
    body.classList.toggle('dark-mode');
    
    if (body.classList.contains('dark-mode')) {
        localStorage.setItem('theme', 'dark');
        themeToggleBtn.textContent = 'Լուսավոր ռեժիմ';
    } else {
        localStorage.setItem('theme', 'light');
        themeToggleBtn.textContent = 'Մութ ռեժիմ';
    }
});

// Վիկտորինայի տրամաբանություն
function checkAnswer(isCorrect) {
    const resultText = document.getElementById('quiz-result');
    
    if (isCorrect) {
        resultText.textContent = "Ճիշտ է։ Էթիկական հաքերները պաշտպանում են համակարգերը։ ✅";
        resultText.style.color = "#22c55e"; // Կանաչ
    } else {
        resultText.textContent = "Սխալ է։ Փորձիր նորից։ ❌";
        resultText.style.color = "#ef4444"; // Կարմիր
    }
}
