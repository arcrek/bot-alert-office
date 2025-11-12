import logging
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from bot.config import TELEGRAM_BOT_TOKEN
from bot.sheets_manager import SheetsManager
from bot.alert_manager import AlertManager
from bot.handlers import BotHandlers
from bot.scheduler import AlertScheduler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Office Telegram Bot...")
    
    sheets_manager = SheetsManager()
    logger.info("Google Sheets manager initialized")
    
    alert_manager = AlertManager(sheets_manager)
    logger.info("Alert manager initialized")
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    bot_handlers = BotHandlers(sheets_manager, alert_manager)
    
    application.add_handler(CommandHandler('start', bot_handlers.start_command))
    application.add_handler(CommandHandler('startmon', bot_handlers.startmon_command))
    application.add_handler(CommandHandler('renew', bot_handlers.renew_command))
    application.add_handler(CommandHandler('check', bot_handlers.check_command))
    
    application.add_handler(MessageHandler(
        filters.TEXT & filters.REPLY & ~filters.COMMAND,
        bot_handlers.handle_done_reply
    ))
    
    logger.info("Handlers registered")
    
    scheduler = AlertScheduler(alert_manager, application)
    
    async def post_init(app: Application):
        scheduler.set_whitelisted_groups(bot_handlers.get_whitelisted_groups())
        scheduler.start()
        logger.info("Bot is ready and scheduler is running")
    
    application.post_init = post_init
    
    async def post_shutdown(app: Application):
        scheduler.stop()
        logger.info("Scheduler stopped")
    
    application.post_shutdown = post_shutdown
    
    logger.info("Starting bot polling...")
    application.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == '__main__':
    main()

