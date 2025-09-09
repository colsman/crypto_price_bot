# Crypto Price Bot

Телеграм-бот для отслеживания цены криптовалют через CoinGecko API. 

## Функции

- Узнать текущую цену
- Отслеживать цену с заданным интервалом
- Получать уведомления в Telegram

## Установка

1. Склонировать репозиторий:

git clone https://github.com/colsman/crypto_price_bot.git

2. Установить зависимости:
pip install -r requirements.txt

3. Вставить свой API Token
app = ApplicationBuilder().token("YOUR_TOKEN").build()

4. Запустить бота
python crypto_price_bot

