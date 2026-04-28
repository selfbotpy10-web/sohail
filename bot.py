from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import yt_dlp
import asyncio
import threading
import os

# =========================
# توکن ربات مادر
# =========================
MAIN_BOT_TOKEN = "توکن_اینجا"

# =========================
# فقط یک دکمه
# =========================
bot_keyboard = ReplyKeyboardMarkup(
    [["🤖 ساخت ربات"]],
    resize_keyboard=True
)

users = {}
running_bots = {}

# =====================================================
# ربات فرزند (موزیک یاب)
# =====================================================

async def child_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 ربات موزیک یاب فعال شد\n\nنام آهنگ را ارسال کن:"
    )

async def child_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text

    await update.message.reply_text("🔎 در حال جستجو...")

    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "quiet": True,
        "default_search": "ytsearch1",
        "outtmpl": "%(title)s.%(ext)s",
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)

            if "entries" in info:
                info = info["entries"][0]

            title = info["title"]
            file_path = ydl.prepare_filename(info)

            await update.message.reply_audio(
                audio=open(file_path, "rb"),
                title=title,
                caption=f"🎧 {title}"
            )

            await update.message.reply_text("✅ ارسال شد")

            if os.path.exists(file_path):
                os.remove(file_path)

    except Exception as e:
        await update.message.reply_text(f"❌ خطا:\n{str(e)}")


def run_child_bot(token):
    async def start_bot():
        app = ApplicationBuilder().token(token).build()

        app.add_handler(CommandHandler("start", child_start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, child_music))

        await app.initialize()
        await app.start()
        await app.updater.start_polling()

        while True:
            await asyncio.sleep(999999)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_bot())


def start_child_bot(token):
    if token in running_bots:
        return

    t = threading.Thread(target=run_child_bot, args=(token,), daemon=True)
    t.start()

    running_bots[token] = True


# =====================================================
# ربات مادر
# =====================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 ربات آماده است\n\nروی دکمه زیر بزن:",
        reply_markup=bot_keyboard
    )


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if text == "🤖 ساخت ربات":
        users[user_id] = {"step": "waiting_token"}

        await update.message.reply_text("🔑 توکن ربات را ارسال کن:")
        return

    if user_id in users and users[user_id].get("step") == "waiting_token":
        try:
            start_child_bot(text)
            users[user_id]["step"] = "done"

            await update.message.reply_text(
                "✅ ربات فرزند فعال شد 🎵\n\n"
                "برو داخل ربات فرزند /start بزن"
            )

        except:
            await update.message.reply_text("❌ توکن اشتباه است")


# =====================================================
# اجرا
# =====================================================

app = ApplicationBuilder().token(MAIN_BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

print("🚀 Bot Running...")
app.run_polling()
