# -*- coding: utf-8 -*-
"""
NexStarz — from-scratch replica of @NexStarz_Bot (visible behaviour only)
=========================================================================
Single-file bot built with aiogram 3.x + SQLite (stdlib sqlite3).

Clean-room re-implementation of everything a normal user can SEE in
@NexStarz_Bot: forced-join gate (@nexStarz + @nexStarzGP), welcome text,
the tatweel (kashida) reply keyboard, Stars / Gifts / Premium / TON-GRAM
shops, channel Boost shop, wallet & account levels, orders, referral
(Earn), support (Nexy AI stub + direct message), NexStarz Cards and the
games centre, plus a functional admin panel.

Supplier / Fragment / payment backends are TODO stubs (see
deliver_order() and the payment handlers). Only visible behaviour is
replicated.

Coloured buttons (Bot API 9.x):
  Telegram inline/reply buttons support `style`:
      "success" -> green, "primary" -> blue/teal, "danger" -> red/brown-ish.
  In the original bot the brown buttons are Back / cancel / secondary
  actions; the Bot API has no dedicated "brown" style, so this replica
  maps the original's brown to "danger" (the closest Bot API style,
  which renders in the same warm red/brown family on current clients):

      COLOR_MAP = {
          "green": "success",   # buy / confirm / main shop rows
          "blue":  "primary",   # blue/teal service rows
          "brown": "danger",    # back / cancel / insufficient-balance rows
      }

  btn()/kbtn() pass style= and icon_custom_emoji_id= when the installed
  aiogram version supports them and silently fall back to plain buttons
  on older aiogram versions.

Custom (premium) emojis:
  The original bot decorates many labels with Telegram custom emojis.
  Their custom_emoji_id values CANNOT be extracted from Telegram Web, so
  CUSTOM_EMOJI_IDS ships EMPTY ({}) and labels keep their standard emoji
  prefixes. To use the real premium emojis: open your own bot, send
  yourself a message containing each premium emoji, read its
  custom_emoji_id (e.g. via a debug handler printing message.entities),
  fill CUSTOM_EMOJI_IDS and the buttons render them via
  icon_custom_emoji_id automatically (see btn()/kbtn()).
"""

import asyncio
import json
import logging
import os
import random
import sqlite3
import string
import time
from contextlib import closing

from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)

# ---------------------------------------------------------------------------
# Config (.env)
# ---------------------------------------------------------------------------

def _load_dotenv(path: str = ".env") -> None:
    """Tiny .env loader (no external dependency)."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


_load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_IDS = {
    int(x) for x in os.environ.get(
        "ADMIN_IDS", "8534895292,8839933177").replace(";", ",").split(",")
    if x.strip().lstrip("-").isdigit()
}
DB_PATH = os.environ.get("DB_PATH", os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "bot.db"))

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("nexstarz-replica")

# ---------------------------------------------------------------------------
# Custom emoji IDs — EMPTY on purpose (see module docstring).
# IDs are NOT extractable from Telegram Web; standard emoji fallbacks are
# used in the labels. Fill this dict with real custom_emoji_id values and
# btn()/kbtn() will pass them as icon_custom_emoji_id automatically.
# ---------------------------------------------------------------------------
CUSTOM_EMOJI_IDS = {}

# Colour mapping observed in the original bot (see module docstring).
STYLE_SUCCESS = "success"   # green — buy / confirm / shop rows
STYLE_PRIMARY = "primary"   # blue/teal — service rows
STYLE_DANGER = "danger"     # brown-ish in the original — back / cancel


def btn(text, callback_data=None, *, style=None, emoji_key=None, url=None,
        web_app=None):
    """InlineKeyboardButton with optional Bot API style + custom emoji icon.

    Falls back to a plain button when the installed aiogram version does
    not know the style/icon_custom_emoji_id/web_app fields yet.
    """
    kwargs = {"text": text}
    if callback_data is not None:
        kwargs["callback_data"] = callback_data
    if url is not None:
        kwargs["url"] = url
    if web_app is not None:
        kwargs["web_app"] = web_app
    icon = CUSTOM_EMOJI_IDS.get(emoji_key) if emoji_key else None
    attempts = []
    full = dict(kwargs)
    if style is not None:
        full["style"] = style
    if icon:
        full["icon_custom_emoji_id"] = icon
    attempts.append(full)
    if icon:
        no_icon = dict(kwargs)
        if style is not None:
            no_icon["style"] = style
        attempts.append(no_icon)
    attempts.append(dict(kwargs))
    last_exc = None
    for att in attempts:
        try:
            return InlineKeyboardButton(**att)
        except Exception as exc:  # older aiogram without style/icon fields
            last_exc = exc
    raise last_exc


def kbtn(text, *, style=None, emoji_key=None, web_app=None,
         request_contact=False):
    """Reply KeyboardButton with optional Bot API style + custom emoji icon."""
    kwargs = {"text": text}
    if web_app is not None:
        kwargs["web_app"] = web_app
    if request_contact:
        kwargs["request_contact"] = True
    icon = CUSTOM_EMOJI_IDS.get(emoji_key) if emoji_key else None
    attempts = []
    full = dict(kwargs)
    if style is not None:
        full["style"] = style
    if icon:
        full["icon_custom_emoji_id"] = icon
    attempts.append(full)
    if icon:
        no_icon = dict(kwargs)
        if style is not None:
            no_icon["style"] = style
        attempts.append(no_icon)
    attempts.append(dict(kwargs))
    last_exc = None
    for att in attempts:
        try:
            return KeyboardButton(**att)
        except Exception as exc:
            last_exc = exc
    raise last_exc


def ikb(rows):
    return InlineKeyboardMarkup(inline_keyboard=rows)


def fmt(n) -> str:
    """Format a Toman amount with thousands separators (e.g. 225,500)."""
    try:
        return f"{int(round(float(n))):,}"
    except (TypeError, ValueError):
        return str(n)


# ---------------------------------------------------------------------------
# Static catalogue data (seeded from the exploration report; prices also
# live in the settings table and are admin-editable)
# ---------------------------------------------------------------------------

# Stars packs shown in the shop (custom amount: min 50, max 1000).
STARS_PACKS = [50, 100, 200, 500]
STARS_MIN, STARS_MAX = 50, 1000

# 11 star gifts: key -> (label, stars, toman price at report time).
# Prices float in the original; these are the observed snapshot values and
# the per-gift Toman price is recomputed from the star value when the
# admin changes `price_per_star` only if `gift_price_mode` is "auto"
# (default: fixed snapshot below, editable in the admin panel).
GIFTS = [
    # key,        label,                    stars, toman
    ("heart",     "💗 قلب",                 15,    68000),
    ("bear",      "🧸 تدی",                 15,    69000),
    ("giftbox",   "🎁 کادو",                25,    114000),
    ("rose",      "🌹 گل رز",               25,    114000),
    ("cake",      "🎂 کیک",                 50,    229000),
    ("bouquet",   "💐 گل",                  50,    229000),
    ("rocket",    "🚀 سفینه",               50,    229000),
    ("trophy",    "🏆 جام",                 100,   458000),
    ("ring",      "💍 حلقه",                100,   458000),
    ("bottle",    "🍾 بطری",                50,    229000),
    ("diamond",   "💎 الماس",               100,   458000),
]
GIFT_BY_KEY = {g[0]: g for g in GIFTS}

# Premium plans: months -> toman price (report snapshot, admin-editable).
PREMIUM_PLANS = {3: 3555500, 6: 4740500, 12: 8596000}

# Boost plans. duration_days -> list of plan dicts.
# Fields: key, label, style, price per boost (Toman), min, max, time text.
# NOTE (from the report): the plain 30-day «به‌صرفه» plan appears ONLY in
# the comparison table of the original — it has no price and no order
# button there. It is therefore comparison-only here as well
# (orderable=False).
BOOST_PLANS = {
    7: [
        {"key": "speed7", "label": "پلن سرعتی", "style": STYLE_SUCCESS,
         "price": 26000, "min": 1, "max": 100000, "time": "1 ساعت",
         "avg": "1 ساعت", "quality": "معمولی",
         "orderable": True},
        {"key": "vip7", "label": "پلن ویژه", "style": STYLE_SUCCESS,
         "price": 14300, "min": 2, "max": 100000, "time": "24 ساعت",
         "avg": "24 ساعت", "quality": "عالی - تضمینی",
         "orderable": True},
    ],
    30: [
        {"key": "speed30", "label": "پلن سرعتی", "style": STYLE_SUCCESS,
         "price": 79900, "min": 1, "max": 100000, "time": "30 دقیقه",
         "avg": "30 دقیقه", "quality": "معمولی",
         "orderable": True},
        {"key": "vip30", "label": "پلن ویژه", "style": STYLE_SUCCESS,
         "price": 55500, "min": 2, "max": 100000, "time": "18 ساعت",
         "avg": "18 ساعت", "quality": "بهترین - تضمینی",
         "orderable": True},
        {"key": "sav_speed30", "label": "پلن به‌صرفه - سرعتی",
         "style": STYLE_SUCCESS,
         "price": 47300, "min": 10, "max": 100000, "time": "1 ساعت",
         "avg": "1 ساعت", "quality": "معمولی",
         "orderable": True},
        # Comparison-only entry — no price / no order button in original.
        {"key": "sav30", "label": "پلن به‌صرفه", "style": STYLE_SUCCESS,
         "price": None, "min": 10, "max": 100000, "time": "3 ساعت",
         "avg": "3 ساعت", "quality": "معمولی",
         "orderable": False},
    ],
}

# Account levels: level -> (daily top-up limit in Toman, requirement text)
LEVELS = {
    1: (500_000, "احراز هویت سطح ۱ (شماره موبایل)"),
    2: (2_000_000, "تکمیل احراز هویت سطح ۲"),
    3: (8_000_000, "تکمیل احراز هویت سطح ۳"),
}

# Games centre: (key, label) — 6 games, 3 rows of 2.
GAMES = [
    ("doz", "⭕ دوز"),
    ("mine", "💣 مین یاب"),
    ("dice", "🎲 تاس"),
    ("rps", "✊ سنگ کاغذ قیچی"),
    ("dart", "🎯 دارت"),
    ("bowling", "🎳 بولینگ"),
]
GAME_BY_KEY = {g[0]: g[1] for g in GAMES}


# ---------------------------------------------------------------------------
# Database (SQLite)
# ---------------------------------------------------------------------------

DEFAULT_SETTINGS = {
    # Forced-join gate
    "gate_enabled": "1",
    "gate_channels": "@nexStarz,@nexStarzGP",
    # Stars
    "price_per_star": "4512",          # Toman per star (floats in original)
    "stars_price_50": "225500",        # observed 50-star pack price
    # Premium (Toman)
    "premium_3": str(PREMIUM_PLANS[3]),
    "premium_6": str(PREMIUM_PLANS[6]),
    "premium_12": str(PREMIUM_PLANS[12]),
    # TON / GRAM (Toman per 1 TON)
    "ton_wallet_price": "328500",      # buy via personal wallet method
    "ton_direct_price": "329750",      # direct Telegram charge method
    "ton_wallet_address": "",          # admin sets the deposit address
    # Boost prices JSON: {"speed7": 26000, ...} — overrides BOOST_PLANS
    "boost_prices": "{}",
    # Referral
    "referral_percent": "2",
    # Support
    "support_username": "@NexStarzSupport",
    # WebApp placeholders (NFT market / my referrals)
    "nft_webapp_url": "https://nexstarz.example/nft",
    "referrals_webapp_url": "https://nexstarz.example/referrals",
    "games_group_link": "",
}


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with closing(db()) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users(
                user_id     INTEGER PRIMARY KEY,
                username    TEXT,
                full_name   TEXT,
                balance     INTEGER NOT NULL DEFAULT 0,
                level       INTEGER NOT NULL DEFAULT 0,
                banned      INTEGER NOT NULL DEFAULT 0,
                referrer_id INTEGER,
                joined_at   INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS settings(
                key   TEXT PRIMARY KEY,
                value TEXT
            );
            CREATE TABLE IF NOT EXISTS orders(
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                code        TEXT UNIQUE,
                user_id     INTEGER NOT NULL,
                kind        TEXT NOT NULL,
                title       TEXT NOT NULL,
                amount      INTEGER NOT NULL DEFAULT 0,
                price       INTEGER NOT NULL DEFAULT 0,
                recipient   TEXT,
                status      TEXT NOT NULL DEFAULT 'pending',
                created_at  INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS discount_codes(
                code    TEXT PRIMARY KEY,
                percent INTEGER NOT NULL,
                active  INTEGER NOT NULL DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS tickets(
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                text       TEXT,
                created_at INTEGER NOT NULL
            );
            """
        )
        for k, v in DEFAULT_SETTINGS.items():
            conn.execute(
                "INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)",
                (k, v))
        conn.commit()


def get_setting(key: str, default: str = "") -> str:
    with closing(db()) as conn:
        row = conn.execute(
            "SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default


def set_setting(key: str, value: str) -> None:
    with closing(db()) as conn:
        conn.execute(
            "INSERT INTO settings(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value))
        conn.commit()


def setting_int(key: str, default: int = 0) -> int:
    try:
        return int(float(get_setting(key, str(default))))
    except ValueError:
        return default


def gate_channels() -> list:
    raw = get_setting("gate_channels", "@nexStarz,@nexStarzGP")
    return [c.strip() for c in raw.split(",") if c.strip()]


def ensure_user(user_id: int, username: str = "", full_name: str = "",
                referrer_id: int = None) -> dict:
    with closing(db()) as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
        if row is None:
            conn.execute(
                "INSERT INTO users(user_id,username,full_name,referrer_id,"
                "joined_at) VALUES(?,?,?,?,?)",
                (user_id, username or "", full_name or "", referrer_id,
                 int(time.time())))
            conn.commit()
            row = conn.execute(
                "SELECT * FROM users WHERE user_id=?",
                (user_id,)).fetchone()
        else:
            conn.execute(
                "UPDATE users SET username=?, full_name=? WHERE user_id=?",
                (username or row["username"], full_name or row["full_name"],
                 user_id))
            conn.commit()
    return dict(row)


def get_user(user_id: int):
    with closing(db()) as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
    return dict(row) if row else None


def change_balance(user_id: int, delta: int) -> int:
    with closing(db()) as conn:
        conn.execute(
            "UPDATE users SET balance=balance+? WHERE user_id=?",
            (delta, user_id))
        conn.commit()
        row = conn.execute(
            "SELECT balance FROM users WHERE user_id=?",
            (user_id,)).fetchone()
    return row["balance"] if row else 0


def new_order_code() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(random.choice(alphabet) for _ in range(8))


def create_order(user_id: int, kind: str, title: str, amount: int,
                 price: int, recipient: str = "") -> str:
    code = new_order_code()
    with closing(db()) as conn:
        while conn.execute("SELECT 1 FROM orders WHERE code=?",
                           (code,)).fetchone():
            code = new_order_code()
        conn.execute(
            "INSERT INTO orders(code,user_id,kind,title,amount,price,"
            "recipient,status,created_at) VALUES(?,?,?,?,?,?,?, 'pending', ?)",
            (code, user_id, kind, title, amount, price, recipient,
             int(time.time())))
        conn.commit()
    return code


def get_order(code: str):
    with closing(db()) as conn:
        row = conn.execute(
            "SELECT * FROM orders WHERE code=?", (code.strip().upper(),)
        ).fetchone()
    return dict(row) if row else None


def user_orders(user_id: int, limit: int = 20) -> list:
    with closing(db()) as conn:
        rows = conn.execute(
            "SELECT * FROM orders WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (user_id, limit)).fetchall()
    return [dict(r) for r in rows]


def discount_percent(code: str):
    with closing(db()) as conn:
        row = conn.execute(
            "SELECT percent FROM discount_codes WHERE code=? AND active=1",
            (code.strip(),)).fetchone()
    return row["percent"] if row else None


def boost_price(plan: dict) -> int:
    """Boost price with admin override from the boost_prices JSON setting."""
    try:
        overrides = json.loads(get_setting("boost_prices", "{}") or "{}")
    except json.JSONDecodeError:
        overrides = {}
    if plan["key"] in overrides:
        return int(overrides[plan["key"]])
    return plan["price"] or 0


def stars_price(amount: int) -> int:
    """Price of a Stars amount. 50-pack uses its seeded price; other
    amounts are amount x price_per_star (both admin-editable)."""
    if amount == 50:
        return setting_int("stars_price_50", 225500)
    return amount * setting_int("price_per_star", 4512)


async def deliver_order(bot: Bot, order_code: str) -> bool:
    """TODO stub: real delivery (Fragment / supplier API) is NOT
    implemented — in the original bot delivery is automatic after
    payment. This stub only marks the order as delivered so the flow
    can be tested end-to-end with wallet payments."""
    with closing(db()) as conn:
        conn.execute("UPDATE orders SET status='delivered' WHERE code=?",
                     (order_code,))
        conn.commit()
    return True


# ---------------------------------------------------------------------------
# Texts (verbatim from the exploration report where quoted there)
# ---------------------------------------------------------------------------

WELCOME_TEXT = (
    "سلام! اینجا نِکستارزه، سریعترین و مطمئنترین برای خرید:\n"
    "⭐️ استارز تلگرام\n"
    "✅ تلگرام پرمیوم\n"
    "🪙 ارز تونکوین\n"
    "🎁 گیفتهای تلگرامی\n"
    "⚡ بوست کانال\n"
    "رفیق، سفارشت کاملاً خودکار و در سریعترین زمان ممکن انجام میشه. خیالت راحت!\n"
    "👇 لطفاً برای شروع، از منوی زیر استفاده کنید: 🎉"
)

GATE_TEXT = (
    "🔒 برای استفاده از ربات، ابتدا در کانال و گروه زیر عضو شوید و سپس "
    "دکمه «بررسی عضویت» را بزنید:"
)

STARS_INTRO = (
    "⭐ خرید استارز تلگرام\n\n"
    "تعداد استارز موردنظرت رو انتخاب کن یا روی «مقدار دلخواه» بزن و تعداد "
    "رو وارد کن.\n"
    "حداقل خرید: ۵۰ استارز | حداکثر خرید: ۱۰۰۰ استارز\n\n"
    "تحویل سفارش کاملاً خودکار و فوریه. 🚀"
)

GIFTS_INTRO = (
    "🎁 خرید گیفت‌های استارزی تلگرام\n\n"
    "گیفت موردنظرت رو انتخاب کن تا برای خودت یا دوستت ارسال بشه. ✨"
)

GIFT_SENDER_GATE_TEXT = (
    "❗️ عدم ثبت پیام گیرنده به اکانت فرستنده!\n\n"
    "کاربر گیرنده … هنوز به اکانت فرستنده پیامی ارسال نکرده است.\n\n"
    "💡 طبق قوانین اسپم تلگرام، برای ارسال گیفت، کاربر گیرنده باید "
    "حداقل یک پیام به اکانت فرستنده ارسال کرده باشد؛ تا زمانی که گیرنده "
    "به اکانت فرستنده پیام نداده باشد، تلگرام اجازه ارسال گیفت را "
    "نمی‌دهد. لطفاً از گیرنده بخواهید ابتدا یک پیام به اکانت فرستنده "
    "ارسال کند، سپس دکمه «پیام ارسال شد» را بزنید."
)

PREMIUM_INTRO = (
    "💎 خرید پرمیوم تلگرام\n\n"
    "پلن موردنظرت رو انتخاب کن. پرمیوم به‌صورت خودکار و فوری روی اکانت "
    "فعال می‌شه. 🚀"
)

PREMIUM_LOADING = "⏳ در حال بارگذاری پلن‌های پرمیوم..."

TON_INTRO = (
    "💠 خرید تون (TON) و گرام (GRAM)\n\n"
    "روش خرید رو انتخاب کن:\n\n"
    "۱) کیف پول شخصی: ارز به آدرس کیف پول خودت ارسال می‌شه.\n"
    "۲) شارژ مستقیم تلگرام: موجودی تون مستقیم روی اکانت تلگرامت شارژ می‌شه."
)

TON_WALLET_ADDRESS_PROMPT = (
    "💠 خرید تون با روش کیف پول شخصی\n\n"
    "آدرس کیف پول TON خودت رو ارسال کن.\n\n"
    "⚠️ هشدار: آدرس رو با دقت وارد کن؛ در صورت اشتباه بودن آدرس، ارز به "
    "کیف پول اشتباه ارسال می‌شه و امکان بازگشت وجود نداره!"
)

TON_DIRECT_INTRO = (
    "💠 شارژ مستقیم تون تلگرام\n\n"
    "تعداد تون موردنظرت رو به‌صورت عدد صحیح وارد کن (مثلاً 5)."
)

BOOST_INTRO = (
    "🚀 خرید بوست چنل\n\n"
    "مدت زمان بوست رو انتخاب کن:"
)

ACCOUNT_LEVELS_TEXT = (
    "🏅 سطوح کاربری نکس‌استارز\n\n"
    "سطح ۱ ← سقف افزایش موجودی روزانه: ۵۰۰,۰۰۰ تومان\n"
    "سطح ۲ ← سقف افزایش موجودی روزانه: ۲,۰۰۰,۰۰۰ تومان\n"
    "سطح ۳ ← سقف افزایش موجودی روزانه: ۸,۰۰۰,۰۰۰ تومان\n\n"
    "برای ارتقای سطح، احراز هویت رو کامل کنید."
)

KYC_BLOCK_TEXT = (
    "❗️ محدودیت خرید ریالی (نیاز به احراز هویت)\n"
    "کاربر گرامی، در حال حاضر خرید یا شارژ ریالی برای حساب شما غیرفعال است.\n"
    "لطفاً جهت فعالسازی و افزایش سقف تراکنشهای خود، شماره همراه خود را تایید کرده و به سطح 1 ارتقا یابید"
)

ORDERS_EMPTY_TEXT = (
    "🧾 سفارش‌های من\n\n"
    "هنوز سفارشی ثبت نکرده‌اید."
)

EARN_INTRO = (
    "💰 کسب درآمد با نکس‌استارز\n\n"
    "دوستانت رو با لینک اختصاصی خودت دعوت کن و از هر خرید اون‌ها ۲٪ "
    "کمیسیون بگیر!\n"
    "کمیسیون به‌صورت خودکار به کیف پولت اضافه می‌شه. 🎉"
)

SUPPORT_INTRO = (
    "🛎 پشتیبانی نکس‌استارز\n\n"
    "می‌تونید با دستیار هوشمند «نکسی» چت کنید یا پیام‌تون رو مستقیم برای "
    "تیم پشتیبانی ارسال کنید."
)

GAMES_TEXT = (
    "🎮 مرکز بازیهای نکستارز\n"
    "• دوز • مین یاب • سنگ کاغذ قیچی • تاس، دارت و بولینگ\n"
    "💡 روش بازی:\n"
    "• تمامی بازیها در بستر گروهها با پرتابهای زنده اجرا میشوند.\n"
    "• با دکمه «افزودن به گروه» در زیر، ربات را به گروه خود اضافه کنید و با دوستان خود بازی کنید! 🎉"
)

CARDS_TEXT = (
    "💳 کارت‌های نکس‌استارز (NexStarz Cards)\n\n"
    "کارت‌های اختصاصی نکس‌استارز رو جمع‌آوری کنید و از مزایای ویژه هر "
    "کارت بهره‌مند بشید. اطلاعات کارت‌های شما بعد از اولین خرید نمایش "
    "داده می‌شه."
)


def invoice_text(title: str, detail: str, price: int, balance: int,
                 code: str) -> str:
    """The shared invoice template (Stars / Premium / TON / gifts)."""
    return (
        f"🧾 پیش‌فاکتور خرید\n\n"
        f"📦 محصول: {title}\n"
        f"{detail}\n"
        f"💰 مبلغ قابل پرداخت: {fmt(price)} تومان\n"
        f"👛 موجودی کیف پول شما: {fmt(balance)} تومان\n"
        f"🔖 کد سفارش: {code}\n\n"
        f"⏰ این پیش‌فاکتور فقط ۱۵ دقیقه اعتبار دارد."
    )


# ---------------------------------------------------------------------------
# Main reply keyboard labels (tatweel / kashida stretched, as reported)
# ---------------------------------------------------------------------------

BTN_STARS = "⭐ خریـد استـارز"
BTN_GIFT = "🎁 خریـد گیفـت"
BTN_PREMIUM = "💎 خریـد پرمیـوم"
BTN_TON = "💠 خریـد تـون | گـرام"
BTN_BOOST = "🚀 خریـد بـوسـت چنـل"
BTN_NFT = "🖼 بـازار NFT"
BTN_ACCOUNT = "👤 حسـاب کـاربـری"
BTN_ORDERS = "🧾 سفـارش‌هـای مـن"
BTN_EARN = "💰 کسـب درآمـد"
BTN_SUPPORT = "🛎 پشتیبـانـی"
BTN_GAMES = "🎮 بـازی‌هـا"

MAIN_MENU_BUTTONS = {
    BTN_STARS, BTN_GIFT, BTN_PREMIUM, BTN_TON, BTN_BOOST, BTN_NFT,
    BTN_ACCOUNT, BTN_ORDERS, BTN_EARN, BTN_SUPPORT, BTN_GAMES,
}


# ---------------------------------------------------------------------------
# Keyboard builders (used by handlers AND by the smoke test)
# ---------------------------------------------------------------------------

def kb_main_reply():
    """Main menu — exactly the reported 7 rows with their colours."""
    from aiogram.types import WebAppInfo
    return ReplyKeyboardMarkup(
        keyboard=[
            [kbtn(BTN_STARS, style=STYLE_SUCCESS, emoji_key="star"),
             kbtn(BTN_GIFT, style=STYLE_SUCCESS, emoji_key="gift")],
            [kbtn(BTN_PREMIUM, style=STYLE_PRIMARY, emoji_key="premium"),
             kbtn(BTN_TON, style=STYLE_PRIMARY, emoji_key="ton")],
            [kbtn(BTN_BOOST, style=STYLE_SUCCESS, emoji_key="boost")],
            [kbtn(BTN_NFT, style=STYLE_PRIMARY, emoji_key="nft",
                  web_app=WebAppInfo(url=get_setting(
                      "nft_webapp_url", "https://nexstarz.example/nft")))],
            [kbtn(BTN_ACCOUNT, style=STYLE_SUCCESS, emoji_key="account"),
             kbtn(BTN_ORDERS, style=STYLE_SUCCESS, emoji_key="orders")],
            [kbtn(BTN_EARN, style=STYLE_SUCCESS, emoji_key="earn"),
             kbtn(BTN_SUPPORT, style=STYLE_SUCCESS, emoji_key="support")],
            [kbtn(BTN_GAMES, style=STYLE_PRIMARY, emoji_key="games")],
        ],
        resize_keyboard=True,
    )


def kb_gate():
    rows = []
    for ch in gate_channels():
        rows.append([btn(f"📢 عضویت در {ch}", url=f"https://t.me/{ch.lstrip('@')}",
                         style=STYLE_PRIMARY, emoji_key="channel")])
    rows.append([btn("✅ بررسی عضویت", callback_data="gate:check",
                     style=STYLE_SUCCESS, emoji_key="check")])
    return ikb(rows)


def kb_back_main():
    return ikb([[btn("🏠 منوی اصلی", callback_data="nav:main",
                     style=STYLE_DANGER)]])


def kb_stars():
    rows = []
    row = []
    for amount in STARS_PACKS:
        row.append(btn(f"⭐ {amount} استارز — {fmt(stars_price(amount))} تومان",
                       callback_data=f"stars:pack:{amount}",
                       style=STYLE_SUCCESS, emoji_key="star"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([btn("✏️ مقدار دلخواه", callback_data="stars:custom",
                     style=STYLE_PRIMARY)])
    rows.append([btn("🏠 منوی اصلی", callback_data="nav:main",
                     style=STYLE_DANGER)])
    return ikb(rows)


def kb_recipient(prefix: str):
    """Recipient step used by stars/gift/premium/ton flows."""
    return ikb([
        [btn("👤 برای خودم", callback_data=f"{prefix}:self",
             style=STYLE_SUCCESS)],
        [btn("🏠 منوی اصلی", callback_data="nav:main", style=STYLE_DANGER)],
    ])


def kb_invoice(code: str, balance: int, price: int):
    rows = []
    if balance >= price:
        rows.append([btn("👛 پرداخت با کیف پول", callback_data=f"pay:wallet:{code}",
                         style=STYLE_SUCCESS)])
    else:
        rows.append([btn("❌ موجودی کیف پول کافی نیست",
                         callback_data="pay:nobalance", style=STYLE_DANGER)])
    rows.append([btn("💳 پرداخت آنلاین", callback_data=f"pay:online:{code}",
                     style=STYLE_SUCCESS)])
    rows.append([btn("🎟 اعمال کد تخفیف", callback_data=f"pay:discount:{code}",
                     style=STYLE_SUCCESS)])
    rows.append([btn("🔙 بازگشت", callback_data="nav:back",
                     style=STYLE_SUCCESS)])
    rows.append([btn("🏠 منوی اصلی", callback_data="nav:main",
                     style=STYLE_DANGER)])
    return ikb(rows)


def kb_gifts():
    rows = []
    row = []
    for key, label, stars, price in GIFTS:
        row.append(btn(f"{label} — {stars}⭐ ({fmt(price)} تومان)",
                       callback_data=f"gift:open:{key}",
                       style=STYLE_SUCCESS, emoji_key="gift"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([btn("🏠 منوی اصلی", callback_data="nav:main",
                     style=STYLE_DANGER)])
    return ikb(rows)


def kb_gift_detail(key: str):
    return ikb([
        [btn("🙂 مشخص", callback_data=f"gift:vis:{key}:named",
             style=STYLE_SUCCESS),
         btn("🕶 ناشناس", callback_data=f"gift:vis:{key}:anon",
             style=STYLE_SUCCESS)],
        [btn("🔙 بازگشت", callback_data="gift:list", style=STYLE_SUCCESS)],
        [btn("🏠 منوی اصلی", callback_data="nav:main", style=STYLE_DANGER)],
    ])


def kb_premium():
    rows = []
    for months in (3, 6, 12):
        price = setting_int(f"premium_{months}", PREMIUM_PLANS[months])
        rows.append([btn(f"💎 پرمیوم {months} ماهه — {fmt(price)} تومان",
                         callback_data=f"premium:plan:{months}",
                         style=STYLE_SUCCESS, emoji_key="premium")])
    rows.append([btn("🏠 منوی اصلی", callback_data="nav:main",
                     style=STYLE_DANGER)])
    return ikb(rows)


def kb_ton_methods():
    wallet_price = setting_int("ton_wallet_price", 328500)
    direct_price = setting_int("ton_direct_price", 329750)
    return ikb([
        [btn(f"👛 کیف پول شخصی — هر تون {fmt(wallet_price)} تومان",
             callback_data="ton:method:wallet", style=STYLE_SUCCESS)],
        [btn(f"⚡ شارژ مستقیم تلگرام — هر تون {fmt(direct_price)} تومان",
             callback_data="ton:method:direct", style=STYLE_SUCCESS)],
        [btn("🏠 منوی اصلی", callback_data="nav:main", style=STYLE_DANGER)],
    ])


def kb_boost_durations():
    return ikb([
        [btn("📅 بوست ۷ روزه", callback_data="boost:days:7",
             style=STYLE_PRIMARY),
         btn("📅 بوست ۳۰ روزه", callback_data="boost:days:30",
             style=STYLE_PRIMARY)],
        [btn("🏠 منوی اصلی", callback_data="nav:main", style=STYLE_DANGER)],
    ])


def kb_boost_plans(days: int):
    orderable = [p for p in BOOST_PLANS[days] if p["orderable"]]
    rows = []
    if days == 30:
        # سرعتی + ویژه green in one row, به‌صرفه - سرعتی green full width
        first = orderable[:2]
        rows.append([btn(
            plan['label'],
            callback_data=f"boost:plan:{days}:{plan['key']}",
            style=STYLE_SUCCESS) for plan in first])
        for plan in orderable[2:]:
            rows.append([btn(
                plan['label'],
                callback_data=f"boost:plan:{days}:{plan['key']}",
                style=STYLE_SUCCESS)])
    else:
        for plan in orderable:
            rows.append([btn(
                plan['label'],
                callback_data=f"boost:plan:{days}:{plan['key']}",
                style=STYLE_SUCCESS)])
    rows.append([btn("مقایسه پلنها", callback_data=f"boost:compare:{days}",
                     style=STYLE_PRIMARY)])
    rows.append([btn("بازگشت", callback_data="boost:home",
                     style=STYLE_DANGER)])
    return ikb(rows)


def boost_compare_text(days: int) -> str:
    lines = [f"📊 مقایسه پلنهای بوست {days} روزه\n"]
    for plan in BOOST_PLANS[days]:
        price = (fmt(boost_price(plan)) + " تومان"
                 if plan["price"] is not None else "—")
        lines.append(
            f"{plan['label']}\n"
            f"💰 قیمت هر عدد: {price}\n"
            f"🎙 حداقل: {fmt(plan['min'])} عدد | حداکثر: "
            f"{fmt(plan['max'])} عدد\n"
            f"⏱ میانگین زمان تحویل: {plan.get('avg', plan['time'])}\n"
            f"✨ کیفیت: {plan.get('quality', '')}\n")
    return "\n".join(lines)


def kb_gift_sender_gate():
    return ikb([
        [btn("ارسال پیام به فرستنده", callback_data="gift:gate:send",
             style=STYLE_PRIMARY)],
        [btn("پیام ارسال شد", callback_data="gift:gate:sent",
             style=STYLE_SUCCESS)],
        [btn("تغییر گیرنده", callback_data="gift:gate:change",
             style=STYLE_SUCCESS)],
        [btn("منوی اصلی", callback_data="nav:main",
             style=STYLE_DANGER)],
    ])


def kb_kyc_block():
    return ikb([
        [btn("ارتقای سطح و احراز هویت", callback_data="account:verify1",
             style=STYLE_PRIMARY)],
    ])


def kb_account(user: dict):
    return ikb([
        [btn("💰 افزایش موجودی", callback_data="wallet:topup",
             style=STYLE_SUCCESS)],
        [btn("🏅 سطح کاربری من", callback_data="account:levels",
             style=STYLE_PRIMARY),
         btn("💳 کارت‌های نکس‌استارز", callback_data="account:cards",
             style=STYLE_PRIMARY)],
        [btn("🏠 منوی اصلی", callback_data="nav:main", style=STYLE_DANGER)],
    ])


def kb_topup_methods():
    return ikb([
        [btn("💳 شارژ ریالی (کارت بانکی)", callback_data="wallet:rial",
             style=STYLE_SUCCESS)],
        [btn("🪙 شارژ با ارز دیجیتال", callback_data="wallet:crypto",
             style=STYLE_PRIMARY)],
        [btn("🔙 بازگشت", callback_data="account:home", style=STYLE_SUCCESS)],
        [btn("🏠 منوی اصلی", callback_data="nav:main", style=STYLE_DANGER)],
    ])


def kb_levels():
    return ikb([
        [btn("📱 احراز هویت سطح ۱ با شماره موبایل",
             callback_data="account:verify1", style=STYLE_SUCCESS)],
        [btn("🔙 بازگشت", callback_data="account:home", style=STYLE_SUCCESS)],
        [btn("🏠 منوی اصلی", callback_data="nav:main", style=STYLE_DANGER)],
    ])


def kb_orders():
    return ikb([
        [btn("🔍 جستجو با کد سفارش", callback_data="orders:search",
             style=STYLE_PRIMARY)],
        [btn("🏠 منوی اصلی", callback_data="nav:main", style=STYLE_DANGER)],
    ])


def kb_earn(user_id: int, bot_username: str = ""):
    from aiogram.types import WebAppInfo
    link = f"https://t.me/{bot_username}?start=ref_{user_id}" if bot_username \
        else f"ref_{user_id}"
    return ikb([
        [btn("🔗 لینک دعوت من", callback_data="earn:link",
             style=STYLE_PRIMARY)],
        [btn("👥 زیرمجموعه‌های من", web_app=WebAppInfo(
            url=get_setting("referrals_webapp_url",
                            "https://nexstarz.example/referrals")),
            style=STYLE_SUCCESS)],
        [btn("💸 برداشت کمیسیون", callback_data="earn:withdraw",
             style=STYLE_SUCCESS)],
        [btn("🏠 منوی اصلی", callback_data="nav:main", style=STYLE_DANGER)],
    ]), link


def kb_support():
    return ikb([
        [btn("🤖 چت با نکسی (دستیار هوشمند)", callback_data="support:nexy",
             style=STYLE_SUCCESS)],
        [btn("✉️ ارسال پیام مستقیم به پشتیبانی",
             callback_data="support:direct", style=STYLE_PRIMARY)],
        [btn("🏠 منوی اصلی", callback_data="nav:main", style=STYLE_DANGER)],
    ])


def kb_cancel_support():
    return ikb([[btn("❌ انصراف", callback_data="support:cancel",
                     style=STYLE_DANGER)]])


def kb_games():
    rows = []
    row = []
    for key, label in GAMES:
        row.append(btn(label, callback_data=f"game:open:{key}",
                       style=STYLE_SUCCESS, emoji_key="games"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    group_link = get_setting("games_group_link", "")
    if group_link:
        rows.append([btn("➕ افزودن به گروه", url=group_link,
                         style=STYLE_PRIMARY)])
    else:
        rows.append([btn("➕ افزودن به گروه", callback_data="game:addgroup",
                         style=STYLE_PRIMARY)])
    rows.append([btn("🔙 بازگشت", callback_data="nav:main",
                     style=STYLE_DANGER)])
    return ikb(rows)


def kb_game_modes(key: str):
    return ikb([
        [btn("😊 بازی دوستانه", callback_data=f"game:mode:{key}:friendly",
             style=STYLE_SUCCESS),
         btn("🏆 بازی رقابتی", callback_data=f"game:mode:{key}:competitive",
             style=STYLE_SUCCESS)],
        [btn("🔙 بازگشت", callback_data="game:home", style=STYLE_DANGER)],
    ])


def kb_game_created():
    return ikb([
        [btn("❌ لغو بازی", callback_data="game:cancel", style=STYLE_DANGER)],
        [btn("🎮 مرکز بازی‌ها", callback_data="game:home",
             style=STYLE_SUCCESS)],
    ])


# ---------------------------------------------------------------------------
# FSM states
# ---------------------------------------------------------------------------

class StarsFlow(StatesGroup):
    custom_amount = State()
    recipient = State()
    discount = State()


class GiftFlow(StatesGroup):
    sender_message = State()
    recipient = State()


class PremiumFlow(StatesGroup):
    recipient = State()


class TonFlow(StatesGroup):
    wallet_address = State()
    wallet_amount = State()
    direct_amount = State()
    recipient = State()


class BoostFlow(StatesGroup):
    quantity = State()
    link = State()


class WalletFlow(StatesGroup):
    topup_amount = State()
    crypto_hash = State()


class AccountFlow(StatesGroup):
    phone = State()   # Level-1 verification stub (no real KYC collection)


class OrdersFlow(StatesGroup):
    search_code = State()


class SupportFlow(StatesGroup):
    nexy = State()
    direct = State()


class AdminFlow(StatesGroup):
    set_setting = State()
    broadcast_text = State()
    add_discount = State()
    user_lookup = State()
    balance_adjust = State()


router = Router()

BOT_USERNAME_CACHE = {"username": ""}


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


async def is_member(bot: Bot, user_id: int, channel: str) -> bool:
    """One channel membership check; any API error counts as NOT a member
    for normal users but never hard-crashes the gate (logged instead)."""
    try:
        member = await bot.get_chat_member(channel, user_id)
        return member.status not in ("left", "kicked")
    except Exception as exc:
        log.warning("getChatMember failed for %s/%s: %s", channel, user_id, exc)
        return False


async def gate_passed(bot: Bot, user_id: int) -> bool:
    if is_admin(user_id):
        return True
    if get_setting("gate_enabled", "1") != "1":
        return True
    for channel in gate_channels():
        if not await is_member(bot, user_id, channel):
            return False
    return True


async def send_gate(message: Message) -> None:
    await message.answer(GATE_TEXT, reply_markup=kb_gate())


async def send_main(message: Message, text: str = WELCOME_TEXT) -> None:
    await message.answer(text, reply_markup=kb_main_reply())


# ---------------------------------------------------------------------------
# /start + gate
# ---------------------------------------------------------------------------

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, bot: Bot) -> None:
    await state.clear()
    args = (message.text or "").split(maxsplit=1)
    referrer_id = None
    if len(args) > 1 and args[1].startswith("ref_"):
        try:
            referrer_id = int(args[1][4:])
            if referrer_id == message.from_user.id:
                referrer_id = None
        except ValueError:
            referrer_id = None
    user = ensure_user(message.from_user.id, message.from_user.username or "",
                       message.from_user.full_name or "", referrer_id)
    if user["banned"]:
        await message.answer("⛔ حساب شما مسدود شده است.")
        return
    if not await gate_passed(bot, message.from_user.id):
        await send_gate(message)
        return
    await send_main(message)


@router.callback_query(F.data == "gate:check")
async def gate_check(call: CallbackQuery, bot: Bot) -> None:
    if await gate_passed(bot, call.from_user.id):
        await call.message.delete()
        await call.message.answer(WELCOME_TEXT, reply_markup=kb_main_reply())
        await call.answer("✅ عضویت شما تأیید شد.")
    else:
        await call.answer("❌ هنوز در همه کانال‌ها عضو نشده‌اید.",
                          show_alert=True)


@router.message(Command("buy"))
async def cmd_buy(message: Message, bot: Bot) -> None:
    """Original lists only /start; /buy is a convenience shortcut that
    opens the Stars shop directly."""
    ensure_user(message.from_user.id, message.from_user.username or "",
                message.from_user.full_name or "")
    if not await gate_passed(bot, message.from_user.id):
        await send_gate(message)
        return
    await message.answer(STARS_INTRO, reply_markup=kb_stars())


@router.callback_query(F.data == "nav:main")
async def nav_main(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    try:
        await call.message.delete()
    except TelegramBadRequest:
        pass
    await call.message.answer(WELCOME_TEXT, reply_markup=kb_main_reply())
    await call.answer()


@router.callback_query(F.data == "nav:back")
async def nav_back(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.answer(STARS_INTRO, reply_markup=kb_stars())
    await call.answer()


@router.callback_query(F.data == "pay:nobalance")
async def pay_no_balance(call: CallbackQuery) -> None:
    await call.answer("❌ موجودی کیف پول شما کافی نیست. ابتدا کیف پول را "
                      "شارژ کنید.", show_alert=True)


# ---------------------------------------------------------------------------
# Invoice helpers shared by stars / premium / ton / gifts
# ---------------------------------------------------------------------------

async def show_invoice(message: Message, user_id: int, kind: str,
                       title: str, detail: str, amount: int, price: int,
                       recipient: str) -> str:
    user = get_user(user_id) or ensure_user(user_id)
    code = create_order(user_id, kind, title, amount, price, recipient)
    await message.answer(
        invoice_text(title, detail, price, user["balance"], code),
        reply_markup=kb_invoice(code, user["balance"], price))
    return code


async def ask_recipient(message: Message, state: FSMContext, prefix: str,
                        prompt: str) -> None:
    await message.answer(prompt, reply_markup=kb_recipient(prefix))


# ---------------------------------------------------------------------------
# Stars shop
# ---------------------------------------------------------------------------

async def open_stars(message: Message) -> None:
    await message.answer(STARS_INTRO, reply_markup=kb_stars())


@router.callback_query(F.data.startswith("stars:pack:"))
async def stars_pack(call: CallbackQuery, state: FSMContext) -> None:
    amount = int(call.data.rsplit(":", 1)[1])
    await state.update_data(kind="stars", amount=amount,
                            price=stars_price(amount))
    await ask_recipient(
        call.message, state, "stars",
        f"⭐ خرید {amount} استارز\n\nگیرنده استارز چه کسی باشد؟\n"
        "می‌توانید دکمه «برای خودم» را بزنید یا آیدی عددی / یوزرنیم گیرنده "
        "را ارسال کنید:")
    await state.set_state(StarsFlow.recipient)
    await call.answer()


@router.callback_query(F.data == "stars:custom")
async def stars_custom(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.answer(
        f"✏️ تعداد استارز موردنظرت رو وارد کن (بین {STARS_MIN} تا "
        f"{STARS_MAX}):")
    await state.set_state(StarsFlow.custom_amount)
    await call.answer()


@router.message(StarsFlow.custom_amount)
async def stars_custom_amount(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if not text.isdigit() or not (STARS_MIN <= int(text) <= STARS_MAX):
        await message.answer(
            f"⚠️ لطفاً یک عدد بین {STARS_MIN} تا {STARS_MAX} وارد کنید.")
        return
    amount = int(text)
    await state.update_data(kind="stars", amount=amount,
                            price=stars_price(amount))
    await ask_recipient(
        message, state, "stars",
        f"⭐ خرید {amount} استارز\n\nگیرنده استارز چه کسی باشد؟\n"
        "می‌توانید دکمه «برای خودم» را بزنید یا آیدی عددی / یوزرنیم گیرنده "
        "را ارسال کنید:")
    await state.set_state(StarsFlow.recipient)


@router.callback_query(F.data == "stars:self", StarsFlow.recipient)
async def stars_recipient_self(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()
    uname = call.from_user.username
    recipient = f"@{uname}" if uname else str(call.from_user.id)
    await show_invoice(call.message, call.from_user.id, "stars",
                       f"خرید {data['amount']} استارز تلگرام",
                       f"👤 گیرنده: {recipient}", data["amount"],
                       data["price"], recipient)
    await call.answer()


@router.message(StarsFlow.recipient)
async def stars_recipient_text(message: Message, state: FSMContext) -> None:
    recipient = (message.text or "").strip()
    if recipient in MAIN_MENU_BUTTONS:
        await state.clear()
        await route_main_menu(message, state)
        return
    data = await state.get_data()
    await state.clear()
    await show_invoice(message, message.from_user.id, "stars",
                       f"خرید {data['amount']} استارز تلگرام",
                       f"👤 گیرنده: {recipient}", data["amount"],
                       data["price"], recipient)


# ---------------------------------------------------------------------------
# Payment callbacks (wallet = real against balance; online = TODO stub)
# ---------------------------------------------------------------------------

@router.callback_query(F.data.startswith("pay:wallet:"))
async def pay_wallet(call: CallbackQuery, bot: Bot) -> None:
    code = call.data.rsplit(":", 1)[1]
    order = get_order(code)
    if not order or order["user_id"] != call.from_user.id:
        await call.answer("❌ سفارش یافت نشد.", show_alert=True)
        return
    user = get_user(call.from_user.id)
    if user["balance"] < order["price"]:
        await call.answer("❌ موجودی کیف پول کافی نیست.", show_alert=True)
        return
    change_balance(call.from_user.id, -order["price"])
    await deliver_order(bot, code)
    # Referral commission: 2% of the purchase to the referrer.
    if user.get("referrer_id"):
        commission = int(order["price"] * setting_int("referral_percent", 2)
                         / 100)
        if commission > 0:
            change_balance(user["referrer_id"], commission)
    await call.message.answer(
        f"✅ پرداخت با موفقیت انجام شد!\n\n"
        f"📦 سفارش: {order['title']}\n"
        f"🔖 کد سفارش: {code}\n"
        f"🚀 سفارش شما در حال تحویل است.")
    await call.answer()


@router.callback_query(F.data.startswith("pay:online:"))
async def pay_online(call: CallbackQuery) -> None:
    # TODO stub: the original redirects to an online Rial gateway; the
    # gateway itself (and its KYC gate) is not replicated. See wallet
    # Rial top-up for the KYC block message.
    await call.answer("💳 درگاه پرداخت آنلاین در این نسخه نمایشی فعال نیست؛ "
                      "از پرداخت با کیف پول استفاده کنید.", show_alert=True)


@router.callback_query(F.data.startswith("pay:discount:"))
async def pay_discount_start(call: CallbackQuery, state: FSMContext) -> None:
    code = call.data.rsplit(":", 1)[1]
    await state.update_data(invoice_code=code)
    await call.message.answer("🎟 کد تخفیف خود را ارسال کنید:")
    await state.set_state(StarsFlow.discount)
    await call.answer()


@router.message(StarsFlow.discount)
async def pay_discount_apply(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()
    order = get_order(data.get("invoice_code", ""))
    percent = discount_percent(message.text or "")
    if not order:
        await message.answer("❌ سفارش یافت نشد.")
        return
    if percent is None:
        await message.answer("❌ کد تخفیف معتبر نیست.")
        return
    new_price = order["price"] - int(order["price"] * percent / 100)
    with closing(db()) as conn:
        conn.execute("UPDATE orders SET price=? WHERE code=?",
                     (new_price, order["code"]))
        conn.commit()
    user = get_user(message.from_user.id)
    await message.answer(
        f"✅ کد تخفیف {percent}٪ اعمال شد.\n\n" +
        invoice_text(order["title"], f"👤 گیرنده: {order['recipient'] or '—'}",
                     new_price, user["balance"], order["code"]),
        reply_markup=kb_invoice(order["code"], user["balance"], new_price))


# ---------------------------------------------------------------------------
# Gifts shop
# ---------------------------------------------------------------------------

async def open_gifts(message: Message) -> None:
    await message.answer(GIFTS_INTRO, reply_markup=kb_gifts())


@router.callback_query(F.data == "gift:list")
async def gift_list(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.answer(GIFTS_INTRO, reply_markup=kb_gifts())
    await call.answer()


@router.callback_query(F.data.startswith("gift:open:"))
async def gift_open(call: CallbackQuery) -> None:
    key = call.data.rsplit(":", 1)[1]
    gift = GIFT_BY_KEY.get(key)
    if not gift:
        await call.answer("❌ گیفت یافت نشد.", show_alert=True)
        return
    _, label, stars, price = gift
    await call.message.answer(
        f"{label}\n\n"
        f"⭐ ارزش: {stars} استارز\n"
        f"💰 قیمت: {fmt(price)} تومان\n\n"
        "گیفت با نام شما ارسال شود یا ناشناس؟",
        reply_markup=kb_gift_detail(key))
    await call.answer()


@router.callback_query(F.data.startswith("gift:vis:"))
async def gift_visibility(call: CallbackQuery, state: FSMContext) -> None:
    # gift:vis:<key>:<named|anon> — the original gates the flow on a
    # sender pre-message: the verbatim gate text is shown first.
    parts = call.data.split(":")
    key, vis = parts[2], parts[3]
    gift = GIFT_BY_KEY.get(key)
    if not gift:
        await call.answer("❌ گیفت یافت نشد.", show_alert=True)
        return
    await state.update_data(gift_key=key, gift_vis=vis)
    await call.message.answer(GIFT_SENDER_GATE_TEXT,
                              reply_markup=kb_gift_sender_gate())
    await call.answer()


@router.callback_query(F.data == "gift:gate:send")
async def gift_gate_send(call: CallbackQuery) -> None:
    await call.answer(
        "لطفاً از گیرنده بخواهید ابتدا یک پیام به اکانت فرستنده ارسال کند.",
        show_alert=True)


@router.callback_query(F.data == "gift:gate:sent")
async def gift_gate_sent(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.answer("✍️ حالا پیام همراه گیفت را بنویسید:")
    await state.set_state(GiftFlow.sender_message)
    await call.answer()


@router.callback_query(F.data == "gift:gate:change")
async def gift_gate_change(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.answer(GIFTS_INTRO, reply_markup=kb_gifts())
    await call.answer()


@router.message(GiftFlow.sender_message)
async def gift_sender_message(message: Message, state: FSMContext) -> None:
    if (message.text or "") in MAIN_MENU_BUTTONS:
        await state.clear()
        await route_main_menu(message, state)
        return
    await state.update_data(sender_message=message.text or "")
    await message.answer(
        "👤 آیدی عددی یا یوزرنیم گیرنده گیفت را ارسال کنید:",
        reply_markup=kb_recipient("gift"))
    await state.set_state(GiftFlow.recipient)


@router.callback_query(F.data == "gift:self", GiftFlow.recipient)
async def gift_recipient_self(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()
    gift = GIFT_BY_KEY[data["gift_key"]]
    uname = call.from_user.username
    recipient = f"@{uname}" if uname else str(call.from_user.id)
    vis = "مشخص" if data.get("gift_vis") == "named" else "ناشناس"
    await show_invoice(call.message, call.from_user.id, "gift",
                       f"ارسال گیفت {gift[1]}",
                       f"👤 گیرنده: {recipient}\n🙂 حالت ارسال: {vis}",
                       gift[2], gift[3], recipient)
    await call.answer()


@router.message(GiftFlow.recipient)
async def gift_recipient_text(message: Message, state: FSMContext) -> None:
    recipient = (message.text or "").strip()
    if recipient in MAIN_MENU_BUTTONS:
        await state.clear()
        await route_main_menu(message, state)
        return
    data = await state.get_data()
    await state.clear()
    gift = GIFT_BY_KEY[data["gift_key"]]
    vis = "مشخص" if data.get("gift_vis") == "named" else "ناشناس"
    await show_invoice(message, message.from_user.id, "gift",
                       f"ارسال گیفت {gift[1]}",
                       f"👤 گیرنده: {recipient}\n🙂 حالت ارسال: {vis}",
                       gift[2], gift[3], recipient)


# ---------------------------------------------------------------------------
# Premium shop
# ---------------------------------------------------------------------------

async def open_premium(message: Message) -> None:
    await message.answer(PREMIUM_INTRO, reply_markup=kb_premium())


@router.callback_query(F.data.startswith("premium:plan:"))
async def premium_plan(call: CallbackQuery, state: FSMContext) -> None:
    months = int(call.data.rsplit(":", 1)[1])
    price = setting_int(f"premium_{months}", PREMIUM_PLANS[months])
    await state.update_data(kind="premium", months=months, price=price)
    loading = await call.message.answer(PREMIUM_LOADING)
    await asyncio.sleep(0.5)
    try:
        await loading.delete()
    except TelegramBadRequest:
        pass
    await ask_recipient(
        call.message, state, "premium",
        f"💎 خرید پرمیوم {months} ماهه\n\nگیرنده پرمیوم چه کسی باشد؟\n"
        "می‌توانید دکمه «برای خودم» را بزنید یا آیدی عددی / یوزرنیم گیرنده "
        "را ارسال کنید:")
    await state.set_state(PremiumFlow.recipient)
    await call.answer()


@router.callback_query(F.data == "premium:self", PremiumFlow.recipient)
async def premium_recipient_self(call: CallbackQuery,
                                 state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()
    uname = call.from_user.username
    recipient = f"@{uname}" if uname else str(call.from_user.id)
    await show_invoice(call.message, call.from_user.id, "premium",
                       f"خرید پرمیوم {data['months']} ماهه تلگرام",
                       f"👤 گیرنده: {recipient}", data["months"],
                       data["price"], recipient)
    await call.answer()


@router.message(PremiumFlow.recipient)
async def premium_recipient_text(message: Message,
                                 state: FSMContext) -> None:
    recipient = (message.text or "").strip()
    if recipient in MAIN_MENU_BUTTONS:
        await state.clear()
        await route_main_menu(message, state)
        return
    data = await state.get_data()
    await state.clear()
    await show_invoice(message, message.from_user.id, "premium",
                       f"خرید پرمیوم {data['months']} ماهه تلگرام",
                       f"👤 گیرنده: {recipient}", data["months"],
                       data["price"], recipient)


# ---------------------------------------------------------------------------
# TON / GRAM shop
# ---------------------------------------------------------------------------

async def open_ton(message: Message) -> None:
    await message.answer(TON_INTRO, reply_markup=kb_ton_methods())


@router.callback_query(F.data == "ton:method:wallet")
async def ton_method_wallet(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.answer(TON_WALLET_ADDRESS_PROMPT)
    await state.set_state(TonFlow.wallet_address)
    await call.answer()


@router.message(TonFlow.wallet_address)
async def ton_wallet_address(message: Message, state: FSMContext) -> None:
    address = (message.text or "").strip()
    if address in MAIN_MENU_BUTTONS:
        await state.clear()
        await route_main_menu(message, state)
        return
    if len(address) < 24:
        await message.answer("⚠️ آدرس واردشده معتبر به نظر نمی‌رسد؛ دوباره "
                             "ارسال کنید.")
        return
    await state.update_data(ton_address=address)
    price = setting_int("ton_wallet_price", 328500)
    await message.answer(
        f"💠 هر تون: {fmt(price)} تومان\n\nتعداد تون موردنظرت رو وارد کن "
        "(می‌تونه اعشاری باشه، مثلاً 2.5):")
    await state.set_state(TonFlow.wallet_amount)


@router.message(TonFlow.wallet_amount)
async def ton_wallet_amount(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip().replace(",", ".")
    try:
        amount = float(text)
        assert amount > 0
    except (ValueError, AssertionError):
        await message.answer("⚠️ لطفاً تعداد تون را به‌صورت عدد وارد کنید.")
        return
    data = await state.get_data()
    await state.clear()
    price = int(amount * setting_int("ton_wallet_price", 328500))
    await show_invoice(message, message.from_user.id, "ton",
                       f"خرید {amount} تون (کیف پول شخصی)",
                       f"👛 آدرس کیف پول: {data.get('ton_address', '')}",
                       int(amount * 1000), price,
                       data.get("ton_address", ""))


@router.callback_query(F.data == "ton:method:direct")
async def ton_method_direct(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.answer(TON_DIRECT_INTRO)
    await state.set_state(TonFlow.direct_amount)
    await call.answer()


@router.message(TonFlow.direct_amount)
async def ton_direct_amount(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if not text.isdigit() or int(text) <= 0:
        await message.answer("⚠️ در روش شارژ مستقیم، تعداد تون باید یک عدد "
                             "صحیح باشد (مثلاً 5).")
        return
    await state.update_data(ton_amount=int(text))
    await ask_recipient(
        message, state, "ton",
        f"💠 شارژ مستقیم {text} تون\n\nگیرنده چه کسی باشد؟\n"
        "می‌توانید دکمه «برای خودم» را بزنید یا آیدی عددی / یوزرنیم گیرنده "
        "را ارسال کنید:")
    await state.set_state(TonFlow.recipient)


@router.callback_query(F.data == "ton:self", TonFlow.recipient)
async def ton_recipient_self(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()
    amount = data["ton_amount"]
    price = amount * setting_int("ton_direct_price", 329750)
    uname = call.from_user.username
    recipient = f"@{uname}" if uname else str(call.from_user.id)
    # NOTE: the TON invoice screen was not separately captured in the
    # exploration; it is presumed to reuse the shared invoice template.
    await show_invoice(call.message, call.from_user.id, "ton",
                       f"شارژ مستقیم {amount} تون تلگرام",
                       f"👤 گیرنده: {recipient}", amount * 1000, price,
                       recipient)
    await call.answer()


@router.message(TonFlow.recipient)
async def ton_recipient_text(message: Message, state: FSMContext) -> None:
    recipient = (message.text or "").strip()
    if recipient in MAIN_MENU_BUTTONS:
        await state.clear()
        await route_main_menu(message, state)
        return
    data = await state.get_data()
    await state.clear()
    amount = data["ton_amount"]
    price = amount * setting_int("ton_direct_price", 329750)
    await show_invoice(message, message.from_user.id, "ton",
                       f"شارژ مستقیم {amount} تون تلگرام",
                       f"👤 گیرنده: {recipient}", amount * 1000, price,
                       recipient)


# ---------------------------------------------------------------------------
# Boost shop
# ---------------------------------------------------------------------------

async def open_boost(message: Message) -> None:
    await message.answer(BOOST_INTRO, reply_markup=kb_boost_durations())


@router.callback_query(F.data == "boost:home")
async def boost_home(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.answer(BOOST_INTRO, reply_markup=kb_boost_durations())
    await call.answer()


@router.callback_query(F.data.startswith("boost:days:"))
async def boost_days(call: CallbackQuery) -> None:
    days = int(call.data.rsplit(":", 1)[1])
    await call.message.answer(
        f"🚀 پلن‌های بوست {days} روزه\n\nیک پلن انتخاب کن یا جدول مقایسه "
        "رو ببین:",
        reply_markup=kb_boost_plans(days))
    await call.answer()


@router.callback_query(F.data.startswith("boost:compare:"))
async def boost_compare(call: CallbackQuery) -> None:
    days = int(call.data.rsplit(":", 1)[1])
    await call.message.answer(boost_compare_text(days),
                              reply_markup=kb_boost_plans(days))
    await call.answer()


@router.callback_query(F.data.startswith("boost:plan:"))
async def boost_plan(call: CallbackQuery, state: FSMContext) -> None:
    parts = call.data.split(":")
    days, key = int(parts[2]), parts[3]
    plan = next((p for p in BOOST_PLANS[days] if p["key"] == key), None)
    if not plan or not plan["orderable"]:
        await call.answer("❌ این پلن قابل سفارش نیست.", show_alert=True)
        return
    await state.update_data(boost_days=days, boost_key=key)
    await call.message.answer(
        f"🚀 بوست {days} روزه — {plan['label']}\n"
        f"💰 قیمت هر عدد: {fmt(boost_price(plan))} تومان\n"
        f"🎙 حداقل: {fmt(plan['min'])} عدد | حداکثر: {fmt(plan['max'])} عدد\n"
        f"⏱ میانگین زمان تحویل: {plan.get('avg', plan['time'])}\n"
        f"✨ کیفیت: {plan.get('quality', '')}\n\n"
        "تعداد بوست موردنظرت رو وارد کن:")
    await state.set_state(BoostFlow.quantity)
    await call.answer()


@router.message(BoostFlow.quantity)
async def boost_quantity(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    data = await state.get_data()
    plan = next((p for p in BOOST_PLANS[data["boost_days"]]
                 if p["key"] == data["boost_key"]), None)
    if not text.isdigit():
        await message.answer("⚠️ لطفاً تعداد را به‌صورت عدد وارد کنید.")
        return
    qty = int(text)
    if qty < plan["min"] or qty > plan["max"]:
        await message.answer(
            f"⚠️ تعداد باید بین {plan['min']} تا {plan['max']} باشد.")
        return
    await state.update_data(boost_qty=qty)
    await message.answer("🔗 لینک چنلی که می‌خوای بوست بشه رو ارسال کن "
                         "(مثلاً https://t.me/channel):")
    await state.set_state(BoostFlow.link)


@router.message(BoostFlow.link)
async def boost_link(message: Message, state: FSMContext) -> None:
    link = (message.text or "").strip()
    if link in MAIN_MENU_BUTTONS:
        await state.clear()
        await route_main_menu(message, state)
        return
    data = await state.get_data()
    await state.clear()
    plan = next((p for p in BOOST_PLANS[data["boost_days"]]
                 if p["key"] == data["boost_key"]), None)
    price = boost_price(plan) * data["boost_qty"]
    await show_invoice(
        message, message.from_user.id, "boost",
        f"بوست {data['boost_days']} روزه — پلن {plan['label']} × "
        f"{data['boost_qty']}",
        f"🔗 لینک چنل: {link}\n⏱ زمان تحویل: {plan['time']}",
        data["boost_qty"], price, link)


# ---------------------------------------------------------------------------
# Account / Wallet / Levels / Cards
# ---------------------------------------------------------------------------

def account_text(user: dict) -> str:
    level = user["level"] or 0
    limit = LEVELS.get(max(level, 1), LEVELS[1])[0]
    uname = f"@{user['username']}" if user.get("username") else "—"
    return (
        "👤 حساب کاربری شما\n\n"
        f"🆔 آیدی عددی: {user['user_id']}\n"
        f"👤 یوزرنیم: {uname}\n"
        f"👛 موجودی کیف پول: {fmt(user['balance'])} تومان\n"
        f"🏅 سطح کاربری: سطح {level if level else '— (بدون احراز هویت)'}\n"
        f"📈 سقف افزایش موجودی روزانه: {fmt(limit)} تومان"
    )


async def open_account(message: Message, user_id: int) -> None:
    user = get_user(user_id) or ensure_user(user_id)
    await message.answer(account_text(user), reply_markup=kb_account(user))


@router.callback_query(F.data == "account:home")
async def account_home(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    user = get_user(call.from_user.id) or ensure_user(call.from_user.id)
    await call.message.answer(account_text(user),
                              reply_markup=kb_account(user))
    await call.answer()


@router.callback_query(F.data == "wallet:topup")
async def wallet_topup(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.answer("💰 مبلغ افزایش موجودی رو به تومان وارد کن:")
    await state.set_state(WalletFlow.topup_amount)
    await call.answer()


@router.message(WalletFlow.topup_amount)
async def wallet_topup_amount(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip().replace(",", "")
    if not text.isdigit() or int(text) <= 0:
        await message.answer("⚠️ لطفاً مبلغ را به‌صورت عدد (تومان) وارد "
                             "کنید.")
        return
    await state.update_data(topup_amount=int(text))
    await message.answer(
        f"💰 افزایش موجودی به مبلغ {fmt(int(text))} تومان\n\n"
        "روش شارژ رو انتخاب کن:",
        reply_markup=kb_topup_methods())


@router.callback_query(F.data == "wallet:rial")
async def wallet_rial(call: CallbackQuery) -> None:
    # Rial top-up is blocked until KYC is complete in the original.
    user = get_user(call.from_user.id)
    if not user or (user["level"] or 0) < 1:
        await call.message.answer(KYC_BLOCK_TEXT,
                                  reply_markup=kb_kyc_block())
    else:
        await call.message.answer(
            "💳 شارژ ریالی: رسید پرداخت کارت‌به‌کارت رو برای پشتیبانی ارسال "
            "کنید تا موجودی شما شارژ شود. (درگاه آنلاین: TODO)")
    await call.answer()


@router.callback_query(F.data == "wallet:crypto")
async def wallet_crypto(call: CallbackQuery, state: FSMContext) -> None:
    address = get_setting("ton_wallet_address", "")
    addr_line = f"\n👛 آدرس واریز: {address}" if address else ""
    await call.message.answer(
        "🪙 شارژ با ارز دیجیتال\n\n"
        "مبلغ رو به تون (TON) به آدرس زیر واریز کنید و بعد هش تراکنش رو "
        f"ارسال کنید.{addr_line}")
    await state.set_state(WalletFlow.crypto_hash)
    await call.answer()


@router.message(WalletFlow.crypto_hash)
async def wallet_crypto_hash(message: Message, state: FSMContext) -> None:
    await state.clear()
    # TODO stub: no on-chain verification in the replica.
    await message.answer("✅ هش تراکنش دریافت شد و در صف بررسی قرار گرفت. "
                         "بعد از تأیید، موجودی شما شارژ می‌شود.")


@router.callback_query(F.data == "account:levels")
async def account_levels(call: CallbackQuery) -> None:
    await call.message.answer(ACCOUNT_LEVELS_TEXT, reply_markup=kb_levels())
    await call.answer()


@router.callback_query(F.data == "account:verify1")
async def account_verify1(call: CallbackQuery, state: FSMContext) -> None:
    # Stub only: like the original, Level 1 asks the user to share their
    # phone number. The replica does NOT store or verify real KYC data.
    await call.message.answer(
        "📱 احراز هویت سطح ۱\n\n"
        "برای فعال‌سازی سطح ۱، شماره موبایل خودتون رو با دکمه زیر به "
        "اشتراک بگذارید:")
    await state.set_state(AccountFlow.phone)
    await call.answer()


@router.message(AccountFlow.phone, F.contact)
async def account_phone_shared(message: Message, state: FSMContext) -> None:
    await state.clear()
    # Mark level 1 locally; the shared number itself is never stored.
    with closing(db()) as conn:
        conn.execute("UPDATE users SET level=1 WHERE user_id=? AND level<1",
                     (message.from_user.id,))
        conn.commit()
    await message.answer(
        "✅ شماره شما دریافت شد. سطح کاربری شما به سطح ۱ ارتقا یافت "
        "(سقف شارژ روزانه: ۵۰۰,۰۰۰ تومان).",
        reply_markup=kb_main_reply())


@router.message(AccountFlow.phone)
async def account_phone_text(message: Message, state: FSMContext) -> None:
    await message.answer("⚠️ لطفاً شماره را فقط با دکمه اشتراک‌گذاری "
                         "شماره ارسال کنید.")


@router.callback_query(F.data == "account:cards")
async def account_cards(call: CallbackQuery) -> None:
    await call.message.answer(CARDS_TEXT, reply_markup=kb_back_main())
    await call.answer()


# ---------------------------------------------------------------------------
# My Orders
# ---------------------------------------------------------------------------

async def open_orders(message: Message, user_id: int) -> None:
    orders = user_orders(user_id)
    if not orders:
        await message.answer(ORDERS_EMPTY_TEXT, reply_markup=kb_orders())
        return
    lines = ["🧾 سفارش‌های من\n"]
    for o in orders:
        lines.append(f"🔖 {o['code']} — {o['title']} — {o['status']}")
    await message.answer("\n".join(lines), reply_markup=kb_orders())


@router.callback_query(F.data == "orders:search")
async def orders_search(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.answer("🔍 کد ۸ کاراکتری سفارش رو ارسال کن:")
    await state.set_state(OrdersFlow.search_code)
    await call.answer()


@router.message(OrdersFlow.search_code)
async def orders_search_code(message: Message, state: FSMContext) -> None:
    code = (message.text or "").strip()
    await state.clear()
    order = get_order(code)
    if not order or order["user_id"] != message.from_user.id:
        await message.answer("❌ سفارشی با این کد یافت نشد.")
        return
    await message.answer(
        f"🧾 جزئیات سفارش\n\n"
        f"🔖 کد: {order['code']}\n"
        f"📦 محصول: {order['title']}\n"
        f"💰 مبلغ: {fmt(order['price'])} تومان\n"
        f"📊 وضعیت: {order['status']}")


# ---------------------------------------------------------------------------
# Earn / Referral
# ---------------------------------------------------------------------------

async def open_earn(message: Message, user_id: int, bot: Bot) -> None:
    me = await bot.get_me()
    BOT_USERNAME_CACHE["username"] = me.username or ""
    markup, link = kb_earn(user_id, me.username or "")
    await message.answer(
        EARN_INTRO + f"\n\n🔗 لینک دعوت شما:\n{link}", reply_markup=markup)


@router.callback_query(F.data == "earn:link")
async def earn_link(call: CallbackQuery, bot: Bot) -> None:
    me = await bot.get_me()
    link = f"https://t.me/{me.username}?start=ref_{call.from_user.id}"
    await call.message.answer(f"🔗 لینک دعوت شما:\n{link}")
    await call.answer()


@router.callback_query(F.data == "earn:withdraw")
async def earn_withdraw(call: CallbackQuery) -> None:
    # Commission lands directly in the wallet balance in this replica,
    # so withdrawing is a no-op information screen.
    user = get_user(call.from_user.id)
    bal = user["balance"] if user else 0
    await call.message.answer(
        "💸 کمیسیون‌های شما به‌صورت خودکار به موجودی کیف پول‌تان اضافه "
        f"می‌شود.\n👛 موجودی فعلی: {fmt(bal)} تومان")
    await call.answer()


# ---------------------------------------------------------------------------
# Support (Nexy AI stub + direct message)
# ---------------------------------------------------------------------------

def nexy_reply(text: str) -> str:
    """STUB: the original «Nexy» is a real AI assistant. This replica
    ships a tiny FAQ responder; at minimum it answers the Stars price
    from live settings."""
    t = (text or "").lower()
    if any(w in t for w in ("استارز", "stars", "قیمت")):
        return (f"⭐ قیمت فعلی هر استارز {fmt(setting_int('price_per_star', 4512))} "
                f"تومان است و پک ۵۰ استارزی {fmt(setting_int('stars_price_50', 225500))} "
                "تومان. از دکمه «خرید استارز» در منوی اصلی می‌تونید سفارش بدید.")
    if any(w in t for w in ("پرمیوم", "premium")):
        return ("💎 پلن‌های پرمیوم: ۳ ماهه "
                f"{fmt(setting_int('premium_3', PREMIUM_PLANS[3]))}، ۶ ماهه "
                f"{fmt(setting_int('premium_6', PREMIUM_PLANS[6]))} و ۱۲ ماهه "
                f"{fmt(setting_int('premium_12', PREMIUM_PLANS[12]))} تومان.")
    if any(w in t for w in ("تون", "ton", "گرام", "gram")):
        return (f"💠 قیمت هر تون با روش کیف پول شخصی "
                f"{fmt(setting_int('ton_wallet_price', 328500))} تومان و با "
                f"شارژ مستقیم {fmt(setting_int('ton_direct_price', 329750))} تومان است.")
    if any(w in t for w in ("سفارش", "پیگیری", "order")):
        return "🧾 برای پیگیری سفارش از بخش «سفارش‌های من» و کد ۸ کاراکتری سفارش استفاده کنید."
    return ("🤖 من «نکسی» هستم، دستیار هوشمند نکس‌استارز. درباره قیمت "
            "استارز، پرمیوم، تون و پیگیری سفارش می‌تونم کمکتون کنم؛ برای "
            "موارد دیگه از «ارسال پیام مستقیم به پشتیبانی» استفاده کنید.")


async def open_support(message: Message) -> None:
    await message.answer(SUPPORT_INTRO, reply_markup=kb_support())


@router.callback_query(F.data == "support:nexy")
async def support_nexy(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.answer(
        "🤖 سلام! من «نکسی» هستم. سوالت رو بپرس:",
        reply_markup=kb_cancel_support())
    await state.set_state(SupportFlow.nexy)
    await call.answer()


@router.message(SupportFlow.nexy)
async def support_nexy_msg(message: Message, state: FSMContext) -> None:
    if (message.text or "") in MAIN_MENU_BUTTONS:
        await state.clear()
        await route_main_menu(message, state)
        return
    await message.answer(nexy_reply(message.text or ""),
                         reply_markup=kb_cancel_support())


@router.callback_query(F.data == "support:direct")
async def support_direct(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.answer(
        "✉️ پیام‌ت رو بنویس تا مستقیم برای تیم پشتیبانی ارسال بشه:",
        reply_markup=kb_cancel_support())
    await state.set_state(SupportFlow.direct)
    await call.answer()


@router.message(SupportFlow.direct)
async def support_direct_msg(message: Message, state: FSMContext,
                             bot: Bot) -> None:
    if (message.text or "") in MAIN_MENU_BUTTONS:
        await state.clear()
        await route_main_menu(message, state)
        return
    await state.clear()
    with closing(db()) as conn:
        conn.execute(
            "INSERT INTO tickets(user_id,text,created_at) VALUES(?,?,?)",
            (message.from_user.id, message.text or "", int(time.time())))
        conn.commit()
    # Forwarding stub: notify admins (original forwards to its support team).
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                f"✉️ پیام پشتیبانی جدید از {message.from_user.id} "
                f"(@{message.from_user.username or '—'}):\n\n{message.text}")
        except Exception:
            pass
    await message.answer("✅ پیام شما برای پشتیبانی ارسال شد. به‌زودی پاسخ "
                         "می‌گیرید.")


@router.callback_query(F.data == "support:cancel")
async def support_cancel(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.answer(SUPPORT_INTRO, reply_markup=kb_support())
    await call.answer("لغو شد.")


# ---------------------------------------------------------------------------
# Games centre
# ---------------------------------------------------------------------------

async def open_games(message: Message) -> None:
    await message.answer(GAMES_TEXT, reply_markup=kb_games())


@router.callback_query(F.data == "game:home")
async def game_home(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.answer(GAMES_TEXT, reply_markup=kb_games())
    await call.answer()


@router.callback_query(F.data == "game:addgroup")
async def game_addgroup(call: CallbackQuery, bot: Bot) -> None:
    me = await bot.get_me()
    await call.answer(
        f"برای افزودن ربات به گروه، از لینک زیر استفاده کنید:\n"
        f"https://t.me/{me.username}?startgroup=true", show_alert=True)


@router.callback_query(F.data.startswith("game:open:"))
async def game_open(call: CallbackQuery) -> None:
    key = call.data.rsplit(":", 1)[1]
    label = GAME_BY_KEY.get(key, "بازی")
    await call.message.answer(
        f"{label}\n\nحالت بازی رو انتخاب کن:",
        reply_markup=kb_game_modes(key))
    await call.answer()


@router.callback_query(F.data.startswith("game:mode:"))
async def game_mode(call: CallbackQuery, state: FSMContext) -> None:
    # game:mode:<key>:<friendly|competitive>
    # Fully implemented for دوز (doz) friendly creation as reported;
    # the other games share this mode-choice stub (marked as such).
    parts = call.data.split(":")
    key, mode = parts[2], parts[3]
    label = GAME_BY_KEY.get(key, "بازی")
    if mode == "competitive":
        await call.answer("🏆 بازی‌های رقابتی به‌زودی فعال می‌شوند.",
                          show_alert=True)
        return
    await state.update_data(game_key=key)
    await call.message.answer(
        f"✅ بازی دوستانه «{label}» ساخته شد!\n\n"
        "لینک دعوت بازی برای شما ساخته شد؛ اون رو برای دوستت بفرست تا "
        "به بازی ملحق بشه. 🎉",
        reply_markup=kb_game_created())
    await call.answer()


@router.callback_query(F.data == "game:cancel")
async def game_cancel(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.answer("❌ بازی لغو شد.", reply_markup=kb_games())
    await call.answer()


# ---------------------------------------------------------------------------
# NFT market (Web App placeholder — the market itself is a Telegram
# Web App in the original and is not replicated as bot screens)
# ---------------------------------------------------------------------------

async def open_nft(message: Message, bot: Bot) -> None:
    me = await bot.get_me()
    from aiogram.types import InlineKeyboardMarkup as _IKM  # local alias
    url = get_setting("nft_webapp_url", "https://nexstarz.example/nft")
    await message.answer(
        "🖼 بازار NFT نکس‌استارز در قالب وب‌اپ باز می‌شود. دکمه «بازار NFT» "
        "در منوی اصلی را با آدرس وب‌اپ واقعی خودتان در تنظیمات ادمین "
        "جایگزین کنید.",
        reply_markup=kb_back_main())


# ---------------------------------------------------------------------------
# Main reply-keyboard routing
# ---------------------------------------------------------------------------

async def route_main_menu(message: Message, state: FSMContext,
                          bot: Bot = None) -> None:
    text = message.text or ""
    user_id = message.from_user.id
    ensure_user(user_id, message.from_user.username or "",
                message.from_user.full_name or "")
    user = get_user(user_id)
    if user and user["banned"]:
        await message.answer("⛔ حساب شما مسدود شده است.")
        return
    if bot is not None and not await gate_passed(bot, user_id):
        await send_gate(message)
        return
    if text == BTN_STARS:
        await open_stars(message)
    elif text == BTN_GIFT:
        await open_gifts(message)
    elif text == BTN_PREMIUM:
        await open_premium(message)
    elif text == BTN_TON:
        await open_ton(message)
    elif text == BTN_BOOST:
        await open_boost(message)
    elif text == BTN_NFT:
        if bot is not None:
            await open_nft(message, bot)
    elif text == BTN_ACCOUNT:
        await open_account(message, user_id)
    elif text == BTN_ORDERS:
        await open_orders(message, user_id)
    elif text == BTN_EARN:
        if bot is not None:
            await open_earn(message, user_id, bot)
    elif text == BTN_SUPPORT:
        await open_support(message)
    elif text == BTN_GAMES:
        await open_games(message)


@router.message(F.text.in_(MAIN_MENU_BUTTONS), StateFilter(None))
async def main_menu_buttons(message: Message, state: FSMContext,
                            bot: Bot) -> None:
    await route_main_menu(message, state, bot)


# ---------------------------------------------------------------------------
# Admin panel
# ---------------------------------------------------------------------------

SETTING_LABELS = {
    "gate_enabled": "گیت عضویت اجباری (1/0)",
    "gate_channels": "کانال‌های گیت (با کاما)",
    "price_per_star": "قیمت هر استارز (تومان)",
    "stars_price_50": "قیمت پک ۵۰ استارزی (تومان)",
    "premium_3": "پرمیوم ۳ ماهه (تومان)",
    "premium_6": "پرمیوم ۶ ماهه (تومان)",
    "premium_12": "پرمیوم ۱۲ ماهه (تومان)",
    "ton_wallet_price": "قیمت تون — روش کیف پول (تومان)",
    "ton_direct_price": "قیمت تون — شارژ مستقیم (تومان)",
    "ton_wallet_address": "آدرس کیف پول تون",
    "boost_prices": "قیمت‌های بوست (JSON)",
    "referral_percent": "درصد کمیسیون رفرال",
    "support_username": "یوزرنیم پشتیبانی",
    "nft_webapp_url": "آدرس وب‌اپ بازار NFT",
    "referrals_webapp_url": "آدرس وب‌اپ زیرمجموعه‌ها",
    "games_group_link": "لینک افزودن به گروه (بازی‌ها)",
}


def kb_admin_home():
    return ikb([
        [btn("📊 آمار", callback_data="admin:stats", style=STYLE_PRIMARY)],
        [btn("⚙️ تنظیمات", callback_data="admin:settings",
             style=STYLE_PRIMARY)],
        [btn("👥 کاربران", callback_data="admin:users:0",
             style=STYLE_SUCCESS),
         btn("🎟 کدهای تخفیف", callback_data="admin:discounts",
             style=STYLE_SUCCESS)],
        [btn("📣 ارسال همگانی", callback_data="admin:broadcast",
             style=STYLE_SUCCESS)],
        [btn("🏠 منوی اصلی", callback_data="nav:main", style=STYLE_DANGER)],
    ])


def kb_admin_settings():
    rows = []
    for key, label in SETTING_LABELS.items():
        rows.append([btn(f"{label}: {get_setting(key, '')[:28]}",
                         callback_data=f"admin:set:{key}",
                         style=STYLE_PRIMARY)])
    rows.append([btn("🔙 بازگشت", callback_data="admin:home",
                     style=STYLE_DANGER)])
    return ikb(rows)


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    await message.answer("🛠 پنل مدیریت نکس‌استارز",
                         reply_markup=kb_admin_home())


@router.callback_query(F.data == "admin:home")
async def admin_home(call: CallbackQuery, state: FSMContext) -> None:
    if not is_admin(call.from_user.id):
        await call.answer("⛔", show_alert=True)
        return
    await state.clear()
    await call.message.answer("🛠 پنل مدیریت نکس‌استارز",
                              reply_markup=kb_admin_home())
    await call.answer()


@router.callback_query(F.data == "admin:stats")
async def admin_stats(call: CallbackQuery) -> None:
    if not is_admin(call.from_user.id):
        await call.answer("⛔", show_alert=True)
        return
    with closing(db()) as conn:
        users = conn.execute("SELECT COUNT(*) c FROM users").fetchone()["c"]
        orders = conn.execute("SELECT COUNT(*) c FROM orders").fetchone()["c"]
        delivered = conn.execute(
            "SELECT COUNT(*) c FROM orders WHERE status='delivered'"
        ).fetchone()["c"]
        revenue = conn.execute(
            "SELECT COALESCE(SUM(price),0) s FROM orders "
            "WHERE status='delivered'").fetchone()["s"]
        tickets = conn.execute("SELECT COUNT(*) c FROM tickets").fetchone()["c"]
    await call.message.answer(
        f"📊 آمار ربات\n\n👥 کاربران: {users}\n🧾 سفارش‌ها: {orders}\n"
        f"✅ تحویل‌شده: {delivered}\n💰 درآمد (تحویل‌شده): {fmt(revenue)} "
        f"تومان\n✉️ تیکت‌ها: {tickets}",
        reply_markup=kb_admin_home())
    await call.answer()


@router.callback_query(F.data == "admin:settings")
async def admin_settings(call: CallbackQuery) -> None:
    if not is_admin(call.from_user.id):
        await call.answer("⛔", show_alert=True)
        return
    await call.message.answer("⚙️ تنظیمات — برای ویرایش روی هر مورد بزنید:",
                              reply_markup=kb_admin_settings())
    await call.answer()


@router.callback_query(F.data.startswith("admin:set:"))
async def admin_set_start(call: CallbackQuery, state: FSMContext) -> None:
    if not is_admin(call.from_user.id):
        await call.answer("⛔", show_alert=True)
        return
    key = call.data.split(":", 2)[2]
    await state.update_data(setting_key=key)
    await call.message.answer(
        f"⚙️ {SETTING_LABELS.get(key, key)}\nمقدار فعلی: "
        f"{get_setting(key, '')}\n\nمقدار جدید را ارسال کنید:")
    await state.set_state(AdminFlow.set_setting)
    await call.answer()


@router.message(AdminFlow.set_setting)
async def admin_set_value(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    data = await state.get_data()
    await state.clear()
    key = data["setting_key"]
    if key == "boost_prices":
        try:
            json.loads(message.text or "{}")
        except json.JSONDecodeError:
            await message.answer("❌ JSON معتبر نیست؛ دوباره تلاش کنید.")
            return
    set_setting(key, (message.text or "").strip())
    await message.answer(f"✅ تنظیم «{SETTING_LABELS.get(key, key)}» ذخیره شد.",
                         reply_markup=kb_admin_settings())


@router.callback_query(F.data.startswith("admin:users:"))
async def admin_users(call: CallbackQuery) -> None:
    if not is_admin(call.from_user.id):
        await call.answer("⛔", show_alert=True)
        return
    page = int(call.data.rsplit(":", 1)[1])
    with closing(db()) as conn:
        rows = conn.execute(
            "SELECT * FROM users ORDER BY joined_at DESC LIMIT 10 OFFSET ?",
            (page * 10,)).fetchall()
    if not rows:
        await call.message.answer("کاربر دیگری نیست.",
                                  reply_markup=kb_admin_home())
        await call.answer()
        return
    kb_rows = []
    for r in rows:
        kb_rows.append([btn(
            f"{r['user_id']} — @{r['username'] or '—'} — "
            f"{fmt(r['balance'])} تومان" + (" ⛔" if r["banned"] else ""),
            callback_data=f"admin:user:{r['user_id']}", style=STYLE_PRIMARY)])
    nav = []
    if page > 0:
        nav.append(btn("⬅️ قبلی", callback_data=f"admin:users:{page-1}",
                       style=STYLE_SUCCESS))
    nav.append(btn("➡️ بعدی", callback_data=f"admin:users:{page+1}",
                   style=STYLE_SUCCESS))
    kb_rows.append(nav)
    kb_rows.append([btn("🔙 بازگشت", callback_data="admin:home",
                        style=STYLE_DANGER)])
    await call.message.answer("👥 کاربران (جدیدترین‌ها):",
                              reply_markup=ikb(kb_rows))
    await call.answer()


@router.callback_query(F.data.startswith("admin:user:"))
async def admin_user_detail(call: CallbackQuery, state: FSMContext) -> None:
    if not is_admin(call.from_user.id):
        await call.answer("⛔", show_alert=True)
        return
    uid = int(call.data.rsplit(":", 1)[1])
    user = get_user(uid)
    if not user:
        await call.answer("یافت نشد.", show_alert=True)
        return
    await state.update_data(target_user=uid)
    kb = ikb([
        [btn("💰 تغییر موجودی", callback_data="admin:adjbal",
             style=STYLE_SUCCESS),
         btn("⛔ بن / آنبن" if not user["banned"] else "✅ آنبن",
             callback_data="admin:ban", style=STYLE_DANGER)],
        [btn("🔙 بازگشت", callback_data="admin:users:0",
             style=STYLE_DANGER)],
    ])
    await call.message.answer(
        f"👤 کاربر {uid}\nیوزرنیم: @{user['username'] or '—'}\n"
        f"موجودی: {fmt(user['balance'])} تومان\nسطح: {user['level']}\n"
        f"وضعیت: {'مسدود ⛔' if user['banned'] else 'فعال ✅'}",
        reply_markup=kb)
    await call.answer()


@router.callback_query(F.data == "admin:ban")
async def admin_ban(call: CallbackQuery, state: FSMContext) -> None:
    if not is_admin(call.from_user.id):
        await call.answer("⛔", show_alert=True)
        return
    data = await state.get_data()
    uid = data.get("target_user")
    if uid:
        with closing(db()) as conn:
            conn.execute(
                "UPDATE users SET banned=1-banned WHERE user_id=?", (uid,))
            conn.commit()
        await call.message.answer(f"✅ وضعیت بن کاربر {uid} تغییر کرد.",
                                  reply_markup=kb_admin_home())
    await call.answer()


@router.callback_query(F.data == "admin:adjbal")
async def admin_adjbal_start(call: CallbackQuery, state: FSMContext) -> None:
    if not is_admin(call.from_user.id):
        await call.answer("⛔", show_alert=True)
        return
    await call.message.answer("💰 مبلغ تغییر موجودی را ارسال کنید (عدد "
                              "منفی برای کسر):")
    await state.set_state(AdminFlow.balance_adjust)
    await call.answer()


@router.message(AdminFlow.balance_adjust)
async def admin_adjbal_value(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    data = await state.get_data()
    await state.clear()
    try:
        delta = int((message.text or "").strip().replace(",", ""))
    except ValueError:
        await message.answer("❌ مبلغ معتبر نیست.")
        return
    new_bal = change_balance(data["target_user"], delta)
    await message.answer(f"✅ موجودی جدید کاربر: {fmt(new_bal)} تومان",
                         reply_markup=kb_admin_home())


@router.callback_query(F.data == "admin:discounts")
async def admin_discounts(call: CallbackQuery) -> None:
    if not is_admin(call.from_user.id):
        await call.answer("⛔", show_alert=True)
        return
    with closing(db()) as conn:
        rows = conn.execute("SELECT * FROM discount_codes").fetchall()
    lines = ["🎟 کدهای تخفیف\n"]
    kb_rows = []
    for r in rows:
        lines.append(f"• {r['code']} — {r['percent']}٪ "
                     f"({'فعال' if r['active'] else 'غیرفعال'})")
        kb_rows.append([btn(f"🗑 حذف {r['code']}",
                            callback_data=f"admin:discdel:{r['code']}",
                            style=STYLE_DANGER)])
    kb_rows.append([btn("➕ افزودن کد", callback_data="admin:discadd",
                        style=STYLE_SUCCESS)])
    kb_rows.append([btn("🔙 بازگشت", callback_data="admin:home",
                        style=STYLE_DANGER)])
    await call.message.answer("\n".join(lines), reply_markup=ikb(kb_rows))
    await call.answer()


@router.callback_query(F.data == "admin:discadd")
async def admin_discadd_start(call: CallbackQuery, state: FSMContext) -> None:
    if not is_admin(call.from_user.id):
        await call.answer("⛔", show_alert=True)
        return
    await call.message.answer("🎟 کد و درصد را با فرمت «CODE:10» ارسال "
                              "کنید:")
    await state.set_state(AdminFlow.add_discount)
    await call.answer()


@router.message(AdminFlow.add_discount)
async def admin_discadd_value(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    await state.clear()
    try:
        code, percent = (message.text or "").rsplit(":", 1)
        percent = int(percent)
        assert code.strip() and 1 <= percent <= 90
    except (ValueError, AssertionError):
        await message.answer("❌ فرمت اشتباه است. مثال: WELCOME:10")
        return
    with closing(db()) as conn:
        conn.execute(
            "INSERT INTO discount_codes(code,percent,active) VALUES(?,?,1) "
            "ON CONFLICT(code) DO UPDATE SET percent=excluded.percent, "
            "active=1", (code.strip(), percent))
        conn.commit()
    await message.answer("✅ کد تخفیف ذخیره شد.",
                         reply_markup=kb_admin_home())


@router.callback_query(F.data.startswith("admin:discdel:"))
async def admin_discdel(call: CallbackQuery) -> None:
    if not is_admin(call.from_user.id):
        await call.answer("⛔", show_alert=True)
        return
    code = call.data.split(":", 2)[2]
    with closing(db()) as conn:
        conn.execute("DELETE FROM discount_codes WHERE code=?", (code,))
        conn.commit()
    await call.message.answer("🗑 کد حذف شد.", reply_markup=kb_admin_home())
    await call.answer()


@router.callback_query(F.data == "admin:broadcast")
async def admin_broadcast_start(call: CallbackQuery,
                                state: FSMContext) -> None:
    if not is_admin(call.from_user.id):
        await call.answer("⛔", show_alert=True)
        return
    await call.message.answer("📣 متن پیام همگانی را ارسال کنید:")
    await state.set_state(AdminFlow.broadcast_text)
    await call.answer()


@router.message(AdminFlow.broadcast_text)
async def admin_broadcast_send(message: Message, state: FSMContext,
                               bot: Bot) -> None:
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    await state.clear()
    with closing(db()) as conn:
        rows = conn.execute(
            "SELECT user_id FROM users WHERE banned=0").fetchall()
    ok = fail = 0
    for r in rows:
        try:
            await bot.send_message(r["user_id"], message.text or "")
            ok += 1
        except Exception:
            fail += 1
        await asyncio.sleep(0.05)
    await message.answer(f"📣 ارسال همگانی تمام شد.\n✅ موفق: {ok}\n"
                         f"❌ ناموفق: {fail}", reply_markup=kb_admin_home())


# ---------------------------------------------------------------------------
# Fallback: unknown text while idle -> gentle hint
# ---------------------------------------------------------------------------

@router.message(StateFilter(None))
async def fallback_text(message: Message) -> None:
    await message.answer("از منوی پایین یکی از گزینه‌ها رو انتخاب کن 👇",
                         reply_markup=kb_main_reply())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main() -> None:
    if not BOT_TOKEN:
        raise SystemExit("BOT_TOKEN is not set (see .env.example)")
    init_db()
    bot = Bot(BOT_TOKEN, default=None)
    # aiogram 3.7+: set parse mode via DefaultBotProperties when available.
    try:
        from aiogram.client.default import DefaultBotProperties
        bot = Bot(BOT_TOKEN,
                  default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    except Exception:
        bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    # The original bot lists only /start as its command.
    try:
        from aiogram.types import BotCommand
        await bot.set_my_commands([BotCommand(command="start",
                                              description="شروع")])
    except Exception as exc:
        log.warning("set_my_commands failed: %s", exc)
    log.info("NexStarz replica polling started (admins: %s)", ADMIN_IDS)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
