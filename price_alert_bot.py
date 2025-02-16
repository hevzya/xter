import requests
import asyncio
from telegram import Bot
from telegram.error import TelegramError

# Замініть на ваш Telegram Bot Token та Chat ID
TELEGRAM_BOT_TOKEN = 'bot_token'
CHAT_ID = '@'

# Bitget API URL для ф'ючерсів
BITGET_API_URL = 'https://api.bitget.com/api/v2/mix/market/symbol-price'
# Параметри для запиту
BITGET_PARAMS = {
    'productType': 'usdt-futures',  # Тип продукту (ф'ючерси)
    'symbol': 'XTERUSDT'            # Символ пари
}

# MEXC API URL (залишаємо без змін)
MEXC_API_URL = 'https://api.mexc.com/api/v3/ticker/price?symbol=XTERUSDT'

# Ініціалізація Telegram бота
bot = Bot(token=TELEGRAM_BOT_TOKEN)

def get_bitget_price():
    try:
        response = requests.get(BITGET_API_URL, params=BITGET_PARAMS)
        response.raise_for_status()  # Перевірка на помилки HTTP
        data = response.json()

        # Перевірка структури відповіді
        if 'data' in data and len(data['data']) > 0 and 'price' in data['data'][0]:
            return float(data['data'][0]['price'])
        else:
            print("Неправильна структура відповіді Bitget API:", data)
            return None
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP помилка: {http_err}")
    except Exception as err:
        print(f"Інша помилка: {err}")
    return None

def get_mexc_price():
    try:
        response = requests.get(MEXC_API_URL)
        response.raise_for_status()  # Перевірка на помилки HTTP
        data = response.json()

        # Перевірка структури відповіді
        if 'price' in data:
            return float(data['price'])
        else:
            print("Неправильна структура відповіді MEXC API:", data)
            return None
    except Exception as e:
        print(f"Помилка отримання ціни MEXC: {e}")
        return None

async def send_notification(message):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
    except TelegramError as e:
        print(f"Помилка відправки повідомлення: {e}")

async def monitor_prices():
    while True:
        bitget_price = get_bitget_price()
        mexc_price = get_mexc_price()

        if bitget_price is None or mexc_price is None:
            print("Не вдалося отримати ціни. Повторна спроба через 60 секунд...")
            await asyncio.sleep(60)
            continue

        print(f"Ціна на Bitget: {bitget_price}, Ціна на MEXC: {mexc_price}")

        #if bitget_price - mexc_price >= 0.0001:
         #   difference = bitget_price - mexc_price
          #  await send_notification(f"Ціна на Bitget вища на {difference:.4f}\nBitget: {bitget_price}, MEXC: {mexc_price}")


        if mexc_price - bitget_price >= 0.0001:
            difference = mexc_price - bitget_price
            await send_notification(f"Ціна на MEXC вища на {difference:.4f}\nBitget: {bitget_price}, MEXC: {mexc_price}")

        # Чекаємо 60 секунд перед наступною перевіркою
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(monitor_prices())
