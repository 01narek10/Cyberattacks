from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Վիկտորինայի հարցերի բազա
QUIZ_QUESTIONS = [
    {
        "id": 1,
        "question": "Ի՞նչ է նշանակում Phishing:",
        "options": ["Համակարգչի ֆիզիկական գողություն", "Խաբեությամբ գաղտնի տվյալների կորզում", "Վիրուսային ծրագրի տեսակ"],
        "answer": 1
    },
    {
        "id": 2,
        "question": "Ո՞րն է White Hat հաքերի նպատակը:",
        "options": ["Գումար շորթելը", "Համակարգը կոտրելն ու վնասելը", "Խոցելիությունները գտնելն ու պաշտպանելը"],
        "answer": 2
    },
    {
        "id": 3,
        "question": "Ի՞նչ է Ransomware-ը:",
        "options": ["Ծրագիր, որը կոդավորում է ֆայլերը և փրկագին պահանջում", "Անվճար հակավիրուսային ծրագիր", "Անձնական նկարներ խմբագրող հավելված"],
        "answer": 0
    },
    {
        "id": 4,
        "question": "DDoS հարձակման նպատակը ո՞րն է:",
        "options": ["Գաղտնաբառեր գողանալը", "Սերվերը ծանրաբեռնելն ու խափանելը", "Տվյալների բազան ջնջելը"],
        "answer": 1
    }
]

@app.route('/')
def home():
    return render_template('index.html', title="Գլխավոր")

@app.route('/types')
def types():
    return render_template('types.html', title="Կիբեռհանցագործություններ")

@app.route('/hackers')
def hackers():
    return render_template('hackers.html', title="Հաքերներ")

@app.route('/quiz')
def quiz():
    return render_template('quiz.html', title="Վիկտորինա")

# API էնդփոյնթ (endpoint) վիկտորինայի տվյալները JS-ին ուղարկելու համար
@app.route('/api/questions')
def get_questions():
    return jsonify(QUIZ_QUESTIONS)

if __name__ == '__main__':
    app.run(debug=True)
