import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, jsonify, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'kibervahan-secret-key-2026'

DB_PATH = 'leaderboard.db'

# ============ ԹԱՐԳՄԱՆՈՒԹՅՈՒՆՆԵՐ ============
TRANSLATIONS = {
    'hy': {
        'nav_home': 'Գլխավոր', 'nav_threats': 'Սպառնալիքներ', 'nav_hackers': 'Հաքերներ',
        'nav_phishing': 'Ֆիշինգ', 'nav_cases': 'Քեյսեր', 'nav_defense': 'Պաշտպանություն',
        'nav_quiz': 'Թեստ', 'nav_leaderboard': 'Առաջատարների Աղյուսակ',
        'footer_about': 'Նախագիծ՝ նվիրված կիբեռանվտանգությանը, ֆիշինգին և հաքերների աշխարհին։',
        'footer_sections': 'Բաժիններ', 'footer_contact': 'Կապ',
        'footer_copyright': '© 2026 ԿիբեռՎահան | ԹԳՀԳ նախագծային աշխատանք',
        'nav_theme': 'Թեմա', 'nav_sound_on': 'Ձայնը միացված է', 'nav_sound_off': 'Ձայնն անջատված է',
        'quiz_badge': 'Ինտերակտիվ Թեստ',
        'quiz_title': 'Ստուգիր Գիտելիքներդ',
        'quiz_subtitle': 'Ընտրիր բարդության մակարդակը, մուտքագրիր անունդ և մրցիր լավագույնների հետ',
        'quiz_select_diff': 'Ընտրիր Բարդության Մակարդակը',
        'quiz_select_diff_desc': 'Ամեն մակարդակ ունի իր ժամանակը, միավորները և հարցաքանակը',
        'quiz_easy': 'Հեշտ', 'quiz_easy_desc': 'Սկսնակների Համար',
        'quiz_medium': 'Միջին', 'quiz_medium_desc': 'Փորձառուների Համար',
        'quiz_hard': 'Բարդ', 'quiz_hard_desc': 'Մասնագետների Համար',
        'quiz_questions': 'Հարց', 'quiz_seconds': 'Մեկ Հարց', 'quiz_points': 'Միավոր',
        'quiz_select': 'Ընտրել', 'quiz_enter_name': 'Մուտքագրիր անունդ',
        'quiz_name_placeholder': 'Օրինակ՝ Անի կամ Արամ',
        'quiz_name_hint': 'Անունը կհայտնվի լիդերբորդում',
        'quiz_start': 'Սկսել Թեստը', 'quiz_score': 'Միավոր', 'quiz_correct': 'Ճիշտ',
        'quiz_question': 'ՀԱՐՑ', 'quiz_loading': 'Բեռնվում է...',
        'quiz_time_up': 'Ժամանակը սպառվեց', 'quiz_correct_msg': 'Ճիշտ է։',
        'quiz_wrong_msg': 'Սխալ է։', 'quiz_points_added': 'միավոր',
        'quiz_restart': 'Կրկին Փորձել', 'quiz_view_lb': 'Տեսնել Լիդերբորդը',
        'quiz_stat_correct': 'Ճիշտ Պատասխան', 'quiz_stat_time': 'Ծախսված Ժամանակ',
        'quiz_stat_rank': 'Տեղ Լիդերբորդում', 'quiz_score_unit': 'միավոր',
        'quiz_excellent': 'Հիանալի է։', 'quiz_excellent_sub': 'Դու իսկական մասնագետ ես։',
        'quiz_great': 'Շատ լավ է։', 'quiz_great_sub': 'Մի փոքր էլ ջանք ու դու կհասնես գագաթին։',
        'quiz_good': 'Լավ է։', 'quiz_good_sub': 'Կարող ես ավելի լավ։ Փորձիր նորից։',
        'quiz_learn': 'Շարունակիր Սովորել։', 'quiz_learn_sub': 'Նայիր մյուս բաժինները և փորձիր նորից։',
        'lb_badge': 'Փառքի Սրահ', 'lb_title': 'Առաջատարների Աղյուսակ',
        'lb_subtitle': 'Լավագույն խաղացողները բոլոր բարդության մակարդակներից',
        'lb_all': 'Բոլորը', 'lb_easy': 'Հեշտ', 'lb_medium': 'Միջին', 'lb_hard': 'Բարդ',
        'lb_player': 'Խաղացող', 'lb_level': 'Մակարդակ', 'lb_score': 'Միավոր',
        'lb_correct': 'Ճիշտ', 'lb_time': 'Ժամանակ', 'lb_date': 'Ամսաթիվ',
        'lb_loading': 'Բեռնվում է...', 'lb_empty': 'Դեռևս արդյունքներ չկան',
        'lb_empty_desc': 'Եղիր առաջինը ով կգրանցի իր անունը լիդերբորդում',
        'lb_start_quiz': 'Սկսել Թեստը',
    },
    'en': {
        'nav_home': 'Home', 'nav_threats': 'Threats', 'nav_hackers': 'Hackers',
        'nav_phishing': 'Phishing', 'nav_cases': 'Cases', 'nav_defense': 'Defense',
        'nav_quiz': 'Quiz', 'nav_leaderboard': 'Leaderboard',
        'footer_about': 'A project dedicated to cybersecurity, phishing and the world of hackers.',
        'footer_sections': 'Sections', 'footer_contact': 'Contact',
        'footer_copyright': '© 2026 CyberShield | Educational Project',
        'nav_theme': 'Theme', 'nav_sound_on': 'Sound On', 'nav_sound_off': 'Sound Off',
        'quiz_badge': 'Interactive Quiz',
        'quiz_title': 'Test Your Knowledge',
        'quiz_subtitle': 'Choose a difficulty level, enter your name and compete with the best',
        'quiz_select_diff': 'Choose Difficulty Level',
        'quiz_select_diff_desc': 'Each level has its own time, points and questions',
        'quiz_easy': 'Easy', 'quiz_easy_desc': 'For Beginners',
        'quiz_medium': 'Medium', 'quiz_medium_desc': 'For Experienced',
        'quiz_hard': 'Hard', 'quiz_hard_desc': 'For Experts',
        'quiz_questions': 'Questions', 'quiz_seconds': 'Per Question', 'quiz_points': 'Points',
        'quiz_select': 'Select', 'quiz_enter_name': 'Enter your name',
        'quiz_name_placeholder': 'e.g. Ani or Aram',
        'quiz_name_hint': 'Your name will appear on the leaderboard',
        'quiz_start': 'Start Quiz', 'quiz_score': 'Score', 'quiz_correct': 'Correct',
        'quiz_question': 'QUESTION', 'quiz_loading': 'Loading...',
        'quiz_time_up': 'Time is up', 'quiz_correct_msg': 'Correct!',
        'quiz_wrong_msg': 'Wrong!', 'quiz_points_added': 'points',
        'quiz_restart': 'Try Again', 'quiz_view_lb': 'View Leaderboard',
        'quiz_stat_correct': 'Correct Answers', 'quiz_stat_time': 'Time Spent',
        'quiz_stat_rank': 'Leaderboard Rank', 'quiz_score_unit': 'points',
        'quiz_excellent': 'Excellent!', 'quiz_excellent_sub': 'You are a true expert.',
        'quiz_great': 'Very Good!', 'quiz_great_sub': 'A bit more effort and you will reach the top.',
        'quiz_good': 'Good!', 'quiz_good_sub': 'You can do better. Try again.',
        'quiz_learn': 'Keep Learning.', 'quiz_learn_sub': 'Check other sections and try again.',
        'lb_badge': 'Hall of Fame', 'lb_title': 'Leaderboard',
        'lb_subtitle': 'Top players from all difficulty levels',
        'lb_all': 'All', 'lb_easy': 'Easy', 'lb_medium': 'Medium', 'lb_hard': 'Hard',
        'lb_player': 'Player', 'lb_level': 'Level', 'lb_score': 'Score',
        'lb_correct': 'Correct', 'lb_time': 'Time', 'lb_date': 'Date',
        'lb_loading': 'Loading...', 'lb_empty': 'No results yet',
        'lb_empty_desc': 'Be the first to register your name on the leaderboard',
        'lb_start_quiz': 'Start Quiz',
    },
    'ru': {
        'nav_home': 'Главная', 'nav_threats': 'Угрозы', 'nav_hackers': 'Хакеры',
        'nav_phishing': 'Фишинг', 'nav_cases': 'Кейсы', 'nav_defense': 'Защита',
        'nav_quiz': 'Тест', 'nav_leaderboard': 'Рейтинг',
        'footer_about': 'Проект, посвященный кибербезопасности, фишингу и миру хакеров.',
        'footer_sections': 'Разделы', 'footer_contact': 'Контакты',
        'footer_copyright': '© 2026 КиберЩит | Учебный проект',
        'nav_theme': 'Тема', 'nav_sound_on': 'Звук включен', 'nav_sound_off': 'Звук выключен',
        'quiz_badge': 'Интерактивный Тест',
        'quiz_title': 'Проверь Свои Знания',
        'quiz_subtitle': 'Выбери уровень сложности, введи имя и соревнуйся с лучшими',
        'quiz_select_diff': 'Выбери Уровень Сложности',
        'quiz_select_diff_desc': 'У каждого уровня свое время, очки и количество вопросов',
        'quiz_easy': 'Легкий', 'quiz_easy_desc': 'Для Начинающих',
        'quiz_medium': 'Средний', 'quiz_medium_desc': 'Для Опытных',
        'quiz_hard': 'Сложный', 'quiz_hard_desc': 'Для Экспертов',
        'quiz_questions': 'Вопросов', 'quiz_seconds': 'На Вопрос', 'quiz_points': 'Очков',
        'quiz_select': 'Выбрать', 'quiz_enter_name': 'Введи свое имя',
        'quiz_name_placeholder': 'Например: Ани или Арам',
        'quiz_name_hint': 'Имя появится в рейтинге',
        'quiz_start': 'Начать Тест', 'quiz_score': 'Очки', 'quiz_correct': 'Верно',
        'quiz_question': 'ВОПРОС', 'quiz_loading': 'Загрузка...',
        'quiz_time_up': 'Время вышло', 'quiz_correct_msg': 'Верно!',
        'quiz_wrong_msg': 'Неверно!', 'quiz_points_added': 'очков',
        'quiz_restart': 'Попробовать Снова', 'quiz_view_lb': 'Смотреть Рейтинг',
        'quiz_stat_correct': 'Верных Ответов', 'quiz_stat_time': 'Затрачено Времени',
        'quiz_stat_rank': 'Место в Рейтинге', 'quiz_score_unit': 'очков',
        'quiz_excellent': 'Отлично!', 'quiz_excellent_sub': 'Ты настоящий эксперт.',
        'quiz_great': 'Очень Хорошо!', 'quiz_great_sub': 'Еще немного усилий и ты достигнешь вершины.',
        'quiz_good': 'Хорошо!', 'quiz_good_sub': 'Можешь лучше. Попробуй снова.',
        'quiz_learn': 'Продолжай Учиться.', 'quiz_learn_sub': 'Посмотри другие разделы и попробуй снова.',
        'lb_badge': 'Зал Славы', 'lb_title': 'Рейтинг',
        'lb_subtitle': 'Лучшие игроки всех уровней сложности',
        'lb_all': 'Все', 'lb_easy': 'Легкий', 'lb_medium': 'Средний', 'lb_hard': 'Сложный',
        'lb_player': 'Игрок', 'lb_level': 'Уровень', 'lb_score': 'Очки',
        'lb_correct': 'Верно', 'lb_time': 'Время', 'lb_date': 'Дата',
        'lb_loading': 'Загрузка...', 'lb_empty': 'Пока нет результатов',
        'lb_empty_desc': 'Стань первым, кто зарегистрирует свое имя в рейтинге',
        'lb_start_quiz': 'Начать Тест',
    }
}


# ============ SQLite ՏՎՅԱԼՆԵՐԻ ԲԱԶԱ ============
def init_db():
    """Ստեղծել աղյուսակը եթե գոյություն չունի"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS leaderboard (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            score INTEGER NOT NULL,
            difficulty TEXT NOT NULL,
            difficulty_label TEXT,
            correct INTEGER,
            total INTEGER,
            time REAL,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ============ ՀԱՐՑԵՐԻ ԲԱԶԱ ============
QUESTIONS_BY_DIFFICULTY = {
    "easy": {
        "label_hy": "Հեշտ", "label_en": "Easy", "label_ru": "Легкий",
        "time": 30, "points": 10,
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
        "label_hy": "Միջին", "label_en": "Medium", "label_ru": "Средний",
        "time": 25, "points": 20,
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
        "label_hy": "Բարդ", "label_en": "Hard", "label_ru": "Сложный",
        "time": 20, "points": 30,
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
            {"id": 7, "question": "Ի՞նչ է Տվյալների Կանոնավոր Կորուստը (DLP).",
             "options": ["Համակարգ՝ գաղտնի տվյալների արտահոսքը կանխելու համար", "Հակավիրուս", "Պահուստային պատճեն", "VPN"],
             "answer": 0},
            {"id": 8, "question": "Ի՞նչ է Ռեֆլեքսիվ Ծրագրավորման Հարձակումը (XSS).",
             "options": ["Կոդ ներարկել վեբ էջում", "Գողանալ սերվերի տվյալները", "Անջատել ցանցը", "Փոխել գաղտնաբառը"],
             "answer": 0},
            {"id": 9, "question": "Ո՞րն է ասիմետրիկ կրիպտոգրաֆիայի ալգորիթմը.",
             "options": ["AES", "RSA", "MD5", "SHA-256"],
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


# ============ ՀԱՄԱՏԵՔՍՏԻ ՊՐՈՑԵՍՈՐ ============
@app.context_processor
def inject_translations():
    lang = session.get('lang', 'hy')
    if lang not in TRANSLATIONS:
        lang = 'hy'
    return {'t': TRANSLATIONS[lang], 'lang': lang}


@app.route('/set-language/<lang>')
def set_language(lang):
    if lang in TRANSLATIONS:
        session['lang'] = lang
    return redirect(request.referrer or url_for('home'))


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
    lang = session.get('lang', 'hy')
    if difficulty not in QUESTIONS_BY_DIFFICULTY:
        return jsonify({"error": "Սխալ բարդության մակարդակ"}), 404

    level = QUESTIONS_BY_DIFFICULTY[difficulty]
    safe_questions = [
        {"id": q["id"], "question": q["question"], "options": q["options"]}
        for q in level["questions"]
    ]
    label_key = f"label_{lang}"
    label = level.get(label_key, level["label_hy"])
    return jsonify({
        "difficulty": difficulty,
        "label": label,
        "time": level["time"],
        "points": level["points"],
        "questions": safe_questions
    })


@app.route('/api/check', methods=['POST'])
def check_answer():
    data = request.get_json()
    difficulty = data.get('difficulty')
    qid = data.get('question_id')
    selected = data.get('selected')

    if difficulty not in QUESTIONS_BY_DIFFICULTY:
        return jsonify({"error": "Սխալ բարդության մակարդակ"}), 400

    for q in QUESTIONS_BY_DIFFICULTY[difficulty]["questions"]:
        if q["id"] == qid:
            return jsonify({
                "correct": (q["answer"] == selected),
                "correct_index": q["answer"]
            })

    return jsonify({"error": "Հարցը չի գտնվել"}), 404


# ============ API ԼԻԴԵՐԲՈՐԴ ============
@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('''
            SELECT name, score, difficulty, difficulty_label, correct, total, time, date
            FROM leaderboard
            ORDER BY score DESC, time ASC
            LIMIT 100
        ''')
        rows = c.fetchall()
        conn.close()

        result = []
        for r in rows:
            result.append({
                "name": r["name"],
                "score": r["score"],
                "difficulty": r["difficulty"],
                "difficulty_label": r["difficulty_label"],
                "correct": r["correct"],
                "total": r["total"],
                "time": r["time"],
                "date": r["date"]
            })
        return jsonify(result[:10])
    except Exception as e:
        print(f"Լիդերբորդի սխալ. {e}")
        return jsonify([])


@app.route('/api/leaderboard', methods=['POST'])
def add_to_leaderboard():
    try:
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

        lang = session.get('lang', 'hy')
        label_key = f"label_{lang}"
        diff_label = QUESTIONS_BY_DIFFICULTY[difficulty].get(
            label_key,
            QUESTIONS_BY_DIFFICULTY[difficulty]["label_hy"]
        )

        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")

        conn = get_db()
        c = conn.cursor()
        c.execute('''
            INSERT INTO leaderboard (name, score, difficulty, difficulty_label, correct, total, time, date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, score, difficulty, diff_label, correct, total, round(time_spent, 1), date_str))
        conn.commit()

        # Գտնում ենք տեղը
        c.execute('''
            SELECT COUNT(*) + 1 AS pos FROM leaderboard
            WHERE score > ? OR (score = ? AND time < ?)
        ''', (score, score, time_spent))
        position = c.fetchone()["pos"]
        conn.close()

        return jsonify({
            "success": True,
            "position": position,
            "entry": {
                "name": name, "score": score, "difficulty": difficulty,
                "correct": correct, "total": total, "time": round(time_spent, 1),
                "date": date_str
            }
        })
    except Exception as e:
        print(f"Ավելացման սխալ. {e}")
        return jsonify({"error": "Սերվերի սխալ"}), 500


# Մեկնարկին ստեղծում ենք DB-ն
init_db()

if __name__ == '__main__':
    app.run(debug=True)
