
from infra.tz_clock import TZClock
from infra.logging import setup_logger, get_logger
from infra.database.sqlite_db import SqliteDatabase
from infra.database.setup import setup_database
from infra.telegram.bot import TelegramBotInfra

from adapters.outbound.repositories.quiz_repo import QuizRepo
from adapters.outbound.repositories.users_repo import UsersRepo
from adapters.outbound.repositories.telegram_auth_repo import TelegramAuthRepo
from adapters.outbound.repositories.quiz_session_repo import QuizSessionRepo
from adapters.outbound.parsers.excel_parser import ExcelParser

from adapters.inbound.telegram_ui.app import TelegramUI

from app.app_actions import AppActions

from dotenv import load_dotenv
load_dotenv()


async def wait_shutdown():
    stop_event = asyncio.Event()
    
    def signal_handler():
        stop_event.set()
    
    signal.signal(signal.SIGINT, lambda s, f: signal_handler())
    signal.signal(signal.SIGTERM, lambda s, f: signal_handler())

    await stop_event.wait()


async def main():
    # -------- Infra --------
    tz_clock = TZClock(os.getenv("TIMEZONE", "UTC"))

    setup_logger(name="HRBOT", log_dir="logs", clock=tz_clock, debug_enabled=False)

    logger = get_logger()

    logger.info("🚀 Program start...")

    db = SqliteDatabase("data/app.db")
    await db.connect()
    await setup_database(db)

    tg_bot_token = os.getenv("TG_BOT_TOKEN")
    if not tg_bot_token:
        raise ValueError("No API_TOKEN provided. Please set it in the .env file.")
    
    tg_bot = TelegramBotInfra(tg_bot_token)
    await tg_bot.start_polling()

    # -------- Outbound adapters --------
    quiz_repo = QuizRepo(db)
    users_repo = UsersRepo(db)
    quiz_session_repo = QuizSessionRepo(db, tz_clock=tz_clock)
    tg_auth_repo = TelegramAuthRepo(db)

    excel_parser = ExcelParser()

    # ------------ Use-cases -----------
    actions = AppActions(
        users_repo=users_repo,
        tg_auth_repo=tg_auth_repo,
        quiz_repo=quiz_repo,
        quiz_session_repo=quiz_session_repo,
        excel_parser=excel_parser
    )

    # -------- Indound adapters --------
    TelegramUI(tg_bot, actions)
    
    logger.info("✅ Program started")

    # ------------ Lifecycle ------------
    await wait_shutdown()

    # Close resources
    await db.close()
    await tg_bot.stop_polling()

    logger.info("🏁 Successful shutdown")

if __name__ == "__main__":
    asyncio.run(main())
