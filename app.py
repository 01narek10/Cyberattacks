from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Վիկտորինայի ընդլայնված հարցերի բազա
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
    },
    {
        "id": 5,
        "question": "Ո՞րն է ամենաանվտանգ գաղտնաբառի ստեղծման սկզբունքը:",
        "options": ["Քո ծննդյան թիվը", "Տառերի, թվերի և սիմվոլների համադրություն", "Պարզ բառ, որը հեշտ է հիշել"],
        "answer": 1
    }
]

# Իրական կիբեռմիջադեպերի քեյսեր
CYBER_CASES = [
    {
        "title": "WannaCry (2017)",
        "type": "Ransomware",
        "description": "Համաշխարհային մասշտաբի հարձակում, որը վարակեց հարյուր հազարավոր համակարգեր ավելի քան 150 երկրում՝ արգելափակելով հիվանդանոցների և պետական հաստատությունների աշխատանքը։"
    },
    {
        "title": "Sony Pictures (2014)",
        "type": "Data Breach & Hacktivism",
        "description": "Հսկայական ծավալի գաղտնի տվյալների արտահոսք, ներառյալ չթողարկված ֆիլմեր, աշխատակիցների անձնական նամակագրություն և ֆինանսական փաստաթղթեր։"
    },
    {
        "title": "Twitter (X) Crypto Scam (2020)",
        "type": "Social Engineering",
        "description": "Հաքերները կոտրել էին հայտնի մարդկանց (Բեյք Սթիվ, Իլոն Մասկ, Բիլ Գեյթս) հաշիվները՝ տեղադրելով կեղծ կրիպտոարժույթային հղումներ, որոնց միջոցով հազարավոր դոլարներ գողացան։"
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

@app.route('/cases')
def cases():
    return render_template('cases.html', title="Իրական Քեյսեր", cyber_cases=CYBER_CASES)

@app.route('/quiz')
def quiz():
    return render_template('quiz.html', title="Թեստ")

@app.route('/api/questions')
def get_questions():
    return jsonify(QUIZ_QUESTIONS)

if __name__ == '__main__':
    app.run(debug=True)
