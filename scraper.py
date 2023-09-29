import json
import os
from datetime import datetime

import requests
import telebot
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from helper import get_list_json_files

load_dotenv(".env")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(token=TELEGRAM_BOT_TOKEN)


def format_date(date_str):
    month_mapping = {
        'січня': "01",
        'лютого': "02",
        'березня': "03",
        'квітня': "04",
        'травня': "05",
        'червня': "06",
        'липня': "07",
        'серпня': "08",
        'вересня': "09",
        'жовтня': "10",
        'листопада': "11",
        'грудня': "12"
    }

    if 'Сьогодні' in date_str:
        current_date = datetime.now()
        date_str = date_str.replace('Сьогодні',
                                    current_date.strftime('%d-%m-%y')).replace(
            "о ", "")
        return datetime.strptime(date_str, '%d-%m-%y %H:%M')

    date_str = date_str.replace(" ", "-").replace(" .р", "")
    date_part = date_str.split("-")
    day = date_part[0]
    month = month_mapping[date_part[1]]
    year = date_part[2].replace("20", "")
    hours = "00"
    minutes = "00"
    date_str = f"{day}-{month}-{year} {hours}:{minutes}"

    return datetime.strptime(date_str, '%d-%m-%y %H:%M')


def send_report_to_user(chat_id, url, search_name):
    bot.send_message(chat_id, f"За цим {search_name} пошуком нові оголошення!\n{url}" )


def scraping_all_url():
    json_files = get_list_json_files()

    for file in json_files:
        chat_id = file.replace(".json", "")
        with open(file, "r") as json_file:
            data = json.load(json_file)

        for i, search in enumerate(data):
            search_name = list(search.keys())[0]
            url = search[search_name]["url"]
            previous_date = search[search_name]["datetime"]

            newest_advertisement = get_new_advertisements(url)
            if previous_date == "" or newest_advertisement > datetime.strptime(
                    previous_date, '%Y-%m-%d %H:%M'):
                send_report_to_user(chat_id=chat_id, search_name=search_name, url=url)
                data[i][search_name]["datetime"] = str(newest_advertisement)[
                                                   :-3]

        with open(file, "w") as json_file:
            json.dump(data, json_file, indent=4)


def get_new_advertisements(url):
    page = requests.get(url)

    soup = BeautifulSoup(page.content, "html.parser")

    advertisement_text = soup.find_all('p', {'data-testid': 'location-date',
                                             'class': 'css-veheph er34gjf0'})
    list_advertisement_date = [
        text.text.split(" - ")[1].replace("р.", "")
        for text in advertisement_text
    ]

    datetime_list = [format_date(date_str) for date_str in
                     list_advertisement_date if
                     format_date(date_str)]
    return sorted(datetime_list)[-1]


if __name__ == "__main__":
    scraping_all_url()

