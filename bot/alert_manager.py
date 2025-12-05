import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from bot.config import TIMEZONE
from bot.sheets_manager import SheetsManager

logger = logging.getLogger(__name__)

class AlertManager:
    def __init__(self, sheets_manager: SheetsManager):
        self.sheets_manager = sheets_manager
        self.alert_tracking = {}  # message_id -> row_index
        self.email_messages = {}  # email -> [(chat_id, message_id)]
    
    def check_for_alerts(self) -> List[Dict[str, any]]:
        alerts = []
        try:
            data = self.sheets_manager.get_sheet_data('A:I')
            current_time = datetime.now(TIMEZONE)
            current_time_str = current_time.strftime('%H:%M:%S')
            
            logger.info(f"Checking {len(data)} rows at {current_time_str}")
            
            for idx, row in enumerate(data, start=1):
                if idx == 1:
                    continue
                
                if len(row) < 9:
                    continue
                
                email = row[0] if len(row) > 0 else ''
                password = row[1] if len(row) > 1 else ''
                c_column = row[2] if len(row) > 2 else ''
                h_value_str = row[7] if len(row) > 7 else ''
                i_time = row[8] if len(row) > 8 else ''
                
                if not email or not h_value_str or not i_time:
                    continue
                
                try:
                    h_value = int(h_value_str)
                except (ValueError, TypeError):
                    continue
                
                if h_value < 0 or (h_value == 0 and i_time < current_time_str):
                    alert = {
                        'row_index': idx,
                        'email': email,
                        'password': password,
                        'c_column': c_column,
                        'expiry_time': i_time
                    }
                    alerts.append(alert)
                    logger.info(f"Alert triggered for row {idx}: {email}, H={h_value}, Time={i_time}")
            
            logger.info(f"Found {len(alerts)} alerts to send")
            return alerts
            
        except Exception as error:
            logger.error(f"Error checking for alerts: {error}")
            return []
    
    def check_for_daily_summary(self) -> List[Dict[str, any]]:
        """Check for all expired accounts (H <= 0) regardless of time for daily summary"""
        alerts = []
        try:
            data = self.sheets_manager.get_sheet_data('A:I')
            current_time = datetime.now(TIMEZONE)
            current_time_str = current_time.strftime('%H:%M:%S')
            
            logger.info(f"Running daily summary check for {len(data)} rows at {current_time_str}")
            
            for idx, row in enumerate(data, start=1):
                if idx == 1:
                    continue
                
                if len(row) < 9:
                    continue
                
                email = row[0] if len(row) > 0 else ''
                password = row[1] if len(row) > 1 else ''
                c_column = row[2] if len(row) > 2 else ''
                h_value_str = row[7] if len(row) > 7 else ''
                i_time = row[8] if len(row) > 8 else ''
                
                if not email or not h_value_str or not i_time:
                    continue
                
                try:
                    h_value = int(h_value_str)
                except (ValueError, TypeError):
                    continue
                
                # For daily summary: check only H <= 0, ignore time comparison
                if h_value <= 0:
                    alert = {
                        'row_index': idx,
                        'email': email,
                        'password': password,
                        'c_column': c_column,
                        'expiry_time': i_time,
                        'days_remaining': h_value
                    }
                    alerts.append(alert)
                    logger.info(f"Daily summary: row {idx}: {email}, H={h_value}, Time={i_time}")
            
            logger.info(f"Found {len(alerts)} expired accounts for daily summary")
            return alerts
            
        except Exception as error:
            logger.error(f"Error checking for daily summary: {error}")
            return []
    
    def format_alert_message(self, alert: Dict[str, any]) -> str:
        email = alert['email']
        password = alert['password']
        c_column = alert.get('c_column', '').lower()
        expiry_time = alert['expiry_time']
        
        if 'copilot' in c_column:
            alert_title = "🔔 Renew Copilot:"
        else:
            alert_title = "🔔 Renew 365:"
        
        message = f"{alert_title}\n"
        message += f"Email: `{email}`\n"
        message += f"Password: `{password}`\n"
        message += f"Giờ hết hạn: {expiry_time}"
        
        return message
    
    def format_daily_summary_message(self, alerts: List[Dict[str, any]]) -> str:
        """Format daily summary message with all expired accounts"""
        if not alerts:
            return "📊 Daily Summary (7:00 AM)\n\n✅ No expired accounts today!"
        
        current_date = datetime.now(TIMEZONE).strftime('%Y-%m-%d')
        message = f"📊 Daily Summary - {current_date}\n"
        message += f"Total expired accounts: {len(alerts)}\n"
        message += "=" * 30 + "\n\n"
        
        # Group by type (Copilot vs 365)
        copilot_alerts = []
        office_alerts = []
        
        for alert in alerts:
            c_column = alert.get('c_column', '').lower()
            if 'copilot' in c_column:
                copilot_alerts.append(alert)
            else:
                office_alerts.append(alert)
        
        # Add Copilot section
        if copilot_alerts:
            message += f"🤖 Copilot Accounts ({len(copilot_alerts)}):\n"
            for alert in copilot_alerts:
                message += f"• `{alert['email']}` - Expires: {alert['expiry_time']}\n"
            message += "\n"
        
        # Add Office 365 section
        if office_alerts:
            message += f"📦 Office 365 Accounts ({len(office_alerts)}):\n"
            for alert in office_alerts:
                message += f"• `{alert['email']}` - Expires: {alert['expiry_time']}\n"
        
        return message
    
    def update_row_after_done(self, row_index: int) -> bool:
        now = datetime.now(TIMEZONE)
        date_value = now.strftime('%Y-%m-%d')
        time_value = now.strftime('%H:%M:%S')
        
        success = self.sheets_manager.update_row(row_index, date_value, time_value)
        
        if success:
            logger.info(f"Successfully updated row {row_index} after 'done' reply")
        else:
            logger.error(f"Failed to update row {row_index} after 'done' reply")
        
        return success
    
    def track_alert_message(self, message_id: int, row_index: int, email: str, chat_id: int):
        self.alert_tracking[message_id] = row_index
        
        # Track message by email for duplicate detection
        if email not in self.email_messages:
            self.email_messages[email] = []
        self.email_messages[email].append((chat_id, message_id))
        
        logger.info(f"Tracking alert message {message_id} for row {row_index}, email {email}, chat {chat_id}")
    
    def get_row_from_message(self, message_id: int) -> Optional[int]:
        return self.alert_tracking.get(message_id)
    
    def get_email_from_row(self, row_index: int) -> Optional[str]:
        """Get email address for a given row index from the tracking data"""
        for message_id, tracked_row in self.alert_tracking.items():
            if tracked_row == row_index:
                # Find email from email_messages
                for email, messages in self.email_messages.items():
                    for chat_id, msg_id in messages:
                        if msg_id == message_id:
                            return email
        return None
    
    def get_old_messages_for_email(self, email: str, chat_id: int) -> List[int]:
        """Get all message IDs for a given email in a specific chat"""
        if email not in self.email_messages:
            return []
        
        message_ids = [msg_id for cid, msg_id in self.email_messages[email] if cid == chat_id]
        return message_ids
    
    def remove_message_tracking(self, message_id: int):
        """Remove a message from tracking"""
        # Remove from alert_tracking
        row_index = self.alert_tracking.pop(message_id, None)
        
        # Remove from email_messages
        for email, messages in list(self.email_messages.items()):
            self.email_messages[email] = [(cid, mid) for cid, mid in messages if mid != message_id]
            if not self.email_messages[email]:
                del self.email_messages[email]
        
        if row_index:
            logger.info(f"Removed tracking for message {message_id} (row {row_index})")

