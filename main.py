import sys
import subprocess
import os

try:
    import telebot
    from bs4 import BeautifulSoup
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyTelegramBotAPI", "requests", "beautifulsoup4"])
    import telebot
    from bs4 import BeautifulSoup

import requests
import time

TOKEN = '8796939526:AAHd7EU4yQDGOmxlWW8jSQlj-lxBUQrabnw'
SCRAPER_API_KEY = 'a3601cb5e55392f1f78b0ae8095ad612'

bot = telebot.TeleBot(TOKEN)

# Ссылка на Киев от хозяев
OLX_URL = "https://www.olx.ua/ru/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/kiev/?search%5Bprivate_business%5D=private"
PORT = int(os.environ.get("PORT", 8080))
def get_latest_ads():
    try:
        payload = {'api_key': SCRAPER_API_KEY, 'url': OLX_URL}
        response = requests.get('http://api.scraperapi.com', params=payload, timeout=25)
        if response.status_code != 200:
            return []
        soup = BeautifulSoup(response.text, 'html.parser')
        ads_links = []
        cards = soup.find_all('a', href=True)
        for card in cards:
            link = card.get('href')
            if link and '/d/obyavlenie/' in link:
                if not link.startswith('http'):
                    link = 'https://www.olx.ua' + link
                if link not in ads_links:
                    ads_links.append(link)
                if len(ads_links) >= 5:
                    break
        return ads_links
    except Exception as e:
        print(f"Ошибка парсинга: {e}")
        return []

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! 🏠 Я бот для поиска квартир от хозяев.\n\nЖми /find для получения свежих объявлений.")

@bot.message_handler(commands=['find'])
def find_apartments(message):
    bot.send_message(message.chat.id, "⏳ Ищу последние объявления через защищенный канал...")
    ads = get_latest_ads()
    if ads:
        for ad in ads:
            bot.send_message(message.chat.id, ad)
            time.sleep(1)
    else:
        bot.send_message(message.chat.id, "❌ На OLX пока пусто по этому фильтру или обнови ссылку. Попробуй позже.")

if __name__ == '__main__':
    print("Бот успешно запущен на Render!")
    bot.polling(none_stop=True)
