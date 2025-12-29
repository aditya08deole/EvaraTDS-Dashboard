"""
Email Alert Service using Brevo (formerly SendinBlue)
Sends automated email alerts when TDS/Temperature thresholds are exceeded
"""

import os
import json
from datetime import datetime, timedelta
from typing import List
import aiohttp
import aiosmtplib
from email.message import EmailMessage
from pathlib import Path

ALERT_LOG_FILE = "backend/data/alert_log.json"
BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")
BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"

# Generic SMTP fallback (works with Sender SMTP credentials)
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_FROM = os.getenv("SMTP_FROM", "alerts@evaratds.com")

# Throttle settings: Don't send more than 1 email per 15 minutes for same alert type
THROTTLE_MINUTES = 15

class EmailAlertService:
    """Handle email alerts with throttling to prevent spam"""
    
    @staticmethod
    def ensure_alert_log():
        """Ensure alert log file exists"""
        Path(ALERT_LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
        if not os.path.exists(ALERT_LOG_FILE):
            with open(ALERT_LOG_FILE, 'w') as f:
                json.dump({"tds_alerts": [], "temp_alerts": []}, f)
    
    @staticmethod
    def load_alert_log():
        """Load alert log from file"""
        EmailAlertService.ensure_alert_log()
        try:
            with open(ALERT_LOG_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {"tds_alerts": [], "temp_alerts": []}
    
    @staticmethod
    def save_alert_log(log_data):
        """Save alert log to file"""
        EmailAlertService.ensure_alert_log()
        with open(ALERT_LOG_FILE, 'w') as f:
            json.dump(log_data, f, indent=2)
    
    @staticmethod
    def should_send_alert(alert_type: str) -> bool:
        """Check if enough time has passed since last alert"""
        log_data = EmailAlertService.load_alert_log()
        alerts = log_data.get(f"{alert_type}_alerts", [])
        
        if not alerts:
            return True
        
        last_alert_str = alerts[-1].get("sent_at")
        if not last_alert_str:
            return True
        
        last_alert = datetime.fromisoformat(last_alert_str)
        time_diff = datetime.utcnow() - last_alert
        
        return time_diff >= timedelta(minutes=THROTTLE_MINUTES)
    
    @staticmethod
    def log_alert(alert_type: str, recipients: List[str], value: float, threshold: float):
        """Log that an alert was sent"""
        log_data = EmailAlertService.load_alert_log()
        
        alert_entry = {
            "sent_at": datetime.utcnow().isoformat(),
            "recipients": recipients,
            "value": value,
            "threshold": threshold
        }
        
        log_data[f"{alert_type}_alerts"].append(alert_entry)
        
        # Keep only last 50 alerts per type
        log_data[f"{alert_type}_alerts"] = log_data[f"{alert_type}_alerts"][-50:]
        
        EmailAlertService.save_alert_log(log_data)
    
    @staticmethod
    async def send_tds_alert(recipients: List[dict], tds_value: float, threshold: float):
        """Send TDS threshold exceeded alert"""
        if not BREVO_API_KEY:
            print("⚠️  BREVO_API_KEY not set - skipping email")
            return False
        
        if not EmailAlertService.should_send_alert("tds"):
            print(f"⏰ TDS alert throttled - last sent within {THROTTLE_MINUTES} minutes")
            return False
        
        subject = f"🚨 CRITICAL: High TDS Detected - {tds_value:.1f} PPM"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
                .container {{ background-color: white; border-radius: 10px; padding: 30px; max-width: 600px; margin: 0 auto; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
                .alert-box {{ background-color: #fee; border-left: 4px solid #f00; padding: 15px; margin: 20px 0; }}
                .metric {{ font-size: 32px; font-weight: bold; color: #f00; }}
                .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚨 Water Quality Alert</h1>
                </div>
                <div class="alert-box">
                    <h2>High TDS Level Detected</h2>
                    <p>The Total Dissolved Solids (TDS) level has exceeded the configured threshold.</p>
                    <p><strong>Current TDS:</strong> <span class="metric">{tds_value:.1f} PPM</span></p>
                    <p><strong>Threshold:</strong> {threshold:.1f} PPM</p>
                    <p><strong>Time:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
                </div>
                <p>⚠️ <strong>Action Required:</strong> Please check the water quality monitoring system and take necessary corrective actions.</p>
                <div class="footer">
                    <p>This is an automated alert from EvaraTDS Monitoring System</p>
                    <p>© 2025 EvaraTech & IIIT Hyderabad</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        success = await EmailAlertService._send_email(recipients, subject, html_content)
        
        if success:
            recipient_emails = [r['email'] for r in recipients]
            EmailAlertService.log_alert("tds", recipient_emails, tds_value, threshold)
        
        return success
    
    @staticmethod
    async def send_temp_alert(recipients: List[dict], temp_value: float, threshold: float):
        """Send Temperature threshold exceeded alert"""
        if not BREVO_API_KEY:
            print("⚠️  BREVO_API_KEY not set - skipping email")
            return False
        
        if not EmailAlertService.should_send_alert("temp"):
            print(f"⏰ Temperature alert throttled - last sent within {THROTTLE_MINUTES} minutes")
            return False
        
        subject = f"🌡️ WARNING: High Temperature Detected - {temp_value:.1f}°C"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
                .container {{ background-color: white; border-radius: 10px; padding: 30px; max-width: 600px; margin: 0 auto; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
                .alert-box {{ background-color: #fff3cd; border-left: 4px solid #ffa500; padding: 15px; margin: 20px 0; }}
                .metric {{ font-size: 32px; font-weight: bold; color: #ffa500; }}
                .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌡️ Temperature Alert</h1>
                </div>
                <div class="alert-box">
                    <h2>High Temperature Detected</h2>
                    <p>The water temperature has exceeded the configured threshold.</p>
                    <p><strong>Current Temperature:</strong> <span class="metric">{temp_value:.1f}°C</span></p>
                    <p><strong>Threshold:</strong> {threshold:.1f}°C</p>
                    <p><strong>Time:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
                </div>
                <p>⚠️ <strong>Action Required:</strong> Please check the water temperature monitoring system and take necessary corrective actions.</p>
                <div class="footer">
                    <p>This is an automated alert from EvaraTDS Monitoring System</p>
                    <p>© 2025 EvaraTech & IIIT Hyderabad</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        success = await EmailAlertService._send_email(recipients, subject, html_content)
        
        if success:
            recipient_emails = [r['email'] for r in recipients]
            EmailAlertService.log_alert("temp", recipient_emails, temp_value, threshold)
        
        return success
    
    @staticmethod
    async def _send_email(recipients: List[dict], subject: str, html_content: str):
        """Send email: prefer Brevo API, fallback to SMTP if configured"""

        # Try Brevo API if key present
        if BREVO_API_KEY:
            try:
                # Prepare recipient list for Brevo
                to_list = [{"email": r['email'], "name": r['name']} for r in recipients]
                payload = {
                    "sender": {"name": "EvaraTDS Monitor", "email": SMTP_FROM},
                    "to": to_list,
                    "subject": subject,
                    "htmlContent": html_content
                }
                headers = {
                    "accept": "application/json",
                    "api-key": BREVO_API_KEY,
                    "content-type": "application/json"
                }
                async with aiohttp.ClientSession() as session:
                    async with session.post(BREVO_API_URL, json=payload, headers=headers) as response:
                        if response.status in [200, 201]:
                            print(f"✅ Email sent successfully via Brevo to {len(to_list)} recipients")
                            return True
                        else:
                            error_text = await response.text()
                            print(f"❌ Brevo send failed: {response.status} - {error_text}")
            except Exception as e:
                print(f"❌ Brevo send error: {str(e)}")

        # Fallback to SMTP if configured
        if SMTP_HOST and SMTP_USER and SMTP_PASS:
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
                print(f"✅ Email sent successfully via SMTP to {len(recipients)} recipients")
                return True
            except Exception as e:
                print(f"❌ SMTP send error: {str(e)}")

        print("⚠️ No email provider configured (BREVO_API_KEY or SMTP settings required)")
        return False
