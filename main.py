#!/usr/bin/env python3
import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# تنظیمات لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# اطلاعات ربات
TOKEN = os.environ.get('BOT_TOKEN')

async def start(update: Update, context: CallbackContext):
    """دستور شروع"""
    user = update.effective_user
    await update.message.reply_text(f"✅ ربات فعال شد! سلام {user.first_name}")

def main():
    """تابع اصلی"""
    if not TOKEN:
        print("❌ خطا: BOT_TOKEN تنظیم نشده است!")
        return
        
    print("🤖 در حال راه‌اندازی ربات...")
    
    try:
        # ایجاد اپلیکیشن
        application = Application.builder().token(TOKEN).build()
        
        # اضافه کردن هندلرها
        application.add_handler(CommandHandler("start", start))
        
        # شروع ربات
        print("✅ ربات فعال شد!")
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"❌ خطا در اجرای ربات: {e}")

if __name__ == '__main__':
    main()
