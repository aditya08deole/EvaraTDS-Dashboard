"""
Telegram Bot Service - Secure messaging wrapper
Token is loaded from environment variables only, never hardcoded
"""
import os
from typing import List, Optional
from telegram import Bot
from telegram.error import TelegramError
import asyncio
import logging

logger = logging.getLogger(__name__)

class TelegramService:
    """Secure Telegram bot service wrapper"""
    
    def __init__(self):
        # CRITICAL: Load token from environment only, never expose in code
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        
        if not self.bot_token:
            logger.warning("TELEGRAM_BOT_TOKEN not set in environment variables")
            self.bot = None
        else:
            # Validate token format (basic check)
            if not self._validate_token_format(self.bot_token):
                logger.error("Invalid Telegram bot token format")
                self.bot = None
            else:
                self.bot = Bot(token=self.bot_token)
                logger.info("Telegram bot initialized successfully")
    
    def _validate_token_format(self, token: str) -> bool:
        """Validate basic token format without exposing it"""
        # Telegram tokens are in format: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz
        parts = token.split(':')
        return len(parts) == 2 and parts[0].isdigit() and len(parts[1]) >= 35
    
    async def send_alert(self, chat_id: str, message: str, parse_mode: str = "HTML") -> bool:
        """
        Send alert message to Telegram chat
        
        Args:
            chat_id: Telegram chat ID (obtained when user sends /start to bot)
            message: Alert message text
            parse_mode: Message formatting (HTML or Markdown)
        
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.bot:
            logger.error("Telegram bot not initialized. Check TELEGRAM_BOT_TOKEN in .env")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=parse_mode
            )
            logger.info(f"Alert sent successfully to chat_id: {chat_id[:4]}***")  # Partial ID for privacy
            return True
        except TelegramError as e:
            logger.error(f"Failed to send Telegram alert: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram alert: {str(e)}")
            return False
    
    async def send_bulk_alert(self, chat_ids: List[str], message: str) -> dict:
        """
        Send alert to multiple recipients
        
        Returns:
            dict: {'success': int, 'failed': int, 'total': int}
        """
        if not self.bot:
            return {'success': 0, 'failed': len(chat_ids), 'total': len(chat_ids)}
        
        results = {'success': 0, 'failed': 0, 'total': len(chat_ids)}
        
        for chat_id in chat_ids:
            success = await self.send_alert(chat_id, message)
            if success:
                results['success'] += 1
            else:
                results['failed'] += 1
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.05)
        
        return results
    
    async def get_bot_info(self) -> Optional[dict]:
        """Get bot information for verification (no sensitive data exposed)"""
        if not self.bot:
            return None
        
        try:
            bot_info = await self.bot.get_me()
            return {
                'username': bot_info.username,
                'first_name': bot_info.first_name,
                'can_join_groups': bot_info.can_join_groups,
                'can_read_all_group_messages': bot_info.can_read_all_group_messages
            }
        except TelegramError as e:
            logger.error(f"Failed to get bot info: {str(e)}")
            return None
    
    def format_alert_message(
        self, 
        alert_type: str, 
        tds: float, 
        temp: float, 
        voltage: float,
        threshold: float
    ) -> str:
        """
        Format professional alert message
        
        Args:
            alert_type: 'high_tds', 'high_temp', etc.
            tds: Current TDS value
            temp: Current temperature
            voltage: Current voltage
            threshold: Threshold that was exceeded
        """
        severity_emoji = {
            'high_tds': '🚨',
            'high_temp': '🌡️',
            'low_voltage': '⚡',
            'critical': '🔴'
        }
        
        emoji = severity_emoji.get(alert_type, '⚠️')
        
        message = f"""
{emoji} <b>EVARA TDS ALERT</b> {emoji}

<b>Alert Type:</b> {alert_type.replace('_', ' ').title()}
<b>Threshold Exceeded:</b> {threshold}

<b>Current Readings:</b>
• TDS: <code>{tds:.2f} ppm</code>
• Temperature: <code>{temp:.2f}°C</code>
• Voltage: <code>{voltage:.2f}V</code>

<b>Timestamp:</b> {self._get_timestamp()}

<i>This is an automated alert from Evara TDS Monitoring System</i>
"""
        return message.strip()
    
    def _get_timestamp(self) -> str:
        """Get formatted timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Singleton instance
_telegram_service = None

def get_telegram_service() -> TelegramService:
    """Get or create Telegram service instance"""
    global _telegram_service
    if _telegram_service is None:
        _telegram_service = TelegramService()
    return _telegram_service
