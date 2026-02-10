import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from src.config import TELEGRAM_BOT_TOKEN, DEFAULT_BIDDING_ZONE
from src.fetcher import fetch_day_ahead_prices, fetch_latest_prices, ZONE_MAP
from src.predictor import PricePredictor
from src.formatter import format_price_forecast, format_current_prices

logger = logging.getLogger(__name__)

predictor = PricePredictor()

# In-memory subscriber store  (swap for Redis / SQLite in production)
subscribers: dict[int, dict] = {}


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Register user and show help."""
    chat_id = update.effective_chat.id
    subscribers[chat_id] = {"zone": DEFAULT_BIDDING_ZONE, "subscribed": False}
    await update.message.reply_text(
        "\u26a1 *Welcome to EnergyPulse!*\n\n"
        "I predict electricity spot prices so you can shift usage "
        "to the cheapest hours.\n\n"
        "*Commands:*\n"
        "/price \u2014 Today's actual prices\n"
        "/predict \u2014 Tomorrow's LSTM forecast\n"
        "/zone CODE \u2014 Change region (DE\\_LU, FR, NL, AT, BE)\n"
        "/subscribe \u2014 Daily forecast at 20:00\n"
        "/unsubscribe \u2014 Stop daily alerts\n",
        parse_mode="Markdown",
    )


async def cmd_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show today's actual spot prices."""
    chat_id = update.effective_chat.id
    zone = subscribers.get(chat_id, {}).get("zone", DEFAULT_BIDDING_ZONE)
    try:
        prices = fetch_latest_prices(zone)
        msg = format_current_prices(prices)
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        logger.error("Error fetching prices: %s", e)
        await update.message.reply_text(
            "\u274c Failed to fetch prices. Please try again later."
        )


async def cmd_predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Run LSTM prediction for next 24h."""
    chat_id = update.effective_chat.id
    zone = subscribers.get(chat_id, {}).get("zone", DEFAULT_BIDDING_ZONE)
    try:
        prices = fetch_day_ahead_prices(zone, days=14)
        predictions = predictor.predict(prices)
        msg = format_price_forecast(predictions)
        await update.message.reply_text(msg, parse_mode="Markdown")
    except RuntimeError:
        await update.message.reply_text(
            "\u26a0\ufe0f Model not trained yet. An admin needs to run /train first."
        )
    except Exception as e:
        logger.error("Prediction error: %s", e)
        await update.message.reply_text(
            "\u274c Prediction failed. Please try again later."
        )


async def cmd_zone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set the user's bidding zone."""
    available = list(ZONE_MAP.keys())
    if context.args and context.args[0].upper() in available:
        chat_id = update.effective_chat.id
        zone = context.args[0].upper()
        if chat_id not in subscribers:
            subscribers[chat_id] = {"subscribed": False}
        subscribers[chat_id]["zone"] = zone
        await update.message.reply_text(
            f"\u2705 Region set to *{zone}*", parse_mode="Markdown"
        )
    else:
        zone_list = "\n".join(f"\u2022 {z}" for z in available)
        await update.message.reply_text(
            f"Usage: /zone <CODE>\n\nAvailable zones:\n{zone_list}",
            parse_mode="Markdown",
        )


async def cmd_subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Subscribe to daily forecast push."""
    chat_id = update.effective_chat.id
    if chat_id not in subscribers:
        subscribers[chat_id] = {"zone": DEFAULT_BIDDING_ZONE}
    subscribers[chat_id]["subscribed"] = True
    await update.message.reply_text(
        "\u2705 Subscribed! You'll receive daily forecasts at 20:00 CET."
    )


async def cmd_unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unsubscribe from daily forecast push."""
    chat_id = update.effective_chat.id
    if chat_id in subscribers:
        subscribers[chat_id]["subscribed"] = False
    await update.message.reply_text("\u2705 Unsubscribed from daily forecasts.")


async def cmd_train(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin: retrain the LSTM model on recent data."""
    await update.message.reply_text(
        "\U0001f504 Training model on 90 days of data... Please wait."
    )
    try:
        zone = subscribers.get(update.effective_chat.id, {}).get(
            "zone", DEFAULT_BIDDING_ZONE
        )
        prices = fetch_day_ahead_prices(zone, days=90)
        predictor.train(prices, epochs=50)
        await update.message.reply_text("\u2705 Model trained successfully!")
    except Exception as e:
        logger.error("Training error: %s", e)
        await update.message.reply_text(f"\u274c Training failed: {e}")


async def send_daily_forecasts(app: Application):
    """Push daily forecasts to all subscribed users."""
    for chat_id, info in subscribers.items():
        if not info.get("subscribed"):
            continue
        try:
            zone = info.get("zone", DEFAULT_BIDDING_ZONE)
            prices = fetch_day_ahead_prices(zone, days=14)
            predictions = predictor.predict(prices)
            msg = format_price_forecast(predictions)
            await app.bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")
        except Exception as e:
            logger.error("Failed to send forecast to %d: %s", chat_id, e)


def create_bot() -> Application:
    """Build and configure the Telegram bot application."""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("price", cmd_price))
    app.add_handler(CommandHandler("predict", cmd_predict))
    app.add_handler(CommandHandler("zone", cmd_zone))
    app.add_handler(CommandHandler("subscribe", cmd_subscribe))
    app.add_handler(CommandHandler("unsubscribe", cmd_unsubscribe))
    app.add_handler(CommandHandler("train", cmd_train))
    return app
