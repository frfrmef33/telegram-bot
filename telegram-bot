import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import random
import string

TOKEN = "8531211768:AAEFE_A9ZoHtnCDTIfbA9xuUSh_wd-ROlu0"
ADMIN_ID = 7720197045
PASSWORD = "6guyh989"

bot = telebot.TeleBot(TOKEN)

authorized = set()
banned = set()
admins = set([ADMIN_ID])

settings = {}
admin_state = {}


# ---------------- КЛАВИАТУРЫ ----------------
def main_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("поиск"))
    kb.add(KeyboardButton("настройки"))
    kb.add(KeyboardButton("админ"))
    return kb


def settings_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(KeyboardButton("4"), KeyboardButton("5"), KeyboardButton("6"))
    kb.row(KeyboardButton("цифры: да"), KeyboardButton("цифры: нет"))
    kb.add(KeyboardButton("буквы"))
    kb.add(KeyboardButton("назад"))
    return kb


def admin_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("пользователи"))
    kb.add(KeyboardButton("бан"))
    kb.add(KeyboardButton("разбан"))
    kb.add(KeyboardButton("админы"))
    kb.add(KeyboardButton("назад"))
    return kb


# ---------------- INIT ----------------
def init_user(user_id):
    if user_id not in settings:
        settings[user_id] = {
            "length": 5,
            "digits": False,
            "letters": "",
            "await_letters": False
        }


# ---------------- GENERATOR ----------------
def generate_username(user_id):
    init_user(user_id)

    length = settings[user_id]["length"]
    digits = settings[user_id]["digits"]
    letters = settings[user_id]["letters"]

    pool = letters if letters else string.ascii_lowercase

    username = ''.join(random.choice(pool) for _ in range(length))

    if digits:
        username += str(random.randint(0, 9))

    return username


def is_taken(username):
    try:
        bot.get_chat("@" + username)
        return True
    except:
        return False


# ---------------- START ----------------
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id

    if user_id in banned:
        bot.send_message(user_id, "Ты заблокирован")
        return

    if user_id in authorized:
        bot.send_message(user_id, "Меню", reply_markup=main_keyboard())
        return

    bot.send_message(user_id, "Введи пароль:")


# ---------------- MAIN HANDLER ----------------
@bot.message_handler(func=lambda m: True)
def handler(message):
    user_id = message.chat.id
    text = message.text

    if user_id in banned:
        return

    init_user(user_id)

    # ---------------- ПАРОЛЬ ----------------
    if user_id not in authorized:
        if text == PASSWORD:
            authorized.add(user_id)
            bot.send_message(
                user_id,
                "✅ УСПЕШНЫЙ ВХОД\nДобро пожаловать в систему",
                reply_markup=main_keyboard()
            )
        else:
            bot.send_message(user_id, "Неверный пароль")
        return

    # ---------------- АДМИН ----------------
    if text == "админ":
        if user_id not in admins:
            return
        bot.send_message(user_id, "АДМИН ПАНЕЛЬ", reply_markup=admin_keyboard())
        return

    if text == "назад":
        bot.send_message(user_id, "Меню", reply_markup=main_keyboard())
        return

    # ---------------- ПОЛЬЗОВАТЕЛИ (С ЮЗЕРАМИ И ССЫЛКАМИ) ----------------
    if text == "пользователи":
        if user_id not in admins:
            return

        result = "👤 USERS:\n\n"

        for uid in authorized:
            try:
                chat = bot.get_chat(uid)
                username = chat.username

                if username:
                    result += f"ID: {uid}\n@{username}\nhttps://t.me/{username}\n\n"
                else:
                    result += f"ID: {uid}\ntg://user?id={uid}\n\n"

            except:
                result += f"ID: {uid}\nunknown\n\n"

        bot.send_message(user_id, result)
        return
    # ---------------- АДМИНЫ ----------------
    if text == "админы":
        if user_id not in admins:
            return
        bot.send_message(user_id, f"ADMINS:\n{list(admins)}")
        return

    # ---------------- БАН ----------------
    if text == "бан":
        if user_id not in admins:
            return
        admin_state[user_id] = "ban"
        bot.send_message(user_id, "Введи ID")
        return

    if text == "разбан":
        if user_id not in admins:
            return
        admin_state[user_id] = "unban"
        bot.send_message(user_id, "Введи ID")
        return

    # ---------------- ОБРАБОТКА АДМИН ДЕЙСТВИЙ ----------------
    if user_id in admin_state:
        try:
            target = int(text)

            if admin_state[user_id] == "ban":
                banned.add(target)
                authorized.discard(target)
                bot.send_message(user_id, f"Забанен {target}")

            elif admin_state[user_id] == "unban":
                banned.discard(target)
                bot.send_message(user_id, f"Разбанен {target}")

            admin_state.pop(user_id)

        except:
            bot.send_message(user_id, "Ошибка ID")
        return

    # ---------------- ПОИСК ----------------
    if text == "поиск":
        bot.send_message(user_id, "Ищу username...")

        for _ in range(40):
            username = generate_username(user_id)

            if not is_taken(username):
                bot.send_message(user_id, f"Найден:\n@{username}")
                return

        bot.send_message(user_id, "Не найдено")
        return

    # ---------------- НАСТРОЙКИ ----------------
    if text == "настройки":
        bot.send_message(user_id, "Настройки:", reply_markup=settings_keyboard())
        return

    if text in ["4", "5", "6"]:
        settings[user_id]["length"] = int(text)
        bot.send_message(user_id, f"Длина: {text}")
        return

    if text in ["цифры: да", "цифры: нет"]:
        settings[user_id]["digits"] = (text == "цифры: да")
        bot.send_message(user_id, f"Цифры: {settings[user_id]['digits']}")
        return

    if text == "буквы":
        settings[user_id]["await_letters"] = True
        bot.send_message(user_id, "Введи буквы:")
        return

    if settings[user_id]["await_letters"]:
        if text.isalpha():
            settings[user_id]["letters"] = text.lower()
            settings[user_id]["await_letters"] = False
            bot.send_message(user_id, "Сохранено", reply_markup=main_keyboard())
        else:
            bot.send_message(user_id, "Только буквы")


# ---------------- RUN ----------------
bot.polling()
