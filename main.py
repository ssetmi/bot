import telebot
import psycopg2
from telebot import types

conn = psycopg2.connect(dbname='Proect', user='postgres',
                        password='password', host='localhost')
cursor = conn.cursor()

bot = telebot.TeleBot('7090200012:AAHBwqU1_kEXnWveEi0ZhLp2Z3Tw1xhbPyM')

h=open('hello .txt','r',encoding='UTF-8')
hello=h.read()
h.close()

p=open('program.txt','r',encoding='UTF-8')
program=p.read()
p.close()


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,hello,reply_markup=generate_menu())

# Генерация кнопок меню
def generate_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('О программе')
    item2 = types.KeyboardButton('Я хочу сдать вещь')
    item3 = types.KeyboardButton('Я хочу сдать материалы')
    item4 = types.KeyboardButton('Я хочу учавствовать в реставрации вещей')
    item5 = types.KeyboardButton('Я хочу забрать вещь')
    markup.add(item1, item2, item3, item4, item5)
    return markup

@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text.strip() == 'О программе':
        answer = program
        bot.send_message(message.chat.id,answer)
    if message.text == "Я хочу сдать вещь":
        send_type_request(message)

# Функция для отправки запроса на выбор типа вещи
def send_type_request(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    cursor.execute("SELECT type FROM typeObject")
    types_result = cursor.fetchall()
    for row in types_result:
        markup.add(types.KeyboardButton(row[0]))
    bot.send_message(message.chat.id, "Выберите тип вещи:", reply_markup=markup)
    bot.register_next_step_handler(message, process_type_step)

# Обработка выбора типа вещи
def process_type_step(message):
    type_selected = message.text
    send_quality_request(message, type_selected)

# Функция для отправки запроса на выбор состояния вещи
def send_quality_request(message, type_selected):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    cursor.execute("SELECT quality FROM qualityObject")
    quality_result = cursor.fetchall()
    for row in quality_result:
        markup.add(types.KeyboardButton(row[0]))
    bot.send_message(message.chat.id, "Выберите состояние вещи:", reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: process_quality_step(msg, type_selected))

# Обработка выбора состояния вещи
def process_quality_step(message, type_selected):
    quality_selected = message.text
    add_request_to_database(message, type_selected, quality_selected)

# Функция для добавления заявки в базу данных
def add_request_to_database(message, type_selected, quality_selected):
    type_id = get_type_id(type_selected)
    quality_id = get_quality_id(quality_selected)
    cursor.execute("INSERT INTO object (type, quality) VALUES (%s, %s) RETURNING id", (type_id, quality_id))
    object_id = cursor.fetchone()[0]
    cursor.execute("INSERT INTO request (type, status, object) VALUES (%s, %s, %s)", (1, 1, object_id))  # Временные значения для типа и статуса
    conn.commit()

    bot.send_message(message.chat.id, "Заявка успешно добавлена!",reply_markup=generate_menu())


# Функция для получения ID типа вещи из базы данных
def get_type_id(type_selected):
    cursor.execute("SELECT id FROM typeObject WHERE type = %s", (type_selected,))
    return cursor.fetchone()[0]

# Функция для получения ID состояния вещи из базы данных
def get_quality_id(quality_selected):
    cursor.execute("SELECT id FROM qualityObject WHERE quality = %s", (quality_selected,))
    return cursor.fetchone()[0]
bot.polling(none_stop=True)
