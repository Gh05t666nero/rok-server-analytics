# utils/notification.py
import os
import json
import logging
import re
from datetime import datetime
import streamlit as st
from config import NOTIFICATION_CONFIG
import asyncio
import nest_asyncio

# Aktifkan nest_asyncio untuk mengatasi masalah "no current event loop"
try:
    nest_asyncio.apply()
except:
    pass

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class NotificationManager:
    """
    Manajer untuk sistem notifikasi server Rise of Kingdoms.
    Mendukung notifikasi email dan Telegram untuk pembukaan server baru.
    """

    def __init__(self):
        """Initialize notification manager with configuration."""
        self.log = logging.getLogger("notification_manager")

        # Pastikan direktori data ada
        os.makedirs('data', exist_ok=True)

        self.subscribers_file = NOTIFICATION_CONFIG.get("subscribers_file", "data/subscribers.json")
        self.subscribers = self._load_subscribers()

        # Email setup - hanya inisialisasi jika API key tersedia
        self.sendgrid_api_key = NOTIFICATION_CONFIG.get("sendgrid_api_key")
        self.sender_email = NOTIFICATION_CONFIG.get("sender_email", "noreply@rokanalytics.com")
        self.sender_name = NOTIFICATION_CONFIG.get("sender_name", "ROK Server Analytics")

        # Telegram setup - hanya inisialisasi jika token tersedia
        self.telegram_token = NOTIFICATION_CONFIG.get("telegram_token")
        self.telegram_channel_id = NOTIFICATION_CONFIG.get("telegram_channel_id")

        # Tambahkan timestamp terakhir notifikasi untuk rate limiting
        self.last_notification_sent = {}

    def _load_subscribers(self):
        """Load subscribers from JSON file."""
        if not os.path.exists(self.subscribers_file):
            # Create directory if not exists
            os.makedirs(os.path.dirname(self.subscribers_file), exist_ok=True)
            # Create empty subscribers file
            with open(self.subscribers_file, 'w') as f:
                json.dump({"email": [], "telegram": []}, f)
            return {"email": [], "telegram": []}

        try:
            with open(self.subscribers_file, 'r') as f:
                data = json.load(f)
                # Validasi struktur data
                if not isinstance(data, dict):
                    self.log.error("Invalid subscribers data structure")
                    return {"email": [], "telegram": []}

                # Pastikan memiliki kunci yang diharapkan
                if "email" not in data:
                    data["email"] = []
                if "telegram" not in data:
                    data["telegram"] = []

                return data
        except Exception as e:
            self.log.error(f"Error loading subscribers: {e}")
            return {"email": [], "telegram": []}

    def _save_subscribers(self):
        """Save subscribers to JSON file."""
        try:
            # Gunakan atomic write untuk menghindari corrupt file
            temp_file = f"{self.subscribers_file}.tmp"
            with open(temp_file, 'w') as f:
                json.dump(self.subscribers, f)

            # Rename untuk atomic replace
            os.replace(temp_file, self.subscribers_file)
            return True
        except Exception as e:
            self.log.error(f"Error saving subscribers: {e}")
            return False

    def add_email_subscriber(self, email):
        """
        Add a new email subscriber.

        Parameters:
            email (str): Email address to subscribe

        Returns:
            bool: Success status
        """
        # Sanitasi dan validasi email
        email = email.strip().lower()
        if not self._validate_email(email):
            return False

        # Check for rate limiting (maksimal 5 pendaftaran per email per hari)
        current_time = datetime.now().timestamp()
        rate_key = f"email_subscribe_{email}"

        if rate_key in self.last_notification_sent:
            # Cek jika pendaftaran terakhir kurang dari 24 jam yang lalu
            time_diff = current_time - self.last_notification_sent[rate_key]
            if time_diff < 86400:  # 24 jam dalam detik
                self.log.warning(f"Rate limit exceeded for email subscription: {email}")
                return False

        # Mencegah duplikasi
        if email not in self.subscribers["email"]:
            self.subscribers["email"].append(email)
            success = self._save_subscribers()
            if success:
                # Update rate limiting timestamp
                self.last_notification_sent[rate_key] = current_time
                self.log.info(f"Added new email subscriber: {email}")
                return True
        return False

    def add_telegram_subscriber(self, telegram_id):
        """
        Add a new Telegram subscriber.

        Parameters:
            telegram_id (int or str): Telegram user ID to subscribe

        Returns:
            bool: Success status
        """
        # Validasi telegram_id
        try:
            # Konversi ke int jika string
            if isinstance(telegram_id, str):
                telegram_id = int(telegram_id)
        except (ValueError, TypeError):
            self.log.error(f"Invalid Telegram ID: {telegram_id}")
            return False

        # Check for rate limiting
        current_time = datetime.now().timestamp()
        rate_key = f"telegram_subscribe_{telegram_id}"

        if rate_key in self.last_notification_sent:
            time_diff = current_time - self.last_notification_sent[rate_key]
            if time_diff < 86400:  # 24 jam dalam detik
                self.log.warning(f"Rate limit exceeded for Telegram subscription: {telegram_id}")
                return False

        # Mencegah duplikasi
        if telegram_id not in self.subscribers["telegram"]:
            self.subscribers["telegram"].append(telegram_id)
            success = self._save_subscribers()
            if success:
                self.last_notification_sent[rate_key] = current_time
                self.log.info(f"Added new Telegram subscriber: {telegram_id}")
                return True
        return False

    def remove_email_subscriber(self, email):
        """
        Remove an email subscriber.

        Parameters:
            email (str): Email address to unsubscribe

        Returns:
            bool: Success status
        """
        # Sanitasi email
        email = email.strip().lower()
        if not self._validate_email(email):
            return False

        if email in self.subscribers["email"]:
            self.subscribers["email"].remove(email)
            success = self._save_subscribers()
            if success:
                self.log.info(f"Removed email subscriber: {email}")
                return True
        return False

    def remove_telegram_subscriber(self, telegram_id):
        """
        Remove a Telegram subscriber.

        Parameters:
            telegram_id (int): Telegram user ID to unsubscribe

        Returns:
            bool: Success status
        """
        # Validasi telegram_id
        try:
            # Konversi ke int jika string
            if isinstance(telegram_id, str):
                telegram_id = int(telegram_id)
        except (ValueError, TypeError):
            self.log.error(f"Invalid Telegram ID: {telegram_id}")
            return False

        if telegram_id in self.subscribers["telegram"]:
            self.subscribers["telegram"].remove(telegram_id)
            success = self._save_subscribers()
            if success:
                self.log.info(f"Removed Telegram subscriber: {telegram_id}")
                return True
        return False

    def _validate_email(self, email):
        """
        Validate email format.

        Parameters:
            email (str): Email address to validate

        Returns:
            bool: Validation result
        """
        if not email or not isinstance(email, str):
            return False

        # RFC 5322 compliant regex pattern for email validation
        pattern = r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
        return bool(re.match(pattern, email))

    def _send_telegram_message(self, chat_id, message):
        """
        Helper method to send a single Telegram message synchronously.
        This is a synchronous wrapper around the async Telegram API.

        Parameters:
            chat_id (int or str): Telegram chat ID to send message to
            message (str): Message content

        Returns:
            bool: Success status
        """
        if not self.telegram_token:
            self.log.error("Telegram token not configured")
            return False

        try:
            # Import libraries only when needed
            import telegram

            # Prepare the async function
            async def send_message_async():
                try:
                    bot = telegram.Bot(token=self.telegram_token)
                    await bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                    return True
                except Exception as e:
                    self.log.error(f"Error sending Telegram message to {chat_id}: {e}")
                    return False

            # Use the event loop properly
            try:
                # Try to get the current event loop
                loop = asyncio.get_event_loop()
            except RuntimeError:
                # If there's no event loop in this thread, create one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            # Run the async function
            if loop.is_running():
                # We're in an async context, create a task
                future = asyncio.run_coroutine_threadsafe(send_message_async(), loop)
                return future.result(10)  # Wait up to 10 seconds
            else:
                # We're not in an async context, run it directly
                return loop.run_until_complete(send_message_async())

        except ImportError:
            self.log.error("Telegram package not installed")
            return False
        except Exception as e:
            self.log.error(f"Error in Telegram message sending: {e}")
            return False

    def send_telegram_notification(self, message):
        """
        Send notification to all Telegram subscribers.
        This is a synchronous method that handles async operations internally.

        Parameters:
            message (str): Message to send

        Returns:
            bool: Success status
        """
        if not self.telegram_token:
            self.log.error("Telegram token not configured")
            return False

        # Check for rate limiting (maksimal 1 notifikasi setiap jam)
        current_time = datetime.now().timestamp()
        rate_key = "telegram_notification"

        if rate_key in self.last_notification_sent:
            time_diff = current_time - self.last_notification_sent[rate_key]
            if time_diff < 3600:  # 1 jam dalam detik
                self.log.warning("Rate limit exceeded for Telegram notifications")
                return False

        success = False

        # Send to channel if configured
        if self.telegram_channel_id:
            channel_success = self._send_telegram_message(
                self.telegram_channel_id,
                message
            )
            if channel_success:
                success = True

        # Send to individual subscribers
        for user_id in self.subscribers.get("telegram", []):
            try:
                user_success = self._send_telegram_message(user_id, message)
                if user_success:
                    success = True
            except Exception as e:
                self.log.error(f"Error sending Telegram message to {user_id}: {e}")

        if success:
            self.last_notification_sent[rate_key] = current_time

        return success

    def send_email_notification(self, subject, message):
        """
        Send notification to all email subscribers.

        Parameters:
            subject (str): Email subject
            message (str): Email content

        Returns:
            bool: Success status
        """
        if not self.sendgrid_api_key:
            self.log.error("SendGrid API key not configured")
            return False

        # Check for rate limiting (maksimal 1 email setiap jam)
        current_time = datetime.now().timestamp()
        rate_key = "email_notification"

        if rate_key in self.last_notification_sent:
            time_diff = current_time - self.last_notification_sent[rate_key]
            if time_diff < 3600:  # 1 jam dalam detik
                self.log.warning("Rate limit exceeded for email notifications")
                return False

        try:
            # Import sendgrid di dalam fungsi untuk menghindari error jika tidak terinstall
            import sendgrid
            from sendgrid.helpers.mail import Mail, Email, To, Content

            sg = sendgrid.SendGridAPIClient(api_key=self.sendgrid_api_key)

            from_email = Email(self.sender_email, self.sender_name)
            content = Content("text/html", message)

            # Batasi jumlah email yang dikirim dalam satu batch
            batch_size = 50
            success = False

            # Send to each subscriber in batches
            email_subscribers = self.subscribers.get("email", [])
            for i in range(0, len(email_subscribers), batch_size):
                batch = email_subscribers[i:i + batch_size]

                for email in batch:
                    try:
                        # Sanitasi email
                        email = email.strip().lower()
                        if not self._validate_email(email):
                            continue

                        to_email = To(email)
                        mail = Mail(from_email, to_email, subject, content)
                        response = sg.client.mail.send.post(request_body=mail.get())

                        if response.status_code in [200, 201, 202]:
                            success = True
                        else:
                            self.log.error(f"Error sending to {email}: {response.status_code}")
                    except Exception as e:
                        self.log.error(f"Error sending email to {email}: {e}")

            if success:
                self.last_notification_sent[rate_key] = current_time

            return success
        except ImportError:
            self.log.error("SendGrid package not installed")
            return False
        except Exception as e:
            self.log.error(f"Error sending email notifications: {e}")
            return False

    def notify_new_server(self, server_data):
        """
        Send notifications about new server opening.

        Parameters:
            server_data (dict): Server details including ID, date, time, and map type

        Returns:
            bool: Success status
        """
        # Validasi data server
        required_fields = ['ServerId', 'Tanggal', 'Jam', 'MapType', 'DistrictId', 'Estimasi']
        if not all(field in server_data for field in required_fields):
            self.log.error(f"Invalid server data: {server_data}")
            return False

        # Sanitasi data untuk keamanan
        for field in required_fields:
            if isinstance(server_data[field], str):
                server_data[field] = self._sanitize_html(server_data[field])

        # Format email content
        email_subject = f"Server Baru ROK #{server_data['ServerId']} akan Dibuka Segera!"
        email_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #6200EE; color: white; padding: 10px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .server-info {{ margin: 20px 0; }}
                .server-info span {{ font-weight: bold; color: #6200EE; }}
                .footer {{ font-size: 12px; text-align: center; margin-top: 30px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Server Baru Rise of Kingdoms!</h2>
                </div>
                <div class="content">
                    <p>Halo Gubernur,</p>
                    <p>Server baru akan segera dibuka di Rise of Kingdoms. Berikut adalah detailnya:</p>

                    <div class="server-info">
                        <p>ID Server: <span>{server_data['ServerId']}</span></p>
                        <p>Tanggal: <span>{server_data['Tanggal']}</span></p>
                        <p>Jam: <span>{server_data['Jam']}</span></p>
                        <p>Jenis Peta: <span>{server_data['MapType']}</span></p>
                        <p>ID District: <span>{server_data['DistrictId']}</span></p>
                    </div>

                    <p>Perkiraan waktu pembukaan: <strong>{server_data['Estimasi']}</strong></p>
                    <p>Jangan lewatkan kesempatan untuk memulai di server baru!</p>
                </div>
                <div class="footer">
                    <p>Email ini dikirim dari ROK Server Analytics.</p>
                    <p>Untuk berhenti berlangganan, kunjungi dashboard dan batalkan berlangganan.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Format Telegram content
        telegram_content = f"""
*🚨 Server Baru ROK akan Dibuka! 🚨*

📋 *Detail Server:*
• ID Server: `{server_data['ServerId']}`
• Tanggal: `{server_data['Tanggal']}`
• Jam: `{server_data['Jam']}`
• Jenis Peta: `{server_data['MapType']}`
• ID District: `{server_data['DistrictId']}`

⏱️ Perkiraan: *{server_data['Estimasi']}*

Bersiaplah untuk petualangan baru di Rise of Kingdoms!
        """

        # Send notifications (both are now synchronous)
        email_success = self.send_email_notification(email_subject, email_content)
        telegram_success = self.send_telegram_notification(telegram_content)

        return email_success or telegram_success

    def _sanitize_html(self, text):
        """
        Sanitize HTML input to prevent XSS.

        Parameters:
            text (str): Text to sanitize

        Returns:
            str: Sanitized text
        """
        if not isinstance(text, str):
            return str(text)

        # Replace potentially dangerous characters
        return text.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')