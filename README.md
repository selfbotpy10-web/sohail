# NexStarz Replica — بازسازی @NexStarz_Bot

A from-scratch (clean-room) replica of the Telegram bot **@NexStarz_Bot**,
built only from its publicly visible behaviour. Single file, aiogram 3.x +
SQLite.

## Contents
- `bot.py` — the whole bot (shops, wallet, boost, games, referral, support, admin panel)
- `REPORT.md` — full Persian exploration report (prices, colours, flows, limitations)
- `smoke_test.py` — keyboard/style smoke test (49 checks)
- `requirements.txt`, `.env.example`

## Setup
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env   # fill BOT_TOKEN (and ADMIN_IDS if needed)
.venv/bin/python bot.py
```

## Notes
- Button colours use Bot API `style` (`success`=green, `primary`=blue,
  `danger`=brown-ish for back/cancel). See the colour table in `REPORT.md`.
- `CUSTOM_EMOJI_IDS` in `bot.py` ships empty: Telegram custom-emoji IDs
  cannot be extracted from Telegram Web. Fill it in and the premium emojis
  are applied automatically via `icon_custom_emoji_id`.
- Supplier/Fragment delivery, the online Rial gateway, on-chain crypto
  verification, real KYC and the Nexy AI are TODO stubs (marked in code).
- Prices are seeded from the exploration snapshot (they float in the
  original) and are all editable in the `/admin` panel.
