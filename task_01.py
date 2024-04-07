from abc import ABC, abstractmethod
from collections import UserDict
import datetime
import pickle
import re


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        if len(value) != 0:
            super().__init__(value)
        else:
            raise ValueError("Name cannot be empty.")


class Phone(Field):
    def __init__(self, value):
        pattern = r'^\d{10}$'
        if not re.match(pattern, value):
            return "Invalid phone number format. The phone number must contain 10 digits"
        super().__init__(value)

    def __str__(self):
        return super().__str__()


class Birthday(Field):
    def __init__(self, value: str) -> None:
        try:
            b_date = datetime.datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(b_date)
        except:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    def __init__(self, name: str):
        self.name = Name(name)
        self.birthday = None
        self.phones = []

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def add_birthday(self, b_day):
        b_day = Birthday(b_day)
        if b_day:
            self.birthday = b_day

    def remove_phone(self, phone_number):
        phone_obj = Phone(phone_number)
        for obj in self.phones:
            if obj.value == phone_obj.value:
                self.phones.remove(obj)

    def edit_phone(self, old_number, new_number):
        self.find_phone(old_number)
        self.remove_phone(old_number)
        self.add_phone(new_number)

    def find_phone(self, phone_number):
        ph = Phone(phone_number)
        if ph in self.phones:
            return ph
        else:
            raise ValueError

    def __str__(self) -> str:
        all_phones_str = []
        for tel in self.phones:
            all_phones_str.append(str(tel))
        return f" Phones:{str(all_phones_str)} Birthday: {self.birthday}"


class AddressBook(UserDict):

    def add_record(self, record_item: Record):
        self.data[record_item.name.value] = record_item

    def find(self, key):
        return self[key]

    def delete(self, key):
        del self[key]

    def get_birthdays(self, for_the_period: 7):
        congrats_list = []
        bd_dict = {k: v.birthday.value for k,
                   v in self.items() if v.birthday is not None}
        curr_date = datetime.datetime.today().date()
        end_date = curr_date + datetime.timedelta(for_the_period)
        for k, v in bd_dict.items():
            bd_date = v
            bd_date_this_year = datetime.date(
                curr_date.year, bd_date.month, bd_date.day)
            if bd_date_this_year.weekday() == 6:
                bd_date_this_year = bd_date_this_year + datetime.timedelta(1)
            if bd_date_this_year.weekday() == 5:
                bd_date_this_year = bd_date_this_year + datetime.timedelta(2)

            if (bd_date_this_year <= end_date) and (bd_date_this_year >= curr_date):
                dct = {
                    "Name": k, "Congratulation_date": bd_date_this_year.strftime("%Y.%m.%d")}
                congrats_list.append(dct)
        return congrats_list

    def __str__(self) -> str:
        dict = {}
        result_str = ""
        for k, v in self.items():
            dict[k] = str(v)
            result_str = "\n".join([f"{k}:{v}" for k, v in dict.items()])
        return str(result_str)


list_of_commands = "Commands:\n"\
    "add [name] [phone] - Create a new contact\n"\
    "change [name] [new_phone] - Change phone number\n"\
    "phone [name] - Show phone number\n"\
    "all - Show all contacts\n"\
    "add-birthday [name] [birthday] - Create birthday\n"\
    "show-birthday [name] - Show birthday\n"\
    "birthdays - Show upcoming birthdays"


class BotInterface(ABC):

    @abstractmethod
    def message_welcome(self, address_book: AddressBook):
        pass

    @abstractmethod
    def show_commands(self, commands):
        pass

    @abstractmethod
    def show_contacts(self, contact):
        pass

    @abstractmethod
    def show_congratuation(self, congrats_list):
        pass


class UserInterface(BotInterface):
    def message_welcome(self, address_book: AddressBook):
        print("Welcome to the assistant bot!\n",
              "Type 'help' for a list of available commands")

    def show_commands(self, commands):
        print('Commands: ')
        for i in commands:
            print(i)

    def show_contacts(self, contact):
        if isinstance(contact, Record):
            print('Contacts: ')
            print(f"{contact.name}: {contact}")
        else:
            print('Contacts: ')
            for i in contact:
                print(f" {i[0]}: {i[1]}")

    def show_congratuation(self, congrats_list):
        if len(congrats_list) != 0:
            print(f"Congratulations! Birthday: {congrats_list}")
        else:
            print("There are no congratulations")

    def show_birthday(self, record: Record):
        print(
            f"Birthday of {record.name}: {record.birthday.strftime('%Y.%m.%d')}")


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "+rb") as f:
            restored_bk = pickle.load(f)
            return restored_bk
    except (FileNotFoundError, EOFError, pickle.UnpicklingError):
        return AddressBook()


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except IndexError:
            return "Command not Found."
        except KeyError:
            return "Name not Found."
        except NameError:
            return "Name not Found."
        except Exception as e:
            return f"Error: {e}"

    return inner


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error
def add_contact(*args):
    if args[0] in book:
        record = book.find(args[0])
        record.add_phone(args[1])
    else:
        record = Record(args[0])
        record.add_phone(args[1])
        book.add_record(record)
    return record


@input_error
def change_contact(command, *args):
    record = book.find(args[0])
    record.edit_phone(args[1], args[2])
    return record


@input_error
def show_phone(*args):
    record = book.find(args[0])
    return record


@input_error
def show_all():
    return book


@input_error
def show_birthday(*args):
    record = book.find(args[0])
    return record


@input_error
def add_birthday(*args):
    record = book.find(args[0])
    record.add_birthday(args[1])
    return record


book = load_data()


def main():
    user = UserInterface()
    user.message_welcome(book)
    while True:
        user_input = input("Enter a command: ").strip().lower()
        command, *args = parse_input(user_input)
        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            new_contact = add_contact(*args)
            user.show_contacts(new_contact)
        elif command == 'change':
            changed_contact = change_contact(command, *args)
            user.show_contacts(new_contact)
        elif command == "phone":
            phones = show_phone(*args)
            user.show_contacts(new_contact)
        elif command == "all":
            all_records = [i for i in book.items()]
            user.show_contacts(new_contact)
        elif command == "add-birthday":
            contact = add_birthday(*args)
            user.show_contacts(new_contact)
        elif command == "show-birthday":
            b_day = show_birthday(*args)
            user.show_birthday(b_day)
        elif command == "birthdays":
            congrats_list = book.get_birthdays(7)
            user.show_congratuation(congrats_list)
        elif command == "help":
            user.show_commands(list_of_commands)
        else:
            print("Invalid command")


if __name__ == '__main__':
    main()
