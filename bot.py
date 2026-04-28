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

# =====================================
# توکن ربات مادر
# =====================================
# توکن واقعی ربات مادر را اینجا بگذار
MAIN_BOT_TOKEN = "8705315410:AAHFhgOJwRd9WhxIdAgn-Eh3zsIKu372S5k"

# =====================================
# دکمه ساخت ربات
# =====================================
bot_keyboard = ReplyKeyboardMarkup(
    [["🤖 ساخت ربات"]],
    resize_keyboard=True
)

# ذخیره وضعیت کاربران
users = {}

# جلوگیری از اجرای چندباره ربات فرزند
running_bots = {}

# =====================================
# ربات فرزند (موزیک یاب)
# =====================================

async def child_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 ربات موزیک یاب فعال شد\n\n"
        "نام آهنگ مورد نظر را ارسال کن:"
    )


async def child_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text

    await update.message.reply_text(
        "🔎 در حال جستجوی موزیک..."
    )

    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "quiet": True,
        "default_search": "ytsearch1",
        "outtmpl": "%(title)s.%(ext)s",
        "nocheckcertificate": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)

            if "entries" in info:
                info = info["entries"][0]

            title = info.get("title", "Music")
            file_path = ydl.prepare_filename(info)

            if not os.path.exists(file_path):
                await update.message.reply_text(
                    "❌ فایل موزیک پیدا نشد"
                )
                return

            with open(file_path, "rb") as audio_file:
                await update.message.reply_audio(
                    audio=audio_file,
                    title=title,
                    caption=f"🎧 {title}"
                )

            await update.message.reply_text(
                "✅ موزیک با موفقیت ارسال شد"
            )

            if os.path.exists(file_path):
                os.remove(file_path)

    except Exception:
        await update.message.reply_text(
            "❌ دانلود موزیک انجام نشد\n"
            "ممکن است مشکل از هاست یا محدودیت سرور باشد"
        )


def run_child_bot(token):
    async def start_bot():
        try:
            app = ApplicationBuilder().token(token).build()

            app.add_handler(
                CommandHandler("start", child_start)
            )

            app.add_handler(
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    child_music
                )
            )

            print(f"Child Bot Running: {token}")

            await app.initialize()
            await app.start()
            await app.updater.start_polling()

            await asyncio.Event().wait()

        except Exception as e:
            print(f"Child Bot Error: {e}")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_bot())


def start_child_bot(token):
    if token in running_bots:
        return

    thread = threading.Thread(
        target=run_child_bot,
        args=(token,),
        daemon=True
    )
    thread.start()

    running_bots[token] = True


# =====================================
# ربات مادر
# =====================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 ربات آماده است\n\n"
        "روی دکمه زیر بزن:",
        reply_markup=bot_keyboard
    )


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # کلیک روی ساخت ربات
    if text == "🤖 ساخت ربات":
        users[user_id] = {
            "step": "waiting_token"
        }

        await update.message.reply_text(
            "🔑 توکن ربات فرزند را ارسال کن:"
        )
        return

    # دریافت توکن ربات فرزند
    if (
        user_id in users
        and users[user_id].get("step") == "waiting_token"
    ):
        child_token = text

        try:
            start_child_bot(child_token)

            users[user_id]["step"] = "done"

            await update.message.reply_text(
                "✅ ربات فرزند فعال شد\n\n"
                "حالا داخل همان ربات /start بزن\n\n"
                "🎵 ربات موزیک یاب آماده است"
            )

        except Exception:
            await update.message.reply_text(
                "❌ توکن نامعتبر است"
            )

        return


# =====================================
# اجرای ربات مادر
# =====================================

app = ApplicationBuilder().token(MAIN_BOT_TOKEN).build()

app.add_handler(
    CommandHandler("start", start)
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handler
    )
)

print("🚀 Pro Music Bot Running...")

if __name__ == "__main__":
    app.run_polling()
