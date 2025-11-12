import json
import logging
import os
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from bot.config import WHITELIST_FILE, TIMEZONE
from bot.alert_manager import AlertManager
from bot.sheets_manager import SheetsManager

logger = logging.getLogger(__name__)

class BotHandlers:
    def __init__(self, sheets_manager: SheetsManager, alert_manager: AlertManager):
        self.sheets_manager = sheets_manager
        self.alert_manager = alert_manager
        self.whitelist = self._load_whitelist()
    
    def _load_whitelist(self) -> set:
        if os.path.exists(WHITELIST_FILE):
            try:
                with open(WHITELIST_FILE, 'r') as f:
                    data = json.load(f)
                    return set(data.get('group_ids', []))
            except Exception as e:
                logger.error(f"Error loading whitelist: {e}")
                return set()
        return set()
    
    def _save_whitelist(self):
        os.makedirs(os.path.dirname(WHITELIST_FILE), exist_ok=True)
        try:
            with open(WHITELIST_FILE, 'w') as f:
                json.dump({'group_ids': list(self.whitelist)}, f, indent=2)
            logger.info("Whitelist saved successfully")
        except Exception as e:
            logger.error(f"Error saving whitelist: {e}")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Office Telegram Bot\n\n"
            "Available commands:\n"
            "/startmon - Enable monitoring for this group\n"
            "/renew <email> - Manually renew for specific email\n"
            "/check - Manually run check for alerts\n\n"
            "Reply 'done' to any alert to mark it as renewed."
        )
    
    async def startmon_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        chat_type = update.effective_chat.type
        
        if chat_type not in ['group', 'supergroup']:
            await update.message.reply_text("This command only works in groups!")
            return
        
        if chat_id not in self.whitelist:
            self.whitelist.add(chat_id)
            self._save_whitelist()
            await update.message.reply_text(
                f"Monitoring enabled for this group!\n"
                f"Group ID: {chat_id}\n"
                "You will now receive alerts every 15 minutes."
            )
            logger.info(f"Added group {chat_id} to whitelist")
        else:
            await update.message.reply_text("Monitoring is already enabled for this group!")
    
    async def renew_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("Usage: /renew <email>")
            return
        
        email = ' '.join(context.args)
        
        row_index = self.sheets_manager.find_row_by_email(email)
        
        if row_index is None:
            await update.message.reply_text(f"Email not found: {email}")
            logger.warning(f"Email not found for renewal: {email}")
            return
        
        success = self.alert_manager.update_row_after_done(row_index)
        
        if success:
            now = datetime.now(TIMEZONE)
            await update.message.reply_text(
                f"Successfully renewed for {email}\n"
                f"Updated at: {now.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            logger.info(f"Manual renewal completed for {email} (row {row_index})")
        else:
            await update.message.reply_text(f"Failed to renew for {email}. Please try again.")
    
    async def check_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        status_message = await update.message.reply_text("Running manual check...")
        
        alerts = self.alert_manager.check_for_alerts()
        
        if not alerts:
            no_alerts_message = await update.message.reply_text("No alerts found.")
            # Delete status messages after 2 seconds
            try:
                await asyncio.sleep(2)
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=status_message.message_id)
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=no_alerts_message.message_id)
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
            except Exception as e:
                logger.warning(f"Failed to delete status messages: {e}")
            return
        
        chat_id = update.effective_chat.id
        
        for alert in alerts:
            email = alert['email']
            
            # Delete old messages for this email in this chat
            old_message_ids = self.alert_manager.get_old_messages_for_email(email, chat_id)
            for old_msg_id in old_message_ids:
                try:
                    await context.bot.delete_message(chat_id=chat_id, message_id=old_msg_id)
                    self.alert_manager.remove_message_tracking(old_msg_id)
                    logger.info(f"Deleted old message {old_msg_id} for email {email}")
                except Exception as e:
                    logger.warning(f"Failed to delete old message {old_msg_id}: {e}")
            
            # Send new alert message
            message_text = self.alert_manager.format_alert_message(alert)
            sent_message = await context.bot.send_message(
                chat_id=chat_id,
                text=message_text,
                parse_mode='Markdown'
            )
            self.alert_manager.track_alert_message(
                sent_message.message_id, 
                alert['row_index'],
                email,
                chat_id
            )
        
        # Delete status messages after sending alerts
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=status_message.message_id)
            await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
        except Exception as e:
            logger.warning(f"Failed to delete status messages: {e}")
    
    async def handle_done_reply(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message
        
        if not message.reply_to_message:
            return
        
        replied_message_id = message.reply_to_message.message_id
        message_text = message.text.lower().strip()
        
        if message_text != 'done':
            return
        
        row_index = self.alert_manager.get_row_from_message(replied_message_id)
        
        if row_index is None:
            return
        
        success = self.alert_manager.update_row_after_done(row_index)
        
        if success:
            now = datetime.now(TIMEZONE)
            confirmation = await message.reply_text(
                f"✅ Renewal confirmed!\n"
                f"Updated at: {now.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            logger.info(f"Renewal via 'done' reply for row {row_index}")
            
            # Delete the alert message and user's "done" reply after 2 seconds
            try:
                await asyncio.sleep(2)
                await context.bot.delete_message(
                    chat_id=message.chat_id,
                    message_id=replied_message_id
                )
                self.alert_manager.remove_message_tracking(replied_message_id)
                await context.bot.delete_message(
                    chat_id=message.chat_id,
                    message_id=message.message_id
                )
                await context.bot.delete_message(
                    chat_id=message.chat_id,
                    message_id=confirmation.message_id
                )
                logger.info(f"Deleted alert message {replied_message_id} and reply messages after 'done'")
            except Exception as e:
                logger.warning(f"Failed to delete messages: {e}")
        else:
            await message.reply_text("Failed to update. Please try again or use /renew command.")
    
    def get_whitelisted_groups(self) -> set:
        return self.whitelist

