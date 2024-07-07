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

    def update_department(self, new_depart):
        self.department = new_depart

    def update_pos(self, new_pos):
        self.pos = new_pos

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
    global curr_qn
    curr_qn = "first"
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
    global curr_qn
    text = message.text
    curr_emp = all_employees.get(USERNAME)
    if curr_qn == "first":
        if text == "Executive" or text == "Staff":
            curr_qn = "second"
            curr_emp.update_pos(text)
            bot.send_message(CHAT_ID, "What is your team? [Sales, IT, Marketing, Others]")
        else :
            bot.send_message(CHAT_ID, "Please key in a valid Position")
    elif curr_qn == "second":
        curr_emp.update_department(text)
        bot.send_message(CHAT_ID, "Please join the following group")
        if text == "Sales":
            bot.reply_to(message, "<tele chat link>")
        elif text == "Marketing":
            bot.reply_to(message, "<tele chat link>")
        elif text == "IT":
            bot.reply_to(message, "<tele chat link>")
        elif text == "Others":
            bot.reply_to(message, "<tele chat link>")
    else:
        bot.reply_to(message, text)

bot.infinity_polling()