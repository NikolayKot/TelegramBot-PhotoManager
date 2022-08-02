import datetime
import os
import telebot
import os.path

from dotenv import load_dotenv
from Functions import website
from Functions import start
from Functions import user_text
from Functions import user_photo

load_dotenv()

mess_time = datetime.datetime.now()
bot = telebot.TeleBot(os.getenv('SECRET_KEY'))


@bot.message_handler(commands=['start'], func=start)
@bot.message_handler(commands=['Начать'], func=website)
@bot.message_handler(content_types=['text'], func=user_text)
@bot.message_handler(content_types=['photo'])
def get_user_photo(massage):
    user_photo(massage)


bot.polling(none_stop=True)
