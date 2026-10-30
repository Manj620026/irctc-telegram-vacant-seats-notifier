# 🚂 IRCTC Post-Charting Vacant Seats Telegram Bot

[![Powered by irctc.dev](https://img.shields.io/badge/IRCTC_API-irctc.dev-blue?style=flat-square&logo=train)](https://irctc.dev)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg?style=flat-square&logo=python)](https://www.python.org/)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0%20(stdlib%20only)-success?style=flat-square)](#-zero-dependencies)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

A production-ready Telegram alert bot that continuously monitors Indian Railways reservation charts after preparation and instantly alerts you when vacant berths (Current Booking seats) become available.

Powered by the [irctc.dev](https://irctc.dev) high-speed IRCTC API (<10ms in-memory PRS charts).

---

## ⚡ Why Post-Charting Vacant Seats Matter

When Indian Railways prepares the reservation chart (**~4 hours before train departure**), unallocated emergency quotas, VIP berths, and last-minute cancellations are released to the public under **Current Booking**.

These seats are available at regular or discounted fares and confirm immediately (no waitlist). However, they sell out within minutes. This bot monitors the live chart and pushes an instant alert to your Telegram chat the second berths unlock.

---

## 🎯 Key Features

- **Zero External Dependencies:** Built 100% on Python standard library (`urllib`, `json`, `html`, `re`). No `pip install` required!
- **Dual Execution Mode:**
  - **Instant Check (`--check`):** Run a single lookup from terminal and print or send the status.
  - **Live Watcher Loop:** Polls the chart at a configurable interval until seats unlock, then fires an alert.
- **Rich Telegram HTML Alerts:** Coach and berth breakdown (`3A | B2-45 (SL)`), class-wise count, and instant booking guidance.
- **Built-in Mock Fallback:** Automatically prints formatted alerts to the console if no Telegram token is set.
- **Security Hardened:** SSRF-safe base URL validator, strict regex input validation, and HTML-escaped output.

---

## 📸 Telegram Alert Preview

```html
🚨 VACANT BERTHS ALERT: 12557 SAPT KRANTI EXP
📍 Boarding Station: NKE
📋 Status: 🟢 Chart Prepared
💺 Total Vacant Seats: 18
────────────────────────
Available Classes Breakdown:
  • 3A: 12 berths available
  • 2A: 4 berths available
  • 1A: 2 berths available
────────────────────────
Sample Available Berths (Current Booking):
  • 3A | B1-12 (MB) to NDLS
  • 3A | B2-45 (SL) to NDLS
  • 2A | A1-18 (LB) to NDLS

👉 Book immediately on the official IRCTC app under Current Booking.

⚡ Powered by irctc.dev (Sub-10ms Indian Railways IRCTC API)
```

---

## 🚀 2-Minute Quickstart

### 1. Clone the Repository
```bash
git clone https://github.com/Manj620026/irctc-telegram-vacant-seats-notifier.git
cd irctc-telegram-vacant-seats-notifier
```

### 2. Configure Credentials
Copy the example configuration:
```bash
cp .env.example .env
```

Edit `.env`:
```env
# 1. Claim 10,000 Free Credits at https://irctc.dev/dashboard
IRCTC_API_KEY=your_irctc_api_key_here

# 2. Get from @BotFather on Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather

# 3. Get your Chat ID by messaging @userinfobot on Telegram
TELEGRAM_CHAT_ID=your_telegram_chat_id

# 4. Target Train & Station to monitor
WATCH_TRAIN_NO=12557
WATCH_STATION=NKE
WATCH_CLASS=ALL
POLL_INTERVAL_SECONDS=120
```

> **Note:** If you don't configure `TELEGRAM_BOT_TOKEN`, the bot runs in **Mock Console Mode**, printing formatted notifications directly in your terminal.

---

## 🤖 Getting Telegram Bot Credentials in 60 Seconds

1. Open Telegram and search for [@BotFather](https://t.me/botfather).
2. Send `/newbot`, choose a name and username, and copy the **API Token**.
3. Search for [@userinfobot](https://t.me/userinfobot) and send `/start` to get your numeric **Chat ID**.
4. Start your bot by opening its chat and pressing **Start**.

---

## 💻 Usage

### Run Instant One-Shot Check
Check live vacancy status right now without waiting:
```bash
python bot.py --check
```

Pass train number and boarding station dynamically:
```bash
python bot.py 12557 NKE ALL --check
```

### Start Continuous Watcher Loop
Run the automated monitoring daemon:
```bash
python bot.py
```

Override targets via command-line arguments:
```bash
python bot.py 12557 NKE 3A
```

---

## 🛠️ Configuration Options

| Variable | Default | Description |
| :--- | :--- | :--- |
| `IRCTC_API_KEY` | `""` | API key from [irctc.dev/dashboard](https://irctc.dev/dashboard) (10k free credits) |
| `IRCTC_API_BASE_URL` | `https://api.irctc.dev` | API Gateway Base URL |
| `TELEGRAM_BOT_TOKEN` | `""` | Bot token from `@BotFather` |
| `TELEGRAM_CHAT_ID` | `""` | Target Telegram user or group chat ID |
| `WATCH_TRAIN_NO` | `12557` | 4 or 5 digit Indian Railways train number |
| `WATCH_STATION` | `NKE` | Station code where you want to board |
| `WATCH_CLASS` | `ALL` | Travel class filter (`ALL`, `1A`, `2A`, `3A`, `SL`, etc.) |
| `POLL_INTERVAL_SECONDS` | `120` | Interval between chart polls in seconds (min 30s) |

---

## 📄 License

MIT © [irctc.dev Developer Platform](https://irctc.dev)
