import os
import telebot
import time
import random
import string
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# ================= НАСТРОЙКИ =================
TOKEN = os.getenv("TOKEN") # ← Только через переменную окружения!

if not TOKEN:
    print("❌ ОШИБКА: TOKEN не найден в переменных окружения!")
    exit(1)

ADMIN_ID = 7720197045
PASSWORD = "6guyh989"

bot = telebot.TeleBot(TOKEN)

authorized = set()
banned = set()
admins = {ADMIN_ID}

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
    kb.row(KeyboardButton("пользователи"), KeyboardButton("админы"))
    kb.row(KeyboardButton("бан"), KeyboardButton("разбан"))
    kb.row(KeyboardButton("выдать админа"), KeyboardButton("снять админа"))
    kb.add(KeyboardButton("назад"))
    return kb


# ---------------- НАСТРОЙКИ ПОЛЬЗОВАТЕЛЯ ----------------
def init_user(user_id):
    if user_id not in settings:
        settings[user_id] = {
            "length": 5,
            "digits": False,
            "letters": "",
            "await_letters": False
        }


# ---------------- ГЕНЕРАЦИЯ ----------------
def generate_username(user_id):
    init_user(user_id)
    length = settings[user_id]["length"]
    digits = settings[user_id]["digits"]
    letters = settings[user_id]["letters"].lower()

    username = [random.choice(string.ascii_lowercase) for _ in range(length)]

    if letters:
        count = min(len(letters), random.randint(1, 2))
        selected = random.sample(list(letters), count)
        positions = random.sample(range(length), count)
        for pos, char in zip(positions, selected):
            username[pos] = char

    username = ''.join(username)
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
        bot.send_message(user_id, "Ты заблокирован.")
        return

    if user_id in authorized:
        bot.send_message(user_id, "✅ Ты уже авторизован.", reply_markup=main_keyboard())
        return

    bot.send_message(user_id, "Введи пароль:")


# ---------------- ОСНОВНОЙ ХЕНДЛЕР ----------------
@bot.message_handler(func=lambda m: True)
def handler(message):
    user_id = message.chat.id
    text = message.text

    if user_id in banned:
        return

    init_user(user_id)

    # ПАРОЛЬ
    if user_id not in authorized:
        if text == PASSWORD:
            authorized.add(user_id)
            bot.send_message(user_id, "✅ Доступ разрешён.\nДобро пожаловать в систему.", reply_markup=main_keyboard())
        else:
            bot.send_message(user_id, "Неверный пароль.")
        return

    # ... (весь остальной код без изменений) ...
    if text == "админ":
        if user_id not in admins:
            bot.send_message(user_id, "Эта панель доступна только администраторам.")
            return
        bot.send_message(user_id, "АДМИН ПАНЕЛЬ", reply_markup=admin_keyboard())
        return

    if text == "назад":
        settings[user_id]["await_letters"] = False
        bot.send_message(user_id, "Меню", reply_markup=main_keyboard())
        return
    # Пользователи, админы, бан и т.д. — оставил как было
    if text == "пользователи":
        if user_id not in admins: return
        result = "👤 Пользователи:\n\n"
        for uid in authorized:
            try:
                chat = bot.get_chat(uid)
                if chat.username:
                    result += f"ID: {uid}\n@{chat.username}\nhttps://t.me/{chat.username}\n\n"
                else:
                    result += f"ID: {uid}\n tg://user?id={uid}\n\n"
            except:
                result += f"ID: {uid}\n\n"
        bot.send_message(user_id, result)
        return

    if text == "админы":
        if user_id not in admins: return
        bot.send_message(user_id, f"Админы:\n{list(admins)}")
        return

    if text == "выдать админа":
        if user_id != ADMIN_ID:
            bot.send_message(user_id, "Только главный админ может выдавать права.")
            return
        admin_state[user_id] = "add_admin"
        bot.send_message(user_id, "Введи ID пользователя:")
        return

    if text == "снять админа":
        if user_id != ADMIN_ID:
            bot.send_message(user_id, "Только главный админ может снимать права.")
            return
        admin_state[user_id] = "remove_admin"
        bot.send_message(user_id, "Введи ID пользователя:")
        return

    if text == "бан":
        if user_id not in admins: return
        admin_state[user_id] = "ban"
        bot.send_message(user_id, "Введи ID:")
        return

    if text == "разбан":
        if user_id not in admins: return
        admin_state[user_id] = "unban"
        bot.send_message(user_id, "Введи ID:")
        return

    if user_id in admin_state:
        try:
            target = int(text)
            action = admin_state[user_id]

            if action == "ban":
                banned.add(target)
                authorized.discard(target)
                bot.send_message(user_id, f"✅ {target} забанен")
            elif action == "unban":
                banned.discard(target)
                bot.send_message(user_id, f"✅ {target} разбанен")
            elif action == "add_admin":
                admins.add(target)
                bot.send_message(user_id, f"✅ {target} теперь администратор")
            elif action == "remove_admin":
                if target == ADMIN_ID:
                    bot.send_message(user_id, "⛔ Нельзя снять главного администратора.")
                else:
                    admins.discard(target)
                    bot.send_message(user_id, f"✅ {target} больше не администратор")
            admin_state.pop(user_id)
        except:
            bot.send_message(user_id, "Введи корректный ID.")
        return

    if text == "поиск":
        bot.send_message(user_id, "🔍 Ищу username...")
        for _ in range(40):
            username = generate_username(user_id)
            if not is_taken(username):
                bot.send_message(user_id, f"Найден:\n@{username}")
                return
        bot.send_message(user_id, "Ничего не найдено.")
        return

    if text == "настройки":
        bot.send_message(user_id, "Настройки:", reply_markup=settings_keyboard())
        return

    if text in ["4", "5", "6"]:
        settings[user_id]["length"] = int(text)
        bot.send_message(user_id, f"Длина: {text}")
        return

    if text in ["цифры: да", "цифры: нет"]:
        settings[user_id]["digits"] = (text == "цифры: да")
        bot.send_message(user_id, f"Цифры: {'включены' if settings[user_id]['digits'] else 'выключены'}")
        return

    if text == "буквы":
        settings[user_id]["await_letters"] = True
        bot.send_message(user_id, "Введи буквы, которые должны встречаться в username.\n\nНапример: gh")
        return

    if settings[user_id]["await_letters"]:
        if text.isalpha():
            settings[user_id]["letters"] = text.lower()
            settings[user_id]["await_letters"] = False
            bot.send_message(user_id, f"✅ Сохранено: {text.lower()}", reply_markup=main_keyboard())
        else:
            bot.send_message(user_id, "❌ Можно вводить только буквы.")
        return


# ================= ЗАПУСК С АВТОПЕРЕЗАПУСКОМ =================
if __name__ == "__main__":
    print("🤖 Бот запущен...")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=30)
        except Exception as e:
            print(f"⚠️ Ошибка: {e}")
            time.sleep(5)