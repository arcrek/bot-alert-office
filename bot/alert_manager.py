import logging
from datetime import datetime
from typing import List, Dict, Optional
from bot.config import TIMEZONE
from bot.sheets_manager import SheetsManager

logger = logging.getLogger(__name__)

class AlertManager:
    def __init__(self, sheets_manager: SheetsManager):
        self.sheets_manager = sheets_manager
        self.alert_tracking = {}
    
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
                
                if h_value <= 0 and i_time < current_time_str:
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
    
    def track_alert_message(self, message_id: int, row_index: int):
        self.alert_tracking[message_id] = row_index
        logger.info(f"Tracking alert message {message_id} for row {row_index}")
    
    def get_row_from_message(self, message_id: int) -> Optional[int]:
        return self.alert_tracking.get(message_id)

