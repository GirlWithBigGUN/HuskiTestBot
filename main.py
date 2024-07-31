import telebot
import webbrowser
from telebot import *
import sqlite3
import requests
import json
from currency_converter import *

bot = telebot.TeleBot('7344200411:AAGNh5ifR_lW9-4y_211ljFfkk4nikNcxm4')
WeatherAPI = '748a2000c929016d6422d7e29307d7b9'
conv = CurrencyConverter(fallback_on_wrong_date=True)


class global_data():
    def __init__(self):
        self.fname = ''
        self.psw = ''
        self.curr_one = ''
        self.curr_two = ''
        self.amount = 0

    #setters
    def set_name(self,fname):
        self.fname = fname 
    def set_psw(self,psw):
        self.psw = psw       
    def set_curr_one(self, curr):
        self.curr_one = curr
    def set_curr_two(self, curr):
        self.curr_two = curr
    def set_amount(self, amount):
        self.amount = amount
    
    #getters
    def get_name(self):
        return self.fname
    def get_psw(self):
        return self.psw
    def get_curr_one(self):
        return self.curr_one
    def get_curr_two(self):
        return self.curr_two
    def get_amount(self):
        return self.amount

global_data_inst = global_data()


@bot.message_handler(commands=['start'])
def startfunc(message):
    
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Help')
    btn2 = types.KeyboardButton('Site')
    btn3 = types.KeyboardButton('SQLite3 Example')
    btn4 = types.KeyboardButton('Open SQLite Example')
    btn5 = types.KeyboardButton('Get Weather')
    btn6 = types.KeyboardButton('Convert Currency')
    markup.row(btn1, btn2, btn3)
    markup.row(btn4, btn5, btn6)
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

        bot.send_message(message.chat.id, info,reply_markup=return_to_menu_markup())
        bot.register_next_step_handler(message, startfunc)


    elif message.text == 'Get Weather':
        bot.send_message(message.chat.id, f"Enter City", parse_mode='html',reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_weather)
    
    elif message.text == 'Convert Currency':
        usd_cur = types.KeyboardButton('USD')
        rub_cur = types.KeyboardButton('RUB')
        eur_cur = types.KeyboardButton('EUR')

        markup_converter = types.ReplyKeyboardMarkup()
        markup_converter.row(usd_cur, rub_cur, eur_cur)

        
        bot.send_message(message.chat.id, f"Choose currency to convert from", parse_mode='html', reply_markup=markup_converter)
        
        bot.register_next_step_handler(message, convert_cur_step_one)

    return

def convert_cur_step_one(message):
    global_data_inst.set_curr_one(message.text)
    bot.send_message(message.chat.id, f"Enter amount to convert", parse_mode='html',reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message,convert_amount)

def convert_amount(message):
    try:
        global_data_inst.set_amount(int(message.text))
    except ValueError:
        bot.send_message(message.chat.id, f"Enter a NUMBER", parse_mode='html')
        bot.register_next_step_handler(message,convert_amount)
        return
    
    if global_data_inst.get_amount() < 0:
        bot.send_message(message.chat.id, f"Enter a POSITIVE NUMBER", parse_mode='html')
        bot.register_next_step_handler(message,convert_amount)
    else:
        usd_cur = types.KeyboardButton('USD')
        rub_cur = types.KeyboardButton('RUB')
        eur_cur = types.KeyboardButton('EUR')

        markup_converter = types.ReplyKeyboardMarkup()
        markup_converter.row(usd_cur, rub_cur, eur_cur)

        bot.send_message(message.chat.id, f"Choose currency to convert to", parse_mode='html', reply_markup=markup_converter)
        
        bot.register_next_step_handler(message, convert_result)

def convert_result(message):
    global_data_inst.set_curr_two(message.text)
    converted_value = conv.convert(global_data_inst.get_amount(), global_data_inst.get_curr_one(), global_data_inst.get_curr_two())
    bot.send_message(message.chat.id, f"{global_data_inst.get_amount()} {global_data_inst.get_curr_one()} equals to {round(converted_value,2)} {global_data_inst.get_curr_two()}",reply_markup=return_to_menu_markup())
    bot.register_next_step_handler(message, startfunc)

def get_weather(message):
    try:
        city = message.text.strip().lower()
        req = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WeatherAPI}&units=metric')
        data = json.loads(req.text)
        bot.send_message(message.chat.id, f'Weather in {data["name"]}: Temp {data["main"]["temp"]}',reply_markup=return_to_menu_markup())
        bot.register_next_step_handler(message, startfunc)
    except Exception :
        bot.send_message(message.chat.id, f"Weather is not available for now or City doesn't' exists",reply_markup=return_to_menu_markup())
        bot.register_next_step_handler(message, startfunc)

def user_name(message):
    global_data_inst.set_name(message.text.strip())
    bot.send_message(message.chat.id, f"Enter Password", parse_mode='html')
    bot.register_next_step_handler(message, user_pass)


def user_pass(message):
    global_data_inst.set_psw(message.text.strip())

    conn = sqlite3.connect('example.sql')
    cur = conn.cursor()
    
    cur.execute("INSERT INTO users (name, pass) VALUES ('%s', '%s')" % (global_data_inst.get_name(), global_data_inst.get_psw()))
    
    conn.commit()
    cur.close()
    conn.close()

    bot.send_message(message.chat.id, f"You've been registered", parse_mode='html', reply_markup=return_to_menu_markup())
    bot.register_next_step_handler(message, startfunc)

def return_to_menu_markup():
    return_btn = types.KeyboardButton('Return to Menu')

    return_markup = types.ReplyKeyboardMarkup()
    return_markup.row(return_btn)

    # bot.send_message(message.chat.id, f" ", parse_mode='html', reply_markup=return_markup)
    
    # bot.register_next_step_handler(message, convert_result)

    return return_markup

bot.polling(non_stop=True)