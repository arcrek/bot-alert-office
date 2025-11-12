import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Optional, Tuple
from bot.config import GOOGLE_CREDENTIALS_PATH, GOOGLE_SHEET_ID

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class SheetsManager:
    def __init__(self):
        self.credentials = service_account.Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_PATH, scopes=SCOPES
        )
        self.service = build('sheets', 'v4', credentials=self.credentials)
        self.spreadsheet_id = GOOGLE_SHEET_ID
        
    def get_sheet_data(self, range_name: str = 'A:I') -> List[List[str]]:
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            values = result.get('values', [])
            logger.info(f"Retrieved {len(values)} rows from sheet")
            return values
        except HttpError as error:
            logger.error(f"Error fetching sheet data: {error}")
            raise
    
    def get_row_data(self, row_index: int) -> Optional[Dict[str, str]]:
        try:
            range_name = f'A{row_index}:I{row_index}'
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            values = result.get('values', [])
            
            if not values or not values[0]:
                return None
            
            row = values[0]
            return {
                'email': row[0] if len(row) > 0 else '',
                'password': row[1] if len(row) > 1 else '',
                'c_column': row[2] if len(row) > 2 else '',
                'h_value': row[7] if len(row) > 7 else '',
                'i_time': row[8] if len(row) > 8 else '',
                'row_index': row_index
            }
        except HttpError as error:
            logger.error(f"Error fetching row {row_index}: {error}")
            return None
    
    def update_row(self, row_index: int, date_value: str, time_value: str) -> bool:
        try:
            values = [
                [date_value],
                [time_value]
            ]
            
            data = [
                {
                    'range': f'G{row_index}',
                    'values': [[date_value]]
                },
                {
                    'range': f'I{row_index}',
                    'values': [[time_value]]
                }
            ]
            
            body = {
                'valueInputOption': 'USER_ENTERED',
                'data': data
            }
            
            self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=body
            ).execute()
            
            logger.info(f"Updated row {row_index}: G={date_value}, I={time_value}")
            return True
        except HttpError as error:
            logger.error(f"Error updating row {row_index}: {error}")
            return False
    
    def find_row_by_email(self, email: str) -> Optional[int]:
        try:
            values = self.get_sheet_data('A:A')
            for idx, row in enumerate(values, start=1):
                if row and row[0].strip().lower() == email.strip().lower():
                    return idx
            return None
        except Exception as error:
            logger.error(f"Error finding email {email}: {error}")
            return None

