import datetime

import telebot
from telebot import types

mess_time=datetime.datetime.now()
bot = telebot.TeleBot('5455760931:AAEsGrpm755gvi_2pasRAoKfuD47HmsdHh8')

@bot.message_handler(commands=['start'])
def start(massage):
    mess=f'Привет, {massage.from_user.first_name}, чтобы узнать что я умею воспользуйся командой <b>/help</b>'
    bot.send_message(massage.chat.id, mess, parse_mode='html')

@bot.message_handler(content_types=['data'])
def get_user_photo(massage):
    bot.send_message(massage.chat.id, 'Не стоит скидывать мне картинки, я не хранилище и не ручаюсь за анонимность ;)', parse_mode='html')

@bot.message_handler(commands=['help'])
def website(massage):
    markup = types.ReplyKeyboardMarkup()
    ID = types.KeyboardButton('Узнать своё id')
    Date=types.KeyboardButton("Дата и время")
    markup.add(ID, Date)
    bot.send_message(massage.chat.id, 'Выбери пункт', reply_markup=markup)

@bot.message_handler(content_types=['text'])
def get_user_text(massage):
    if massage.text=="Привет":
        bot.send_message(massage.chat.id,'И тебе привет',parse_mode='html')
    elif massage.text=="Узнать своё id":
        bot.send_message(massage.chat.id,f'Вот твой ID:{massage.from_user.id}',parse_mode='html')
    elif massage.text=="Дата и время":
        bot.send_message(massage.chat.id,f'Сегодняшняя дата и время: {mess_time}',parse_mode='html')
    else:
        bot.send_message(massage.chat.id,'Я не понимаю что ты хочешь',parse_mode='html')

bot.polling(none_stop=True)