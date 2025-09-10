#!/usr/bin/env python3
import os
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# -------------------------
# Logging
# -------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("telegram-bot")

# -------------------------
# Tiny health server
# -------------------------
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Respond 200 for any GET (root, /, /health)
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"OK")

    # quieten the default logging to stderr
    def log_message(self, format, *args):
        return

def start_health_server():
    try:
        port = int(os.environ.get("PORT", "8000"))  # Render sets $PORT in web services
    except Exception:
        port = 8000

    server = HTTPServer(("", port), HealthHandler)
    logger.info("Health server listening on port %s", port)

    # Serve forever (runs in a daemon thread)
    try:
        server.serve_forever()
    except Exception as e:
        logger.exception("Health server stopped: %s", e)

# -------------------------
# Telegram bot handlers
# -------------------------
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name if user and user.first_name else "there"
    text = f"Hey {name}! 👋 I’m alive — send /pay if you want the Stellar (XLM) address."
    await update.message.reply_text(text)

async def pay_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Read address (and optional memo) from env vars
    address = os.getenv("STELLAR_ADDRESS")
    memo_type = os.getenv("STELLAR_MEMO_TYPE")  # e.g., "text" or "id"
    memo = os.getenv("STELLAR_MEMO")

    if not address:
        await update.message.reply_text(
            "Sorry — no Stellar address is configured. The bot owner needs to set STELLAR_ADDRESS."
        )
        return

    lines = [
        "💫 Stellar (XLM) payment info:",
        "",
        f"Address: `{address}`",
    ]
    if memo and memo_type:
        lines.append(f"Memo ({memo_type}): `{memo}`")

    lines += [
        "",
        "⚠️ Double-check the address and enter memo only if you want to add extra words of thanks.",
        "Memo is not needed."
    ]

    # Use plain text (avoid markup issues). If you want Markdown, change accordingly.
    await update.message.reply_text("\n".join(lines))

# -------------------------
# Main
# -------------------------
def main():
    # Start health server thread first (so Render sees the port quickly)
    t = threading.Thread(target=start_health_server, daemon=True)
    t.start()

    # Telegram bot token
    token = os.environ.get("BOT_TOKEN")
    if not token:
        logger.error("Missing BOT_TOKEN environment variable. Exiting.")
        raise SystemExit("Missing BOT_TOKEN environment variable.")

    # Build app
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("pay", pay_cmd))

    # Optional: log that app is starting
    logger.info("Starting Telegram bot (polling).")

    # Run the bot (blocking). PTB will handle signals and shutdown cleanly.
    app.run_polling()

if __name__ == "__main__"
    main()
