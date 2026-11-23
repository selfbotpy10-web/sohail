# -*- coding: utf-8 -*-
"""Keyboard smoke test for the NexStarz replica.

Imports bot.py with a dummy BOT_TOKEN and a throwaway SQLite DB, then
asserts every keyboard builder returns markup whose buttons carry the
expected Bot API styles (success=green, primary=blue, danger=brown-ish)
and labels from the exploration report.

Run:  BOT_TOKEN=dummy DB_PATH=/tmp/nexstarz_smoke.db python smoke_test.py
"""
import os
import sys

os.environ.setdefault("BOT_TOKEN", "123456:dummy")
os.environ.setdefault("DB_PATH", "/tmp/nexstarz_smoke.db")
if os.path.exists("/tmp/nexstarz_smoke.db"):
    os.remove("/tmp/nexstarz_smoke.db")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bot as B  # noqa: E402

B.init_db()

PASS = 0
FAIL = 0
FAILURES = []


def check(name, cond, extra=""):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        FAILURES.append(f"{name} {extra}")


def styles_of(markup, kind="inline"):
    rows = markup.inline_keyboard if kind == "inline" else markup.keyboard
    out = []
    for row in rows:
        out.append([(b.text, getattr(b, "style", None)) for b in row])
    return out


def flat(markup, kind="inline"):
    return [b for row in styles_of(markup, kind) for b in row]


# --- CUSTOM_EMOJI_IDS ships empty -------------------------------------------
check("custom_emoji_ids_empty", B.CUSTOM_EMOJI_IDS == {})

# --- Main reply keyboard: 7 rows, exact colours ------------------------------
mk = B.kb_main_reply()
rows = styles_of(mk, "reply")
check("main_rows_7", len(rows) == 7, f"got {len(rows)}")
check("main_r1_green", all(s == "success" for _, s in rows[0]) and len(rows[0]) == 2)
check("main_r2_blue", all(s == "primary" for _, s in rows[1]) and len(rows[1]) == 2)
check("main_r3_green_full", rows[2][0][1] == "success" and len(rows[2]) == 1)
check("main_r4_blue_webapp", rows[3][0][1] == "primary" and len(rows[3]) == 1)
check("main_r5_green", all(s == "success" for _, s in rows[4]) and len(rows[4]) == 2)
check("main_r6_green", all(s == "success" for _, s in rows[5]) and len(rows[5]) == 2)
check("main_r7_blue_full", rows[6][0][1] == "primary" and len(rows[6]) == 1)
labels = [t for row in rows for t, _ in row]
check("main_labels_tatweel", B.BTN_STARS in labels and B.BTN_GAMES in labels
      and "ـ" in B.BTN_STARS)

# --- Gate ---------------------------------------------------------------------
g = flat(B.kb_gate())
check("gate_channels_2_blue", sum(1 for _, s in g if s == "primary") == 2,
      str(g))
check("gate_check_green", any("بررسی عضویت" in t and s == "success"
                              for t, s in g))

# --- Stars --------------------------------------------------------------------
s = flat(B.kb_stars())
check("stars_packs_green", sum(1 for t, st in s if "استارز" in t
                               and st == "success") == 4, str(s))
check("stars_custom_blue", any("مقدار دلخواه" in t and st == "primary"
                               for t, st in s))
check("stars_price_50", B.stars_price(50) == 225500)
check("stars_price_per", B.stars_price(100) == 100 * 4512)

inv = flat(B.kb_invoice("TESTCODE", balance=0, price=1000))
check("invoice_nobalance_brown", any("کافی نیست" in t and st == "danger"
                                     for t, st in inv))
check("invoice_online_green", any("پرداخت آنلاین" in t and st == "success"
                                  for t, st in inv))
check("invoice_discount_green", any("کد تخفیف" in t and st == "success"
                                    for t, st in inv))
check("invoice_main_brown", any("منوی اصلی" in t and st == "danger"
                                for t, st in inv))
inv2 = flat(B.kb_invoice("TESTCODE", balance=999999, price=1000))
check("invoice_wallet_green", any("کیف پول" in t and st == "success"
                                  for t, st in inv2))

# --- Gifts --------------------------------------------------------------------
gf = flat(B.kb_gifts())
check("gifts_11", sum(1 for t, _ in gf if "⭐" in t) == 11, str(len(gf)))
check("gifts_all_green", all(st == "success" for t, st in gf if "⭐" in t))
check("gifts_main_brown", any("منوی اصلی" in t and st == "danger"
                              for t, st in gf))
gd = flat(B.kb_gift_detail("heart"))
check("gift_vis_green", sum(1 for _, st in gd if st == "success") >= 2)
check("gifts_exact", B.GIFTS == [
    ("heart", "💗 قلب", 15, 68000),
    ("bear", "🧸 تدی", 15, 69000),
    ("giftbox", "🎁 کادو", 25, 114000),
    ("rose", "🌹 گل رز", 25, 114000),
    ("cake", "🎂 کیک", 50, 229000),
    ("bouquet", "💐 گل", 50, 229000),
    ("rocket", "🚀 سفینه", 50, 229000),
    ("trophy", "🏆 جام", 100, 458000),
    ("ring", "💍 حلقه", 100, 458000),
    ("bottle", "🍾 بطری", 50, 229000),
    ("diamond", "💎 الماس", 100, 458000),
], str(B.GIFTS))
grow = styles_of(B.kb_gifts())
check("gifts_rows", len(grow) == 7 and len(grow[5]) == 1
      and len(grow[6]) == 1 and grow[6][0][1] == "danger", str(grow))
check("welcome_exact", B.WELCOME_TEXT == (
    "سلام! اینجا نِکستارزه، سریعترین و مطمئنترین برای خرید:\n"
    "⭐️ استارز تلگرام\n"
    "✅ تلگرام پرمیوم\n"
    "🪙 ارز تونکوین\n"
    "🎁 گیفتهای تلگرامی\n"
    "⚡ بوست کانال\n"
    "رفیق، سفارشت کاملاً خودکار و در سریعترین زمان ممکن انجام میشه. خیالت راحت!\n"
    "👇 لطفاً برای شروع، از منوی زیر استفاده کنید: 🎉"))
check("gift_gate_text", B.GIFT_SENDER_GATE_TEXT.startswith(
    "❗️ عدم ثبت پیام گیرنده به اکانت فرستنده!")
    and "هنوز به اکانت فرستنده پیامی ارسال نکرده است" in B.GIFT_SENDER_GATE_TEXT
    and "💡" in B.GIFT_SENDER_GATE_TEXT)
gatekb = flat(B.kb_gift_sender_gate())
check("gift_gate_buttons", gatekb == [
    ("ارسال پیام به فرستنده", "primary"),
    ("پیام ارسال شد", "success"),
    ("تغییر گیرنده", "success"),
    ("منوی اصلی", "danger"),
], str(gatekb))
check("kyc_exact", B.KYC_BLOCK_TEXT == (
    "❗️ محدودیت خرید ریالی (نیاز به احراز هویت)\n"
    "کاربر گرامی، در حال حاضر خرید یا شارژ ریالی برای حساب شما غیرفعال است.\n"
    "لطفاً جهت فعالسازی و افزایش سقف تراکنشهای خود، شماره همراه خود را تایید کرده و به سطح 1 ارتقا یابید"))
check("kyc_button_blue", flat(B.kb_kyc_block()) == [
    ("ارتقای سطح و احراز هویت", "primary")])

# --- Premium ------------------------------------------------------------------
pm = flat(B.kb_premium())
check("premium_3_green", len([1 for _, st in pm if st == "success"]) == 3)
check("premium_prices", B.PREMIUM_PLANS == {3: 3555500, 6: 4740500,
                                            12: 8596000})

# --- TON ----------------------------------------------------------------------
tn = flat(B.kb_ton_methods())
check("ton_2_green", sum(1 for _, st in tn if st == "success") == 2)
check("ton_prices", B.setting_int("ton_wallet_price") == 328500
      and B.setting_int("ton_direct_price") == 329750)

# --- Boost --------------------------------------------------------------------
bd = flat(B.kb_boost_durations())
check("boost_durations_blue", all(st == "primary" for _, st in bd[:2]))
for days in (7, 30):
    bp = flat(B.kb_boost_plans(days))
    check(f"boost_plans_{days}", len(bp) >= 4)
    check(f"boost_compare_text_{days}", "مقایسه" in B.boost_compare_text(days))
check("boost_sav30_not_orderable",
      [p for p in B.BOOST_PLANS[30] if p["key"] == "sav30"][0]["orderable"]
      is False)
def _plan(days, key):
    return [p for p in B.BOOST_PLANS[days] if p["key"] == key][0]
check("boost_7_speed", (_plan(7, "speed7")["price"],
      _plan(7, "speed7")["min"], _plan(7, "speed7")["max"],
      _plan(7, "speed7")["avg"], _plan(7, "speed7")["quality"],
      _plan(7, "speed7")["label"]) == (26000, 1, 100000, "1 ساعت",
                                       "معمولی", "پلن سرعتی"))
check("boost_7_vip", (_plan(7, "vip7")["price"],
      _plan(7, "vip7")["min"], _plan(7, "vip7")["max"],
      _plan(7, "vip7")["avg"], _plan(7, "vip7")["quality"],
      _plan(7, "vip7")["label"]) == (14300, 2, 100000, "24 ساعت",
                                     "عالی - تضمینی", "پلن ویژه"))
check("boost_30_speed", (_plan(30, "speed30")["price"],
      _plan(30, "speed30")["min"], _plan(30, "speed30")["max"],
      _plan(30, "speed30")["avg"], _plan(30, "speed30")["quality"])
      == (79900, 1, 100000, "30 دقیقه", "معمولی"))
check("boost_30_vip", (_plan(30, "vip30")["price"],
      _plan(30, "vip30")["min"], _plan(30, "vip30")["max"],
      _plan(30, "vip30")["avg"], _plan(30, "vip30")["quality"])
      == (55500, 2, 100000, "18 ساعت", "بهترین - تضمینی"))
check("boost_30_sav_speed", (_plan(30, "sav_speed30")["price"],
      _plan(30, "sav_speed30")["min"], _plan(30, "sav_speed30")["max"],
      _plan(30, "sav_speed30")["avg"], _plan(30, "sav_speed30")["quality"],
      _plan(30, "sav_speed30")["label"])
      == (47300, 10, 100000, "1 ساعت", "معمولی", "پلن به‌صرفه - سرعتی"))
check("boost_30_sav_compare_only", (_plan(30, "sav30")["price"],
      _plan(30, "sav30")["min"], _plan(30, "sav30")["avg"],
      _plan(30, "sav30")["quality"])
      == (None, 10, "3 ساعت", "معمولی"))
check("boost_plans_all_green", all(
    st == "success" for days in (7, 30)
    for t, st in flat(B.kb_boost_plans(days))
    if t.startswith("پلن")))
check("boost_compare_blue_back_brown", all(
    any(t == "مقایسه پلنها" and st == "primary"
        for t, st in flat(B.kb_boost_plans(days)))
    and any(t == "بازگشت" and st == "danger"
            for t, st in flat(B.kb_boost_plans(days)))
    for days in (7, 30)))
check("boost_30_layout", [len(r) for r in styles_of(B.kb_boost_plans(30))]
      == [2, 1, 1, 1], str(styles_of(B.kb_boost_plans(30))))
check("boost_compare_values", "26,000" in B.boost_compare_text(7)
      and "100,000" in B.boost_compare_text(7)
      and "عالی - تضمینی" in B.boost_compare_text(7)
      and "بهترین - تضمینی" in B.boost_compare_text(30)
      and "47,300" in B.boost_compare_text(30))

# --- Account / orders / earn / support / games --------------------------------
ac = flat(B.kb_account({"user_id": 1, "username": "x", "balance": 0,
                        "level": 0}))
check("account_kb", len(ac) >= 3)
od = flat(B.kb_orders())
check("orders_search_blue", any(st == "primary" for _, st in od))
check("orders_main_brown", any("منوی اصلی" in t and st == "danger"
                               for t, st in od))
em, link = B.kb_earn(424242, "SomeBot")
check("earn_link_format",
      link == "https://t.me/SomeBot?start=ref_424242", link)
emf = flat(em)
check("earn_styles", any(st == "primary" for _, st in emf)
      and any(st == "danger" for _, st in emf))
sp = flat(B.kb_support())
check("support_kb", len(sp) == 3)
check("support_cancel_brown",
      flat(B.kb_cancel_support())[0][1] == "danger")
gm = flat(B.kb_games())
check("games_6_green", sum(1 for _, st in gm if st == "success") == 6,
      str(gm))
check("games_addgroup_blue", any("افزودن به گروه" in t and st == "primary"
                                 for t, st in gm))
check("games_back_brown", any("بازگشت" in t and st == "danger"
                              for t, st in gm))
gmodes = flat(B.kb_game_modes("doz"))
check("game_modes", len([1 for _, st in gmodes if st == "success"]) == 2)
check("games_exact", B.GAMES == [
    ("doz", "⭕ دوز"),
    ("mine", "💣 مین یاب"),
    ("dice", "🎲 تاس"),
    ("rps", "✊ سنگ کاغذ قیچی"),
    ("dart", "🎯 دارت"),
    ("bowling", "🎳 بولینگ"),
], str(B.GAMES))
check("games_text_exact", B.GAMES_TEXT == (
    "🎮 مرکز بازیهای نکستارز\n"
    "• دوز • مین یاب • سنگ کاغذ قیچی • تاس، دارت و بولینگ\n"
    "💡 روش بازی:\n"
    "• تمامی بازیها در بستر گروهها با پرتابهای زنده اجرا میشوند.\n"
    "• با دکمه «افزودن به گروه» در زیر، ربات را به گروه خود اضافه کنید و با دوستان خود بازی کنید! 🎉"))

# --- Admin --------------------------------------------------------------------
ah = flat(B.kb_admin_home())
check("admin_home", len(ah) >= 5)
aset = flat(B.kb_admin_settings())
check("admin_settings_rows", len(aset) == len(B.SETTING_LABELS) + 1)

# --- Nexy stub answers stars price --------------------------------------------
check("nexy_stars_price", "4,512" in B.nexy_reply("قیمت استارز چنده؟"))

print(f"PASS={PASS} FAIL={FAIL}")
for f in FAILURES:
    print("FAIL:", f)
sys.exit(1 if FAIL else 0)
