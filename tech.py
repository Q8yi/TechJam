import os
import telebot

BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

CHAT_ID = ""
USERNAME = ""
all_employees = {}
curr_qn = ""

class employee():
    def __init__(self, name, chat_id):
        self.name = name
        self.chat_id = chat_id
        self.department = ""
        self.pos = ""
        self.qn = ""

    def update_department(self, new_depart):
        self.department = new_depart

    def update_pos(self, new_pos):
        self.pos = new_pos

    def update_qn(self, curr_qn):
        self.qn = curr_qn

    def get_qn(self):
        return self.qn

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    print("in")
    global CHAT_ID
    CHAT_ID = message.chat.id
    global USERNAME
    USERNAME = message.from_user.username
    employee1 = employee(CHAT_ID, USERNAME)
    all_employees[USERNAME] = employee1
    #print(all_employees[USERNAME])
    bot.reply_to(message, f"Hello {USERNAME}")
    all_employees[USERNAME].update_qn("first")
    bot.send_message(CHAT_ID, f"Welcome to TechJam! We will be assisting you in your sales enhancement journey")
    bot.send_message(CHAT_ID, "What is your position? [Executive, Staff]")

@bot.poll_handler(func=lambda poll: True)
def get_poll_results(poll):
    print(poll)
    print(poll.value)
    curr_emp = all_employees.get(USERNAME)
    if poll.question == "What is your position":
        bot.send_message(CHAT_ID, "Great! Nice to meet you!")
        bot.send_poll(CHAT_ID, "What is your team", ['Sales', 'IT', "Marketing", "Others"])
    else :
        bot.send_message(CHAT_ID, "You will soon be added to the respective group chats! Please keep me around as I will be giving improvement advices")

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    #print(message)
    curr_emp = all_employees.get(USERNAME)
    curr_qn = curr_emp.get_qn()
    text = message.text.lower()
    if curr_qn == "first":
        if text == "executive" or text == "staff":
            curr_emp.update_qn("second")
            curr_emp.update_pos(text)
            bot.send_message(CHAT_ID, "What is your team? [Sales, IT, Marketing, Others]")
        else :
            bot.send_message(CHAT_ID, "Please key in a valid Position")
    elif curr_qn == "second":
        curr_emp.update_department(text)
        curr_emp.update_qn("")
        bot.send_message(CHAT_ID, "Please join the following group")
        if text == "sales":
            bot.reply_to(message, "<tele chat link>")
        elif text == "marketing":
            bot.reply_to(message, "<tele chat link>")
        elif text == "it":
            bot.reply_to(message, "<tele chat link>")
        elif text == "others":
            bot.reply_to(message, "<tele chat link>")
    else:
        bot.reply_to(message, text)

bot.infinity_polling()