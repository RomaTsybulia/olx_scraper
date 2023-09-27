import asyncio
import json
import requests
from bs4 import BeautifulSoup
from telegram import Bot

with open("variables.json", "r") as json_file:
    data = json.load(json_file)
    TELEGRAM_BOT_TOKEN = data["telegram_bot_token"]
    chat_id = data["chat_id"]
    url = data["url"]
    previous_advertisement_list = data["previous_advertisement_list"]

bot = Bot(token=TELEGRAM_BOT_TOKEN)


async def send_message_to_bot(chat_id, message):
    await bot.send_message(chat_id=chat_id, text=message)


async def get_all_advertisements():
    page = requests.get(url)

    soup = BeautifulSoup(page.content, "html.parser")
    advertisements = soup.find_all('div', {'class': 'css-1sw7q4x'})

    new_advertisement_list = []

    for advertisement in advertisements:
        advertisement.find('div', {'class': 'css-1jh69qu'})
        link_element = advertisement.find('a', class_='css-rc5s2u')

        if link_element and not advertisement.find('div', {'class': 'css-1jh69qu'}):
            link = "https://www.olx.ua/" + link_element['href']
            new_advertisement_list.append(link)
    new_advertisement_list = list(reversed(new_advertisement_list))

    for item in new_advertisement_list:
        if item not in previous_advertisement_list:
            message = f"Знайдено нові оголошення {url}"
            await send_message_to_bot(chat_id=chat_id, message=message)
            break

    with open("variables.json", "w") as json_file:
        data["previous_advertisement_list"] = new_advertisement_list
        json.dump(data, json_file)


async def main():
    await get_all_advertisements()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())