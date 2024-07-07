import os
import telebot
import pandas as pd
import re
#visualisation
import matplotlib.pyplot as plt
import io
from PIL import Image
#ML
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

#for telebot
CHAT_ID = ""
USERNAME = ""
all_employees = {}
curr_qn = ""

#for database
try:
    data = pd.read_csv('data.csv', encoding='utf-8')
except UnicodeDecodeError:
    data = pd.read_csv('data.csv', encoding='latin1')

data['grand_total'] = data['Quantity'] * data['UnitPrice']

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
    USERNAME = message.from_user.first_name
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
    to_send = "Please join the following group"
    if curr_qn == "first":
        if text == "executive" or text == "staff":
            curr_emp.update_qn("second")
            curr_emp.update_pos(text)
            bot.send_message(CHAT_ID, "What is your team? [Sales, IT, Marketing, Others]")
        else :
            bot.send_message(CHAT_ID, "Please key in a valid team")
    elif curr_qn == "second":
        curr_emp.update_department(text)
        curr_emp.update_qn("")
        if text == "sales":
            bot.reply_to(message, f"{to_send} <tele chat link>")
        elif text == "marketing":
            bot.reply_to(message, f"{to_send} <tele chat link>")
        elif text == "it":
            bot.reply_to(message, f"{to_send} <tele chat link>")
        elif text == "others":
            bot.reply_to(message, f"{to_send} <tele chat link>")
        else :
            bot.send_message(CHAT_ID, "Please key in a valid Position")
    elif (("prediction" in text or "forecast" in text) and (curr_emp != None)):
        selected = data.loc[:, ['InvoiceNo', 'Description', 'Quantity', 'InvoiceDate', 'CustomerID', 'Country', 'grand_total']]

        # Convert 'InvoiceDate' to datetime format
        selected['InvoiceDate'] = pd.to_datetime(selected['InvoiceDate'])

        # Extract date and time features
        selected['DayOfWeek'] = selected['InvoiceDate'].dt.dayofweek
        selected['Month'] = selected['InvoiceDate'].dt.month
        selected['Year'] = selected['InvoiceDate'].dt.year
        selected['Hour'] = selected['InvoiceDate'].dt.hour

        # Example: Calculate total quantity per customer
        customer_total_quantity = selected.groupby('CustomerID')['Quantity'].sum().reset_index()
        customer_total_quantity.rename(columns={'Quantity': 'TotalQuantity'}, inplace=True)
        selected = selected.merge(customer_total_quantity, on='CustomerID', how='left')

        # Example: Perform one-hot encoding for the 'Country' column
        country_dummies = pd.get_dummies(selected['Country'], prefix='Country')
        selected = pd.concat([selected, country_dummies], axis=1)

        # Define the features and target variable
        features = ['Quantity', 'DayOfWeek', 'Month', 'Year', 'Hour', 'TotalQuantity', 'Country_United Kingdom']
        X = selected[features]
        y = selected['grand_total']

        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Handle missing values (if any)
        imputer = SimpleImputer(strategy='mean')
        X_train_imputed = imputer.fit_transform(X_train)
        X_test_imputed = imputer.transform(X_test)

        # Scale the features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train_imputed)
        X_test_scaled = scaler.transform(X_test_imputed)

        # Create and train the linear regression model
        model = LinearRegression()
        model.fit(X_train_scaled, y_train)

        # Make predictions
        y_pred = model.predict(X_test_scaled)

        # Evaluate the model
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        print('Mean Squared Error:', mse)
        print('R-squared:', r2)

        plt.figure()
        plt.plot(X_train["Quantity"], y_train, color='blue')
        plt.plot(X_test["Quantity"], y_pred, color='red')
        plt.title("Predictions for grand total against Quantity")

        fig = plt.gcf()
        buffer = io.BytesIO()
        fig.savefig(buffer)
        buffer.seek(0)
        img = Image.open(buffer)
        bot.send_photo(chat_id=CHAT_ID, photo = img)

        plt.figure()
        plt.plot(X_train["Hour"], y_train, color='blue')
        plt.plot(X_test["Hour"], y_pred, color='red')
        plt.title("Predictions for grand total against Hour of Day")

        #send image of graph prediction
        fig = plt.gcf()
        buffer = io.BytesIO()
        fig.savefig(buffer)
        buffer.seek(0)
        img = Image.open(buffer)
        bot.send_photo(chat_id=CHAT_ID, photo = img)

        bot.send_message(CHAT_ID, "Most sales happen between 8am to 2pm")
    elif (("summary" in text) and (curr_emp !=None)):
        plt.figure(figsize=(10, 6))
        plt.plot(data.index, data['grand_total'], label='Daily Sales')
        plt.xlabel('Date')
        plt.ylabel('Sales')
        plt.title('Daily Sales Summary')
        plt.legend()
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        bot.send_photo(message.chat.id, photo=buffer)       
    else:
        bot.reply_to(message, text)

bot.infinity_polling()
