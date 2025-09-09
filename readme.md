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

3. Вставить свой API Token в: 
app = ApplicationBuilder().token("YOUR_TOKEN").build()

4. Запустить бота
python crypto_price_bot

# Работает только с самыми популярными, остальное добавляйте сами по надобности

- Находите нужную монету на CoinGecko и в адресной строке копируете https://www.coingecko.com/ru/Криптовалюты/toncoin ее название
- Далее пишите в файле tickers.py нужный вам тикер и вставляете название монетки по примерам которые там есть

