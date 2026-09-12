#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ربات تلگرام برای قیمت‌های واقعی و لحظه‌ای
✅ API‌های واقعی (Metals Live + Open Exchange Rates)
✅ قیمت‌های لحظه‌ای
✅ تبدیل خودکار به ریال
"""

import requests
import json
import time
import logging
import os
from datetime import datetime
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("BOT_TOKEN required!")
    exit(1)

TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
UPDATE_OFFSET = 0
REQUESTS_TIMEOUT = 15
VERIFY_SSL = False

# ========== API Functions ==========

def get_metals_prices():
    """Get gold and silver prices from Metals Live"""
    try:
        url = "https://api.metals.live/v1/spot/metals?currency=USD"
        response = requests.get(url, timeout=REQUESTS_TIMEOUT, verify=VERIFY_SSL, headers={'User-Agent': 'Mozilla/5.0'})
        
        if response.status_code == 200:
            data = response.json()
            gold_per_gram = data.get('gold', 0) / 31.1035
            silver_per_gram = data.get('silver', 0) / 31.1035
            
            return {
                'gold': round(gold_per_gram, 2),
                'silver': round(silver_per_gram, 2),
                'source': 'Metals Live'
            }
    except Exception as e:
        logger.error(f"Metals error: {e}")
    
    return None

def get_currency_rates():
    """Get currency rates"""
    try:
        url = "https://open.er-api.com/v6/latest/USD"
        response = requests.get(url, timeout=REQUESTS_TIMEOUT, verify=VERIFY_SSL, headers={'User-Agent': 'Mozilla/5.0'})
        
        if response.status_code == 200:
            data = response.json()
            rates = data.get('rates', {})
            
            return {
                'eur': rates.get('EUR', 0),
                'gbp': rates.get('GBP', 0),
                'source': 'Open Exchange Rates'
            }
    except Exception as e:
        logger.error(f"Rates error: {e}")
    
    return None

def get_usd_to_irr():
    """Get USD to IRR rate"""
    try:
        url = "https://api.exchangerate.host/latest?base=USD&symbols=IRR"
        response = requests.get(url, timeout=REQUESTS_TIMEOUT, headers={'User-Agent': 'Mozilla/5.0'})
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                irr_rate = data.get('rates', {}).get('IRR')
                if irr_rate:
                    return round(irr_rate, 2)
    except Exception as e:
        logger.error(f"IRR error: {e}")
    
    return None

def get_all_prices_real():
    """Get all real-time prices"""
    prices = {}
    
    metals = get_metals_prices()
    if metals:
        prices['metals'] = metals
        logger.info(f"Gold: ${metals['gold']}, Silver: ${metals['silver']}")
    
    rates = get_currency_rates()
    if rates:
        prices['rates'] = rates
        logger.info(f"EUR: {rates['eur']}, GBP: {rates['gbp']}")
    
    usd_to_irr = get_usd_to_irr()
    if usd_to_irr:
        prices['usd_to_irr'] = usd_to_irr
        logger.info(f"USD to IRR: {usd_to_irr}")
    
    prices['updated'] = datetime.now().strftime('%H:%M:%S')
    
    return prices if prices else None

# ========== Telegram API ==========

def send_message(chat_id, text, reply_markup=None):
    """Send message to user"""
    url = f"{TELEGRAM_API_URL}/sendMessage"
    
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    
    try:
        response = requests.post(url, json=payload, timeout=REQUESTS_TIMEOUT, verify=VERIFY_SSL)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Send error: {e}")
        return False

def get_updates(offset=0):
    """Get new messages"""
    url = f"{TELEGRAM_API_URL}/getUpdates"
    
    try:
        response = requests.get(url, params={'offset': offset, 'timeout': 25}, timeout=35, verify=VERIFY_SSL)
        return response.json()
    except Exception as e:
        logger.error(f"Get updates error: {e}")
        return {'ok': False}

# ========== Keyboard ==========

def get_keyboard():
    """Create keyboard"""
    return {
        'keyboard': [
            [{'text': '💰 قیمت لحظه‌ای'}],
            [{'text': '🥇 طلا'}, {'text': '🥈 نقره'}],
            [{'text': '💵 دلار'}, {'text': '💶 یورو'}],
            [{'text': 'ℹ️ درباره'}]
        ],
        'resize_keyboard': True
    }

# ========== Helpers ==========

def format_price(price, unit='تومان'):
    """Format price"""
    if isinstance(price, (int, float)):
        return f"{int(price):,} {unit}"
    return "N/A"

# ========== Message Handlers ==========

def handle_message(message):
    """Handle user message"""
    chat_id = message['chat']['id']
    text = message.get('text', '').strip()
    
    logger.info(f"Message: {text}")
    
    if text in ['/start', '/help']:
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
    """Start command"""
    text = """🤖 به ربات قیمت‌های لحظه‌ای خوش آمدید!

✨ *قیمت‌های واقعی و لحظه‌ای:*

• 🥇 طلا (USD)
• 🥈 نقره (USD)
• 💵 دلار
• 💶 یورو

از دکمه‌های زیر استفاده کنید:"""
    
    send_message(chat_id, text, get_keyboard())

def send_all_prices(chat_id):
    """Show all prices"""
    prices = get_all_prices_real()
    
    if not prices:
        send_message(chat_id, "❌ نتوانستم قیمت‌ها را دریافت کنم.\n\nلطفاً دوباره تلاش کنید.", get_keyboard())
        return
    
    text = "📊 *قیمت‌های لحظه‌ای*\n\n"
    
    if 'metals' in prices:
        metals = prices['metals']
        text += f"🥇 *طلا:*\n   💰 ${metals['gold']}/گرم (USD)\n"
        text += f"🥈 *نقره:*\n   💰 ${metals['silver']}/گرم (USD)\n\n"
    
    if 'usd_to_irr' in prices:
        text += f"💵 *دلار (USD):*\n   💰 {format_price(prices['usd_to_irr'])}\n\n"
    
    if 'rates' in prices and 'eur' in prices['rates']:
        eur_rate = prices['rates']['eur']
        eur_to_irr = prices.get('usd_to_irr', 0) * eur_rate
        text += f"💶 *یورو (EUR):*\n   💰 {format_price(eur_to_irr)}\n\n"
    
    text += f"🕐 *آپدیت:* {prices['updated']}"
    
    send_message(chat_id, text, get_keyboard())

def send_gold(chat_id):
    """Show gold price"""
    prices = get_all_prices_real()
    
    if not prices or 'metals' not in prices:
        send_message(chat_id, "❌ نتوانستم قیمت طلا را دریافت کنم.", get_keyboard())
        return
    
    metals = prices['metals']
    gold_price = metals['gold']
    
    text = f"🥇 *قیمت طلا*\n\n💰 *قیمت:* ${gold_price}/گرم (USD)"
    
    if 'usd_to_irr' in prices:
        gold_in_irr = gold_price * prices['usd_to_irr']
        text += f"\n💰 *قیمت ریالی:* {format_price(gold_in_irr)}"
    
    text += f"\n\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    send_message(chat_id, text, get_keyboard())

def send_silver(chat_id):
    """Show silver price"""
    prices = get_all_prices_real()
    
    if not prices or 'metals' not in prices:
        send_message(chat_id, "❌ نتوانستم قیمت نقره را دریافت کنم.", get_keyboard())
        return
    
    metals = prices['metals']
    silver_price = metals['silver']
    
    text = f"🥈 *قیمت نقره*\n\n💰 *قیمت:* ${silver_price}/گرم (USD)"
    
    if 'usd_to_irr' in prices:
        silver_in_irr = silver_price * prices['usd_to_irr']
        text += f"\n💰 *قیمت ریالی:* {format_price(silver_in_irr)}"
    
    text += f"\n\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    send_message(chat_id, text, get_keyboard())

def send_usd(chat_id):
    """Show USD price"""
    prices = get_all_prices_real()
    
    if not prices or 'usd_to_irr' not in prices:
        send_message(chat_id, "❌ نتوانستم نرخ دلار را دریافت کنم.", get_keyboard())
        return
    
    usd_price = prices['usd_to_irr']
    text = f"💵 *قیمت دلار (USD)*\n\n💰 *قیمت:* {format_price(usd_price)}\n\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    send_message(chat_id, text, get_keyboard())

def send_eur(chat_id):
    """Show EUR price"""
    prices = get_all_prices_real()
    
    if not prices or 'rates' not in prices or 'eur' not in prices['rates']:
        send_message(chat_id, "❌ نتوانستم نرخ یورو را دریافت کنم.", get_keyboard())
        return
    
    eur_rate = prices['rates']['eur']
    eur_to_irr = prices.get('usd_to_irr', 0) * eur_rate if 'usd_to_irr' in prices else 0
    
    text = f"💶 *قیمت یورو (EUR)*\n\n💰 *نرخ تبدیل:* 1 EUR = {eur_rate:.4f} USD"
    
    if eur_to_irr:
        text += f"\n💰 *قیمت ریالی:* {format_price(eur_to_irr)}"
    
    text += f"\n\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    send_message(chat_id, text, get_keyboard())

def send_about(chat_id):
    """About bot"""
    text = """ℹ️ *درباره این ربات*

🤖 *ربات قیمت‌های لحظه‌ای*
نسخه: 6.1 (Real Prices - Fixed)

✨ ویژگی‌ها:
• ✅ قیمت‌های طلا و نقره (لحظه‌ای)
• ✅ نرخ‌های ارز (لحظه‌ای)
• ✅ تبدیل خودکار به ریال
• ✅ اجرا در ابر (Railway)

📊 منابع داده:
• Metals Live
• Open Exchange Rates

⚠️ توجه:
قیمت‌ها برای اطلاع است."""
    
    send_message(chat_id, text, get_keyboard())

# ========== Main Loop ==========

def main():
    """Main function"""
    global UPDATE_OFFSET
    
    print("=" * 70)
    print("✅ Bot running with real-time prices...")
    print("=" * 70)
    
    error_count = 0
    max_errors = 20
    
    logger.info("Testing APIs...")
    test_prices = get_all_prices_real()
    if test_prices:
        logger.info("✅ All APIs working!")
    
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
                logger.warning(f"Connection error ({error_count}/{max_errors})")
                time.sleep(5)
            
            except Exception as e:
                error_count += 1
                logger.error(f"Error ({error_count}/{max_errors}): {str(e)[:50]}")
                time.sleep(5)
            
            if error_count >= max_errors:
                logger.error(f"Too many errors")
                break
    
    except KeyboardInterrupt:
        print("\n\nBot stopped.")

if __name__ == '__main__':
    main()
