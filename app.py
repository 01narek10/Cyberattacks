import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, jsonify, request, session, redirect, url_for

# Փորձում ենք բեռնել psycopg2 (PostgreSQL-ի համար)
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

app = Flask(__name__)
app.secret_key = 'kibervahan-secret-key-2026'

# Տվյալների բազայի կարգավորում
DATABASE_URL = os.environ.get('DATABASE_URL')
USE_POSTGRES = bool(DATABASE_URL and HAS_POSTGRES)
SQLITE_PATH = 'leaderboard.db'


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
        'quiz_name_hint': 'Անունը կհայտնվի առաջատարների աղյուսակում',
        'quiz_start': 'Սկսել Թեստը', 'quiz_score': 'Միավոր', 'quiz_correct': 'Ճիշտ',
        'quiz_question': 'ՀԱՐՑ', 'quiz_loading': 'Բեռնվում է...',
        'quiz_time_up': 'Ժամանակը սպառվեց', 'quiz_correct_msg': 'Ճիշտ է։',
        'quiz_wrong_msg': 'Սխալ է։', 'quiz_points_added': 'միավոր',
        'quiz_restart': 'Կրկին Փորձել', 'quiz_view_lb': 'Տեսնել Առաջատարներին',
        'quiz_stat_correct': 'Ճիշտ Պատասխան', 'quiz_stat_time': 'Ծախսված Ժամանակ',
        'quiz_stat_rank': 'Տեղ Աղյուսակում', 'quiz_score_unit': 'միավոր',
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
        'lb_empty_desc': 'Եղիր առաջինը ով կգրանցի իր անունը աղյուսակում',
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
        'quiz_badge': 'Interactive Quiz', 'quiz_title': 'Test Your Knowledge',
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
        'quiz_badge': 'Интерактивный Тест', 'quiz_title': 'Проверь Свои Знания',
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


# ============ ՏՎՅԱԼՆԵՐԻ ԲԱԶԱՅԻ ՖՈՒՆԿՑԻԱՆԵՐ ============
def get_connection():
    """Վերադարձնում է տվյալների բազայի կապը (Postgres կամ SQLite)"""
    if USE_POSTGRES:
        return psycopg2.connect(DATABASE_URL)
    else:
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        return conn


def init_db():
    """Ստեղծել աղյուսակը եթե գոյություն չունի"""
    try:
        conn = get_connection()
        c = conn.cursor()

        if USE_POSTGRES:
            c.execute('''
                CREATE TABLE IF NOT EXISTS leaderboard (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(20) NOT NULL,
                    score INTEGER NOT NULL,
                    difficulty VARCHAR(20) NOT NULL,
                    difficulty_label VARCHAR(50),
                    correct INTEGER,
                    total INTEGER,
                    time REAL,
                    date VARCHAR(30)
                )
            ''')
        else:
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
        print(f"✅ Տվյալների բազան պատրաստ է ({'PostgreSQL' if USE_POSTGRES else 'SQLite'})")
    except Exception as e:
        print(f"❌ Տվյալների բազայի սխալ. {e}")


def execute_query(query, params=None, fetch=False, fetch_one=False):
    """Ունիվերսալ ֆունկցիա query-ների համար"""
    conn = get_connection()
    try:
        if USE_POSTGRES:
            c = conn.cursor(cursor_factory=RealDictCursor)
        else:
            c = conn.cursor()

        # Postgres-ը օգտագործում է %s, SQLite-ը՝ ?
        if USE_POSTGRES and params:
            query = query.replace('?', '%s')

        c.execute(query, params or ())

        result = None
        if fetch:
            result = [dict(row) for row in c.fetchall()]
        elif fetch_one:
            row = c.fetchone()
            result = dict(row) if row else None

        if not fetch and not fetch_one:
            conn.commit()

        return result
    finally:
        conn.close()


# ============ ՀԱՐՑԵՐԻ ԲԱԶԱ (ՄԻՋԱԶԳԱՅԻՆ ՍՏԱՆԴԱՐՏՆԵՐՈՎ) ============
# Աղբյուրներ: OWASP Top 10 (2021), NIST SP 800-63B Rev.4, NIST CSF 2.0,
# ENISA Threat Landscape 2025, CISA, FBI IC3 2025, CompTIA Security+
QUESTIONS_BY_DIFFICULTY = {
    "easy": {
        "label_hy": "Հեշտ", "label_en": "Easy", "label_ru": "Легкий",
        "time": 30, "points": 10,
        "questions": [
            {
                "id": 1,
                "question": {
                    "hy": "Ո՞րն է ամենաապահով գաղտնաբառը՝ համաձայն NIST SP 800-63B Rev.4 (2025) ուղեցույցի:",
                    "en": "Which password is most secure according to NIST SP 800-63B Rev.4 (2025)?",
                    "ru": "Какой пароль самый надежный согласно NIST SP 800-63B Rev.4 (2025)?"
                },
                "options": {
                    "hy": ["Ձեր անունը և ծննդյան տարեթիվը", "Առնվազն 15 նիշ՝ մեծատառ, փոքրատառ, թվեր և սիմվոլներ", "Հեշտ հիշվող բառ առանց թվերի"],
                    "en": ["Your name and birth year", "At least 15 characters with uppercase, lowercase, numbers and symbols", "An easy-to-remember word without numbers"],
                    "ru": ["Ваше имя и год рождения", "Минимум 15 символов: заглавные, строчные, цифры и символы", "Легкое запоминающееся слово без цифр"]
                },
                "answer": 1
            },
            {
                "id": 2,
                "question": {
                    "hy": "Ի՞նչ է Երկփուլանի Վավերացումը (MFA) և ինչո՞ւ է CISA-ն այն համարում «ոսկե ստանդարտ»:",
                    "en": "What is Multi-Factor Authentication (MFA) and why does CISA call it the 'gold standard'?",
                    "ru": "Что такое Многофакторная Аутентификация (MFA) и почему CISA называет её 'золотым стандартом'?"
                },
                "options": {
                    "hy": ["Երկու տարբեր գաղտնաբառի օգտագործում", "Հաշվի կրկնակի գրանցում", "Լրացուցիչ անվտանգության շերտ՝ գաղտնաբառից բացի երկրորդ ապացույց (FIDO2, YubiKey)"],
                    "en": ["Using two different passwords", "Registering the account twice", "An extra security layer requiring a second proof (FIDO2, YubiKey) besides the password"],
                    "ru": ["Использование двух разных паролей", "Двойная регистрация аккаунта", "Дополнительный уровень безопасности: второе доказательство помимо пароля (FIDO2, YubiKey)"]
                },
                "answer": 2
            },
            {
                "id": 3,
                "question": {
                    "hy": "Ի՞նչ է Ֆիշինգը՝ համաձայն CISA-ի սահմանման:",
                    "en": "What is Phishing according to CISA's definition?",
                    "ru": "Что такое Фишинг согласно определению CISA?"
                },
                "options": {
                    "hy": ["Խաբեություն, որով հանցագործը ներկայանում է վստահելի աղբյուր և կորզում է գաղտնի տվյալներ", "Համակարգչի ֆիզիկական գողություն", "Ծրագրային ապահովման անվճար տարածում"],
                    "en": ["A scam where the attacker poses as a trusted source to extract confidential data", "Physical theft of a computer", "Free distribution of software"],
                    "ru": ["Мошенничество, при котором злоумышленник выдает себя за надежный источник", "Физическая кража компьютера", "Бесплатное распространение ПО"]
                },
                "answer": 0
            },
            {
                "id": 4,
                "question": {
                    "hy": "Ո՞րն է ENISA 2025 հաշվետվության համաձայն ամենատարածված հարձակման տեսակը (77%)?",
                    "en": "According to ENISA 2025, which is the most common attack type (77%)?",
                    "ru": "Согласно ENISA 2025, какой тип атак самый распространенный (77%)?"
                },
                "options": {
                    "hy": ["Ransomware", "DDoS (Բաշխված Ծառայությունից Հրաժարում)", "Phishing"],
                    "en": ["Ransomware", "DDoS (Distributed Denial of Service)", "Phishing"],
                    "ru": ["Ransomware", "DDoS (Распределенная атака отказа в обслуживании)", "Фишинг"]
                },
                "answer": 1
            },
            {
                "id": 5,
                "question": {
                    "hy": "Ի՞նչ է Փրկագնային Ծրագիրը (Ransomware)՝ համաձայն ENISA 2025-ի:",
                    "en": "What is Ransomware according to ENISA 2025?",
                    "ru": "Что такое Программа-вымогатель (Ransomware) согласно ENISA 2025?"
                },
                "options": {
                    "hy": ["Հակավիրուսային ծրագիր", "Malware, որը կոդավորում է ֆայլերը և պահանջում է փրկագին", "Պահուստային պատճենող գործիք", "Գովազդային ծրագիր"],
                    "en": ["An antivirus program", "Malware that encrypts files and demands ransom", "A backup tool", "An advertising program"],
                    "ru": ["Антивирусная программа", "Вредоносное ПО, шифрующее файлы и требующее выкуп", "Инструмент резервного копирования", "Рекламная программа"]
                },
                "answer": 1
            },
            {
                "id": 6,
                "question": {
                    "hy": "Ի՞նչ է նշանակում HTTPS-ը վեբ կայքի հասցեում:",
                    "en": "What does HTTPS in a website address mean?",
                    "ru": "Что означает HTTPS в адресе сайта?"
                },
                "options": {
                    "hy": ["Կայքի արագության ցուցիչ", "Կայքի տարիքը", "Տվյալների ապահով գաղտնագրված փոխանցման արձանագրություն"],
                    "en": ["A speed indicator of the site", "The age of the site", "A secure encrypted data transfer protocol"],
                    "ru": ["Показатель скорости сайта", "Возраст сайта", "Протокол защищенной шифрованной передачи данных"]
                },
                "answer": 2
            },
            {
                "id": 7,
                "question": {
                    "hy": "Ինչո՞ւ է վտանգավոր հանրային Wi-Fi ցանցում մուտքագրել բանկային տվյալներ:",
                    "en": "Why is it dangerous to enter banking data on public Wi-Fi?",
                    "ru": "Почему опасно вводить банковские данные в публичном Wi-Fi?"
                },
                "options": {
                    "hy": ["Ցանցը դանդաղ է աշխատում", "Հաքերը կարող է գաղտնալսել չգաղտնագրված տվյալները (MitM հարձակում)", "Բանկը չի թույլատրում"],
                    "en": ["The network is slow", "An attacker can intercept unencrypted data (MitM attack)", "The bank does not allow it"],
                    "ru": ["Сеть работает медленно", "Злоумышленник может перехватить незашифрованные данные (атака MitM)", "Банк не разрешает"]
                },
                "answer": 1
            },
            {
                "id": 8,
                "question": {
                    "hy": "Ինչո՞ւ է կարևոր ծրագրային թարմացումները տեղադրել ժամանակին՝ համաձայն NIST CSF 2.0-ի:",
                    "en": "Why is it important to install software updates on time according to NIST CSF 2.0?",
                    "ru": "Почему важно своевременно устанавливать обновления согласно NIST CSF 2.0?"
                },
                "options": {
                    "hy": ["Միայն նոր դիզայն ավելացնելու համար", "Դրանք փակում են հայտնի անվտանգության խոցելիությունները", "Դա պարտադիր չէ", "Միայն արագության համար"],
                    "en": ["Only to add a new design", "They patch known security vulnerabilities", "It is not necessary", "Only for speed"],
                    "ru": ["Только для нового дизайна", "Они закрывают известные уязвимости безопасности", "Это не обязательно", "Только для скорости"]
                },
                "answer": 1
            },
            {
                "id": 9,
                "question": {
                    "hy": "Ի՞նչ է Հրադադարը (Firewall) ցանցային անվտանգության մեջ:",
                    "en": "What is a Firewall in network security?",
                    "ru": "Что такое Файрвол в сетевой безопасности?"
                },
                "options": {
                    "hy": ["Համակարգ, որը վերահսկում և ֆիլտրում է ցանցային տրաֿֆիկը կանոնների հիման վրա", "Ֆիզիկական պատ", "Անլար ցանց", "Ամպային պահոց"],
                    "en": ["A system that monitors and filters network traffic based on rules", "A physical wall", "A wireless network", "A cloud storage"],
                    "ru": ["Система, контролирующая и фильтрующая трафик на основе правил", "Физическая стена", "Беспроводная сеть", "Облачное хранилище"]
                },
                "answer": 0
            },
            {
                "id": 10,
                "question": {
                    "hy": "Ի՞նչ է Սպիտակ Գլխարկ (White Hat) հաքերը:",
                    "en": "What is a White Hat hacker?",
                    "ru": "Кто такой Белый Хакер (White Hat)?"
                },
                "options": {
                    "hy": ["Չարագործ, որը կոտրում է համակարգերը", "Էթիկական մասնագետ, որը աշխատում է օրինական պայմանագրով՝ գտնելու խոցելիությունները", "Վիրուս ստեղծող"],
                    "en": ["A criminal who breaks into systems", "An ethical specialist working under legal contract to find vulnerabilities", "A virus creator"],
                    "ru": ["Преступник, взламывающий системы", "Этичный специалист, работающий по легальному контракту", "Создатель вирусов"]
                },
                "answer": 1
            }
        ]
    },
    "medium": {
        "label_hy": "Միջին", "label_en": "Medium", "label_ru": "Средний",
        "time": 25, "points": 20,
        "questions": [
            {
                "id": 1,
                "question": {
                    "hy": "Ինչո՞վ է Նշանառու Ֆիշինգը (Spear Phishing) տարբերվում սովորական Ֆիշինգից:",
                    "en": "How does Spear Phishing differ from regular Phishing?",
                    "ru": "Чем Целевой Фишинг отличается от обычного?"
                },
                "options": {
                    "hy": ["Ուղարկվում է զանգվածաբար բոլորին", "Թիրախավորում է կոնկրետ անձի՝ օգտագործելով իրական անուններ և պաշտոններ", "Միայն հեռախոսով է իրականացվում", "Օգտագործում է միայն վիրուսներ"],
                    "en": ["Sent massively to everyone", "Targets a specific person using real names and job titles", "Performed only by phone", "Uses only viruses"],
                    "ru": ["Отправляется массово всем", "Нацелен на конкретное лицо, используя реальные имена и должности", "Осуществляется только по телефону", "Использует только вирусы"]
                },
                "answer": 1
            },
            {
                "id": 2,
                "question": {
                    "hy": "Ի՞նչ է Միջամուղային Հարձակումը (MitM)՝ համաձայն NIST-ի:",
                    "en": "What is a Man-in-the-Middle (MitM) attack according to NIST?",
                    "ru": "Что такое атака «Человек-посередине» (MitM) согласно NIST?"
                },
                "options": {
                    "hy": ["Սերվերի ֆիզիկական գողություն", "Հանցագործը գաղտնի միջամտում է երկու կողմերի կապին և գաղտնալսում կամ փոփոխում է փոխանցվող տվյալները", "Համակարգչի վերագործարկում", "Կեղծ կայքի ստեղծում"],
                    "en": ["Physical theft of the server", "The attacker secretly intercepts communication between two parties and eavesdrops or modifies transmitted data", "Rebooting the computer", "Creating a fake website"],
                    "ru": ["Физическая кража сервера", "Злоумышленник тайно вмешивается в связь между двумя сторонами и перехватывает или изменяет данные", "Перезагрузка компьютера", "Создание поддельного сайта"]
                },
                "answer": 1
            },
            {
                "id": 3,
                "question": {
                    "hy": "Ի՞նչ է Բաշխված Ծառայությունից Հրաժարման Հարձակումը (DDoS)՝ ըստ ENISA 2025-ի:",
                    "en": "What is a Distributed Denial of Service (DDoS) attack according to ENISA 2025?",
                    "ru": "Что такое Распределенная атака отказа в обслуживании (DDoS) согласно ENISA 2025?"
                },
                "options": {
                    "hy": ["Սերվերի ֆայլերի ջնջում", "Մեկ հաքեր կոտրում է սերվերը", "Հազարավոր վարակված սարքեր միաժամանակ հարցումներ են ուղարկում սերվերին՝ խափանելով նրա աշխատանքը", "Գաղտնաբառերի գողություն"],
                    "en": ["Deleting server files", "One hacker breaks into the server", "Thousands of infected devices send simultaneous requests to the server, disrupting its operation", "Password theft"],
                    "ru": ["Удаление файлов сервера", "Один хакер взламывает сервер", "Тысячи зараженных устройств одновременно отправляют запросы серверу, нарушая его работу", "Кража паролей"]
                },
                "answer": 2
            },
            {
                "id": 4,
                "question": {
                    "hy": "Ի՞նչ է Bug Bounty ծրագիրը՝ համաձայն CISA-ի:",
                    "en": "What is a Bug Bounty program according to CISA?",
                    "ru": "Что такое программа Bug Bounty согласно CISA?"
                },
                "options": {
                    "hy": ["Ծրագրային ապահովման անվճար բաշխում", "Ընկերությունները վճարում են էթիկական հաքերներին՝ հայտնաբերված խոցելիությունների համար", "Վիրուսների մրցույթ", "Խաղերի մշակում"],
                    "en": ["Free software distribution", "Companies pay ethical hackers for discovered security vulnerabilities", "A virus competition", "Game development"],
                    "ru": ["Бесплатное распространение ПО", "Компании платят этичным хакерам за найденные уязвимости", "Конкурс вирусов", "Разработка игр"]
                },
                "answer": 1
            },
            {
                "id": 5,
                "question": {
                    "hy": "Ի՞նչ է Սոցիալական Ինժեներիան՝ համաձայն NIST SP 800-61-ի:",
                    "en": "What is Social Engineering according to NIST SP 800-61?",
                    "ru": "Что такое Социальная Инженерия согласно NIST SP 800-61?"
                },
                "options": {
                    "hy": ["Հոգեբանական մանիպուլյացիա՝ մարդուն ստիպելու բացահայտել գաղտնի տվյալներ", "Սոցիալական ցանցերի ալգորիթմ", "Ցանցային արձանագրություն", "Ծրագրավորման մեթոդ"],
                    "en": ["Psychological manipulation to trick a person into revealing confidential data", "A social network algorithm", "A network protocol", "A programming method"],
                    "ru": ["Психологическая манипуляция для получения конфиденциальных данных", "Алгоритм соцсетей", "Сетевой протокол", "Метод программирования"]
                },
                "answer": 0
            },
            {
                "id": 6,
                "question": {
                    "hy": "Ի՞նչ է Զրո-Օրյա (Zero-Day) խոցելիությունը՝ համաձայն MITRE ATT&CK-ի:",
                    "en": "What is a Zero-Day vulnerability according to MITRE ATT&CK?",
                    "ru": "Что такое уязвимость Нулевого дня согласно MITRE ATT&CK?"
                },
                "options": {
                    "hy": ["Հայտնի խոցելիություն, որն արդեն շտկվել է", "Անհայտ խոցելիություն, որի համար դեռ արտադրողը թարմացում չի թողարկել", "Ծրագրային սխալ՝ առանց անվտանգության նշանակության", "Հին վիրուս"],
                    "en": ["A known vulnerability that has been patched", "An unknown vulnerability for which the vendor has not yet released a fix", "A software bug with no security impact", "An old virus"],
                    "ru": ["Известная исправленная уязвимость", "Неизвестная уязвимость, для которой разработчик еще не выпустил обновление", "Ошибка без влияния на безопасность", "Старый вирус"]
                },
                "answer": 1
            },
            {
                "id": 7,
                "question": {
                    "hy": "Ինչո՞ւ է NIST-ը խորհուրդ տալիս օգտագործել Գաղտնաբառերի Կառավարիչ:",
                    "en": "Why does NIST recommend using a Password Manager?",
                    "ru": "Почему NIST рекомендует использовать Менеджер Паролей?"
                },
                "options": {
                    "hy": ["Բարձրացնում է ինտերնետի արագությունը", "Գեներացնում է եզակի, բարդ գաղտնաբառեր և դրանք պահում է գաղտնագրված պահոցում", "Ավտոմատ մաքրում է բրաուզերի պատմությունը", "Փոխարինում է անտիվիրուսին"],
                    "en": ["Increases internet speed", "Generates unique, complex passwords and stores them in an encrypted vault", "Automatically clears browser history", "Replaces antivirus"],
                    "ru": ["Повышает скорость интернета", "Генерирует уникальные сложные пароли и хранит их в зашифрованном хранилище", "Автоматически очищает историю браузера", "Заменяет антивирус"]
                },
                "answer": 1
            },
            {
                "id": 8,
                "question": {
                    "hy": "Ի՞նչ է Հաքտիվիզմը (Hacktivism)՝ ըստ ENISA 2025-ի:",
                    "en": "What is Hacktivism according to ENISA 2025?",
                    "ru": "Что такое Хактивизм согласно ENISA 2025?"
                },
                "options": {
                    "hy": ["Անձնական ֆինանսական շահ", "Ծրագրավորման ոճ", "Հաքերային հարձակում՝ քաղաքական կամ սոցիալական նպատակներով (օրինակ՝ Anonymous)", "Խաղային մրցույթ"],
                    "en": ["Personal financial gain", "A programming style", "Hacking attacks for political or social purposes (e.g., Anonymous)", "A gaming competition"],
                    "ru": ["Личная финансовая выгода", "Стиль программирования", "Хакерские атаки в политических или социальных целях (например, Anonymous)", "Игровой конкурс"]
                },
                "answer": 2
            },
            {
                "id": 9,
                "question": {
                    "hy": "Ի՞նչ է Կրիպտոգրաֆիան՝ ըստ NIST-ի սահմանման:",
                    "en": "What is Cryptography according to NIST's definition?",
                    "ru": "Что такое Криптография согласно определению NIST?"
                },
                "options": {
                    "hy": ["Համակարգչային խաղերի տեսություն", "Գիտություն տեղեկատվության գաղտնագրման և ապահով փոխանցման մասին", "Սոցիալական ցանցերի ալգորիթմ", "Ծրագրավորման լեզու"],
                    "en": ["A theory of computer games", "The science of encrypting and securely transmitting information", "A social network algorithm", "A programming language"],
                    "ru": ["Теория компьютерных игр", "Наука о шифровании и безопасной передаче информации", "Алгоритм соцсетей", "Язык программирования"]
                },
                "answer": 1
            },
            {
                "id": 10,
                "question": {
                    "hy": "Ինչի՞ համար է իրականում օգտագործվում VPN-ը:",
                    "en": "What is a VPN actually used for?",
                    "ru": "Для чего на самом деле используется VPN?"
                },
                "options": {
                    "hy": ["Ստեղծում է գաղտնագրված թունել՝ թաքցնելով ձեր IP-ն և պաշտպանելով փոխանցվող տվյալները", "Բարձրացնում է ինտերնետի արագությունը", "Փոխարինում է անտիվիրուսին", "Ամբողջովին անանուն է դարձնում"],
                    "en": ["Creates an encrypted tunnel, hiding your IP and protecting transmitted data", "Increases internet speed", "Replaces antivirus", "Makes you completely anonymous"],
                    "ru": ["Создает зашифрованный туннель, скрывая ваш IP и защищая данные", "Повышает скорость интернета", "Заменяет антивирус", "Делает полностью анонимным"]
                },
                "answer": 0
            },
            {
                "id": 11,
                "question": {
                    "hy": "Ի՞նչ է Ուժային Հարձակումը (Brute Force)՝ ըստ CompTIA Security+-ի:",
                    "en": "What is a Brute Force attack according to CompTIA Security+?",
                    "ru": "Что такое атака методом перебора согласно CompTIA Security+?"
                },
                "options": {
                    "hy": ["Սերվերի ծանրաբեռնում", "Սոցիալական ինժեներիա", "Համակարգ մուտք գործելու փորձ՝ փորձարկելով բոլոր հնարավոր գաղտնաբառերի համակցությունները", "Ֆիշինգային նամակի ուղարկում"],
                    "en": ["Server overload", "Social engineering", "Attempting to access a system by trying all possible password combinations", "Sending a phishing email"],
                    "ru": ["Перегрузка сервера", "Социальная инженерия", "Попытка доступа путем перебора всех возможных комбинаций паролей", "Отправка фишингового письма"]
                },
                "answer": 2
            },
            {
                "id": 12,
                "question": {
                    "hy": "Ի՞նչ են Վեբ Քուքիները (Cookies) և ինչպե՞ս են դրանք օգտագործվում հարձակումների ժամանակ:",
                    "en": "What are Web Cookies and how are they used in attacks?",
                    "ru": "Что такое Веб-куки и как они используются в атаках?"
                },
                "options": {
                    "hy": ["Համակարգչային վիրուսներ", "Փոքր ֆայլեր, որոնք պահում են տեղեկություններ կայքի մասին. հաքերները կարող են գողանալ դրանք՝ սեսիան հափշտակելու համար", "Սերվերի անվտանգության արձանագրություն", "Հակավիրուսային ծրագրեր"],
                    "en": ["Computer viruses", "Small files that store information about a website; hackers can steal them to hijack sessions", "A server security protocol", "Antivirus programs"],
                    "ru": ["Компьютерные вирусы", "Небольшие файлы, хранящие информацию о сайте; хакеры могут украсть их для перехвата сессии", "Протокол безопасности сервера", "Антивирусные программы"]
                },
                "answer": 1
            }
        ]
    },
    "hard": {
        "label_hy": "Բարդ", "label_en": "Hard", "label_ru": "Сложный",
        "time": 20, "points": 30,
        "questions": [
            {
                "id": 1,
                "question": {
                    "hy": "Ի՞նչ է SQL Ինյեկցիան (SQL Injection)՝ ըստ OWASP Top 10 (2021)-ի:",
                    "en": "What is SQL Injection according to OWASP Top 10 (2021)?",
                    "ru": "Что такое SQL-инъекция согласно OWASP Top 10 (2021)?"
                },
                "options": {
                    "hy": ["Սերվերի վերագործարկում", "Ֆայլերի պահուստավորում", "Վեբ ձևերի միջոցով վնասակար SQL հարցումներ ներարկել տվյալների բազային՝ տվյալներ կորզելու կամ ջնջելու համար", "Կեղծ էլ. նամակ"],
                    "en": ["Server reboot", "File backup", "Injecting malicious SQL queries into the database via web forms to extract or delete data", "A fake email"],
                    "ru": ["Перезагрузка сервера", "Резервное копирование файлов", "Внедрение вредоносных SQL-запросов в базу через веб-формы", "Поддельное письмо"]
                },
                "answer": 2
            },
            {
                "id": 2,
                "question": {
                    "hy": "Ի՞նչ է Խաչաձև Կայքային Սկրիպտինգը (XSS)՝ ըստ OWASP Top 10-ի:",
                    "en": "What is Cross-Site Scripting (XSS) according to OWASP Top 10?",
                    "ru": "Что такое Межсайтовый скриптинг (XSS) согласно OWASP Top 10?"
                },
                "options": {
                    "hy": ["Ներարկում են JavaScript կոդ վեբ էջում, որը գործարկվում է այլ օգտատերերի դիտարկիչներում", "Սերվերի գաղտնագրման ալգորիթմ", "Համակարգչային խաղ", "Ցանցային արձանագրություն"],
                    "en": ["Injecting JavaScript code into a web page that executes in other users' browsers", "A server encryption algorithm", "A computer game", "A network protocol"],
                    "ru": ["Внедрение JavaScript-кода в веб-страницу, выполняемого в браузерах других пользователей", "Алгоритм шифрования сервера", "Компьютерная игра", "Сетевой протокол"]
                },
                "answer": 0
            },
            {
                "id": 3,
                "question": {
                    "hy": "Ի՞նչ է CSRF-ը (Cross-Site Request Forgery)՝ ըստ OWASP-ի:",
                    "en": "What is CSRF (Cross-Site Request Forgery) according to OWASP?",
                    "ru": "Что такое CSRF согласно OWASP?"
                },
                "options": {
                    "hy": ["Վեբ սերվերի արձանագրություն", "Հարձակում, որը ստիպում է վավերացված օգտատիրոջը անգիտակցաբար կատարել անցանկալի գործողություն վստահելի կայքում", "Գաղտնագրման ստանդարտ", "VPN արձանագրություն"],
                    "en": ["A web server protocol", "An attack that forces an authenticated user to unknowingly perform an unwanted action on a trusted site", "An encryption standard", "A VPN protocol"],
                    "ru": ["Протокол веб-сервера", "Атака, заставляющая аутентифицированного пользователя выполнить нежелательное действие", "Стандарт шифрования", "VPN-протокол"]
                },
                "answer": 1
            },
            {
                "id": 4,
                "question": {
                    "hy": "Ի՞նչ է SSRF-ը (Server-Side Request Forgery)՝ ըստ OWASP Top 10-ի:",
                    "en": "What is SSRF (Server-Side Request Forgery) according to OWASP Top 10?",
                    "ru": "Что такое SSRF согласно OWASP Top 10?"
                },
                "options": {
                    "hy": ["Սերվերին ստիպել վնասակար հարցում ուղարկել ներքին ցանց կամ այլ ռեսուրսներ", "Օգտատիրոջ դիտարկիչի վերահսկում", "Ֆայլերի պատճենում", "Հաշվի ջնջում"],
                    "en": ["Forcing the server to send a malicious request to the internal network or other resources", "Controlling the user's browser", "File copying", "Account deletion"],
                    "ru": ["Заставить сервер отправить вредоносный запрос во внутреннюю сеть или другие ресурсы", "Управление браузером пользователя", "Копирование файлов", "Удаление аккаунта"]
                },
                "answer": 0
            },
            {
                "id": 5,
                "question": {
                    "hy": "Ո՞րն է Զրո Վստահության (Zero Trust) ճարտարապետության հիմնական սկզբունքը՝ ըստ NIST CSF 2.0-ի:",
                    "en": "What is the core principle of Zero Trust architecture according to NIST CSF 2.0?",
                    "ru": "Каков основной принцип архитектуры Нулевого Доверия согласно NIST CSF 2.0?"
                },
                "options": {
                    "hy": ["Վստահել բոլոր աշխատակիցներին ներքին ցանցում", "Երբեք չվստահել, միշտ ստուգել՝ անկախ ցանցի դիրքից", "Անջատել բոլոր անվտանգության միջոցները", "Վստահել միայն ադմիններին"],
                    "en": ["Trust all employees inside the internal network", "Never trust, always verify — regardless of network location", "Disable all security measures", "Trust only administrators"],
                    "ru": ["Доверять всем сотрудникам во внутренней сети", "Никогда не доверять, всегда проверять — независимо от расположения в сети", "Отключить все меры безопасности", "Доверять только администраторам"]
                },
                "answer": 1
            },
            {
                "id": 6,
                "question": {
                    "hy": "Ի՞նչ է Ընդլայնված Մշտական Սպառնալիքը (APT)՝ ըստ MITRE ATT&CK-ի:",
                    "en": "What is an Advanced Persistent Threat (APT) according to MITRE ATT&CK?",
                    "ru": "Что такое Продвинутая Постоянная Угроза (APT) согласно MITRE ATT&CK?"
                },
                "options": {
                    "hy": ["Մեկանգամյա զանգվածային հարձակում", "Անվճար ծրագիր", "Երկարաժամկետ, լավ պլանավորված, բազմափուլ հարձակում կոնկրետ թիրախի վրա", "Խաղային տերմին"],
                    "en": ["A one-time mass attack", "Free software", "A long-term, well-planned, multi-stage attack on a specific target", "A gaming term"],
                    "ru": ["Одноразовая массовая атака", "Бесплатное ПО", "Долгосрочная, хорошо спланированная, многоэтапная атака", "Игровой термин"]
                },
                "answer": 2
            },
            {
                "id": 7,
                "question": {
                    "hy": "Ինչի՞ համար է օգտագործվում Սանդբոքսը (Sandbox) անվտանգության ոլորտում:",
                    "en": "What is a Sandbox used for in security?",
                    "ru": "Для чего используется Песочница (Sandbox)?"
                },
                "options": {
                    "hy": ["Մեկուսացված միջավայր է, որտեղ անվտանգ փորձարկում են կասխածելի ծրագրերը", "Ֆիզիկական սերվեր է", "Դիտարկիչի ընդլայնում է", "Ամպային պահոց է"],
                    "en": ["An isolated environment where suspicious programs are safely tested", "A physical server", "A browser extension", "A cloud storage"],
                    "ru": ["Изолированная среда, в которой безопасно тестируют подозрительные программы", "Физический сервер", "Расширение браузера", "Облачное хранилище"]
                },
                "answer": 0
            },
            {
                "id": 8,
                "question": {
                    "hy": "Ինչո՞վ է RSA-ն տարբերվում AES-ից:",
                    "en": "How does RSA differ from AES?",
                    "ru": "Чем RSA отличается от AES?"
                },
                "options": {
                    "hy": ["RSA-ն ավելի արագ է", "AES-ը միայն ցանցերում է օգտագործվում", "RSA-ն ասիմետրիկ է (հանրային/մասնավոր բանալի), AES-ը՝ սիմետրիկ (մեկ բանալի)", "Երկուսն էլ հեշ ֆունկցիաներ են"],
                    "en": ["RSA is faster", "AES is used only in networks", "RSA is asymmetric (public/private key), AES is symmetric (single key)", "Both are hash functions"],
                    "ru": ["RSA быстрее", "AES используется только в сетях", "RSA асимметричен, AES симметричен", "Оба являются хеш-функциями"]
                },
                "answer": 2
            },
            {
                "id": 9,
                "question": {
                    "hy": "Ի՞նչ է Replay Attack-ը (Կրկնման Հարձակում):",
                    "en": "What is a Replay Attack?",
                    "ru": "Что такое атака повторного воспроизведения?"
                },
                "options": {
                    "hy": ["Սերվերի վերագործարկում", "Ֆայլերի պատճենում", "Հարձակվողը որսում է վավերական հաղորդագրությունը և նորից ուղարկում՝ ներկայանալով որպես վավեր օգտատեր", "Կայքի բլոկավորում"],
                    "en": ["Server reboot", "File copying", "The attacker captures a valid message and resends it, impersonating a legitimate user", "Website blocking"],
                    "ru": ["Перезагрузка сервера", "Копирование файлов", "Злоумышленник перехватывает валидное сообщение и повторно отправляет его", "Блокировка сайта"]
                },
                "answer": 2
            },
            {
                "id": 10,
                "question": {
                    "hy": "Ի՞նչ է SSTI-ն (Server-Side Template Injection)՝ ըստ OWASP-ի:",
                    "en": "What is SSTI (Server-Side Template Injection) according to OWASP?",
                    "ru": "Что такое SSTI согласно OWASP?"
                },
                "options": {
                    "hy": ["Սերվերի կաղապարների մեջ վնասակար կոդ ներարկելը, որը կարող է հանգեցնել հեռահար կոդի գործարկման", "Համակարգչի վերակայում", "CSS ֆայլերի փոփոխում", "Կայքի դիզայնի փոփոխում"],
                    "en": ["Injecting malicious code into server templates, potentially leading to remote code execution", "Computer reset", "Modifying CSS files", "Changing site design"],
                    "ru": ["Внедрение вредоносного кода в шаблоны сервера", "Сброс компьютера", "Изменение CSS-файлов", "Изменение дизайна сайта"]
                },
                "answer": 0
            },
            {
                "id": 11,
                "question": {
                    "hy": "Ի՞նչ է Բիզնես Տրամաբանության Սխալը (Business Logic Flaw)՝ ըստ OWASP-ի:",
                    "en": "What is a Business Logic Flaw according to OWASP?",
                    "ru": "Что такое Ошибка Бизнес-логики согласно OWASP?"
                },
                "options": {
                    "hy": ["Ցանցային ուշացում", "Ծրագրի տրամաբանության սխալ, որը թույլ է տալիս օգտատիրոջն անել անսպասելի գործողություններ", "Սարքավորման խնդիր", "Դիզայնի սխալ"],
                    "en": ["Network latency", "A logic flaw in an application that allows a user to perform unexpected actions", "A hardware problem", "A design error"],
                    "ru": ["Сетевая задержка", "Ошибка в логике приложения, позволяющая выполнять неожиданные действия", "Проблема оборудования", "Ошибка дизайна"]
                },
                "answer": 1
            },
            {
                "id": 12,
                "question": {
                    "hy": "Ի՞նչ է Տվյալների Կորստի Կանխարգելումը (DLP)՝ ըստ NIST CSF 2.0-ի:",
                    "en": "What is Data Loss Prevention (DLP) according to NIST CSF 2.0?",
                    "ru": "Что такое Предотвращение Потери Данных (DLP) согласно NIST CSF 2.0?"
                },
                "options": {
                    "hy": ["Համակարգ, որը վերահսկում և կանխում է զգայուն տվյալների արտահոսքը կազմակերպությունից", "Անտիվիրուս", "Պահուստային ծրագիր", "VPN ծառայություն"],
                    "en": ["A system that monitors and prevents leakage of sensitive data outside the organization", "Antivirus", "A backup program", "A VPN service"],
                    "ru": ["Система, контролирующая и предотвращающая утечку конфиденциальных данных", "Антивирус", "Программа резервного копирования", "VPN-сервис"]
                },
                "answer": 0
            },
            {
                "id": 13,
                "question": {
                    "hy": "Ինչո՞ւ է Քվանտային Հաշվարկը (Quantum Computing) սպառնալիք ժամանակակից կրիպտոգրաֿֆիային:",
                    "en": "Why is Quantum Computing a threat to modern cryptography?",
                    "ru": "Почему Квантовые вычисления угрожают современной криптографии?"
                },
                "options": {
                    "hy": ["Քվանտային համակարգիչները ավելի արագ են", "Շորի ալգորիթմը կարող է արդյունավետորեն կոտրել RSA-ն և ECC-ն", "Չի ազդում կրիպտոգրաֿֆիայի վրա", "Միայն ավելի քիչ էներգիա է ծախսում"],
                    "en": ["Quantum computers are faster", "Shor's algorithm can efficiently break RSA and ECC", "It does not affect cryptography", "It only consumes less energy"],
                    "ru": ["Квантовые компьютеры быстрее", "Алгоритм Шора эффективно взламывает RSA и ECC", "Не влияет на криптографию", "Только потребляет меньше энергии"]
                },
                "answer": 1
            },
            {
                "id": 14,
                "question": {
                    "hy": "Ո՞րն է Ներթափանցման Թեստավորման (Penetration Testing) առաջին փուլը՝ ըստ NIST SP 800-115-ի:",
                    "en": "What is the first phase of Penetration Testing according to NIST SP 800-115?",
                    "ru": "Какова первая фаза тестирования на проникновение согласно NIST SP 800-115?"
                },
                "options": {
                    "hy": ["Հետախուզության հավաքում (Reconnaissance)", "Մուտքի ստացում", "Վերջնական հաշվետվության գրում", "Համակարգի ջնջում"],
                    "en": ["Reconnaissance", "Gaining access", "Writing the final report", "Deleting the system"],
                    "ru": ["Разведка", "Получение доступа", "Написание финального отчета", "Удаление системы"]
                },
                "answer": 0
            },
            {
                "id": 15,
                "question": {
                    "hy": "Ի՞նչ է Honeypot-ը (Մեղրամոմիկ)՝ ըստ CISA-ի:",
                    "en": "What is a Honeypot according to CISA?",
                    "ru": "Что такое Ханипот (Приманка) согласно CISA?"
                },
                "options": {
                    "hy": ["Հակավիրուս", "Ֆայլի պահոց", "Խաբուսիկ համակարգ, որը նախատեսված է հարձակվողներին գրավելու և նրանց մեթոդները ուսումնասիրելու համար", "Գաղտնաբառերի կառավարիչ"],
                    "en": ["Antivirus", "A file repository", "A decoy system designed to attract attackers and study their methods", "A password manager"],
                    "ru": ["Антивирус", "Файловое хранилище", "Приманка — система для привлечения атакующих и изучения их методов", "Менеджер паролей"]
                },
                "answer": 2
            }
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
    return render_template('leaderboard.html', title="Առաջատարների Աղյուսակ")


@app.route('/api/questions/<difficulty>')
def get_questions(difficulty):
    lang = session.get('lang', 'hy')
    if lang not in TRANSLATIONS:
        lang = 'hy'

    if difficulty not in QUESTIONS_BY_DIFFICULTY:
        return jsonify({"error": "Սխալ բարդության մակարդակ"}), 404

    level = QUESTIONS_BY_DIFFICULTY[difficulty]

    safe_questions = []
    for q in level["questions"]:
        safe_questions.append({
            "id": q["id"],
            "question": q["question"].get(lang, q["question"]["hy"]),
            "options": q["options"].get(lang, q["options"]["hy"])
        })

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


# ============ API ԱՌԱՋԱՏԱՐՆԵՐԻ ԱՂՅՈՒՍԱԿ ============
@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    try:
        rows = execute_query(
            '''SELECT name, score, difficulty, difficulty_label, correct, total, time, date
               FROM leaderboard
               ORDER BY score DESC, time ASC
               LIMIT 10''',
            fetch=True
        )
        return jsonify(rows or [])
    except Exception as e:
        print(f"Առաջատարների սխալ. {e}")
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

        # Ավելացնում ենք գրառումը
        execute_query(
            '''INSERT INTO leaderboard 
               (name, score, difficulty, difficulty_label, correct, total, time, date)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (name, score, difficulty, diff_label, correct, total, round(time_spent, 1), date_str)
        )

        # Գտնում ենք տեղը
        row = execute_query(
            '''SELECT COUNT(*) + 1 AS pos FROM leaderboard
               WHERE score > ? OR (score = ? AND time < ?)''',
            (score, score, time_spent),
            fetch_one=True
        )
        position = row['pos'] if row else None

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
