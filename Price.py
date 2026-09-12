#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ربات تلگرام برای قیمت‌های واقعی و لحظه‌ای
✅ API‌های واقعی
✅ قیمت‌های لحظه‌ای
✅ قیمت‌های ریالی (تبدیل خودکار)
✅ هیچ mock data نیست
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
    exit(1)

TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
UPDATE_OFFSET = 0

REQUESTS_TIMEOUT = 15
VERIFY_SSL = False

# ========== API‌های واقعی ==========

def get_metals_prices():
    """
    دریافت قیمت‌های طلا و نقره از Metals Live
    قیمت‌ها بر اساس USD/troy oz
    """
    try:
        url = "https://api.metals.live/v1/spot/metals?currency=USD"
        
        response = requests.get(
            url,
            timeout=REQUESTS_TIMEOUT,
            verify=VERIFY_SSL,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # تبدیل troy oz به گرم
            # 1 troy oz = 31.1035 گرم
            gold_per_gram = data.get('gold', 0) / 31.1035
            silver_per_gram = data.get('silver', 0) / 31.1035
            
            return {
                'gold': round(gold_per_gram, 2),
                'silver': round(silver_per_gram, 2),
                'source': 'Metals Live'
            }
    except Exception as e:
        logger.error(f"❌ خطا در دریافت قیمت‌های فلزات: {e}")
    
    return None

def get_currency_rates():
    """
    دریافت نرخ‌های ارز از Open Exchange Rates
    """
    try:
        # API بدون کلید
        url = "https://open.er-api.com/v6/latest/USD"
        
        response = requests.get(
            url,
            timeout=REQUESTS_TIMEOUT,
            verify=VERIFY_SSL,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        if response.status_code == 200:
            data = response.json()
            rates = data.get('rates', {})
            
            return {
                'eur': rates.get('EUR', 0),
                'gbp': rates.get('GBP', 0),
                'jpy': rates.get('JPY', 0),
                'source': 'Open Exchange Rates'
            }
    except Exception as e:
        logger.error(f"❌ خطا در دریافت نرخ‌های ارز: {e}")
    
    # سعی کنید ExchangeRate.host استفاده کنید
    try:
        url = "https://api.exchangerate.host/latest?base=USD&symbols=EUR,GBP,JPY,IRR"
        
        response = requests.get(
            url,
            timeout=REQUESTS_TIMEOUT,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                rates = data.get('rates', {})
                return {
                    'eur': rates.get('EUR', 0),
                    'gbp': rates.get('GBP', 0),
                    'jpy': rates.get('JPY', 0),
                    'irr': rates.get('IRR', 0),
                    'source': 'ExchangeRate Host'
                }
    except Exception as e:
        logger.error(f"❌ خطا در ExchangeRate Host: {e}")
    
    return None

def get_usd_to_irr():
    """
    دریافت نرخ دلار به ریال
    """
    try:
        # سعی کنید از API‌های مختلف دریافت کنید
        url = "https://api.exchangerate.host/latest?base=USD&symbols=IRR"
        
        response = requests.get(
            url,
            timeout=REQUESTS_TIMEOUT,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                irr_rate = data.get('rates', {}).get('IRR', None)
                if irr_rate:
                    return round(irr_rate, 2)
    except Exception as e:
        logger.error(f"❌ خطا: {e}")
    
    return None

def get_all_prices_real():
    """
    دریافت تمام قیمت‌های واقعی و لحظه‌ای
    """
    prices = {}
    
    # دریافت قیمت‌های فلزات
    metals = get_metals_prices()
    if metals:
        prices['metals'] = metals
        logger.info(f"✅ قیمت‌های فلزات: طلا ${metals['gold']}, نقره ${metals['silver']}")
    
    # دریافت نرخ‌های ارز
    rates = get_currency_rates()
    if rates:
        prices['rates'] = rates
        logger.info(f"✅ نرخ‌های ارز: EUR {rates['eur']}, GBP {rates['gbp']}")
    
    # نرخ دلار به ریال
    usd_to_irr = get_usd_to_irr()
    if usd_to_irr:
        prices['usd_to_irr'] = usd_to_irr
        logger.info(f"✅ نرخ دلار: {usd_to_irr} تومان")
    
    prices['updated'] = datetime.now().strftime('%H:%M:%S')
    
    return prices if prices else None

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
    """قالب‌بندی قیمت"""
    if isinstance(price, (int, float)):
        return f"{int(price):,} {unit}"
    return "N/A"

# ========== پیام‌های ربات ==========

def handle_message(message):
    """پردازش پیام‌های دریافتی"""
    chat_id = message['chat']['id']
    text = message.get('text', '').strip()
    
    logger.info(f"پیام: {text}")
    
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

✨ *قیمت‌های واقعی و لحظه‌ای:*

• 🥇 طلا (USD)
• 🥈 نقره (USD)
• 💵 دلار
• 💶 یورو

📡 منابع: Metals Live, Open Exchange Rates

از دکمه‌های زیر استفاده کنید:"""
    
    send_message(chat_id, text, get_keyboard())

def send_all_prices(chat_id):
    """نمایش تمام قیمت‌ها"""
    prices = get_all_prices_real()
    
    if not prices:
        send_message(chat_id, "❌ متأسفانه نتوانستم قیمت‌ها را دریافت کنم.\n\nلطفاً دوباره تلاش کنید.", get_keyboard())
        return
    
    text = "📊 *قیمت‌های لحظه‌ای*\n\n"
    
    # طلا
    if 'metals' in prices:
        metals = prices['metals']
        text += f"🥇 *طلا:*\n"
        text += f"   💰 ${metals['gold']}/گرم (USD)\n"
    
    # نقره
    if 'metals' in prices:
        metals = prices['metals']
        text += f"🥈 *نقره:*\n"
        text += f"   💰 ${metals['silver']}/گرم (USD)\n\n"
    
    # دلار
    if 'usd_to_irr' in prices:
        text += f"💵 *دلار (USD):*\n"
        text += f"   💰 {format_price(prices['usd_to_irr'])}\n\n"
    
    # یورو
    if 'rates' in prices and 'eur' in prices['rates']:
        eur_rate = prices['rates']['eur']
        eur_to_irr = prices.get('usd_to_irr', 0) * eur_rate
        text += f"💶 *یورو (EUR):*\n"
        text += f"   💰 {format_price(eur_to_irr)}\n\n"
    
    text += f"🕐 *آپدیت:* {prices['updated']}\n"
    text += f"📡 *منابع:* Metals Live, Open Exchange Rates"
    
    send_message(chat_id, text, get_keyboard())

def send_gold(chat_id):
    """نمایش قیمت طلا"""
    prices = get_all_prices_real()
    
    if not prices or 'metals' not in prices:
        send_message(chat_id, "❌ نتوانستم قیمت طلا را دریافت کنم.", get_keyboard())
        return
    
    metals = prices['metals']
    gold_price = metals['gold']
    
    # تبدیل به ریال اگر نرخ دلار موجود باشد
    text = f"""🥇 *قیمت طلا*

💰 *قیمت:* ${gold_price}/گرم (USD)"""
    
    if 'usd_to_irr' in prices:
        gold_in_irr = gold_price * prices['usd_to_irr']
        text += f"\n💰 *قیمت ریالی:* {format_price(gold_in_irr)}"
    
    text += f"\n\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    send_message(chat_id, text, get_keyboard())

def send_silver(chat_id):
    """نمایش قیمت نقره"""
    prices = get_all_prices_real()
    
    if not prices or 'metals' not in prices:
        send_message(chat_id, "❌ نتوانستم قیمت نقره را دریافت کنم.", get_keyboard())
        return
    
    metals = prices['metals']
    silver_price = metals['silver']
    
    text = f"""🥈 *قیمت نقره*

💰 *قیمت:* ${silver_price}/گرم (USD)"""
    
    if 'usd_to_irr' in prices:
        silver_in_irr = silver_price * prices['usd_to_irr']
        text += f"\n💰 *قیمت ریالی:* {format_price(silver_in_irr)}"
    
    text += f"\n\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    send_message(chat_id, text, get_keyboard())

def send_usd(chat_id):
    """نمایش قیمت دلار"""
    prices = get_all_prices_real()
    
    if not prices or 'usd_to_irr' not in prices:
        send_message(chat_id, "❌ نتوانستم نرخ دلار را دریافت کنم.", get_keyboard())
        return
    
    usd_price = prices['usd_to_irr']
    
    text = f"""💵 *قیمت دلار (USD)*

💰 *قیمت:* {format_price(usd_price)}

🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    send_message(chat_id, text, get_keyboard())

def send_eur(chat_id):
    """نمایش قیمت یورو"""
    prices = get_all_prices_real()
    
    if not prices or 'rates' not in prices or 'eur' not in prices['rates']:
        send_message(chat_id, "❌ نتوانستم نرخ یورو را دریافت کنم.", get_keyboard())
        return
    
    eur_rate = prices['rates']['eur']
    eur_to_irr = prices.get('usd_to_irr', 0) * eur_rate if 'usd_to_irr' in prices else 0
    
    text = f"""💶 *قیمت یورو (EUR)*

💰 *نرخ تبدیل:* 1 EUR = {eur_rate:.4f} USD"""
    
    if eur_to_irr:
        text += f"\n💰 *قیمت ریالی:* {format_price(eur_to_irr)}"
    
    text += f"\n\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    send_message(chat_id, text, get_keyboard())

def send_about(chat_id):
    """درباره ربات"""
    text = """ℹ️ *درباره این ربات*

🤖 *ربات قیمت‌های لحظه‌ای*
نسخه: 6.0 (Real Prices)

✨ ویژگی‌ها:
• ✅ قیمت‌های طلا و نقره (لحظه‌ای)
• ✅ نرخ‌های ارز (لحظه‌ای)
• ✅ تبدیل خودکار به ریال
• ✅ اجرا در ابر (Railway)
• ✅ بروز رسانی هر بار

📊 منابع داده:
• Metals Live API (طلا، نقره)
• Open Exchange Rates (نرخ‌های ارز)

🕐 *قیمت‌ها هر بار درخواست جدید می‌شوند*

⚠️ توجه:
برای معاملات واقعی منابع رسمی را بررسی کنید."""
    
    send_message(chat_id, text, get_keyboard())

# ========== حلقه اصلی ==========

def main():
    """برنامه اصلی"""
    global UPDATE_OFFSET
    
    print("=" * 70)
    print("✅ ربات قیمت‌های لحظه‌ای (API واقعی) در حال اجرا است...")
    print("☁️  میزبان: Railway.app")
    print("🌍 منابع: Metals Live, Open Exchange Rates")
    print("=" * 70)
    
    error_count = 0
    max_errors = 20
    
    # تست اولیه
    logger.info("🔍 تست اتصال API‌ها...")
    test_prices = get_all_prices_real()
    if test_prices:
        logger.info("✅ تمام API‌ها در دسترس هستند!")
    else:
        logger.warning("⚠️ برخی API‌ها موجود نیستند. ربات ادامه می‌دهد...")
    
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
            
            except requests.exceptions.ConnectionError:
                error_count += 1
                logger.warning(f"⚠️ خطای اتصال ({error_count}/{max_errors})")
                time.sleep(5)
            
            except Exception as e:
                error_count += 1
                logger.error(f"❌ خطا ({error_count}/{max_errors}): {str(e)[:50]}...")
                time.sleep(5)
            
            if error_count >= max_errors:
                logger.error(f"❌ بیش از {max_errors} خطا")
                break
    
    except KeyboardInterrupt:
        print("\n\n👋 ربات متوقف شد.")

if __name__ == '__main__':
    main()
nError as e:
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
        
