import sqlite3
from datetime import date
import csv

connection = sqlite3.connect("budget_tracker.db")
cursor = connection.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100),
                password VARCHAR(100),
                income INT,
                saving_rate FLOAT
                )""")

cursor.execute("""CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100),
                amount INT,
                category VARCHAR(100),
                transaction_date DATE
                )""")

logged_in = False
action_selected = False

welcome = input("Welcome to the EmmZaa Budget Tracker. Are you a new user? Enter Y or N. \t")

while logged_in is False and welcome == "Y":
    username = str(input("\nSelect a username. \t"))
    cursor.execute("SELECT count(*) FROM users WHERE username = ?", (username,))
    temp = cursor.fetchall()

    if temp[0][0] == 0:
        password = str(input("Select a password. \t"))
        income = float(input("Enter your monthly income in CAD. \t"))
        saving_rate = float(input("Enter the percentage of your income you would like to save each month. \t"))
        cursor.execute("INSERT INTO users (username, password, income, saving_rate) "
                       "VALUES (?, ?, ?, ?)", (username, password, income, saving_rate))
        connection.commit()
        logged_in = True
        print("\nYour account has been successfully created.")

    else:
        print("\nThis username already exists. Please select a different username.")

while logged_in is False and welcome == "N":
    username = str(input("Enter your username. \t"))
    password = str(input("Enter your password. \t"))
    cursor.execute("SELECT username, password FROM users WHERE username = ?", (username,))
    temp = cursor.fetchall()

    if len(temp) == 1 and username == temp[0][0] and password == temp[0][1]:
        logged_in = True
        print("\nYou have successfully logged in.")

    else:
        print("\nThe details you entered are incorrect. Please try again.\n")


while logged_in is True and action_selected is False:
    action = input("\nWhat would you like to do?\n"
                   "Enter VIEW to view your transactions from any given month.\n"
                   "Enter T.NEW to log a new transaction for today.\n"
                   "Enter C.NEW to log a new transaction for a custom date.\n"
                   "Enter LOGOUT to log out of your account. \t")

    if action == "T.NEW":
        action_selected = True
        amount = float(input("\nEnter the amount of this transaction in CAD. \t"))
        category = str(input("Enter the category of this transaction.\n"
                             "Type RU for Rent/Utilities.\n"
                             "Type GE for Groceries/Essentials.\n"
                             "Type EDS for Entertainment, Dining & Shopping.\n"
                             "Type O for Others. \t"))
        transaction_date = str(date.today())
        cursor.execute("INSERT INTO transactions (username, amount, category, transaction_date) "
                       "VALUES (?, ?, ?, ?)", (username, amount, category, transaction_date))
        connection.commit()
        print("\nYour transaction has been successfully logged.")
        action_selected = False

    elif action == "C.NEW":
        action_selected = True
        amount = float(input("\nEnter the amount of this transaction in CAD. \t"))
        category = input("Enter the category of this transaction.\n"
                         "Type RU for Rent/Utilities.\n"
                         "Type GE for Groceries/Essentials.\n"
                         "Type EDS for Entertainment, Dining & Shopping.\n"
                         "Type O for Others. \t")

        transaction_date = input("Enter the date of this transaction in the format YYYY-MM-DD. \t")
        cursor.execute("INSERT INTO transactions (username, amount, category, transaction_date) "
                       "VALUES (?, ?, ?, ?)", (username, amount, category, transaction_date))
        connection.commit()
        print("\nYour transaction has been successfully logged.")
        action_selected = False

    elif action == "VIEW":
        action_selected = True
        month = input("\nEnter the month you would like to view transactions from, in the format YYYY-MM. \t")
        export_decision = input("Would you like to export the data for this month in csv format? Enter Y or N. \t")
        cursor.execute("SELECT transaction_date, amount, category FROM transactions "
                       "WHERE username = ? AND transaction_date LIKE ?", (username, month+"%"))
        temp = cursor.fetchall()

        if len(temp) < 1:
            print(f"\nYou have no transactions logged for {month}.")
        else:
            if export_decision == "Y":
                export_file_name = str(f'{username}' + '_' + f'{month}' + '.csv')
                with open(export_file_name, 'w') as f:
                    writer = csv.writer(f)
                    writer.writerow(['transaction_date', 'amount', 'category'])
                    writer.writerows(temp)
                    print(f"\nYour data for {month} will be exported as {export_file_name} once the app closes.")
                    f.close()

            print(f"\nHere are your transactions for {month}:\n")
            for i in temp:
                transaction_date = i[0]
                amount = i[1]
                category = i[2]
                print(f"On {transaction_date}, you spent {amount} CAD on a {category} transaction.")
            cursor.execute("SELECT COUNT(*), SUM(amount) FROM transactions "
                           "WHERE username = ? AND transaction_date LIKE ?", (username, month + "%"))
            temp = cursor.fetchall()
            total_amount = temp[0][1]
            total_transactions = temp[0][0]
            print(f"\nYou spent a total of {total_amount} CAD over {total_transactions} transactions during {month}.")
        action_selected = False

    elif action == "LOGOUT":
        print("\nYou have been successfully logged out. "
              "Thank you for using the EmmZaa Budget Tracker. Have a nice day!")
        logged_in = False

    else:
        print("\nYou entered an incorrect action. Please try again.")
