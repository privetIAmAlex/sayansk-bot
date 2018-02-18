import telebot
from worker import Worker
import time

bot = telebot.TeleBot("423190741:AAG1Y_CcW6_A0VX33XBkVGGMtB-tYyYMOpU")
worker = Worker()

@bot.message_handler(commands=["create"])
def create_handler(message):
    try:
        worker.CreateInterview(bot, message)
    except Exception as ex:
        bot.send_message(497551952, ex)

@bot.message_handler(commands=["done"])
def done_handler(message):
    try:
        worker.Interview(bot, message)
        worker.Confirmation(bot, message)
    except Exception as ex:
        bot.send_message(497551952, ex)

@bot.message_handler(content_types=["new_chat_members"])
def new_members_handler(message):
    worker.HelloUser(bot, message)
    
@bot.message_handler(content_types=["text"])
def handle_message(message):
    day = time.strftime("%w")    
    if message.text == "hiked29" and message.from_user.id == 497551952:
        if day == '0':
            worker.GetCount(bot, -1001137097313)
        else:
            worker.GetCount(bot, message.chat.id)
        return 

    if "uz" in message.text[:3].lower():
        worker.Translate(bot, message)

    worker.Count(message.from_user.id)
    if worker.FindBadWord(message) == True:
        worker.BlockUser(bot, message.chat.id, message.from_user.id, message.from_user.first_name, message.message_id)

@bot.callback_query_handler(func=lambda c: True)
def likes(c):
    worker.HandlerCLick(c, bot)
    
bot.polling(none_stop=True)