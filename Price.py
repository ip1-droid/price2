#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ربات تلگرام برای قیمت‌ها - با Mock Data ریالی
✅ قیمت‌های ریالی (تومان)
✅ طلا، نقره، دلار، یورو
✅ تغییرات قیمت
"""

import requests
import json
import time
import logging
import os
from datetime import datetime
from urllib3.exceptions import InsecureRequestWarning

# غیرفعال کردن هشدار SSL
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# تنظیمات logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== تنظیمات ==========
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    logger.error("❌ خطا: BOT_TOKEN تنظیم نشده است!")
    logger.error("تنظیمات Railway → Variables → BOT_TOKEN را اضافه کنید")
    exit(1)

TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
UPDATE_OFFSET = 0

# تنظیمات requests
REQUESTS_TIMEOUT = 15
VERIFY_SSL = False

# ========== Mock Data - قیمت‌های ریالی ==========
# این داده‌ها می‌توانند از API‌های واقعی جایگزین شوند

MOCK_PRICES = {
    'gold': {
        'price': 2_850_000,  # تومان (هر گرم)
        'change': 1.5,
        'updated': datetime.now().strftime('%H:%M:%S')
    },
    'silver': {
        'price': 85_000,  # تومان (هر گرم)
        'change': -0.5,
        'updated': datetime.now().strftime('%H:%M:%S')
    },
    'usd': {
        'price': 42_500,  # تومان
        'change': 0.0,
        'updated': datetime.now().strftime('%H:%M:%S')
    },
    'eur': {
        'price': 47_200,  # تومان
        'change': 2.1,
        'updated': datetime.now().strftime('%H:%M:%S')
    }
}

# ========== تابع‌های دریافت قیمت ==========

def get_prices():
    """
    دریافت قیمت‌ها (Mock Data)
    می‌تواند از API واقعی جایگزین شود
    """
    try:
        logger.info("📊 درخواست قیمت‌ها...")
        
        # Update mock prices with current time
        prices = MOCK_PRICES.copy()
        for key in prices:
            prices[key]['updated'] = datetime.now().strftime('%H:%M:%S')
        
        logger.info("✅ قیمت‌ها دریافت شدند")
        return prices
    
    except Exception as e:
        logger.error(f"❌ خطا در دریافت قیمت‌ها: {e}")
        return None

# ========== API تلگرام ==========

def send_message(chat_id, text, reply_markup=None):
    """ارسال پیام"""
    url = f"{TELEGRAM_API_URL}/sendMessage"
    
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    
    try:
        response = requests.post(
            url,
            json=payload,
            timeout=REQUESTS_TIMEOUT,
            verify=VERIFY_SSL
        )
        return response.status_code == 200
    except Exception as e:
        logger.error(f"خطا در ارسال پیام: {e}")
        return False

def get_updates(offset=0):
    """دریافت پیام‌های جدید"""
    url = f"{TELEGRAM_API_URL}/getUpdates"
    
    try:
        response = requests.get(
            url,
            params={'offset': offset, 'timeout': 25},
            timeout=35,
            verify=VERIFY_SSL
        )
        return response.json()
    except Exception as e:
        logger.error(f"خطا در دریافت update‌ها: {e}")
        return {'ok': False}

# ========== صفحه‌کلید ==========

def get_keyboard():
    """ایجاد صفحه‌کلید"""
    return {
        'keyboard': [
            [{'text': '💰 قیمت لحظه‌ای'}],
            [{'text': '🥇 طلا'}, {'text': '🥈 نقره'}],
            [{'text': '💵 دلار'}, {'text': '💶 یورو'}],
            [{'text': 'ℹ️ درباره'}]
        ],
        'resize_keyboard': True
    }

# ========== توابع کمکی ==========

def format_price(price, unit='تومان'):
    """قالب‌بندی قیمت با فاصل"""
    if isinstance(price, (int, float)):
        return f"{int(price):,} {unit}"
    return "N/A"

def get_change_emoji(change):
    """دریافت emoji برای تغییر قیمت"""
    if change > 0:
        return f"📈 +{change}%"
    elif change < 0:
        return f"📉 {change}%"
    else:
        return "➡️ ۰%"

# ========== پیام‌های ربات ==========

def handle_message(message):
    """پردازش پیام‌های دریافتی"""
    chat_id = message['chat']['id']
    text = message.get('text', '').strip()
    
    logger.info(f"پیام از {chat_id}: {text}")
    
    if text == '/start' or text == '/help':
        send_start(chat_id)
    
    elif text == '💰 قیمت لحظه‌ای':
        send_all_prices(chat_id)
    
    elif text == '🥇 طلا':
        send_gold(chat_id)
    
    elif text == '🥈 نقره':
        send_silver(chat_id)
    
    elif text == '💵 دلار':
        send_usd(chat_id)
    
    elif text == '💶 یورو':
        send_eur(chat_id)
    
    elif text == 'ℹ️ درباره':
        send_about(chat_id)
    
    else:
        send_message(chat_id, "لطفاً از دکمه‌های موجود استفاده کنید.", get_keyboard())

def send_start(chat_id):
    """دستور شروع"""
    text = """🤖 به ربات قیمت‌های لحظه‌ای خوش آمدید!

🇮🇷 *قیمت‌های ریالی (تومان):*

• 🥇 طلا (هر گرم)
• 🥈 نقره (هر گرم)
• 💵 دلار آمریکا
• 💶 یورو اروپا

از دکمه‌های زیر استفاده کنید:"""
    
    send_message(chat_id, text, get_keyboard())

def send_all_prices(chat_id):
    """نمایش تمام قیمت‌ها"""
    prices = get_prices()
    
    if not prices:
        send_message(chat_id, "❌ متأسفانه نتوانستم قیمت‌ها را دریافت کنم.\n\nلطفاً دوباره تلاش کنید.", get_keyboard())
        return
    
    text = "📊 *قیمت‌های لحظه‌ای*\n\n"
    
    # طلا
    gold = prices['gold']
    text += f"🥇 *طلا:*\n"
    text += f"   💰 {format_price(gold['price'])}\n"
    text += f"   {get_change_emoji(gold['change'])}\n\n"
    
    # نقره
    silver = prices['silver']
    text += f"🥈 *نقره:*\n"
    text += f"   💰 {format_price(silver['price'])}\n"
    text += f"   {get_change_emoji(silver['change'])}\n\n"
    
    # دلار
    usd = prices['usd']
    text += f"💵 *دلار (USD):*\n"
    text += f"   💰 {format_price(usd['price'])}\n"
    text += f"   {get_change_emoji(usd['change'])}\n\n"
    
    # یورو
    eur = prices['eur']
    text += f"💶 *یورو (EUR):*\n"
    text += f"   💰 {format_price(eur['price'])}\n"
    text += f"   {get_change_emoji(eur['change'])}\n\n"
    
    text += f"🕐 *آپدیت:* {prices['gold']['updated']}\n"
    text += f"📡 *منبع:* Mock Data (برای تست)"
    
    send_message(chat_id, text, get_keyboard())

def send_gold(chat_id):
    """نمایش قیمت طلا"""
    prices = get_prices()
    
    if not prices:
        send_message(chat_id, "❌ نتوانستم قیمت طلا را دریافت کنم.", get_keyboard())
        return
    
    gold = prices['gold']
    text = f"""🥇 *قیمت طلا (هر گرم)*

💰 *قیمت فعلی:* {format_price(gold['price'])}
📊 *تغییر:* {get_change_emoji(gold['change'])}

🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    send_message(chat_id, text, get_keyboard())

def send_silver(chat_id):
    """نمایش قیمت نقره"""
    prices = get_prices()
    
    if not prices:
        send_message(chat_id, "❌ نتوانستم قیمت نقره را دریافت کنم.", get_keyboard())
        return
    
    silver = prices['silver']
    text = f"""🥈 *قیمت نقره (هر گرم)*

💰 *قیمت فعلی:* {format_price(silver['price'])}
📊 *تغییر:* {get_change_emoji(silver['change'])}

🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    send_message(chat_id, text, get_keyboard())

def send_usd(chat_id):
    """نمایش قیمت دلار"""
    prices = get_prices()
    
    if not prices:
        send_message(chat_id, "❌ نتوانستم قیمت دلار را دریافت کنم.", get_keyboard())
        return
    
    usd = prices['usd']
    text = f"""💵 *قیمت دلار آمریکا*

💰 *قیمت فعلی:* {format_price(usd['price'])}
📊 *تغییر:* {get_change_emoji(usd['change'])}

🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    send_message(chat_id, text, get_keyboard())

def send_eur(chat_id):
    """نمایش قیمت یورو"""
    prices = get_prices()
    
    if not prices:
        send_message(chat_id, "❌ نتوانستم قیمت یورو را دریافت کنم.", get_keyboard())
        return
    
    eur = prices['eur']
    text = f"""💶 *قیمت یورو اروپا*

💰 *قیمت فعلی:* {format_price(eur['price'])}
📊 *تغییر:* {get_change_emoji(eur['change'])}

🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    send_message(chat_id, text, get_keyboard())

def send_about(chat_id):
    """درباره ربات"""
    text = """ℹ️ *درباره این ربات*

🤖 *ربات قیمت‌های لحظه‌ای*
نسخه: 5.0 (Railway - Stable)

✨ ویژگی‌ها:
• ✅ قیمت طلا و نقره (ریالی)
• ✅ قیمت دلار و یورو (ریالی)
• ✅ نمایش تغییرات قیمت
• ✅ اجرا در ابر (Railway)
• ✅ 24/7 در دسترس

📊 قیمت‌ها:
• 🥇 طلا: هر گرم
• 🥈 نقره: هر گرم
• 💵 دلار: تومان
• 💶 یورو: تومان

🇮🇷 *تمام قیمت‌ها بر اساس ریال ایران*

⚠️ توجه:
• این نسخه Mock Data استفاده می‌کند
• می‌توان API‌های واقعی را اضافه کرد
• برای معاملات واقعی منابع رسمی را بررسی کنید

👨‍💻 نویسنده: توسعه‌دهنده ایرانی"""
    
    send_message(chat_id, text, get_keyboard())

# ========== حلقه اصلی ==========

def main():
    """برنامه اصلی"""
    global UPDATE_OFFSET
    
    print("=" * 70)
    print("✅ ربات قیمت‌های لحظه‌ای (ریالی) در حال اجرا است...")
    print("☁️  میزبان: Railway.app")
    print("🇮🇷 منبع: Mock Data (قیمت‌های نمونه)")
    print("=" * 70)
    
    error_count = 0
    max_errors = 20
    
    # تست اولیه
    logger.info("🔍 تست سیستم...")
    test_prices = get_prices()
    if test_prices:
        logger.info("✅ سیستم آماده است!")
    else:
        logger.warning("⚠️ هشدار!")
    
    try:
        while True:
            try:
                result = get_updates(UPDATE_OFFSET)
                
                if result.get('ok') and result.get('result'):
                    error_count = 0
                    for update in result['result']:
                        update_id = update['update_id']
                        UPDATE_OFFSET = update_id + 1
                        
                        if 'message' in update:
                            message = update['message']
                            handle_message(message)
                
                time.sleep(0.5)
            
            except requests.exceptions.ConnectionError as e:
                error_count += 1
                logger.warning(f"⚠️ خطای اتصال ({error_count}/{max_errors})")
                time.sleep(5)
            
            except Exception as e:
                error_count += 1
                logger.error(f"❌ خطا ({error_count}/{max_errors}): {str(e)[:50]}...")
                time.sleep(5)
            
            if error_count >= max_errors:
                logger.error(f"❌ بیش از {max_errors} خطا رخ داد.")
                break
    
    except KeyboardInterrupt:
        print("\n\n👋 ربات متوقف شد.")

if __name__ == '__main__':
    main()
        
