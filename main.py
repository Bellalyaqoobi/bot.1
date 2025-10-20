#!/usr/bin/env python3
import logging
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import yt_dlp

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# اطلاعات ربات
TOKEN = os.environ.get('BOT_TOKEN', "8004177215:AAFchGqKk5ci7Mb8qlYXBRAnfAuLIrATqzk")
CHANNEL = "kapisa_2"

async def check_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """بررسی عضویت کاربر در کانال"""
    try:
        chat_member = await context.bot.get_chat_member(f"@{CHANNEL}", user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Error checking membership: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """دستور شروع"""
    user = update.effective_user
    user_id = user.id

    # بررسی عضویت
    is_member = await check_membership(user_id, context)

    if not is_member:
        keyboard = [
            [InlineKeyboardButton("📢 عضویت در کانال", url=f"https://t.me/{CHANNEL}")],
            [InlineKeyboardButton("✅ بررسی مجدد عضویت", callback_data="check_membership")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "❌ برای استفاده از ربات باید در کانال عضو شوید:\n"
            f"👉 @{CHANNEL}\n\n"
            "⚠️ پس از عضویت، دکمه 'بررسی مجدد عضویت' را بزنید",
            reply_markup=reply_markup
        )
        return

    welcome_text = f"""
🎵 سلام {user.first_name}!

🤖 ربات دانلود آهنگ از یوتیوب

✨ **راهنما:**
• نام آهنگ را ارسال کنید
• یا لینک یوتیوب را بفرستید

📥 ربات به صورت خودکار آهنگ را پیدا و دانلود می‌کند
    """
    await update.message.reply_text(welcome_text)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """مدیریت دکمه‌ها"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if query.data == "check_membership":
        is_member = await check_membership(user_id, context)

        if is_member:
            await query.edit_message_text(
                "✅ عالی! حالا می‌توانید از ربات استفاده کنید.\n"
                "🎵 نام آهنگ مورد نظر را ارسال کنید..."
            )
        else:
            keyboard = [
                [InlineKeyboardButton("📢 عضویت در کانال", url=f"https://t.me/{CHANNEL}")],
                [InlineKeyboardButton("✅ بررسی مجدد عضویت", callback_data="check_membership")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "❌ هنوز در کانال عضو نشده‌اید!\n"
                f"👉 @{CHANNEL}\n\n"
                "⚠️ پس از عضویت، دکمه 'بررسی مجدد عضویت' را بزنید",
                reply_markup=reply_markup
            )

async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """پردازش جستجوی کاربر"""
    user_id = update.effective_user.id

    # بررسی عضویت
    is_member = await check_membership(user_id, context)

    if not is_member:
        keyboard = [
            [InlineKeyboardButton("📢 عضویت در کانال", url=f"https://t.me/{CHANNEL}")],
            [InlineKeyboardButton("✅ بررسی مجدد عضویت", callback_data="check_membership")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "❌ برای استفاده از ربات باید در کانال عضو شوید:\n"
            f"👉 @{CHANNEL}\n\n"
            "⚠️ پس از عضویت، دکمه 'بررسی مجدد عضویت' را بزنید",
            reply_markup=reply_markup
        )
        return

    query = update.message.text.strip()

    if not query:
        await update.message.reply_text("❌ لطفاً نام آهنگ را وارد کنید")
        return

    # ارسال پیام وضعیت
    status_msg = await update.message.reply_text("🔍 در حال جستجو در یوتیوب...")

    try:
        # تنظیمات yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True
        }

        # ایجاد پوشه downloads
        os.makedirs('downloads', exist_ok=True)

        # جستجو یا پردازش لینک
        if query.startswith(('http://', 'https://', 'youtube.com', 'youtu.be')):
            video_url = query
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(video_url, download=False)
                title = info.get('title', 'Audio')
        else:
            await status_msg.edit_text("🔍 در حال جستجو...")
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(f"ytsearch1:{query}", download=False)
                if not info['entries']:
                    await status_msg.edit_text("❌ هیچ آهنگی پیدا نشد!")
                    return
                video_url = info['entries'][0]['webpage_url']
                title = info['entries'][0]['title']

        await status_msg.edit_text(f"🎵 پیدا شد: {title}\n📥 در حال دانلود...")

        # دانلود فایل
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            mp3_file = filename.rsplit('.', 1)[0] + '.mp3'

        await status_msg.edit_text("📤 در حال آپلود...")

        # ارسال فایل صوتی
        with open(mp3_file, 'rb') as audio:
            await update.message.reply_audio(
                audio=audio,
                title=title[:64],
                performer="YouTube",
                caption=f"🎵 {title}"
            )

        await status_msg.delete()

        # حذف فایل موقت
        try:
            os.remove(mp3_file)
        except Exception as e:
            logger.error(f"Error deleting file: {e}")

    except Exception as e:
        logger.error(f"Error: {e}")
        await status_msg.edit_text("❌ خطا در پردازش! لطفاً دوباره تلاش کنید.")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """مدیریت خطاها"""
    logger.error(f"Update {update} caused error {context.error}")

def main() -> None:
    """تابع اصلی"""
    print("🤖 در حال راه‌اندازی ربات...")
    
    if not TOKEN:
        print("❌ خطا: BOT_TOKEN تنظیم نشده است!")
        return

    try:
        # ایجاد اپلیکیشن
        application = Application.builder().token(TOKEN).build()

        # اضافه کردن هندلرها
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search))

        # مدیریت خطاها
        application.add_error_handler(error_handler)

        # شروع ربات
        print("✅ ربات فعال شد!")
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"❌ خطا در راه‌اندازی ربات: {e}")

if __name__ == '__main__':
    main()
