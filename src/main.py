import datetime
import os
import telebot
import os.path

from dotenv import load_dotenv
from Functions import *
load_dotenv()

mess_time = datetime.datetime.now()
bot = telebot.TeleBot(os.getenv('SECRET_KEY'))
album_name = ''
download_album_name = ''
upload_album_name = ''
menu_key = types.KeyboardButton('/Menu')


@bot.message_handler(commands=['help'])
def help_command(message):
    bot_send_message(message, """
    /help - справка
/Menu - меню команд
/new_album - создать альбом""")


@bot.message_handler(commands=['start'])
def start(message):
    add(types.KeyboardButton('Зарегестрироваться'))
    bot_send_message(message, f'Привет, {message.from_user.first_name}, давай зарегестрируемся')


@bot.message_handler(commands=['new_album'])
def init_new_album(message):
    bot.send_message(message.chat.id, 'Придумай название для альбома', parse_mode='html')
    bot.register_next_step_handler(message, create_new_album)


def create_new_album(message):
    global album_name
    album_name = message.text
    add(types.KeyboardButton('|Да.|'), types.KeyboardButton('|Нет.|'))
    bot_send_message(message, f'Вы назвали альбом как: {album_name}?')
    # Проверка имени на корректность


def download_to_album(message):
    global download_album_name
    download_album_name = message.text
    if os.path.exists(Path('data', f'telegram-{message.chat.id}', f'{download_album_name}')):
        bot_send_message(message, f'Теперь можешь скинуть сюда свои фото и я сохраню их в {download_album_name}')
    else:
        add(types.KeyboardButton('Сохранить мои фото'))
        bot_send_message(message, 'Такого альбома не существует, проверте правильность ввода')


def upload_album(message):
    global upload_album_name
    upload_album_name = message.text
    archived_folders = [Path('data', f'telegram-{message.chat.id}', f'{upload_album_name}')]
    if os.path.exists(Path('data', f'telegram-{message.chat.id}', f'{upload_album_name}')):
        arch_name = "Telegram_photo" + ".zip"
        archivate(arch_name, archived_folders, "w")
        with open(Path(f'{arch_name}'), 'rb') as file:
            bot.send_document(message.chat.id, file)
        os.remove(Path(arch_name))
    else:
        add(types.KeyboardButton('Получить мои фото'))
        bot_send_message(message, 'Такой альбом не существует, проверьте корректность ввода')


@bot.message_handler(commands=['Menu'])
def website(message):
    add(types.KeyboardButton("/help"), types.KeyboardButton("Дата и время"), types.KeyboardButton('Получить мои фото'),
        types.KeyboardButton('Сохранить мои фото'))
    bot_send_message(message, 'Выбири пункт')


@bot.message_handler(func=lambda m: True)
def user_text(message):
    global menu_key
    text = 'Я не понимаю что ты хочешь'
    if message.text == "Привет":
        text = 'И тебе привет'
    elif message.text == "Зарегестрироваться":
        user_path = Path('data', f'telegram-{message.chat.id}')
        if os.path.exists(f'{user_path}'):
            text = 'Вы уже зарегестрированны'
        else:
            os.mkdir(
                path=Path('data', f'telegram-{message.chat.id}'))  # path = Path('data', f'telegram-{message.chat.id}')
            text = 'Отлично, ты зарегестрирован, можешь начать работу со мной'
    elif message.text == "Дата и время":
        text = f'Сегодняшняя дата и время: {mess_time}'
    elif message.text == "Сохранить мои фото":
        bot_send_message(message, 'Вот какие альбомы уже существуют:')
        with os.scandir(Path('data', f'telegram-{message.chat.id}')) as it:
            for entry in it:
                bot_send_message(message, f'<b>{entry.name}</b>')
        text = 'Напиши название альбома в который хочешь сохранить'
        bot.register_next_step_handler(message, download_to_album)
    elif message.text == 'Получить мои фото':
        bot_send_message(message, 'Вот какие альбомы уже существуют:')
        with os.scandir(Path('data', f'telegram-{message.chat.id}')) as it:
            for entry in it:
                bot_send_message(message, f'<b>{entry.name}</b>')
        text = 'Напиши название альбома который хочешь получить'
        bot.register_next_step_handler(message, upload_album)
    elif message.text == '|Да.|':
        path = Path('data', f'telegram-{message.chat.id}', f'{album_name}')
        if os.path.exists(f'{path}'):
            add(types.KeyboardButton('/new_album'))
            text = 'Такой альбом уже существует, ты можешь создать другой альбом или перейти в меню'
        else:
            os.mkdir(path)
            add()
            text = 'Альбом создан'
    elif message.text == '|Нет.|':
        text = 'Хорошо, ты можешь создать другой альбом или перейти в меню'
        add(types.KeyboardButton('/new_album'))

    bot_send_message(message, text)


@bot.message_handler(content_types=['photo'])
def user_photo(message):
    path = Path('data', f'telegram-{message.chat.id}', f'{download_album_name}')
    if os.path.exists(f'{path}'):
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        with open(f'{path}\\' + message.photo[0].file_id + '.jpg', 'wb') as file:
            file.write(bot.download_file(file_info.file_path))
        bot_send_message(message, 'Фото сохранил')
    else:
        bot_send_message(message, f'Вы пытаетесть сохранить фото в несуществующий альбом')


bot.polling(none_stop=True)
