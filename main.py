from telegram.ext import Application, MessageHandler, filters, CommandHandler
from bot.handlers import handle_message, handle_start, handle_help, handle_memory, handle_clear
from scheduler.jobs import scheduler
import config

application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

async def post_init(application):
    scheduler.start()
    print("Scheduler started!")

async def error_handler(update,context):
    print(f"Error: {context.error}")

def main():
    # app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", handle_start))
    application.add_handler(CommandHandler("help", handle_help))
    application.add_handler(CommandHandler("memory", handle_memory))
    application.add_handler(CommandHandler("clear", handle_clear))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    application.post_init = post_init

    print("Krish is running ...")
    application.run_polling()

if __name__ == "__main__":
    main()