from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "8705315410:AAHFhgOJwRd9WhxIdAgn-Eh3zsIKu372S5k"

# =========================
# /start
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام 👋\nهر چی بگی، اگر سلام باشه جواب میدم")

# =========================
# پیام‌ها
# =========================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if "سلام" in text:
        await update.message.reply_text("علیک سلام 🤝")
    else:
        await update.message.reply_text("فقط وقتی سلام بگی جواب میدم 🙂")

# =========================
# اجرا (مهم‌ترین بخش)
# =========================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
