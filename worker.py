import time
from telebot import types
import random

class Worker:

    bad_words = []
    black_list = {}
    admins = [351956291, 259089620]
    messages = 0
    stat = {}

    phrases = [
        "Добро пожаловать, {0}!☺️\n\nУ нас культурный чат! Здесь нельзя материться и оскорблять других участников.🚫\nВсе правила ты можешь посмотреть в закреплённом сверху сообщении👆\n\nДавай познакомимся? Расскажи немного о себе!🤗",
        "Приветствую тебя, {0}!✋️\n\nУ нас культурный чат! Здесь нельзя материться и оскорблять других участников.🚫\nВсе правила ты можешь посмотреть в закреплённом сверху сообщении👆\n\nРасскажешь что-нибудь о себе?😊",
        "Какие люди! Привет, {0}!😎\n\nПожалуйста, соблюдай правила группы, а то забаню. Шутка🤣\nВсе правила ты можешь посмотреть в закреплённом сверху сообщении👆\n\nДавай познакомимся? Расскажи что-нибудь о себе🤗",
        "Привет, {0}!🤓\n\nУ нас очень дружелюбный чат, так что не бойся писать, мы не кусаемся!😄 Только не матерись пожалуйста😉\nВсе правила ты можешь посмотреть в закреплённом сверху сообщении👆"
    ]

    BOT = None
    question = ""
    variants = {}
    voters = {}

    def __init__(self):
        with open('badwords.txt', 'r', encoding='cp1251') as f:  
            content = f.readlines()
            for word in content:
                self.bad_words.append(word[:-1])

    def FindBadWord(self, message):
        for word in message.text.split(' '):
            word = word.lower()
            for bad_word in self.bad_words:
                if word == bad_word or "хуен" in word:
                    return True
        return False

    def BlockUser(self, _bot, chat_id, user_id, user_firstname, message_id):
        if user_id in self.admins:
            _bot.send_message(chat_id, "Тебе повезло, что ты админ😑", reply_to_message_id=message_id)
            return
        time_now = time.time()
        black_keys = self.black_list.keys()
        if user_id in black_keys:
            count = self.black_list.get(user_id)
            count += 1
            self.black_list[user_id] = count

            if count == 2:
                _bot.restrict_chat_member(chat_id, user_id, until_date=time_now+300)
                _bot.send_message(chat_id, "<b>{} заблокирован(а) на 5 минут</b>\n\n{}, у нас нельзя материться!\nВ следующий раз наказание будет строже!".format(user_firstname, user_firstname), parse_mode="html")

            elif count >= 3:
                _bot.restrict_chat_member(chat_id, user_id, until_date=time_now+3600)
                _bot.send_message(chat_id, "<b>{} заблокирован(а) на 1 час</b>\n\n{}, у нас нельзя материться!\nВ следующий раз наказание будет строже!".format(user_firstname, user_firstname), parse_mode="html")
        else:
            self.black_list.update({user_id:1})
            _bot.restrict_chat_member(chat_id, user_id, until_date=time_now+60)
            _bot.send_message(chat_id, "<b>{} заблокирован(а) на 1 минуту</b>\n\n{}, у нас нельзя материться!\nВ следующий раз наказание будет строже!".format(user_firstname, user_firstname), parse_mode="html")
        _bot.delete_message(chat_id, message_id)

    def Count(self, user_id):
        self.messages += 1
        ids = self.stat.keys()
        if user_id in ids:
            self.stat[user_id] += 1
        else:
            self.stat.update({user_id:1})

    def GetKey(self, d, value):
        for k, v in d.items():
            if v == value:
                return k

    def GetUsernameByID(self, _bot, chat_id, id):
        user_info = _bot.get_chat_member(chat_id, id)
        if user_info.user.username != None:
            return "@" + user_info.user.username
        else:
            return user_info.user.first_name

    def CurrentWord(self, number):
        iy = ['11', '12', '13', '14', '5', '6', '7', '8', '9', '0']
        for i in range(len(iy)):
            if iy[i] in number:
                return "сообщений"          
        if number.endswith('1'):
            return "сообщение"
        elif number.endswith('2') or number.endswith('3') or number.endswith('4'):
            return "сообщения"
        else:
            return "сообщ."

    def GetCount(self, _bot, chat_id):
        names = ""
        word = self.CurrentWord(str(self.messages))
        sorted_stat = sorted(self.stat.values(), reverse=True)
        try:
            for i in range(9):
                username = self.GetUsernameByID(_bot, chat_id, self.GetKey(self.stat, sorted_stat[i]))
                names += "{} - {}\n".format(username, sorted_stat[i])
        except Exception:
            pass
        letter = "Вот и подошла к концу ещё одна неделя! И вот вам немного статистики:\n\n<i>Самые активные участники:</i>\n{}\nА всего было напечатано <b>{}</b> {}!\nУдачи в наступающей неделе!😉".format(names, self.messages, word)
        _bot.send_message(chat_id, letter, parse_mode="HTML")

    def HelloUser(self, _bot, _message):
        user_name = _message.new_chat_member.first_name
        _bot.send_message(_message.chat.id, random.choice(self.phrases).format(user_name))

    def ButtonsKeyboard(self):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(*[types.InlineKeyboardButton(text=f"{str(var)} - {str(self.variants.get(var))}", callback_data=f"{str(var)} - {str(self.variants.get(var))}") for var in self.variants.keys()])        
        return keyboard

    def Interview(self, _bot, _message):
        _bot.send_message(_message.chat.id, self.question, reply_markup=self.ButtonsKeyboard())

    def HandlerCLick(self, _c, _bot):
        answer = _c.data.split(' ')
        try:
            for key in self.variants:
                if answer[0] == key and _c.from_user.id not in self.voters:
                    self.variants[key] += 1
                    self.voters.update({_c.from_user.id:answer[0]})              
                    _bot.edit_message_text(
                        chat_id=_c.message.chat.id,
                        message_id=_c.message.message_id,
                        text=self.question,
                        reply_markup=self.ButtonsKeyboard()
                    )
                    return
                elif answer[0] == key and _c.from_user.id in self.voters:
                    self.variants[self.voters[_c.from_user.id]] -= 1
                    self.variants[key] += 1                
                    self.voters.update({_c.from_user.id:answer[0]})
                    _bot.edit_message_text(
                        chat_id=_c.message.chat.id,
                        message_id=_c.message.message_id,
                        text=self.question,
                        reply_markup=self.ButtonsKeyboard()
                    )
                    return
        except Exception:
            pass        
                
    def CreateInterview(self, _bot, _message):
        self.BOT = _bot
        self.BOT.send_message(_message.from_user.id, "Введите вопрос:")
        self.BOT.register_next_step_handler(_message, self.add_question)
    
    def add_question(self, _message):
        self.question = _message.text
        self.BOT.send_message(_message.chat.id, "Напишите варианты ответа:")
        self.BOT.register_next_step_handler(_message, self.variant)
    
    def variant(self, _message):
        if _message.text == "/done":
            return
        self.variants.update({_message.text:0})
        self.BOT.send_message(_message.chat.id, f"Вариант <b>'{_message.text}'</b> добавлен. Если вы хотите закончиить создание опроса, напишите /done\nЕсли хотите добавить ещё вариантов ответа, то продолжайте отправлять их", parse_mode="HTML")
        self.BOT.register_next_step_handler(_message, self.variant)

    def Confirmation(self, _bot, _message):
        keyboard = types.ReplyKeyboardMarkup(True, True)
        keyboard.row("Опубликовать", "Удалить")
        _bot.send_message(_message.from_user.id, "Отправить этот опрос в группу?", reply_markup=keyboard)
        _bot.register_next_step_handler(_message, self._conf)
    
    def _conf(self, _message):
        if _message.text == "Опубликовать":
            self.BOT.send_message(-1001138206230, self.question, reply_markup=self.ButtonsKeyboard())#1001137097313
            self.BOT.send_message(_message.from_user.id, "Опубликовано")
            self.variants.clear()
            self.voters.clear()
        else:
            self.variants.clear()
            self.voters.clear()
            self.question = ""
            self.BOT.send_message(_message.from_user.id, "Удалено")            
            self.BOT = None