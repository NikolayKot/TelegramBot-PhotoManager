import os
import telebot
import os.path
import json

from dotenv import load_dotenv
from Functions import *

load_dotenv()
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

mess_time = datetime.datetime.now()
bot = telebot.TeleBot(os.getenv('SECRET_KEY'))
menu_key = types.KeyboardButton('/Menu')
album_name = ''
download_album_name = 'Общий'
upload_album_name = 'Общий'
delete_album_name = ''
watch_album_name = 'Общий'


@bot.message_handler(commands=['Команды'])
def help_command(message):
    bot_send_message(message, """
    /help - справка
/Menu - меню команд
/new_album - создать альбом
/Skrol - просмотреть фото в альбоме
""")


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    req = call.data.split('_')
    images = os.listdir(Path('data', f'telegram-{call.message.chat.id}', f'{watch_album_name}'))
    # Обработка кнопки - скрыть
    if req[0] == 'unseen':
        bot.delete_message(call.message.chat.id, call.message.message_id)
    # Обработка кнопок - вперед и назад
    elif 'pagination' in req[0]:
        json_string = json.loads(req[0])
        count = json_string['CountPage']
        page = json_string['NumberPage']
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(text='Скрыть', callback_data='unseen'))
        # markup для первой страницы
        if page == 0:
            markup.add(InlineKeyboardButton(text=f'{page}/{count - 1}', callback_data=f' '),
                       InlineKeyboardButton(text=f'Вперёд --->',
                                            callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                                page + 1) + ",\"CountPage\":" + str(count) + "}"))
        # markup для второй страницы
        elif page == count - 1:
            markup.add(InlineKeyboardButton(text=f'<--- Назад',
                                            callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                                page - 1) + ",\"CountPage\":" + str(count) + "}"),
                       InlineKeyboardButton(text=f'{page}/{count - 1}', callback_data=f' '))
        # markup для остальных страниц
        else:
            markup.add(InlineKeyboardButton(text=f'<--- Назад',
                                            callback_data="{\"method\":\"pagination\",\"NumberPage\":"
                                                          + str(page - 1) + ",\"CountPage\":" + str(count) + "}"),
                       InlineKeyboardButton(text=f'{page}/{count - 1}', callback_data=f' '),
                       InlineKeyboardButton(text=f'Вперёд --->',
                                            callback_data="{\"method\":\"pagination\",\"NumberPage\":" + str(
                                                page + 1) + ",\"CountPage\":" + str(count) + "}"))
        img = open(Path('data', f'telegram-{call.message.chat.id}', f'{watch_album_name}', f'{images[page]}'), 'rb')
        bot.edit_message_media(media=telebot.types.InputMedia(media=img, caption=f"Фото номер {page}", type="photo"),
                               reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)


@bot.message_handler(commands=['start'])
def start(message):
    add(types.KeyboardButton('Зарегестрироваться'))
    bot_send_message(message, f'Привет, {message.from_user.first_name}, давай зарегестрируемся')


@bot.message_handler(commands=['new_album'])
def init_new_album(message):
    bot.send_message(message.chat.id, 'Придумай название для альбома', parse_mode='html')
    bot.register_next_step_handler(message, create_new_album)


@bot.message_handler(commands=['Menu'])
def website(message):
    add(types.KeyboardButton('Скрыть клавиатуру'),
        types.KeyboardButton("/Команды"),
        types.KeyboardButton('Получить мои фото'),
        types.KeyboardButton('Сохранить мои фото'),
        types.KeyboardButton('Просмотреть мои фото'),
        types.KeyboardButton('Удалить альбом'), )
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
            os.mkdir(path=Path('data', f'telegram-{message.chat.id}'))
            os.mkdir(path=Path('data', f'telegram-{message.chat.id}', 'Общий'))
            text = 'Отлично, ты зарегестрирован, можешь начать работу со мной'
        add()
    elif message.text == 'Скрыть клавиатуру':
        text = 'Если она понадобится то нажми /Menu'
        bot.send_message(message.chat.id, 'Хорошо', reply_markup=types.ReplyKeyboardRemove())
        add()
    elif message.text == 'Просмотреть мои фото':
        bot_send_message(message, 'Вот какие альбомы уже существуют:')
        with os.scandir(Path('data', f'telegram-{message.chat.id}')) as albums:
            for album_names in albums:
                bot_send_message(message, f'<b>{album_names.name}</b>')
        text = 'Напиши название альбома в который хочешь посмотреть'
        bot.register_next_step_handler(message, watch_album)
    elif message.text == "Сохранить мои фото":
        bot_send_message(message, 'Вот какие альбомы уже существуют:')
        with os.scandir(Path('data', f'telegram-{message.chat.id}')) as albums:
            for album_names in albums:
                bot_send_message(message, f'<b>{album_names.name}</b>')
        text = 'Напиши название альбома в который хочешь сохранить'
        bot.register_next_step_handler(message, download_to_album)
    elif message.text == 'Получить мои фото':
        bot_send_message(message, 'Вот какие альбомы уже существуют:')
        with os.scandir(
                Path('data', f'telegram-{message.chat.id}')) as albums:
            for album_names in albums:
                bot_send_message(message, f'<b>{album_names.name}</b>')
        text = 'Напиши название альбома который хочешь получить'
        bot.register_next_step_handler(message, upload_album)
    elif message.text == 'Удалить альбом':
        bot_send_message(message, 'Вот какие альбомы уже существуют:')
        with os.scandir(Path('data', f'telegram-{message.chat.id}')) as albums:
            for album_names in albums:
                bot_send_message(message, f'<b>{album_names.name}</b>')
        text = 'Напиши название альбома который хочешь удалить'
        bot.register_next_step_handler(message, delete_album)
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
        with open(f'{path}\\{message.photo[0].file_id}.jpg', 'wb') as file:
            file.write(bot.download_file(file_info.file_path))
    else:
        bot_send_message(message, f'Вы пытаетесть сохранить фото в альбом {upload_album_name}, а он несуществует')


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


def delete_album(message):
    global delete_album_name
    delete_album_name = message.text
    if os.path.exists(Path('data', f'telegram-{message.chat.id}', f'{delete_album_name}')):
        shutil.rmtree(Path('data', f'telegram-{message.chat.id}', f'{delete_album_name}'))
        text = f'Альбом {delete_album_name} удалён'
    else:
        text = 'Такой альбом не существует'
    add()
    bot_send_message(message, text)


def watch_album(message):
    global watch_album_name
    watch_album_name = message.text
    images = os.listdir(Path('data', f'telegram-{message.chat.id}', f'{watch_album_name}'))
    count = len(images)
    markup = InlineKeyboardMarkup()
    page = 0
    if count == 0:
        bot_send_message(message, 'Альбом пуст')
    elif count == 1:
        markup.add(InlineKeyboardButton(text='Скрыть', callback_data='unseen'))
        bot.send_photo(message.from_user.id,
                       photo=open(Path('data', f'telegram-{message.chat.id}', f'{watch_album_name}', f'{images[page]}'),
                                  'rb'), reply_markup=markup)
    else:
        markup.add(InlineKeyboardButton(text='Скрыть', callback_data='unseen'))
        markup.add(InlineKeyboardButton(text=f'{page}/{count - 1}', callback_data=f' '),
                   InlineKeyboardButton(text=f'Вперёд --->', callback_data="{\"method\":\"pagination\",\"NumberPage\":"
                                                                           + str(page + 1) + ",\"CountPage\":" + str(
                       count) + "}"))
        bot.send_photo(message.from_user.id,
                       photo=open(Path('data', f'telegram-{message.chat.id}', f'{watch_album_name}', f'{images[page]}'),
                                  'rb'), reply_markup=markup)


def create_new_album(message):
    global album_name
    album_name = message.text
    add(types.KeyboardButton('|Да.|'), types.KeyboardButton('|Нет.|'))
    bot_send_message(message, f'Вы назвали альбом как: {album_name}?')


def download_to_album(message):
    global download_album_name
    download_album_name = message.text
    if os.path.exists(Path('data', f'telegram-{message.chat.id}', f'{download_album_name}')):
        bot_send_message(message, f'Теперь можешь скинуть сюда свои фото и я сохраню их в <b>{download_album_name}</b>')
    else:
        add(types.KeyboardButton('Сохранить мои фото'))
        bot_send_message(message, 'Такого альбома не существует, проверте правильность ввода')


bot.polling(none_stop=True)
