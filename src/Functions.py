import datetime
import os
import telebot
import pathlib
import os.path

from pathlib import Path
from dotenv import load_dotenv
from telebot import types

load_dotenv()

mess_time = datetime.datetime.now()
bot = telebot.TeleBot(os.getenv('SECRET_KEY'))

b=bot.send_message

def website(massage):
    markup = types.ReplyKeyboardMarkup()
    Date = types.KeyboardButton("Дата и время")
    get_photo = types.KeyboardButton('Получить мои фото')
    save_photo = types.KeyboardButton('Сохранить мои фото')
    markup.add(Date, get_photo, save_photo)
    b(massage.chat.id, 'Выбери пункт', reply_markup=markup)


def start(massage):
    markup1 = types.ReplyKeyboardMarkup()
    ID = types.KeyboardButton('Зарегестрироваться')
    markup1.add(ID)
    b(massage.chat.id, f'Привет, {massage.from_user.first_name}, давай зарегестрируемся', reply_markup=markup1)


def user_text(massage):

    markup_help = types.ReplyKeyboardMarkup()
    help = types.KeyboardButton("/Начать")
    markup_help.add(help)

    if massage.text == "Привет":
        b(massage.chat.id, 'И тебе привет', parse_mode='html')
    elif massage.text == "Зарегестрироваться":
        user_path = Path('data', f'telegram-{massage.chat.id}')
        if os.path.exists(f'{user_path}') == True:
            b(massage.chat.id, 'Вы уже зарегестрированны', reply_markup=markup_help)
        else:
            path = Path('data', f'telegram-{massage.chat.id}')
            os.mkdir(path)
            b(massage.chat.id, f'Отлично, ты зарегестрирован, можешь начать работу со мной', reply_markup=markup_help)

    elif massage.text == "Дата и время":
        b(massage.chat.id, f'Сегодняшняя дата и время: {mess_time}', parse_mode='html')
    elif massage.text == "Сохранить мои фото":
        b(massage.chat.id, 'Можешь скинуть своё фото и я его сохраню', parse_mode='html')
    elif massage.text == 'Получить мои фото':
        b(massage.chat.id, 'Я не понимаю что ты хочешь', parse_mode='html')
    else:
        b(massage.chat.id, 'Я не понимаю что ты хочешь', parse_mode='html')


def user_photo(massage):
    file_info = bot.get_file(massage.photo[len(massage.photo) - 1].file_id)
    path = Path('data', f'telegram-{massage.chat.id}')
    with open(f'{path}\\' + massage.photo[0].file_id + '.jpg', 'wb') as file:
        file.write(bot.download_file(file_info.file_path))
    b(massage.chat.id, 'Фото сохранил', parse_mode='html')