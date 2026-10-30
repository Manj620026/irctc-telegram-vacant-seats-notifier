"""
IRCTC Post-Charting Vacant Berths Telegram Alert Bot Starter
Powered by irctc.dev Vacant Berths API (<10ms in-memory PRS charts)

Zero external pip dependencies required — runs out of the box on Python 3.8+!
"""

import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime


def load_dotenv(env_path: str = ".env") -> None:
    """Load key-value pairs from .env file into os.environ if not already set (zero-dep)."""
    if not os.path.isfile(env_path):
        return
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v
    except Exception:
        pass


# Load local .env if present
load_dotenv()


def sanitize_base_url(url: str) -> str:
    """Enforce valid HTTP/HTTPS scheme and strip trailing slashes."""
    clean = (url or "https://api.irctc.dev").strip().rstrip("/")
    try:
        parsed = urllib.parse.urlparse(clean)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            return "https://api.irctc.dev"
        return clean
    except Exception:
        return "https://api.irctc.dev"


BASE_URL = sanitize_base_url(os.environ.get("IRCTC_API_BASE_URL", "https://api.irctc.dev"))
IRCTC_API_KEY = os.environ.get("IRCTC_API_KEY", "").strip()  # Claim 10k free credits at https://irctc.dev/dashboard
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

POLL_INTERVAL_SECONDS = max(30, int(os.environ.get("POLL_INTERVAL_SECONDS", "120")))
FOOTER = "\n\n⚡ <i>Powered by <a href='https://irctc.dev'>irctc.dev</a> (Sub-10ms Indian Railways IRCTC API)</i>"


def send_telegram_message(chat_id: str, text: str) -> bool:
    """Send HTML-formatted notification to Telegram chat. Falls back to console if token missing."""
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "your_bot_token_from_botfather":
        print(f"\n[Telegram Preview Mock] (To: {chat_id})\n{text}\n")
        return True

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "irctc-telegram-vacant-bot/1.0.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[Telegram Alert] Error sending message to {chat_id}: {e}")
        return False


def check_vacant_berths(train_no: str, boarding_station: str, travel_class: str = "ALL", date: str = "") -> dict:
    """Fetch live post-charting vacant berths from irctc.dev API gateway."""
    train_clean = str(train_no).strip()
    station_clean = str(boarding_station).strip().upper()
    class_clean = str(travel_class).strip().upper() or "ALL"

    if not re.match(r"^\d{4,5}$", train_clean):
        return {"success": False, "error": "Invalid train number. Must be 4 or 5 digits."}

    if not re.match(r"^[A-Z]{2,6}$", station_clean):
        return {"success": False, "error": "Invalid station code. Must be 2-6 alphabetic characters."}

    query_params = {
        "boardingStation": station_clean,
        "class": class_clean,
    }
    if date:
        query_params["date"] = date.strip()

    params = urllib.parse.urlencode(query_params)
    url = f"{BASE_URL}/api/v1/trains/{train_clean}/chart-vacant?{params}"

    headers = {
        "Accept": "application/json",
        "User-Agent": "irctc-telegram-vacant-bot/1.0.0",
    }
    if IRCTC_API_KEY:
        headers["x-api-key"] = IRCTC_API_KEY

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read().decode("utf-8")
            return json.loads(data)
    except urllib.error.HTTPError as e:
        try:
            error_body = e.read().decode("utf-8")
            parsed = json.loads(error_body)
            return {"success": False, "error": parsed.get("error") or parsed.get("message") or f"HTTP {e.code}"}
        except Exception:
            return {"success": False, "error": f"HTTP {e.code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def format_vacant_notification(data: dict, train_no: str, station: str) -> str:
    """Format structured HTML alert message matching official irctc.dev chart schema."""
    train_name = html.escape(str(data.get("trainName") or ""))
    total = int(data.get("totalVacantBerths") or 0)

    # Safe chart preparation extraction supporting both nested and flat schemas
    chart_status_obj = data.get("chartStatus")
    if isinstance(chart_status_obj, dict):
        is_prepared = bool(chart_status_obj.get("isChartPrepared"))
    else:
        is_prepared = bool(data.get("isChartPrepared"))

    chart_badge = "🟢 <b>Chart Prepared</b>" if is_prepared else "⏳ <i>Chart Not Yet Prepared</i>"

    lines = [
        f"🚨 <b>VACANT BERTHS ALERT: {train_no} {train_name}</b>",
        f"📍 <b>Boarding Station</b>: {html.escape(station.upper())}",
        f"📋 <b>Status</b>: {chart_badge}",
        f"💺 <b>Total Vacant Seats</b>: <b>{total}</b>",
        "────────────────────────"
    ]

    # Support summaryByClass with fallback to vacantByClass
    by_class = data.get("summaryByClass") or data.get("vacantByClass") or {}
    if isinstance(by_class, dict) and by_class:
        lines.append("<b>Available Classes Breakdown:</b>")
        for cls_name, count in by_class.items():
            if int(count) > 0:
                lines.append(f"  • <b>{html.escape(str(cls_name))}</b>: {count} berths available")
        lines.append("────────────────────────")

    # Sample berth allocations
    sample_berths = (data.get("vacantBerths") or [])[:8]
    if sample_berths:
        lines.append("<b>Sample Available Berths (Current Booking):</b>")
        for b in sample_berths:
            coach = html.escape(str(b.get("coach") or "Coach"))
            berth_no = str(b.get("berthNo") or b.get("berthNumber") or b.get("berth") or "")
            b_type = html.escape(str(b.get("berthType") or ""))
            cls = html.escape(str(b.get("class") or ""))
            dest = html.escape(str(b.get("to") or ""))
            dest_str = f" to {dest}" if dest else ""
            type_str = f" ({b_type})" if b_type else ""
            lines.append(f"  • {cls} | {coach}-{berth_no}{type_str}{dest_str}")

    lines.append("\n👉 Book immediately on the official IRCTC app under <b>Current Booking</b>.")
    lines.append(FOOTER)
    return "\n".join(lines)


def watch_train(train_no: str, boarding_station: str, chat_id: str, travel_class: str = "ALL") -> None:
    """Continuous watcher polling reservation chart until vacant berths open."""
    print(f"👀 [Watcher Started] Monitoring train {train_no} from {boarding_station} (Poll every {POLL_INTERVAL_SECONDS}s)...")
    notified = False

    while True:
        res = check_vacant_berths(train_no, boarding_station, travel_class)
        if not res.get("success"):
            err_msg = res.get("error") or res.get("message") or "Unknown error"
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Note: {err_msg}")
            time.sleep(POLL_INTERVAL_SECONDS)
            continue

        chart_obj = res.get("chartStatus")
        is_prepared = bool(chart_obj.get("isChartPrepared")) if isinstance(chart_obj, dict) else bool(res.get("isChartPrepared"))
        vacant_count = int(res.get("totalVacantBerths") or 0)

        now_str = datetime.now().strftime("%H:%M:%S")
        print(f"[{now_str}] Train {train_no} @ {boarding_station}: ChartPrepared={is_prepared}, VacantSeats={vacant_count}")

        if is_prepared and vacant_count > 0:
            if not notified:
                print(f"🎉 [Seats Detected] Sending Telegram alert ({vacant_count} vacant berths)!")
                msg = format_vacant_notification(res, train_no, boarding_station)
                send_telegram_message(chat_id, msg)
                notified = True
        else:
            notified = False

        time.sleep(POLL_INTERVAL_SECONDS)


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    one_shot = "--check" in sys.argv

    train_no = args[0] if len(args) > 0 else os.environ.get("WATCH_TRAIN_NO", "12557")
    station = args[1] if len(args) > 1 else os.environ.get("WATCH_STATION", "NKE")
    cls = args[2] if len(args) > 2 else os.environ.get("WATCH_CLASS", "ALL")
    target_chat = TELEGRAM_CHAT_ID or "console"

    print("🚂 IRCTC Vacant Berths Telegram Alert Bot")
    print(f"• Target Train: {train_no}")
    print(f"• Station: {station.upper()}")
    print(f"• Class: {cls.upper()}")
    print(f"• Gateway: {BASE_URL}")
    print(f"• Target Chat ID: {target_chat}")
    print("─" * 45)

    if one_shot:
        print("🔎 Performing one-time instant check...")
        res = check_vacant_berths(train_no, station, cls)
        if not res.get("success"):
            print(f"❌ Error: {res.get('error') or res.get('message')}")
            sys.exit(1)
        msg = format_vacant_notification(res, train_no, station)
        send_telegram_message(target_chat, msg)
        return

    try:
        watch_train(train_no, station, target_chat, cls)
    except KeyboardInterrupt:
        print("\n🛑 Watcher stopped by user.")


if __name__ == "__main__":
    main()
