import datetime
import os
import telebot

from dotenv import load_dotenv
from telebot import types

load_dotenv()

mess_time = datetime.datetime.now()
bot = telebot.TeleBot(os.getenv('SECRET_KEY'))


@bot.message_handler(commands=['start'])
def start(massage):
    mess = f'Привет, {massage.from_user.first_name}, чтобы узнать что я умею воспользуйся командой <b>/help</b>'
    bot.send_message(massage.chat.id, mess, parse_mode='html')


@bot.message_handler(commands=['help'])
def website(massage):
    markup = types.ReplyKeyboardMarkup()
    ID = types.KeyboardButton('Узнать своё id')
    Date = types.KeyboardButton("Дата и время")
    markup.add(ID, Date)
    bot.send_message(massage.chat.id, 'Выбери пункт', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def get_user_text(massage):
    if massage.text == "Привет":
        bot.send_message(massage.chat.id, 'И тебе привет', parse_mode='html')
    elif massage.text == "Узнать своё id":
        bot.send_message(massage.chat.id, f'Вот твой ID:{massage.from_user.id}', parse_mode='html')
    elif massage.text == "Дата и время":
        bot.send_message(massage.chat.id, f'Сегодняшняя дата и время: {mess_time}', parse_mode='html')
    else:
        bot.send_message(massage.chat.id, 'Я не понимаю что ты хочешь', parse_mode='html')


@bot.message_handler(content_types=['photo'])
def get_user_photo(message):
    file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
    with open('E:\pythonProject1\data\\' + message.photo[0].file_id + '.jpg', 'wb') as file:
        file.write(bot.download_file(file_info.file_path))
    bot.send_message(message.chat.id, 'Фото сохранил', parse_mode='html')


bot.polling(none_stop=True)
