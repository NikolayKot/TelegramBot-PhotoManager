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
    markup1 = types.ReplyKeyboardMarkup()
    ID = types.KeyboardButton('Зарегестрироваться')
    markup1.add(ID)
    bot.send_message(massage.chat.id, f'Привет, {massage.from_user.first_name}, для начала давай зарегестрируемся', reply_markup=markup1)

@bot.message_handler(commands=['help'])
def website(massage):
    markup = types.ReplyKeyboardMarkup()
    Date = types.KeyboardButton("Дата и время")
    photo = types.KeyboardButton('Получить мои фото')
    photo2 = types.KeyboardButton('Сохранить мои фото')
    markup.add(Date, photo, photo2)
    bot.send_message(massage.chat.id, 'Выбери пункт', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def get_user_text(massage):
    markup2 = types.ReplyKeyboardMarkup()
    helpp = types.KeyboardButton("/help")
    markup2.add(helpp)
    if massage.text == "Привет":
        bot.send_message(massage.chat.id, 'И тебе привет', parse_mode='html')
    elif massage.text == "Зарегестрироваться":
        os.mkdir(f'E:/pythonProject1/data/telegram-{massage.chat.id}')
        bot.send_message(massage.chat.id, f'Отлично, теперь используй команду help чтобы начать работу', reply_markup=markup2)
    elif massage.text == "Дата и время":
        bot.send_message(massage.chat.id, f'Сегодняшняя дата и время: {mess_time}', parse_mode='html')
    elif massage.text == "Сохранить мои фото":
        bot.send_message(massage.chat.id, 'Можешь скинуть своё фото и я его сохраню', parse_mode='html')
    elif massage.text == 'Получить мои фото':
        bot.send_message(massage.chat.id, 'Я не понимаю что ты хочешь', parse_mode='html')
    else:
        bot.send_message(massage.chat.id, 'Я не понимаю что ты хочешь', parse_mode='html')


@bot.message_handler(content_types=['photo'])
def get_user_photo(message):
    file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
    with open(f'E:/pythonProject1/data/telegram-{message.chat.id}\\' + message.photo[0].file_id + '.jpg', 'wb') as file:
        file.write(bot.download_file(file_info.file_path))
    bot.send_message(message.chat.id, 'Фото сохранил', parse_mode='html')


bot.polling(none_stop=True)
