import asyncio
import json
import os

import telebot
from dotenv import load_dotenv

from helper import get_data_from_parameters_file

load_dotenv(".env")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(token=TELEGRAM_BOT_TOKEN)


class JsonFile():
    def __init__(self):
        self.data = []
        self.url = ""


json_data = JsonFile()


@bot.message_handler(commands=["start"])
def start(message) -> None:
    bot.send_message(message.chat.id, "Привіт!\n"
                                      "Я телеграм бот, для пошуку нових оголошень на сайті OLX!\n"
                                      "Я працюю з такими командами:\n"
                                      "- /help - перегляд команд\n"
                                      "- /add - збереження параметрів пошуку\n"
                                      "- /remove - видалення параметрів пошуку\n")


@bot.message_handler(commands=["add"])
def add(message) -> None:
    bot.send_message(message.chat.id, "Будь ласка, введіть URL для пошуку:")
    bot.register_next_step_handler(message, get_url)


def get_url(message) -> None:
    json_data.url = message.text
    bot.send_message(message.chat.id, "Будь ласка, введіть ім'я для пошуку:")
    bot.register_next_step_handler(message, get_search_name)


def get_search_name(message) -> None:
    chat_id = message.chat.id
    parameter_dict = {f"{message.text}": {"url": json_data.url, "datetime": ""}}

    try:
        with open(f"{chat_id}.json", "r") as json_file:
            data = json.load(json_file)
            print(data)

        data.append(parameter_dict)

        print(data)
        with open(f"{chat_id}.json", "w") as json_file:
            json.dump(data, json_file, indent=4)
    except FileNotFoundError:
        new_file = [parameter_dict]
        with open(f"{chat_id}.json", "w") as json_file:
            json.dump(new_file, json_file, indent=4)

    bot.send_message(message.chat.id, "Параметри пошуку збережено!")


@bot.message_handler(commands=["remove"])
def remove(message) -> None:
    chat_id = message.from_user.id

    try:
        data = get_data_from_parameters_file(chat_id)
        message_text = "Оберіть параметр пошуку для видалення, використовуючи їх номери:\n"

        for i, search in enumerate(data):
            search_name = list(search.keys())[0]
            message_text += f"{i + 1}. {search_name}\n"

        bot.send_message(message.chat.id, message_text)
        bot.register_next_step_handler(message, confirm_removal)

    except FileNotFoundError:
        bot.send_message(
            chat_id,
            "Ви ще не створили жодного параметру для пошуку.\n"
            "Введіть /add, щоб додати."
        )
        return


def confirm_removal(message) -> None:
    chat_id = message.from_user.id
    data = get_data_from_parameters_file(chat_id)

    del data[int(message.text) - 1]
    bot.send_message(message.chat.id, "Параметр пошуку був успішно видалений!")

    if len(data) == 0:
        os.remove(f"{chat_id}.json")
    else:
        with open(f"{chat_id}.json", "w") as json_file:
            json.dump(data, json_file, indent=4)


def main():
    bot.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
