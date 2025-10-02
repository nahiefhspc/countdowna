from flask import Flask, jsonify
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
import datetime
import asyncio
import threading
import re

# Define exam dates
EXAMS = {
    "☠️ 𝗝𝗘𝗘 𝗠𝗔𝗜𝗡𝗦 𝟮𝟬𝟮𝟲 𝗝𝗔𝗡 𝗔𝗧𝗧𝗘𝗠𝗣𝗧": datetime.date(2026, 1, 20),
    "😭 𝗝𝗘𝗘 𝗔𝗗𝗩𝗔𝗡𝗖𝗘 𝟮𝟬𝟮𝟲": datetime.date(2026, 5, 18),
    "🙂 𝗝𝗘𝗘 𝗠𝗔𝗜𝗡𝗦 𝟮𝟬𝟮𝟲 𝗔𝗣𝗥𝗜𝗟 𝗔𝗧𝗧𝗘𝗠𝗣𝗧": datetime.date(2026, 4, 1),
    "😒 𝗕𝗜𝗧𝗦𝗔𝗧 𝟮𝟬𝟮𝟲": datetime.date(2026, 5, 26),
    "😑 𝗝𝗘𝗘 𝗠𝗔𝗜𝗡𝗦 𝟮𝟬𝟮𝟳 𝗝𝗔𝗡 𝗔𝗧𝗧𝗘𝗠𝗣𝗧": datetime.date(2027, 1, 20),
    " 😶 𝗝𝗘𝗘 𝗔𝗗𝗩𝗔𝗡𝗖𝗘 𝟮𝟬𝟮𝟳": datetime.date(2027, 1, 20),
    "😗 𝗡𝗘𝗘𝗧 𝟮𝟬𝟮𝟲": datetime.date(2026, 5, 4),
    "👻 𝗖𝗢𝗠𝗘𝗗𝗞 𝟮𝟬𝟮𝟲": datetime.date(2026, 5, 14),
    "💥 𝗩𝗜𝗧𝗘𝗘𝗘 𝟮𝟬𝟮𝟲": datetime.date(2026, 4, 20),    
    "😔 𝗖𝗨𝗘𝗧 𝟮𝟬𝟮𝟲": datetime.date(2026, 5, 15),
}

CHANNEL_ID = "-1002819874763"  # Replace with your actual channel username
app = Flask(__name__)
last_message_id = None  # Store the last message ID for deletion

# Flask health check endpoint for Docker
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK"}), 200

def time_left(exam_date):
    now = datetime.datetime.now()
    exam_datetime = datetime.datetime.combine(exam_date, datetime.time(0, 0))
    delta = exam_datetime - now
    total_seconds = int(delta.total_seconds())
    days = total_seconds // (24 * 3600)
    total_hours = (total_seconds // 3600)  # Total hours including days
    total_seconds_full = total_seconds  # Total seconds including days and hours
    return days, total_hours, total_seconds_full

def get_exam_countdown():
    countdown_text = "<b>Exam Countdown By OPMASTER ☠️</b>\n\n"
    for exam, date in sorted(EXAMS.items()):
        days, total_hours, total_seconds = time_left(date)
        if days >= 0:
            # Use the provided link format, ignore custom link if provided in exam name
            exam_name = exam.split("|")[0] if "|" in exam else exam
            exam_display = f'<b><a href="https://t.me/hidden_officials_5/3">{exam_name}</a></b>'
            countdown_text += f"{exam_display}\n<b>🔹𝐃𝐚𝐲𝐬 𝐋𝐞𝐟𝐭: {days}</b>\n<b>🔹𝐇𝐨𝐮𝐫𝐬 𝐋𝐞𝐟𝐭: {total_hours}</b>\n<b>🔹𝐒𝐞𝐜𝐨𝐧𝐝𝐬 𝐋𝐞𝐟𝐭: {total_seconds}</b>\n\n"
    return countdown_text

async def send_countdown(context: ContextTypes.DEFAULT_TYPE):
    global last_message_id
    bot = context.bot
    
    # Delete previous message if it exists
    if last_message_id:
        try:
            await bot.delete_message(chat_id=CHANNEL_ID, message_id=last_message_id)
        except:
            pass  # Ignore if message can't be deleted
    
    # Send new message and store its ID
    message = await bot.send_message(chat_id=CHANNEL_ID, text=get_exam_countdown(), parse_mode="HTML", disable_web_page_preview=True)
    last_message_id = message.message_id

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text=get_exam_countdown(), parse_mode="HTML", disable_web_page_preview=True)
    await send_countdown(context)

async def add_exam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /add <exam_name> <YYYY-MM-DD> [link]\nExample: /add JEE MAIN|https://jeemain.nta.ac.in 2025-04-01")
        return
    
    try:
        # Extract exam name and date
        args = " ".join(context.args).split()
        date_str = args[-1]
        exam_name = " ".join(args[:-1])
        
        # Validate date format
        exam_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        if exam_date < datetime.date.today():
            await update.message.reply_text("Cannot add past dates!")
            return
            
        # Add exam to dictionary
        EXAMS[exam_name] = exam_date
        await update.message.reply_text(f"Added {exam_name} on {date_str} ✅")
        
        # Send updated countdown
        await send_countdown(context)
        
    except ValueError:
        await update.message.reply_text("Invalid date format! Use YYYY-MM-DD")

async def remove_exam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /remove <exam_name>")
        return
    
    exam_name = " ".join(context.args)
    if exam_name in EXAMS:
        del EXAMS[exam_name]
        await update.message.reply_text(f"Removed {exam_name} 🗑️")
        await send_countdown(context)
    else:
        await update.message.reply_text(f"Exam {exam_name} not found! 😕")

async def daily_update(context: ContextTypes.DEFAULT_TYPE):
    while True:
        await send_countdown(context)
        now = datetime.datetime.now()
        tomorrow = datetime.datetime.combine(now.date() + datetime.timedelta(days=1), datetime.time(0, 0))
        sleep_time = (tomorrow - now).total_seconds()
        await asyncio.sleep(sleep_time)  # Sleep until midnight

def run_flask():
    app.run(host="0.0.0.0", port=8080, use_reloader=False)

async def run_bot():
    TOKEN = "7213717609:AAG4gF6dRvqxPcg-WaovRW2Eu1d5jxT566o"
    application = Application.builder().token(TOKEN).build()

    # Ensure that job_queue is initialized before use
    if application.job_queue is None:
        raise Exception("JobQueue not initialized properly.")

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_exam))
    application.add_handler(CommandHandler("remove", remove_exam))

    # Run the daily update job every 24 hours, starting from 5 seconds after the bot starts
    application.job_queue.run_once(daily_update, when=datetime.timedelta(seconds=5))

    # Send immediate countdown message when the bot starts
    application.job_queue.run_once(lambda context: send_countdown(context), when=datetime.timedelta(seconds=5))

    # Start the Telegram bot
    try:
        await application.initialize()
        await application.start()
        await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        # Keep the bot running until interrupted
        await asyncio.Event().wait()
    finally:
        # Properly shut down the application
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

def main():
    # Create a new event loop for the bot
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Run Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Run the Telegram bot in the main thread
    try:
        loop.run_until_complete(run_bot())
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        # Ensure all tasks are cancelled and the loop is closed
        tasks = [task for task in asyncio.all_tasks(loop) if task is not asyncio.current_task(loop)]
        for task in tasks:
            task.cancel()
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

if __name__ == "__main__":
    main()
