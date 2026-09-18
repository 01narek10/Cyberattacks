from flask import Flask, render_template, jsonify

app = Flask(__name__)

# ============ ՎԻԿՏՈՐԻՆԱՅԻ ՏՎՅԱԼՆԵՐ ============
QUIZ_QUESTIONS = [
    {"id": 1, "question": "Ի՞նչ է նշանակում Phishing:",
     "options": ["Համակարգչի ֆիզիկական գողություն", "Խաբեությամբ գաղտնի տվյալների կորզում", "Վիրուսային ծրագրի տեսակ"],
     "answer": 1},
    {"id": 2, "question": "Ո՞րն է White Hat հաքերի նպատակը:",
     "options": ["Գումար շորթելը", "Համակարգը կոտրելն ու վնասելը", "Խոցելիությունները գտնելն ու պաշտպանելը"],
     "answer": 2},
    {"id": 3, "question": "Ի՞նչ է Ransomware-ը:",
     "options": ["Ծրագիր, որը կոդավորում է ֆայլերը և փրկագին պահանջում", "Անվճար հակավիրուսային ծրագիր", "Հավելված նկարների խմբագրման համար"],
     "answer": 0},
    {"id": 4, "question": "DDoS հարձակման նպատակը ո՞րն է:",
     "options": ["Գաղտնաբառեր գողանալը", "Սերվերը ծանրաբեռնելն ու խափանելը", "Տվյալների բազան ջնջելը"],
     "answer": 1},
    {"id": 5, "question": "Ի՞նչ է 2FA-ն:",
     "options": ["Երկու գաղտնաբառ", "Երկփուլանի վավերացում", "Երկու հաշիվ"],
     "answer": 1},
    {"id": 6, "question": "Ո՞րն է ամենաանվտանգ գաղտնաբառը:",
     "options": ["12345678", "Քո ծննդյան ամսաթիվը", "Մեծատառ + փոքրատառ + թիվ + սիմվոլ"],
     "answer": 2},
    {"id": 7, "question": "Ի՞նչ է Spear Phishing-ը:",
     "options": ["Զանգվածային նամակներ", "Թիրախավորված հարձակում կոնկրետ անձի վրա", "Հեռախոսային զանգ"],
     "answer": 1},
    {"id": 8, "question": "Ի՞նչ է MitM հարձակումը:",
     "options": ["Կապի մեջտեղում միջամտություն", "Սերվերի անջատում", "Ֆայլերի կոդավորում"],
     "answer": 0},
    {"id": 9, "question": "Ի՞նչ է անհրաժեշտ անել կասկածելի նամակ ստանալիս:",
     "options": ["Անմիջապես բացել կցված ֆայլը", "Ստուգել ուղարկողի հասցեն և չսեղմել հղումներին", "Փոխանցել ընկերներին"],
     "answer": 1},
    {"id": 10, "question": "Ի՞նչ է VPN-ը:",
     "options": ["Վիրտուալ մասնավոր ցանց", "Վիրուսային պրոտոկոլ", "Հակավիրուս"],
     "answer": 0},
]

# ============ ԻՐԱԿԱՆ ՔԵՅՍԵՐ ============
CYBER_CASES = [
    {"title": "WannaCry (2017)", "type": "Ransomware", "year": "2017",
     "description": "Համաշխարհային Ransomware հարձակում, որը վարակեց ավելի քան 200,000 համակարգեր 150+ երկրներում։ Հարված հասցրեց հիվանդանոցներին, բանկերին և պետական կառույցներին։ Վնասը գնահատվում է միլիարդավոր դոլարներ։"},
    {"title": "Yahoo Data Breach (2013-2014)", "type": "Data Breach", "year": "2013",
     "description": "Բոլոր ժամանակների ամենամեծ տվյալների արտահոսքը. 3 միլիարդ օգտատերերի հաշիվներ գողացվեցին։ Ընկերության արժեքը Verizon-ի գնման ժամանակ նվազեց 350 միլիոն դոլարով։"},
    {"title": "Sony Pictures Hack (2014)", "type": "Hacktivism", "year": "2014",
     "description": "Հսկայական ծավալի գաղտնի տվյալների արտահոսք, ներառյալ չթողարկված ֆիլմեր, աշխատակիցների նամակագրություն և ֆինանսական փաստաթղթեր։"},
    {"title": "Twitter Crypto Scam (2020)", "type": "Social Engineering", "year": "2020",
     "description": "Հաքերները կոտրեցին Իլոն Մասկի, Բիլ Գեյթսի, Բարաք Օբամայի Twitter հաշիվները՝ տարածելով կեղծ կրիպտոարժույթային հղումներ։ Գողացվեց ավելի քան 120,000 դոլար բիթքոյն։"},
    {"title": "Colonial Pipeline (2021)", "type": "Ransomware", "year": "2021",
     "description": "ԱՄՆ-ի ամենամեծ նավթամուղ ընկերության հարձակում, որը կաթվածահար արեց Արևելյան ափի վառելիքի մատակարարումը։ Փրկագինը՝ 4.4 միլիոն դոլար։"},
    {"title": "Equifax Breach (2017)", "type": "Data Breach", "year": "2017",
     "description": "147 միլիոն ամերիկացիների անձնական տվյալների (սոց. քարտ, վարորդական, վարկային պատմություն) արտահոսք։ Ընկերությունը տուգանվեց 700 միլիոն դոլարով։"},
]

# ============ ԵՐԹՈՒՂԻՆԵՐ ============
@app.route('/')
def home():
    return render_template('index.html', title="Գլխավոր")

@app.route('/types')
def types():
    return render_template('types.html', title="Սպառնալիքներ")

@app.route('/hackers')
def hackers():
    return render_template('hackers.html', title="Հաքերներ")

@app.route('/phishing')
def phishing():
    return render_template('phishing.html', title="Ֆիշինգ")

@app.route('/cases')
def cases():
    return render_template('cases.html', title="Իրական Քեյսեր", cyber_cases=CYBER_CASES)

@app.route('/defense')
def defense():
    return render_template('defense.html', title="Պաշտպանություն")

@app.route('/quiz')
def quiz():
    return render_template('quiz.html', title="Թեստ")

@app.route('/api/questions')
def get_questions():
    return jsonify(QUIZ_QUESTIONS)

if __name__ == '__main__':
    app.run(debug=True)
