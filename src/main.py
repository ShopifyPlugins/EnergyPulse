import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.bot import create_bot, send_daily_forecasts
from src.config import DAILY_FORECAST_HOUR

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting EnergyPulse bot...")
    app = create_bot()

    # Schedule daily forecast push
    scheduler = AsyncIOScheduler(timezone="Europe/Berlin")
    scheduler.add_job(
        send_daily_forecasts,
        CronTrigger(hour=DAILY_FORECAST_HOUR, minute=0),
        args=[app],
    )
    scheduler.start()
    logger.info("Daily forecast scheduled at %02d:00 CET", DAILY_FORECAST_HOUR)

    app.run_polling()


if __name__ == "__main__":
    main()
