import datetime
import os
import telebot
import pathlib
import os.path
import zipfile
import shutil

from pathlib import Path
from dotenv import load_dotenv
from telebot import types
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()

mess_time = datetime.datetime.now()
bot = telebot.TeleBot(os.getenv('SECRET_KEY'))

PARSE_MOD = 'html'
markup = types.ReplyKeyboardMarkup(resize_keyboard=True)


def add(*args):
    global markup
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for i in args:
        markup.add(i)
    markup.add(types.KeyboardButton('/Menu'))


def bot_send_message(telegram_object, message, parse_mode=PARSE_MOD):
    bot.send_message(telegram_object.chat.id, message, parse_mode=parse_mode, reply_markup=markup)


def approved_album(message):
    bot.send_message(message.chat.id, 'Да-да')


def archivate(arch, folders_list, mode):
    zip = zipfile.ZipFile(arch, mode, zipfile.ZIP_DEFLATED, True)
    for add_folder in folders_list:
        for root, dirs, files in os.walk(add_folder):
            for file in files:
                zip.write(os.path.join(root, file))  # path = os.path.join(root, file)
    zip.close()


def create_new_album(message):
    album_name = message.text
    bot_send_message(message, f'Вы назвали альбом как: {album_name}')
    path = Path('data', f'telegram-{message.chat.id}', f'{album_name}')
    if os.path.exists(f'{path}'):
        add(types.KeyboardButton('/new_album'))
        text = 'Такой альбом уже существует, ты можешь создать другой альбом или перейти в меню'
    elif album_name == '/Menu':
        text = 'Нельзя назвать альбом /Menu'
    else:
        os.mkdir(path)
        text = 'Альбом создан'
    add()
    bot_send_message(message, text)

