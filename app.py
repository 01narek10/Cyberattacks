import json
import os
from datetime import datetime
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

LEADERBOARD_FILE = 'leaderboard.json'

# ============ ՀԱՐՑԵՐԻ ԲԱԶԱ ԸՍՏ ԲԱՐԴՈՒԹՅԱՆ ============
QUESTIONS_BY_DIFFICULTY = {
    "easy": {
        "label": "Հեշտ",
        "time": 30,
        "points": 10,
        "questions": [
            {"id": 1, "question": "Ի՞նչ է նշանակում Ֆիշինգ.",
             "options": ["Համակարգչի ֆիզիկական գողություն", "Խաբեությամբ գաղտնի տվյալների կորզում", "Վիրուսային ծրագրի տեսակ"],
             "answer": 1},
            {"id": 2, "question": "Ի՞նչ է անհրաժեշտ անել կասկածելի նամակ ստանալիս.",
             "options": ["Անմիջապես բացել կցված ֆայլը", "Ստուգել ուղարկողի հասցեն և չսեղմել հղումներին", "Փոխանցել ընկերներին"],
             "answer": 1},
            {"id": 3, "question": "Ո՞րն է ամենաանվտանգ գաղտնաբառը.",
             "options": ["12345678", "Քո ծննդյան ամսաթիվը", "Մեծատառ, փոքրատառ, թիվ և սիմվոլ"],
             "answer": 2},
            {"id": 4, "question": "Ի՞նչ է Երկփուլանի Վավերացումը.",
             "options": ["Երկու գաղտնաբառ", "Երկփուլանի վավերացում", "Երկու հաշիվ"],
             "answer": 1},
            {"id": 5, "question": "Ի՞նչ է Վիրտուալ Մասնավոր Ցանցը.",
             "options": ["Վիրտուալ մասնավոր ցանց", "Վիրուսային պրոտոկոլ", "Հակավիրուս"],
             "answer": 0},
            {"id": 6, "question": "Ո՞րն է լավագույնը հանրային անլար ցանցում.",
             "options": ["Մուտքագրել բանկային տվյալներ", "Օգտագործել Վիրտուալ Մասնավոր Ցանց", "Անջատել հակավիրուսը"],
             "answer": 1},
            {"id": 7, "question": "Ի՞նչ է անհրաժեշտ պահել կարևոր ֆայլերի համար.",
             "options": ["Պահուստային պատճեն", "Միայն մեկ սարք", "Չպահել ընդհանրապես"],
             "answer": 0},
            {"id": 8, "question": "Ո՞վ է Էթիկական Հաքերը.",
             "options": ["Չարագործ", "Օրինական մասնագետ, որը ստուգում է խոցելիությունները", "Վիրուս ստեղծող"],
             "answer": 1},
        ]
    },
    "medium": {
        "label": "Միջին",
        "time": 25,
        "points": 20,
        "questions": [
            {"id": 1, "question": "Ի՞նչ է Նշանառու Ֆիշինգը.",
             "options": ["Զանգվածային նամակներ", "Թիրախավորված հարձակում կոնկրետ անձի վրա", "Հեռախոսային զանգ"],
             "answer": 1},
            {"id": 2, "question": "Ի՞նչ է Միջամուղային Հարձակումը.",
             "options": ["Կապի մեջտեղում միջամտություն", "Սերվերի անջատում", "Ֆայլերի կոդավորում"],
             "answer": 0},
            {"id": 3, "question": "Ի՞նչ է Բաշխված Ծառայությունից Հրաժարման Հարձակումը.",
             "options": ["Սերվերը ծանրաբեռնել կեղծ հարցումներով", "Գողանալ գաղտնաբառերը", "Ջնջել ֆայլերը"],
             "answer": 0},
            {"id": 4, "question": "Ո՞րն է Սպիտակ Գլխարկ հաքերի գործունեության հիմնական վարձատրությունը.",
             "options": ["Փրկագին", "Բագ Բաունթի (պարգևատրում խոցելիության համար)", "Գողացված տվյալների վաճառք"],
             "answer": 1},
            {"id": 5, "question": "Ի՞նչ է Սոցիալական Ինժեներիան.",
             "options": ["Հոգեբանական մանիպուլյացիա՝ տվյալներ կորզելու համար", "Ծրագրային հարձակում", "Ֆիզիկական գողություն"],
             "answer": 0},
            {"id": 6, "question": "Ի՞նչ է Փրկագնային Ծրագիրը.",
             "options": ["Ծրագիր, որը կոդավորում է ֆայլերը և փրկագին պահանջում", "Հակավիրուս", "Գովազդային ծրագիր"],
             "answer": 0},
            {"id": 7, "question": "Ո՞րն է Զրո-Օրյա Խոցելիությունը.",
             "options": ["Հայտնի և շտկված խոցելիություն", "Դեռևս անհայտ խոցելիություն", "Հին վիրուս"],
             "answer": 1},
            {"id": 8, "question": "Ի՞նչ է անհրաժեշտ կասկածելի կցված ֆայլի դեպքում.",
             "options": ["Բացել անմիջապես", "Ստուգել վիրուսով և չբացել անհայտ ուղարկողից", "Փոխանցել ուրիշներին"],
             "answer": 1},
            {"id": 9, "question": "Ի՞նչ է Գաղտնաբառերի Կառավարիչը.",
             "options": ["Ծրագիր, որը պահում է բոլոր գաղտնաբառերը անվտանգ", "Սոցցանց", "Խաղ"],
             "answer": 0},
            {"id": 10, "question": "Ի՞նչ է Հաքտիվիզմը.",
             "options": ["Ֆինանսական շահ", "Հարձակում քաղաքական կամ սոցիալական նպատակով", "Անձնական վրեժ"],
             "answer": 1},
        ]
    },
    "hard": {
        "label": "Բարդ",
        "time": 20,
        "points": 30,
        "questions": [
            {"id": 1, "question": "Ո՞ր տեխնոլոգիան է օգտագործում Սպիտակ Գլխարկ հաքերը՝ ցանց մուտք գործելու համար.",
             "options": ["SQL Ինյեկցիա", "Սոցիալական Ինժեներիա", "Ֆիշինգ", "Բոլորը ճիշտ են"],
             "answer": 3},
            {"id": 2, "question": "Ի՞նչ է Ռանսոմվեյրը տարբերվում սովորական վիրուսից.",
             "options": ["Ավելի արագ է տարածվում", "Կոդավորում է ֆայլերը և պահանջում փրկագին", "Չի վնասում համակարգին", "Միայն բանկերին է հարձակվում"],
             "answer": 1},
            {"id": 3, "question": "Ի՞նչ է Ապաթ Սպամի Տեխնիկան (APT).",
             "options": ["Մեկանգամյա հարձակում", "Երկարաժամկետ, նպատակաուղղված, բազմափուլ հարձակում", "Պատահական վիրուս", "Հրապարակային հարձակում"],
             "answer": 1},
            {"id": 4, "question": "Ի՞նչ է Սանդղակի (Sandbox) վերլուծությունը.",
             "options": ["Ծրագիրը գործարկել մեկուսացված միջավայրում", "Ջնջել ծրագիրը", "Կրկնօրինակել ծրագիրը", "Հրապարակել ծրագիրը"],
             "answer": 0},
            {"id": 5, "question": "Ի՞նչ է Քվանտային Հաշվարկի սպառնալիքը կրիպտոգրաֆիային.",
             "options": ["Դա չի սպառնում կրիպտոգրաֆիային", "Կոտրում է ասիմետրիկ գաղտնագրման ալգորիթմները", "Միայն ավելի արագ է", "Չի ազդում"],
             "answer": 1},
            {"id": 6, "question": "Ի՞նչ է Սերվերի Կողմի Հարցումների Կեղծումը (SSRF).",
             "options": ["Հաճախորդին ստիպել վնասակար հարցում ուղարկել", "Սերվերին ստիպել վնասակար հարցում ուղարկել ներքին ցանց", "Ֆայլ ներբեռնել", "Գաղտնաբառ գողանալ"],
             "answer": 1},
            {"id": 7, "question": "Ի՞նչ է Տվյալների Կանոնավոր Կորուստը (Data Loss Prevention - DLP).",
             "options": ["Համակարգ՝ գաղտնի տվյալների արտահոսքը կանխելու համար", "Հակավիրուս", "Պահուստային պատճեն", "VPN"],
             "answer": 0},
            {"id": 8, "question": "Ի՞նչ է Ռեֆլեքսիվ Ծրագրավորման Հարձակումը (XSS).",
             "options": ["Կոդ ներարկել վեբ էջում", "Գողանալ սերվերի տվյալները", "Անջատել ցանցը", "Փոխել գաղտնաբառը"],
             "answer": 0},
            {"id": 9, "question": "Ի՞նչ է Ռեգուլյար Ասիմետրիկ Կրիպտոգրաֆիայի Ալգորիթմը.",
             "options": ["AES (սիմետրիկ)", "RSA (ասիմետրիկ)", "MD5 (հեշ)", "SHA-256 (հեշ)"],
             "answer": 1},
            {"id": 10, "question": "Ի՞նչ է Տոկենի Կրկնակի Օգտագործման Հարձակումը (Replay Attack).",
             "options": ["Կրկին ուղարկել վավերական հաղորդագրություն", "Ջնջել տոկենը", "Կոտրել գաղտնաբառը", "Փոխել IP-ն"],
             "answer": 0},
            {"id": 11, "question": "Ի՞նչ է Սերվերի Կողմում Կաղապարների Ներարկումը (SSTI).",
             "options": ["Ներարկել վնասակար կոդ սերվերի կաղապարների մեջ", "Փոխել HTML", "Գողանալ Քուքի", "Անջատել սերվերը"],
             "answer": 0},
            {"id": 12, "question": "Ի՞նչ է Բիզնեսի Տրամաբանության Սխալը (Business Logic Flaw).",
             "options": ["Կոդի սխալ", "Բիզնես գործընթացի խախտում՝ առանց տեխնիկական սխալի", "Ցանցի խնդիր", "Սերվերի խափանում"],
             "answer": 1},
        ]
    }
}


# ============ ԼԻԴԵՐԲՈՐԴԻ ՖՈՒՆԿՑԻԱՆԵՐ ============
def load_leaderboard():
    """Կարդալ լիդերբորդը JSON ֆայլից"""
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_leaderboard(data):
    """Պահել լիդերբորդը JSON ֆայլում"""
    try:
        with open(LEADERBOARD_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"Չհաջողվեց պահել լիդերբորդը. {e}")


# ============ ԷՋԵՐ ============
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
    cases_data = [
        {"title": "ՎաննաԿրայ (2017)", "type": "Փրկագնային Ծրագիր", "year": "2017",
         "description": "Համաշխարհային Փրկագնային Ծրագրի հարձակում, որը վարակեց ավելի քան 200 000 համակարգեր 150-ից ավելի երկրներում։"},
        {"title": "Յահուի Տվյալների Արտահոսք (2013-2014)", "type": "Տվյալների Արտահոսք", "year": "2013",
         "description": "Բոլոր ժամանակների ամենամեծ տվյալների արտահոսքը. 3 միլիարդ օգտատերերի հաշիվներ գողացվեցին։"},
        {"title": "Սոնի Փիքչրսի Հարձակում (2014)", "type": "Հաքտիվիզմ", "year": "2014",
         "description": "Հսկայական ծավալի գաղտնի տվյալների արտահոսք, ներառյալ չթողարկված ֆիլմեր։"},
        {"title": "Թվիթերի Կրիպտո Խաբեություն (2020)", "type": "Սոցիալական Ինժեներիա", "year": "2020",
         "description": "Հաքերները կոտրեցին հայտնի մարդկանց Թվիթերի հաշիվները՝ տարածելով կեղծ կրիպտոարժույթային հղումներ։"},
        {"title": "Կոլոնիալ Փայփլայն (2021)", "type": "Փրկագնային Ծրագիր", "year": "2021",
         "description": "ԱՄՆ-ի ամենամեծ նավթամուղ ընկերության հարձակում, որը կաթվածահար արեց վառելիքի մատակարարումը։"},
        {"title": "Էքվիֆաքսի Արտահոսք (2017)", "type": "Տվյալների Արտահոսք", "year": "2017",
         "description": "147 միլիոն ամերիկացիների անձնական տվյալների արտահոսք։ Տուգանքը՝ 700 միլիոն դոլար։"},
    ]
    return render_template('cases.html', title="Իրական Քեյսեր", cyber_cases=cases_data)

@app.route('/defense')
def defense():
    return render_template('defense.html', title="Պաշտպանություն")

@app.route('/quiz')
def quiz():
    return render_template('quiz.html', title="Թեստ")

@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html', title="Լիդերբորդ")


# ============ API ՀԱՐՑՈՒՄՆԵՐ ============
@app.route('/api/questions/<difficulty>')
def get_questions(difficulty):
    """Վերադարձնել հարցերը ըստ բարդության մակարդակի"""
    if difficulty not in QUESTIONS_BY_DIFFICULTY:
        return jsonify({"error": "Սխալ բարդության մակարդակ"}), 404

    level = QUESTIONS_BY_DIFFICULTY[difficulty]
    # Ուղարկում ենք առանց ճիշտ պատասխանները ցույց տալու
    safe_questions = [
        {"id": q["id"], "question": q["question"], "options": q["options"]}
        for q in level["questions"]
    ]
    return jsonify({
        "difficulty": difficulty,
        "label": level["label"],
        "time": level["time"],
        "points": level["points"],
        "questions": safe_questions
    })


@app.route('/api/check', methods=['POST'])
def check_answer():
    """Ստուգել պատասխանը և վերադարձնել ճիշտ թե սխալ"""
    data = request.get_json()
    difficulty = data.get('difficulty')
    qid = data.get('question_id')
    selected = data.get('selected')

    if difficulty not in QUESTIONS_BY_DIFFICULTY:
        return jsonify({"error": "Սխալ բարդության մակարդակ"}), 400

    for q in QUESTIONS_BY_DIFFICULTY[difficulty]["questions"]:
        if q["id"] == qid:
            is_correct = (q["answer"] == selected)
            return jsonify({
                "correct": is_correct,
                "correct_index": q["answer"]
            })

    return jsonify({"error": "Հարցը չի գտնվել"}), 404


# ============ API ԼԻԴԵՐԲՈՐԴ ============
@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Վերադարձնել լավագույն 10 արդյունքները"""
    board = load_leaderboard()
    # Դասավորում ենք ըստ միավորների նվազման
    board.sort(key=lambda x: (x.get('score', 0), -x.get('time', 999)), reverse=True)
    return jsonify(board[:10])


@app.route('/api/leaderboard', methods=['POST'])
def add_to_leaderboard():
    """Ավելացնել նոր արդյունք լիդերբորդին"""
    data = request.get_json()

    name = (data.get('name') or '').strip()[:20]
    if not name:
        return jsonify({"error": "Անունը պարտադիր է"}), 400

    score = int(data.get('score', 0))
    difficulty = data.get('difficulty', 'easy')
    correct = int(data.get('correct', 0))
    total = int(data.get('total', 0))
    time_spent = float(data.get('time', 0))

    if difficulty not in QUESTIONS_BY_DIFFICULTY:
        difficulty = 'easy'

    entry = {
        "name": name,
        "score": score,
        "difficulty": difficulty,
        "difficulty_label": QUESTIONS_BY_DIFFICULTY[difficulty]["label"],
        "correct": correct,
        "total": total,
        "time": round(time_spent, 1),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    board = load_leaderboard()
    board.append(entry)
    # Պահում ենք միայն լավագույն 100-ը
    board.sort(key=lambda x: x.get('score', 0), reverse=True)
    board = board[:100]
    save_leaderboard(board)

    # Վերադարձնում ենք դիրքը լիդերբորդում
    board.sort(key=lambda x: (x.get('score', 0), -x.get('time', 999)), reverse=True)
    position = next((i + 1 for i, e in enumerate(board) if e == entry), None)

    return jsonify({
        "success": True,
        "position": position,
        "entry": entry
    })


if __name__ == '__main__':
    app.run(debug=True)
