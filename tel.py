import telebot
import json
from flask import Flask, request
import os
import requests
import logging
import sys



logging.basicConfig(level=logging.INFO)
API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    sys.exit("Ошибка: API-токен не задан в переменных окружения")
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)


@app.route('/')
def index():
    return "Бот запущен"


@app.route(f'/{API_TOKEN})', methods=['post'])
def webhook():
    try:
        json_str = request.get_data(as_text=true)
        update = telebot.types.Update.de_json(json_str)
        if update:
            bot.process_new_updates([update])
    except Exception as e:
        app.logger.exception(f"Webhook error: {str(e)}")
    return '', 200


def load_db():
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return{}

def save_db(data):
    with open("db.json", 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


db = load_db()


@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)


    if user_id not in db:
        db[user_id] = {"name": None, "age": None, "money": 10000, "state": "awaiting_name"}
        save_db(db)
        bot.send_message(message.chat.id, "Привет! Как тебя зовут?")
        return


    keyboardReply = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

    helpbutton = telebot.types.KeyboardButton("помощь")
    infoButton = telebot.types.KeyboardButton("инфо")
    aboutButton = telebot.types.KeyboardButton("о боте")
    slotMachine = telebot.types.KeyboardButton("Игровой автомат")
    buyButton = telebot.types.KeyboardButton("викторина")
    dicebutton = telebot.types.KeyboardButton("Игра в кубик")

    keyboardReply.add(helpbutton, infoButton, aboutButton, slotMachine, buyButton, dicebutton)

    bot.send_message(message.chat.id, "hello bot-world", reply_markup=keyboardReply)

@bot.message_handler(content_types=["text"])
def text_event(message):
    user_id = str(message.from_user.id)

    if "awaiting_name" == db.get(user_id, {}).get("state"):
        name = message.text.strip()
        db[user_id]["name"] = name
        db[user_id]["state"] = "awaiting_age"
        save_db(db)
        bot.send_message(message.chat.id, f"Приятно познакомиться, {name}")
        bot.send_message(message.chat.id, f"сколько тебе лет, {name}")
        return
    elif db.get(user_id, {}).get("state") == "awaiting_age":
        try:
            age = int(message.text.strip())
            db[user_id]["age"] = age
            db[user_id]["stage"] = None
            save_db(db)
            start(message)
            return
        except:
            bot.send_message(message.chat.id, "Ты ввел некорректное значение возраста")
            return



    if message.text == "помощь":
        pass
    if message.text == "Как меня зовут":
        user_name = db[user_id]["name"]
        bot.send_message(message.chat.id, f"Тебя зовут {user.name}")
    elif message.text == "инфо":
        pass
    elif message.text == "о боте":
        pass

    elif message.text == "Игровой автомат":
        if db[user_id]["money"] >= 1000:
            value = bot.send_dice(message.chat.id, emoji='🎰').dice.value

            if value in (1, 22, 43):
                db[user_id]["money"] += 2000
                bot.send_message(message.chat.id, "Победа!")
            elif value in (16, 32, 48):
                db[user_id]["money"] += 2000
                bot.send_message(message.chat.id, "Победа!")
            elif value == 64:
                bot.send_message(message.chat.id, "Jackpot!")
                db[user_id]["money"] += 3000
            else:
                db[user_id]["money"] -= 1000
                bot.send_message(message.chat.id, "Попробуй еще раз")

        else:
            bot.send_message(message.chat.id, f"Недостаточно средств нужно минимум 1000 ваш баланс:",{db[user_id]["money"]})

    elif message.text == "Игра в кубик":
        inlinekeyboard = telebot.types.InlineKeyboardMarkup(row_width=3)

        btn1 = telebot.types.InlineKeyboardButton("1", callback_data='1')
        btn2 = telebot.types.InlineKeyboardButton("2", callback_data='2')
        btn3 = telebot.types.InlineKeyboardButton("3", callback_data='3')
        btn4 = telebot.types.InlineKeyboardButton("4", callback_data='4')
        btn5 = telebot.types.InlineKeyboardButton("5", callback_data='5')
        btn6 = telebot.types.InlineKeyboardButton("6", callback_data='6')

        inlinekeyboard.add(btn1, btn2, btn3, btn4, btn5, btn6)

        bot.send_message(message.chat.id, "угадай число на кубике", reply_markup=inlinekeyboard)

    elif message.text == "викторина":
        ludokeyboard = telebot.types.InlineKeyboardMarkup(row_width=3)

        tovar1button = telebot.types.InlineKeyboardButton("7", callback_data='7')
        tovar2Button = telebot.types.InlineKeyboardButton("147.0409641091", callback_data='147.0409641091')
        tovar3Button = telebot.types.InlineKeyboardButton("147.0409641090", callback_data='147.0409641090')

        ludokeyboard.add(tovar1button, tovar2Button, tovar3Button)

        bot.send_message(message.chat.id, "сколько будет 22 + 46e", reply_markup=ludokeyboard)

    @bot.callback_query_handler(func=lambda call: call.data in ('1', '2', '3', '4', '5', '6'))
    def dice_callback(call):
        value = bot.send_dice(call.message.chat.id, emoji='🎲').dice.value
        if str(value) == call.data:
            bot.send_message(call.message.chat.id, "Ты угадал!")
        else:
            bot.send_message(call.message.chat.id, "попробуй еще раз")


    @bot.callback_query_handler(func=lambda call: call.data in ('7', '147.0409641091', '147.0409641090'))
    def first_question(call):
        if message.text == '147.0409641091':
            bot.send_message(call.message.chat.id, "Ты угадал!")
        else:
            bot.send_message(call.message.chat.id, "попробуй еще раз")



if __name__ == '__main__':
    server_url = os.getenv("RENDER_EXTERNAL_URL")
    if server_url and API_TOKEN:
        webhook.url = f"{server_url.rstrip('/')}/{API_TOKEN}"

        try:
            r = requests.get(f"https://api.telegram.org/bot{API_TOKEN}/setWebhook",
                             params={"url": webhook_url}, timeout=10)
            logging.info(f"вебхук усттановлен: {r.text}")
        except Exception:
            logging.exception("Ошибка при установке webhook")

        port = int(os.getenv("PORT", 10000))
        logging.info(f"Запуск на поорте {port}")
        app.run(host='0.0.0.0', port=port)

    else:
        logging.info("Запуск бота в режиме pooling")
        bot.remove_webhook()
        bot.infinity_polling(timeout=60 )

