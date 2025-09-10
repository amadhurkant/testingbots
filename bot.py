#!/usr/bin/env python3
import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- Logging ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Handlers ---
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name if user and user.first_name else "there"
    text = f"Hey {name}! 👋 I’m alive, created by @amadhurkant"
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
        "Stellar Leumens (XLM) payment info:",
        "",
        f"Address: {address}",
    ]
    if memo and memo_type:
        lines += [f"Memo ({memo_type}): {memo}"]

    lines += [
        "",
        "⚠️ Double-check the address and enter memo if you want to add extra words of thanks.",
        "Memo is not needed."
    ]

    await update.message.reply_text("\n".join(lines))

# --- Main ---
def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("BOT_TOKEN environment variable is missing. Exiting.")
        raise SystemExit("Missing BOT_TOKEN environment variable.")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("pay", pay_cmd))

    # Optional: log errors
    async def on_startup(app):
        logger.info("Bot started (polling).")

    async def on_shutdown(app):
        logger.info("Shutting down...")

    app.post_init = on_startup

    # Run polling (keeps running)
    logger.info("Launching bot polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
