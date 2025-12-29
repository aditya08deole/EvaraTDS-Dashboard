"""
Professional Email Alert Service
Supports: IFTTT Webhooks (primary), SMTP (fallback)
Uses SQLite database for recipients and alert logging
"""

import os
from datetime import datetime, timedelta
from typing import List, Tuple
import aiohttp
import aiosmtplib
from email.message import EmailMessage
import logging

# Import database layer
try:
    from app.database.db import AlertLogDB
except ImportError:
    from database.db import AlertLogDB

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# IFTTT Webhook configuration (primary method)
IFTTT_WEBHOOK_KEY = os.getenv("IFTTT_WEBHOOK_KEY", "")
IFTTT_EVENT_TDS = os.getenv("IFTTT_EVENT_TDS", "evara_tds_alert")
IFTTT_EVENT_TEMP = os.getenv("IFTTT_EVENT_TEMP", "evara_temp_alert")

# SMTP configuration (fallback method)
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_FROM = os.getenv("SMTP_FROM", "alerts@evaratds.com")

# Throttle settings
THROTTLE_MINUTES = int(os.getenv("ALERT_THROTTLE_MINUTES", "15"))


class EmailAlertService:
    """Professional email alert service with IFTTT and SMTP support"""
    
    @staticmethod
    def should_send_alert(alert_type: str) -> bool:
        """Check if enough time has passed since last alert (database-backed)"""
        try:
            last_alert = AlertLogDB.get_last_alert(alert_type)
            
            if not last_alert:
                return True
            
            last_sent = datetime.fromisoformat(last_alert['sent_at'])
            time_diff = datetime.utcnow() - last_sent
            
            should_send = time_diff >= timedelta(minutes=THROTTLE_MINUTES)
            if not should_send:
                logger.info(f"⏰ {alert_type.upper()} alert throttled - last sent {int(time_diff.total_seconds()/60)} minutes ago")
            return should_send
        except Exception as e:
            logger.error(f"Error checking throttle: {e}")
            return True  # Fail open - allow alert on error
    
    @staticmethod
    async def send_tds_alert(recipients: List[dict], tds_value: float, threshold: float) -> bool:
        """Send TDS threshold exceeded alert via IFTTT or SMTP"""
        if not recipients:
            logger.warning("No recipients configured")
            return False
        
        if not EmailAlertService.should_send_alert("tds"):
            return False
        
        subject = f"🚨 CRITICAL: High TDS Detected - {tds_value:.1f} PPM"
        html_content = EmailAlertService._generate_tds_email(tds_value, threshold)
        
        # Try IFTTT first, then SMTP fallback
        method, success = await EmailAlertService._send_via_ifttt(
            IFTTT_EVENT_TDS, tds_value, threshold, "TDS", "PPM", recipients
        )
        
        if not success and (SMTP_HOST and SMTP_USER and SMTP_PASS):
            method, success = await EmailAlertService._send_via_smtp(recipients, subject, html_content)
        
        # Log to database
        recipient_emails = [r['email'] for r in recipients]
        status = "success" if success else "failed"
        AlertLogDB.add("tds", tds_value, threshold, recipient_emails, method, status)
        
        return success
    
    @staticmethod
    async def send_temp_alert(recipients: List[dict], temp_value: float, threshold: float) -> bool:
        """Send Temperature threshold exceeded alert via IFTTT or SMTP"""
        if not recipients:
            logger.warning("No recipients configured")
            return False
        
        if not EmailAlertService.should_send_alert("temp"):
            return False
        
        subject = f"🌡️ WARNING: High Temperature Detected - {temp_value:.1f}°C"
        html_content = EmailAlertService._generate_temp_email(temp_value, threshold)
        
        # Try IFTTT first, then SMTP fallback
        method, success = await EmailAlertService._send_via_ifttt(
            IFTTT_EVENT_TEMP, temp_value, threshold, "Temperature", "°C", recipients
        )
        
        if not success and (SMTP_HOST and SMTP_USER and SMTP_PASS):
            method, success = await EmailAlertService._send_via_smtp(recipients, subject, html_content)
        
        # Log to database
        recipient_emails = [r['email'] for r in recipients]
        status = "success" if success else "failed"
        AlertLogDB.add("temp", temp_value, threshold, recipient_emails, method, status)
        
        return success
    
    @staticmethod
    async def _send_via_ifttt(event_name: str, value: float, threshold: float, 
                             metric_name: str, unit: str, recipients: List[dict]) -> Tuple[str, bool]:
        """Send alert via IFTTT Webhooks"""
        if not IFTTT_WEBHOOK_KEY:
            return ("ifttt", False)
        
        url = f"https://maker.ifttt.com/trigger/{event_name}/with/key/{IFTTT_WEBHOOK_KEY}"
        
        # IFTTT webhook payload (value1, value2, value3)
        payload = {
            "value1": f"{metric_name}: {value:.1f} {unit}",
            "value2": f"Threshold: {threshold:.1f} {unit}",
            "value3": ", ".join([r['email'] for r in recipients])
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"✅ Alert sent via IFTTT to {len(recipients)} recipients")
                        return ("ifttt", True)
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ IFTTT send failed: {response.status} - {error_text}")
                        return ("ifttt", False)
        except Exception as e:
            logger.error(f"❌ IFTTT send error: {str(e)}")
            return ("ifttt", False)
    
    @staticmethod
    async def _send_via_smtp(recipients: List[dict], subject: str, html_content: str) -> Tuple[str, bool]:
        """Send email via SMTP"""
        try:
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = SMTP_FROM
            msg['To'] = ', '.join([r['email'] for r in recipients])
            msg.set_content('This email requires an HTML-capable client.')
            msg.add_alternative(html_content, subtype='html')

            await aiosmtplib.send(
                msg,
                hostname=SMTP_HOST,
                port=SMTP_PORT,
                username=SMTP_USER,
                password=SMTP_PASS,
                start_tls=(SMTP_PORT == 587)
            )
            logger.info(f"✅ Email sent via SMTP to {len(recipients)} recipients")
            return ("smtp", True)
        except Exception as e:
            logger.error(f"❌ SMTP send error: {str(e)}")
            return ("smtp", False)
    
    @staticmethod
    def _generate_tds_email(tds_value: float, threshold: float) -> str:
        """Generate professional HTML email for TDS alert"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; margin: 0; }}
                .container {{ background-color: white; border-radius: 12px; padding: 30px; max-width: 600px; margin: 0 auto; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 24px; border-radius: 12px 12px 0 0; text-align: center; margin: -30px -30px 20px -30px; }}
                .alert-box {{ background-color: #fee; border-left: 5px solid #f00; padding: 20px; margin: 20px 0; border-radius: 4px; }}
                .metric {{ font-size: 36px; font-weight: bold; color: #f00; margin: 10px 0; }}
                .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }}
                .info {{ background-color: #f8f9fa; padding: 15px; border-radius: 4px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">🚨 Water Quality Alert</h1>
                    <p style="margin: 8px 0 0 0; opacity: 0.9;">EvaraTDS Monitoring System</p>
                </div>
                <div class="alert-box">
                    <h2 style="margin: 0 0 15px 0; color: #d32f2f;">High TDS Level Detected</h2>
                    <p style="margin: 10px 0;">The Total Dissolved Solids (TDS) level has exceeded the configured threshold.</p>
                    <div class="metric">{tds_value:.1f} PPM</div>
                    <div class="info">
                        <p style="margin: 5px 0;"><strong>Threshold:</strong> {threshold:.1f} PPM</p>
                        <p style="margin: 5px 0;"><strong>Timestamp:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
                        <p style="margin: 5px 0;"><strong>Severity:</strong> Critical</p>
                    </div>
                </div>
                <div style="background-color: #fff3cd; border-left: 5px solid #ffc107; padding: 15px; border-radius: 4px;">
                    <p style="margin: 0;"><strong>⚠️ Action Required:</strong> Please check the water quality monitoring system immediately and take necessary corrective actions.</p>
                </div>
                <div class="footer">
                    <p style="margin: 5px 0;">This is an automated alert from EvaraTDS Monitoring System</p>
                    <p style="margin: 5px 0;">© 2025 EvaraTech & IIIT Hyderabad</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    @staticmethod
    def _generate_temp_email(temp_value: float, threshold: float) -> str:
        """Generate professional HTML email for Temperature alert"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; margin: 0; }}
                .container {{ background-color: white; border-radius: 12px; padding: 30px; max-width: 600px; margin: 0 auto; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }}
                .header {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 24px; border-radius: 12px 12px 0 0; text-align: center; margin: -30px -30px 20px -30px; }}
                .alert-box {{ background-color: #fff3cd; border-left: 5px solid #ffa500; padding: 20px; margin: 20px 0; border-radius: 4px; }}
                .metric {{ font-size: 36px; font-weight: bold; color: #ffa500; margin: 10px 0; }}
                .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }}
                .info {{ background-color: #f8f9fa; padding: 15px; border-radius: 4px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">🌡️ Temperature Alert</h1>
                    <p style="margin: 8px 0 0 0; opacity: 0.9;">EvaraTDS Monitoring System</p>
                </div>
                <div class="alert-box">
                    <h2 style="margin: 0 0 15px 0; color: #f57c00;">High Temperature Detected</h2>
                    <p style="margin: 10px 0;">The water temperature has exceeded the configured threshold.</p>
                    <div class="metric">{temp_value:.1f}°C</div>
                    <div class="info">
                        <p style="margin: 5px 0;"><strong>Threshold:</strong> {threshold:.1f}°C</p>
                        <p style="margin: 5px 0;"><strong>Timestamp:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
                        <p style="margin: 5px 0;"><strong>Severity:</strong> Warning</p>
                    </div>
                </div>
                <div style="background-color: #e3f2fd; border-left: 5px solid #2196f3; padding: 15px; border-radius: 4px;">
                    <p style="margin: 0;"><strong>ℹ️ Action Required:</strong> Please check the water temperature monitoring system and take necessary corrective actions.</p>
                </div>
                <div class="footer">
                    <p style="margin: 5px 0;">This is an automated alert from EvaraTDS Monitoring System</p>
                    <p style="margin: 5px 0;">© 2025 EvaraTech & IIIT Hyderabad</p>
                </div>
            </div>
        </body>
        </html>
        """
