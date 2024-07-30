import telebot
import webbrowser
from telebot import *
import sqlite3
import requests
import json

bot = telebot.TeleBot('7344200411:AAGNh5ifR_lW9-4y_211ljFfkk4nikNcxm4')
name = None
WeatherAPI = '748a2000c929016d6422d7e29307d7b9'

@bot.message_handler(commands=['start'])
def startfunc(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Help')
    btn2 = types.KeyboardButton('Site')
    btn3 = types.KeyboardButton('SQLite3 Example')
    btn4 = types.KeyboardButton('Open SQLite Example')
    btn5 = types.KeyboardButton('Get Weather')
    markup.row(btn1, btn2, btn3, btn4, btn5)
    bot.send_message(message.chat.id, f'Hello {message.from_user.first_name} {message.from_user.last_name}', reply_markup=markup)
    bot.register_next_step_handler(message, on_click)

def on_click(message):
    if message.text == 'Help':
        bot.send_message(message.chat.id, f"Here's some help", parse_mode='html')
    elif message.text == 'Site':
        bot.send_message(message.chat.id, f"Site was openned", parse_mode='html')
        webbrowser.open('https://www.youtube.com')
    elif message.text == 'SQLite3 Example':
        conn = sqlite3.connect('example.sql')
        cur = conn.cursor()
        
        cur.execute('CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, name varchar(50), pass varchar(50))')
        
        conn.commit()
        cur.close()
        conn.close()

        bot.send_message(message.chat.id, f"Enter Your Name", parse_mode='html')
        bot.register_next_step_handler(message, user_name)


        pass

    elif message.text == 'Open SQLite Example':
        conn = sqlite3.connect('example.sql')
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        
        info = ''

        for el in users:
            info += f'Name: {el[1]}, Password: {el[2]}\n'

        cur.close()
        conn.close()

        bot.send_message(message.chat.id, info)

    elif message.text == 'Get Weather':
        bot.send_message(message.chat.id, f"Enter City", parse_mode='html')
        bot.register_next_step_handler(message, get_weather)
        


    bot.register_next_step_handler(message, on_click)

def get_weather(message):
    try:
        city = message.text.strip().lower()
        req = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WeatherAPI}&units=metric')
        req.status_code == 200
        data = json.loads(req.text)
        bot.send_message(message.chat.id, f'Weather in {data["name"]}: Temp {data["main"]["temp"]}')
    except ConnectionError:
        bot.send_message(message.chat.id, f'Error')


def user_name(message):
    global name
    name = message.text.strip()
    bot.send_message(message.chat.id, f"Enter Password", parse_mode='html')
    bot.register_next_step_handler(message, user_pass)


def user_pass(message):
    password = message.text.strip()

    conn = sqlite3.connect('example.sql')
    cur = conn.cursor()
    
    cur.execute("INSERT INTO users (name, pass) VALUES ('%s', '%s')" % (name, password))
    
    conn.commit()
    cur.close()
    conn.close()

    bot.send_message(message.chat.id, f"You've been registered", parse_mode='html')
    

bot.polling(non_stop=True)