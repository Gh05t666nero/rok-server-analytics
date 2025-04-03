# utils/telegram_bot.py
import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from utils.notification import NotificationManager

# Konfigurasi logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Inisialisasi notification manager
notification_manager = NotificationManager()


# Command handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Perintah /start untuk memulai interaksi dengan bot."""
    user_id = update.effective_user.id
    username = update.effective_user.username or "pengguna"

    await update.message.reply_text(
        f"Halo {username}! 👋\n\n"
        f"Selamat datang di Bot Notifikasi ROK Server.\n\n"
        f"Bot ini akan mengirimkan notifikasi saat server baru akan dibuka di Rise of Kingdoms.\n\n"
        f"Perintah yang tersedia:\n"
        f"• /subscribe - Berlangganan notifikasi\n"
        f"• /unsubscribe - Berhenti berlangganan\n"
        f"• /status - Cek status langganan\n"
        f"• /help - Melihat bantuan"
    )
    logger.info(f"User {user_id} started the bot")


async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Perintah /subscribe untuk berlangganan notifikasi."""
    user_id = update.effective_user.id
    username = update.effective_user.username or "pengguna"

    # Tambahkan user ke daftar subscriber
    success = notification_manager.add_telegram_subscriber(user_id)

    if success:
        await update.message.reply_text(
            f"✅ Berhasil berlangganan!\n\n"
            f"Anda akan menerima notifikasi saat server baru akan dibuka di Rise of Kingdoms.\n\n"
            f"Gunakan /unsubscribe untuk berhenti berlangganan kapan saja."
        )
        logger.info(f"User {user_id} subscribed to notifications")
    else:
        await update.message.reply_text(
            f"ℹ️ Anda sudah berlangganan notifikasi.\n\n"
            f"Gunakan /unsubscribe untuk berhenti berlangganan."
        )
        logger.info(f"User {user_id} attempted to subscribe but was already subscribed")


async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Perintah /unsubscribe untuk berhenti berlangganan notifikasi."""
    user_id = update.effective_user.id
    username = update.effective_user.username or "pengguna"

    # Hapus user dari daftar subscriber
    success = notification_manager.remove_telegram_subscriber(user_id)

    if success:
        await update.message.reply_text(
            f"✅ Anda telah berhenti berlangganan.\n\n"
            f"Anda tidak akan menerima notifikasi server ROK lagi.\n\n"
            f"Gunakan /subscribe untuk berlangganan kembali kapan saja."
        )
        logger.info(f"User {user_id} unsubscribed from notifications")
    else:
        await update.message.reply_text(
            f"ℹ️ Anda tidak berlangganan notifikasi.\n\n"
            f"Gunakan /subscribe untuk mulai berlangganan."
        )
        logger.info(f"User {user_id} attempted to unsubscribe but was not subscribed")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Perintah /status untuk memeriksa status langganan."""
    user_id = update.effective_user.id
    username = update.effective_user.username or "pengguna"

    # Periksa apakah user ada dalam daftar subscriber
    is_subscribed = user_id in notification_manager.subscribers.get("telegram", [])

    if is_subscribed:
        await update.message.reply_text(
            f"✅ Status: Berlangganan Aktif\n\n"
            f"Anda akan menerima notifikasi saat server baru akan dibuka."
        )
    else:
        await update.message.reply_text(
            f"❌ Status: Tidak Berlangganan\n\n"
            f"Anda tidak akan menerima notifikasi.\n"
            f"Gunakan /subscribe untuk mulai berlangganan."
        )
    logger.info(f"User {user_id} checked subscription status: {is_subscribed}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Perintah /help untuk melihat bantuan."""
    await update.message.reply_text(
        f"🤖 Bot Notifikasi ROK Server\n\n"
        f"Bot ini akan mengirimkan notifikasi tentang pembukaan server baru di Rise of Kingdoms.\n\n"
        f"Perintah yang tersedia:\n"
        f"• /start - Mulai bot\n"
        f"• /subscribe - Berlangganan notifikasi\n"
        f"• /unsubscribe - Berhenti berlangganan\n"
        f"• /status - Cek status langganan\n"
        f"• /help - Melihat bantuan\n\n"
        f"Untuk informasi lebih lanjut, kunjungi dashboard kami di:\n"
        f"https://riseofkingdoms.streamlit.app/"
    )
    logger.info(f"User {update.effective_user.id} requested help")


def run_bot():
    """
    Menjalankan bot Telegram dalam mode polling.
    Gunakan fungsi ini untuk menjalankan bot secara terpisah dari aplikasi Streamlit.
    """
    # Ambil token dari variabel lingkungan
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        print("Error: TELEGRAM_BOT_TOKEN not found in environment variables")
        return

    application = ApplicationBuilder().token(token).build()

    # Tambahkan command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("subscribe", subscribe_command))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("help", help_command))

    # Jalankan bot
    print("Starting Telegram bot...")
    application.run_polling()


if __name__ == "__main__":
    run_bot()