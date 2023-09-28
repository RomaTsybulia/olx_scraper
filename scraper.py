import asyncio
import json
import os
import requests
import telebot
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv(".env")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(token=TELEGRAM_BOT_TOKEN)


class JsonFile():
    def __init__(self):
        self.data = {}


json_data = JsonFile()


def send_message_about_adevertisements():
    message = f"Знайдено нові оголошення {json_data.data['url']}"
    bot.send_message(chat_id=json_data.data["chat_id"], text=message)


async def get_all_advertisements(search_name: str):
    with open(f"{search_name}.json", "r") as json_file:
        data = json.load(json_file)
        chat_id = data["chat_id"]
        url = data["url"]
        previous_advertisement = data["previous_advertisement"]

    page = requests.get(url)

    soup = BeautifulSoup(page.content, "html.parser")
    advertisements = soup.find_all('div', {'class': 'css-1sw7q4x'})

    new_advertisement_list = []

    for advertisement in advertisements:
        advertisement.find('div', {'class': 'css-1jh69qu'})
        link_element = advertisement.find('a', class_='css-rc5s2u')

        if link_element and not advertisement.find('div',
                                                   {'class': 'css-1jh69qu'}):
            link = "https://www.olx.ua/" + link_element['href']
            new_advertisement_list.append(link)

    if previous_advertisement != new_advertisement_list[0]:
        send_message_about_adevertisements()

    with open("variables.json", "w") as json_file:
        data["previous_advertisement"] = new_advertisement_list[0]
        json.dump(data, json_file, indent=4)


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
    json_data.data["url"] = message.text
    bot.send_message(message.chat.id, "Будь ласка, введіть ім'я для пошуку:")
    bot.register_next_step_handler(message, get_search_name)


def get_search_name(message) -> None:
    user_id = message.from_user.id
    json_data.data["search_name"] = message.text
    json_data.data["chat_id"] = user_id

    file_name = f"{user_id}_{message.text}.json"

    with open(file_name, "w") as json_file:
        json.dump(json_data.data, json_file, indent=4)

    bot.send_message(message.chat.id, "Параметри пошуку збережено!")


@bot.message_handler(commands=["remove"])
def remove(message) -> None:
    user_id = message.from_user.id
    file_list = os.listdir(os.getcwd())

    json_files = [
        file.replace(str(user_id) + "_", "").replace(".json", "")
        for file in file_list
        if file.endswith(".json") and str(user_id) in file
    ]

    if len(json_files) == 0:
        bot.send_message(message.chat.id, "Параметрів пошуку немає")
        return
    message_text = "Оберіть параметр пошуку для видалення, використовуючи їх номери:\n"
    for i, search_name in enumerate(json_files):
        message_text += f"{i + 1}. {search_name}\n"

    bot.send_message(message.chat.id, message_text)
    bot.register_next_step_handler(message, confirm_removal)


def confirm_removal(message) -> None:
    user_id = message.from_user.id
    file_list = os.listdir(os.getcwd())
    json_files = [
        file
        for file in file_list
        if file.endswith(".json") and str(user_id) in file
    ]
    for i, search_name in enumerate(json_files):
        if str(i + 1) == message.text:
            os.remove(search_name)
            bot.send_message(message.chat.id, "Параметр пошуку був успішно видалений!")
            return


def main():
    bot.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
