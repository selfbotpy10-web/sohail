from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# توکن ربات خودت را اینجا بگذار
TOKEN = "8705315410:AAHFhgOJwRd9WhxIdAgn-Eh3zsIKu372S5k"

async def reply_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if text == "سلام":
        await update.message.reply_text("علیک سلام")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            reply_message
        )
    )

    print("Bot Started...")
    app.run_polling()

if __name__ == "__main__":
    main()
