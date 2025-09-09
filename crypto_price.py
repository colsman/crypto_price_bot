import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from tickers import ticker_to_id

# Словарь для хранения активных задач отслеживания
tracking_jobs = {}  # user_id: job

# Функции работы с CoinGecko
def get_price(ticker):
    converted_ticker = ticker_to_id.get(ticker.upper())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={converted_ticker}&vs_currencies=usd&include_24hr_change=true"
    result = requests.get(url)
    data = result.json()
    return data, converted_ticker

def convert_json(data, converted_ticker):
    price = data[converted_ticker]["usd"]
    change = data[converted_ticker]["usd_24h_change"]
    return price, change

# Главное меню с кнопками под полем ввода
def main_keyboard():
    buttons = [
        [KeyboardButton("Узнать цену"), KeyboardButton("Включить отслеживание")]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выберите действие:", reply_markup=main_keyboard())

# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # Проверка режима
    mode = context.user_data.get("mode")

    if text == "Узнать цену":
        await update.message.reply_text("Введите тикер криптовалюты, например BTC:")
        context.user_data["mode"] = "get_price"
        
    elif text == "Включить отслеживание":
        await update.message.reply_text("Введите тикер для отслеживания:")
        context.user_data["mode"] = "track_ticker"
        
    elif text == "Отмена":
        # отключаем отслеживание
        if user_id in tracking_jobs:
            tracking_jobs[user_id].schedule_removal()
            del tracking_jobs[user_id]
            await update.message.reply_text("Отслеживание остановлено.")
        context.user_data["mode"] = None
        await update.message.reply_text("Выберите действие:", reply_markup=main_keyboard())
        
    elif mode == "get_price":
        data, converted_ticker = get_price(text)
        price, change = convert_json(data, converted_ticker)
        await update.message.reply_text(f"Цена: {price} USD\nИзменение 24ч: {change:.2f}%")
        context.user_data["mode"] = None

    elif mode == "track_ticker":
        context.user_data["ticker"] = text
        context.user_data["mode"] = "track_interval"
        await update.message.reply_text("Введите интервал обновления в минутах:")

    elif mode == "track_interval":
        try:
            interval = int(text)
        except ValueError:
            await update.message.reply_text("Нужно ввести число в минутах!")
            return
        
        ticker = context.user_data.get("ticker")
        
        # создаем задачу в JobQueue
        job = context.job_queue.run_repeating(track_price_callback, interval*60, first=0, data={"user_id": user_id, "ticker": ticker})
        tracking_jobs[user_id] = job
        
        # сразу присылаем текущую цену и сообщение
        data, converted_ticker = get_price(ticker)
        price, change = convert_json(data, converted_ticker)
        await update.message.reply_text(
            f"Оповещение запущено!\nТекущая цена {ticker}: {price} USD\nИзменение 24ч: {change:.2f}%",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Отмена")]], resize_keyboard=True)
        )
        
        context.user_data["mode"] = None

# Callback для JobQueue
async def track_price_callback(context: ContextTypes.DEFAULT_TYPE):
    user_id = context.job.data["user_id"]
    ticker = context.job.data["ticker"]
    
    data, converted_ticker = get_price(ticker)
    price, change = convert_json(data, converted_ticker)
    
    try:
        await context.bot.send_message(
            chat_id=user_id, 
            text=f"[Отслеживание] {ticker}:\nЦена: {price} USD\nИзменение 24ч: {change:.2f}%"
        )
    except Exception as e:
        print(f"Ошибка отправки пользователю {user_id}: {e}")

# main
def main():
    app = ApplicationBuilder().token("YOUR_TOKEN").build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
