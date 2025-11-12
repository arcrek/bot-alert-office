import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from telegram.ext import ContextTypes
from bot.config import CHECK_INTERVAL_MINUTES, TIMEZONE
from bot.alert_manager import AlertManager

logger = logging.getLogger(__name__)

class AlertScheduler:
    def __init__(self, alert_manager: AlertManager, bot_application):
        self.alert_manager = alert_manager
        self.bot_application = bot_application
        self.scheduler = AsyncIOScheduler(timezone=TIMEZONE)
        self.whitelisted_groups = set()
    
    def set_whitelisted_groups(self, groups: set):
        self.whitelisted_groups = groups
    
    async def scheduled_check(self):
        logger.info("Running scheduled alert check...")
        
        if not self.whitelisted_groups:
            logger.info("No whitelisted groups. Skipping alert check.")
            return
        
        alerts = self.alert_manager.check_for_alerts()
        
        if not alerts:
            logger.info("No alerts to send")
            return
        
        logger.info(f"Sending {len(alerts)} alerts to {len(self.whitelisted_groups)} group(s)")
        
        for group_id in self.whitelisted_groups:
            for alert in alerts:
                try:
                    message_text = self.alert_manager.format_alert_message(alert)
                    sent_message = await self.bot_application.bot.send_message(
                        chat_id=group_id,
                        text=message_text,
                        parse_mode='Markdown'
                    )
                    self.alert_manager.track_alert_message(sent_message.message_id, alert['row_index'])
                    logger.info(f"Alert sent to group {group_id} for row {alert['row_index']}")
                except Exception as e:
                    logger.error(f"Error sending alert to group {group_id}: {e}")
    
    def start(self):
        self.scheduler.add_job(
            self.scheduled_check,
            trigger=IntervalTrigger(minutes=CHECK_INTERVAL_MINUTES),
            id='alert_check',
            name='Check for alerts',
            replace_existing=True
        )
        self.scheduler.start()
        logger.info(f"Scheduler started. Checking every {CHECK_INTERVAL_MINUTES} minutes")
    
    def stop(self):
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")

