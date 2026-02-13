import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

TOKEN = "8590144654:AAGemeuT1E3R2JROP5o-hggxWnDb24hO6Ro"

bot = telebot.TeleBot(TOKEN)

TASKS_FILE = "tasks.txt"


# --- Функция сохранения задачи ---
def save_task(user_id, task_text, message_id):
    with open(TASKS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{user_id}|{message_id}|{task_text}\n")


# --- Функция удаления задачи из файла ---
def remove_task(message_id):
    if not os.path.exists(TASKS_FILE):
        return

    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        for line in lines:
            if f"|{message_id}|" not in line:
                f.write(line)


# --- Обработка команды /start ---
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Просто отправляй сюда свои дела")


# --- Обработка текстовых сообщений (создание задачи) ---
@bot.message_handler(content_types=["text"])
def handle_task(message):
    # Игнорируем команды
    if message.text.startswith("/"):
        return

    user_id = message.from_user.id
    chat_id = message.chat.id
    task_text = message.text

    # Удаляем сообщение пользователя
    try:
        bot.delete_message(chat_id, message.message_id)
    except:
        pass

    # Создаем кнопку ✅
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton("✅", callback_data=f"done_{message.message_id}")
    markup.add(button)

    # Отправляем сообщение от имени бота
    sent_message = bot.send_message(chat_id, task_text, reply_markup=markup)

    # Сохраняем задачу в файл
    save_task(user_id, task_text, sent_message.message_id)


# --- Обработка нажатия кнопки ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("done_"))
def complete_task(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    # Удаляем сообщение-задачу
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass

    # Удаляем задачу из файла
    remove_task(message_id)

    bot.answer_callback_query(call.id)


print("Бот запущен...")
bot.infinity_polling()
