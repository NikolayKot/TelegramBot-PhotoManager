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
    key_yes = types.KeyboardButton('|Да.|')
    key_no = types.KeyboardButton('|Нет.|')
    markup.add(key_yes, key_no)
    bot.send_message(message.chat.id, f'Вы назвали альбом как: {album_name}', reply_markup=markup)
    # Проверка имени на корректность


@bot.message_handler(commands=['Menu'])
def website(message):
    help_butt = types.KeyboardButton("/help")
    date = types.KeyboardButton("Дата и время")
    get_photo = types.KeyboardButton('Получить мои фото')
    save_photo = types.KeyboardButton('Сохранить мои фото')
    markup.add(date, get_photo, save_photo, help_butt)
    bot_send_message(message, 'Выбери пункт')


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
        text = 'Можешь скинуть своё фото и я его сохраню'
    elif message.text == 'Получить мои фото':
        archived_folders = [Path('data', f'telegram-{message.chat.id}')]
        arch_name = "Telegram_photo" + ".zip"
        archivate(arch_name, archived_folders, "w")
        with open(f'E:/pythonProject1/{arch_name}', 'rb') as file:  # TODO путь абсоюлтный сделать!
            bot.send_document(message.chat.id, file)
        os.remove(Path(arch_name))
        text = 'Вот все твои фото'
    elif message.text == '|Да.|':
        path = Path('data', f'telegram-{message.chat.id}', f'{album_name}')
        if os.path.exists(f'{path}'):
            new_album_key = types.KeyboardButton('/new_album')
            markup.add(menu_key, new_album_key)
            text = 'Нажми на кнопку Menu или создай новый альбом при помощи кнопки new_album'
            bot.send_message(message.chat.id, 'Такой альбом уже существует', reply_markup=markup)
        else:
            os.mkdir(path)
            text = 'Ты можешь воспользоваться кнопкой Menu'
            markup.add(menu_key)
            bot.send_message(message.chat.id,'Альбом создан',reply_markup=markup)
    elif message.text == '|Нет.|':
        text = 'Просто выбери один из вариантов'
        key_new_name = types.KeyboardButton('/new_album')
        markup.add(key_new_name, menu_key)
        bot.send_message(message.chat.id,
                         'Ты можешь придумать иное название, или использовать другие функции',
                         reply_markup=markup)

    bot_send_message(message, text)


@bot.message_handler(content_types=['photo'])
def user_photo(message):
    file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
    path = Path('data', f'telegram-{message.chat.id}')
    with open(f'{path}\\' + message.photo[0].file_id + '.jpg', 'wb') as file:
        file.write(bot.download_file(file_info.file_path))
    bot_send_message(message, 'Фото сохранил')


bot.polling(none_stop=True)
