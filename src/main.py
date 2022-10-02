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
album_name = 'Общий'
delete_album_name = ''
xyi = ''


def album_worker(message):
    global xyi
    xyi = message.text
    markup = InlineKeyboardMarkup()
    with os.scandir(Path('data', f'telegram-{message.chat.id}')) as albums:
        for album_names in albums:
            markup.add(InlineKeyboardButton(text=f'{album_names.name}', callback_data=f'{album_names.name}'))
        bot.send_message(message.chat.id, 'Вот такие альбомы существуют', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    with os.scandir(Path('data', f'telegram-{call.message.chat.id}')) as albums:
        for album_names in albums:
            if call.data == album_names.name:
                global album_name
                album_name = album_names.name
                bot.send_message(call.message.chat.id, f'Вы выбрали альбом {album_name}')
                call.message.text = album_name
        if xyi == 'Сохранить мои фото':
            download_to_album(call.message)
        elif xyi == 'Получить мои фото':
            upload_album(call.message)
        elif xyi == 'Просмотреть мои фото':
            watch_album(call.message)                       #TODO НЕ РАБОТАЕТ СУКА
        elif xyi == 'Удалить альбом':
            delete_album(call.message)
    req = call.data.split('_')
    images = os.listdir(Path('data', f'telegram-{call.message.chat.id}', f'{album_name}'))
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
        img = open(Path('data', f'telegram-{call.message.chat.id}', f'{album_name}', f'{images[page]}'), 'rb')
        bot.edit_message_media(media=telebot.types.InputMedia(media=img, caption=f"Фото номер {page}", type="photo"),
                               reply_markup=markup, chat_id=call.message.chat.id, message_id=call.message.message_id)


@bot.message_handler(commands=['start'])
def start(message):
    add(types.KeyboardButton('Зарегестрироваться'))
    bot_send_message(message, f'Привет, {message.from_user.first_name}, давай зарегестрируемся')


@bot.message_handler(commands=['Создать_альбом'])
def init_new_album(message):
    bot.send_message(message.chat.id, 'Придумай название для альбома', parse_mode='html',
                     reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, create_new_album)


@bot.message_handler(commands=['Menu'])
def website(message):
    add(types.KeyboardButton('Скрыть клавиатуру'),
        types.KeyboardButton("/Создать_альбом"),
        types.KeyboardButton('Получить мои фото'),
        types.KeyboardButton('Сохранить мои фото'),
        types.KeyboardButton('Просмотреть мои фото'),
        types.KeyboardButton('Удалить альбом'), )
    bot_send_message(message, 'Выбири пункт')


@bot.message_handler(func=lambda m: True)
def user_text(message):
    text = 'Я не понимаю что ты хочешь'
    base = {
        "Сохранить мои фото": album_worker,
        'Получить мои фото': album_worker,
        'Просмотреть мои фото': album_worker,
        'Удалить альбом': album_worker
    }
    for key in base:
        if message.text == key:
            text = 'Напиши название интересующего тебя альбома:'
            base[key](message)
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
    elif message.text == 'Скрыть клавиатуру':
        text = 'Если она понадобится то нажми /Menu'
        bot.send_message(message.chat.id, 'Хорошо', reply_markup=types.ReplyKeyboardRemove())
    add()
    bot_send_message(message, text)


@bot.message_handler(content_types=['photo'])
def user_photo(message):
    path = Path('data', f'telegram-{message.chat.id}', f'{album_name}')
    if os.path.exists(f'{path}'):
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        with open(f'{path}\\{message.photo[0].file_id}.jpg', 'wb') as file:
            file.write(bot.download_file(file_info.file_path))
    else:
        bot_send_message(message, f'Вы пытаетесть сохранить фото в альбом {album_name}, а он несуществует')


def upload_album(message):
    archived_folders = [Path('data', f'telegram-{message.chat.id}', f'{album_name}')]
    if os.path.exists(Path('data', f'telegram-{message.chat.id}', f'{album_name}')):
        arch_name = "Telegram_photo" + ".zip"
        archivate(arch_name, archived_folders, "w")
        with open(Path(f'{arch_name}'), 'rb') as file:
            bot.send_document(message.chat.id, file)
        os.remove(Path(arch_name))
    else:
        add(types.KeyboardButton('Получить мои фото'))
        bot_send_message(message, 'Такой альбом не существует, проверьте корректность ввода')


def delete_album(message):
    if os.path.exists(Path('data', f'telegram-{message.chat.id}', f'{delete_album_name}')):
        shutil.rmtree(Path('data', f'telegram-{message.chat.id}', f'{delete_album_name}'))
        text = f'Альбом {delete_album_name} удалён'
    else:
        text = 'Такой альбом не существует'
    add()
    bot_send_message(message, text)


def watch_album(message):
    if os.path.exists(Path('data', f'telegram-{message.chat.id}', f'{album_name}')):
        images = os.listdir(Path('data', f'telegram-{message.chat.id}', f'{album_name}'))
        count = len(images)
        markup = InlineKeyboardMarkup()
        page = 0
        if count == 0:
            bot_send_message(message, 'Альбом пуст')
        elif count == 1:
            markup.add(InlineKeyboardButton(text='Скрыть', callback_data='unseen'))
            bot.send_photo(message.from_user.id,
                           photo=open(Path('data', f'telegram-{message.chat.id}', f'{album_name}',
                                      f'{images[page]}'),
                                      'rb'), reply_markup=markup)
        else:
            markup.add(InlineKeyboardButton(text='Скрыть', callback_data='unseen'))
            markup.add(InlineKeyboardButton(text=f'{page}/{count - 1}', callback_data=f' '),
                       InlineKeyboardButton(text=f'Вперёд --->', callback_data="{\"method\":\"pagination\","
                                                                               "\"NumberPage\": "
                                                                               + str(page + 1) + ",\"CountPage\":" +
                                                                               str(
                                                                                count) + "}"))
            bot.send_photo(message.from_user.id,
                           photo=open(Path('data', f'telegram-{message.chat.id}', f'{album_name}',
                                      f'{images[page]}'),
                                      'rb'), reply_markup=markup)
    else:
        bot_send_message(message, 'Такого альбома не существует')


def download_to_album(message):
    if os.path.exists(Path('data', f'telegram-{message.chat.id}', f'{album_name}')):
        bot_send_message(message, f'Теперь можешь скинуть сюда свои фото и я сохраню их в <b>{album_name}</b>')
    else:
        add(types.KeyboardButton('Сохранить мои фото'))
        bot_send_message(message, 'Такого альбома не существует, проверте правильность ввода')


bot.polling(none_stop=True)
