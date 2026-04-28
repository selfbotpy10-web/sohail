from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import os

# ====================================
# توکن ربات اصلی
# ====================================
MAIN_BOT_TOKEN = "8705315410:AAHFhgOJwRd9WhxIdAgn-Eh3zsIKu372S5k"

# ====================================
# فقط یک دکمه
# ====================================
bot_keyboard = ReplyKeyboardMarkup(
    [["🤖 ساخت ربات"]],
    resize_keyboard=True
)

users = {}

# ====================================
# /start
# ====================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 ربات آماده است\n\nروی دکمه زیر بزن:",
        reply_markup=bot_keyboard
    )

# ====================================
# مدیریت پیام‌ها
# ====================================
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # دکمه ساخت ربات
    if text == "🤖 ساخت ربات":
        users[user_id] = {"step": "waiting_token"}

        await update.message.reply_text(
            "🔑 توکن ربات جدید را ارسال کن:"
        )
        return

    # دریافت توکن
    if user_id in users and users[user_id].get("step") == "waiting_token":
        child_token = text.strip()

        if ":" not in child_token:
            await update.message.reply_text(
                "❌ توکن اشتباه است"
            )
            return

        users[user_id]["step"] = "done"

        await update.message.reply_text(
            "✅ توکن دریافت شد\n\n"
            "ربات آماده است."
        )
        return

# ====================================
# اجرای اصلی
# ====================================
def main():
    print("🚀 Bot Running...")

    app = ApplicationBuilder().token(MAIN_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handler
        )
    )

    app.run_polling()

# ====================================
# اجرای امن برای Render
# ====================================
if __name__ == "__main__":
    main()
