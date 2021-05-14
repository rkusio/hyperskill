"""Banking apps"""
import random
import sqlite3
import sys
import luhn

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS card"
            " (id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0)")


class Card:
    """Card object"""
    number = None
    pin = None
    balance = 0

    def __init__(self):
        pass

    def gen_card(self):
        """Generate new card number"""
        self.number = self.gen_card_num()
        self.pin = str(format(random.randint(0000, 9999), "04d"))

        cur.execute("insert into card(id, number, pin, balance) \
            values (1, " + self.number + ", " + str(self.pin) + ", " + str(self.balance) + ')')
        conn.commit()

    @staticmethod
    def gen_card_num():
        """Generate card number"""
        card_number = ("400000" + str(format(random.randint(000000000, 999999999), "09d")))

        card_number = luhn.append(card_number)
        return card_number

    def get_card_number(self):
        """Return card number"""
        return self.number

    def get_pin(self):
        """Return pin"""
        return self.pin


def card_create():
    """Method to create card"""
    new_card = Card()
    new_card.gen_card()
    print("\nYour card has been created\n"
          "Your card number:\n"
          f"{new_card.number}\n"
          "Your card PIN:\n"
          f"{new_card.pin}\n")
    return new_card


def account_enter(user):
    """Method to login user"""
    card_number = input("\nEnter your card number:\n")
    pin = input("Enter your PIN:\n")

    user.number = card_number
    cur.execute("SELECT cast(pin as text) FROM card WHERE number=?", (card_number,))

    try:
        user.pin = cur.fetchone()[0]
    except TypeError:
        return print("\nWrong card number or PIN!\n")

    if str(user.pin) != str(pin):
        return print("\nWrong card number or PIN!\n")
    account_menu(user)

    return 0


def get_balance(user):
    """Get balance"""
    cur.execute("SELECT balance FROM card WHERE number=?", (user.number,))
    user.balance = cur.fetchone()[0]
    print(user.balance)
    return user.balance


def add_balance(user, value):
    """Add balance"""
    cur.execute("update card set balance = balance + ? where number = ?", (value, user.number))
    conn.commit()

    print("Income was added!")


def make_transfer(user):
    """Make transfer"""
    print("Transfer")
    print("Enter card number:")
    transfer_to = input()

    if not luhn.verify(transfer_to):
        return print("Probably you made a mistake in the card number. Please try again!")

    if user.number == transfer_to:
        print("You can't transfer money to the same account!")

    cur.execute("SELECT 1 FROM card WHERE number=?", (transfer_to,))

    try:
        transfer_to_exist = cur.fetchone()[0]
    except TypeError:
        return print("\nSuch a card does not exist.\n")

    if transfer_to_exist == 1:
        print("Enter how much money you want to transfer:")
        transfer_amunt = int(input())

        if int(transfer_amunt) > int(get_balance(user)):
            return print("Not enough money!")

        cur.execute("update card set balance = balance - ? where number = ?",
                    (transfer_amunt, user.number))
        cur.execute("update card set balance = balance + ? where number = ?",
                    (transfer_amunt, transfer_to))
        conn.commit()

        print("Success!")
    return 0


def account_menu(user):
    """Account menu"""
    print("\nYou have successfully logged in!\n")
    while True:
        user_input = input("1. Balance\n"
                           "2. Add income\n"
                           "3. Do transfer\n"
                           "4. Close account\n"
                           "5. Log out\n"
                           "0. Exit\n")
        if user_input == "0":
            bye()
        if user_input == "1":
            get_balance(user)
            print(f"\nBalance: {user.balance}\n")
        if user_input == "2":
            print("Enter income:")
            income = int(input())
            add_balance(user, income)
        if user_input == "3":
            make_transfer(user)
        if user_input == "4":
            close_account(user)

        if user_input == "5":
            return print("\nYou have successfully logged out!\n")


def close_account(user):
    """Close account"""
    cur.execute("delete from card where number = ?", (user.number,))
    conn.commit()

    print("The account has been closed!")


def bye():
    """Exit"""
    print("\nBye!")
    sys.exit()


USER_CARD = None
while True:
    main_input = input("1. Create an account\n2. Log into account\n0. Exit\n")
    if main_input == "0":
        bye()
    if main_input == "1":
        USER_CARD = card_create()
    if main_input == "2":
        account_enter(USER_CARD)
