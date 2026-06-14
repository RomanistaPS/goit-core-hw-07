from collections import UserDict
from datetime import datetime, date, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

        super().__init__(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return
        raise ValueError("Phone not found.")

    def edit_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise ValueError("Old phone not found.")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = ", ".join(p.value for p in self.phones)

        if self.birthday:
            return f"{self.name.value}: {phones}, birthday: {self.birthday.value}"

        return f"{self.name.value}: {phones}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value.lower()] = record

    def find(self, name):
        return self.data.get(name.lower())

    def delete(self, name):
        if name.lower() in self.data:
            del self.data[name.lower()]

    def get_upcoming_birthdays(self):
        upcoming_birthday = []
        today = datetime.now().date()

        for record in self.data.values():
            if record.birthday is not None:
                birthday = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                birthday_this_year = birthday.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                delta = (birthday_this_year - today).days

                if 0 <= delta <= 7:
                    congratulation_date = birthday_this_year

                    if congratulation_date.weekday() == 5:
                        congratulation_date += timedelta(days=2)
                    elif congratulation_date.weekday() == 6:
                        congratulation_date += timedelta(days=1)

                    upcoming_birthday.append({
                        "name": record.name.value,
                        "birthday": congratulation_date.strftime("%d.%m.%Y")
                    })

        return upcoming_birthday

    def __str__(self):
        return '\n'.join(str(record) for record in self.data.values())

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Enter username please."
    return inner

def parse_input(user_input):
    parts = user_input.split()
    if not parts:
        return "", []

    cmd = parts[0].strip().lower()
    args = parts[1:]
    return cmd, args

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)

    if record is None:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return "Contact added."
    else:
        record.add_phone(phone)
        return "Phone added."

@input_error
def change_contact(args, book):
    name, phone = args
    record = book.find(name)

    if record is None:
        raise KeyError("Contact not found.")

    old_phone = record.phones[0].value
    record.edit_phone(old_phone, phone)
    return "Contact updated."

@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if record is not None:
        return ', '.join(p.value for p in record.phones)
    raise KeyError("Contact not found.")


@input_error
def show_all(args, book):
    if not book:
        return "No contacts saved."
    else:
        return str(book)

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args

    record = book.find(name)

    if record is None:
        raise KeyError("Contact not found.")

    record.add_birthday(birthday)

    return "Birthday added."

@input_error
def show_birthday(args, book):
    name = args[0]

    record = book.find(name)

    if record is None:
        raise KeyError("Contact not found.")

    if record.birthday is None:
        return "Birthday not set."

    return record.birthday.value

@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()

    if not upcoming:
        return "No birthdays in the next 7 days."

    result = []

    for user in upcoming:
        result.append(
            f"{user['name']} -> "
            f"{user['birthday']}"
        )

    return "\n".join(result)



def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(args, book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()