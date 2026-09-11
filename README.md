# 🤖 ربات قیمت‌های لحظه‌ای تلگرام

ربات تلگرام برای نمایش قیمت‌های لحظه‌ای طلا، نقره، دلار و یورو (ریالی) از منبع TGJU.

## ✨ ویژگی‌ها

✅ **قیمت‌های ریالی** - تومان  
✅ **طلا و نقره** - بروز رسانی لحظه‌ای  
✅ **ارزهای خارجی** - دلار و یورو  
✅ **تغییرات قیمت** - درصد افزایش/کاهش  
✅ **بدون مشکل SSL** - Termux compatible  
✅ **میزبانی ابری** - Railway (رایگان)  

## 🚀 شروع سریع

### داخل Termux

```bash
# نصب
apt install python3 git
pip install requests

# اجرا
git clone https://github.com/YOUR_USERNAME/telegram-price-bot.git
cd telegram-price-bot
nano Price_Railway.py
# جایگزینی: BOT_TOKEN
python3 Price_Railway.py
```

### در Railway (ابر)

1. https://railway.app ثبت‌نام کنید
2. "Deploy from GitHub" انتخاب کنید
3. این Repository را انتخاب کنید
4. Variable `BOT_TOKEN` را تنظیم کنید
5. Deploy ✅

## 📋 متطلبات

- **Python 3.8+**
- **Telegram Bot Token** (از @BotFather)
- **اتصال اینترنت**

## 📥 نصب

### گزینه 1: اجرا محلی

```bash
git clone https://github.com/YOUR_USERNAME/telegram-price-bot.git
cd telegram-price-bot
pip install -r requirements.txt
```

تنظیم `BOT_TOKEN` در `Price_Railway.py`

```bash
python3 Price_Railway.py
```

### گزینه 2: Railway (توصیه شده)

فایل‌های ضروری:
- `Price.py` - ربات
- `Procfile` - دستورات Railway
- `requirements.txt` - بسته‌ها
- `runtime.txt` - نسخه Python

## 🤖 دستورات

| دستور | عملکرد |
|-------|--------|
| `/start` | شروع ربات |
| `/help` | نمایش راهنما |
| `💰 قیمت لحظه‌ای` | تمام قیمت‌ها |
| `🥇 طلا` | قیمت طلا |
| `🥈 نقره` | قیمت نقره |
| `💵 دلار` | قیمت دلار (ریالی) |
| `💶 یورو` | قیمت یورو (ریالی) |

## 📊 نمونه خروجی

```
📊 قیمت‌های لحظه‌ای

🥇 طلا:
   💰 650,000 تومان
   📈 +1.5%

💵 دلار (USD):
   💰 42,500 تومان
   ➡️ ۰%

🕐 آپدیت: 14:30:45
📡 منبع: TGJU.ORG
```

## 🔧 تنظیم

### BOT_TOKEN

دو روش برای تنظیم:

**1. متغیر محیط (Railway)**
```
Variables → BOT_TOKEN → [توکن]
```

**2. فایل (لوکال)**
```python
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TOKEN")
```

### API

منبع قیمت‌ها: **TGJU.ORG**
```
https://tgju.org/api/v1/latest
```

## 📦 محتویات Repository

```
telegram-price-bot/
├── Price.py              # ربات اصلی
├── Price_Railway.py      # نسخه Railway
├── Procfile              # دستورات اجرا
├── requirements.txt      # بسته‌های Python
├── runtime.txt           # نسخه Python
├── .gitignore            # فایل‌های نادیده
├── README.md             # این فایل
└── docs/
    ├── RAILWAY_DEPLOY.md # راهنمای Railway
    ├── RAILWAY_QUICK.md  # شروع سریع Railway
    └── GITHUB_UPLOAD.md  # آپلود GitHub
```

## 🆘 عیب‌یابی

### خطا: "BOT_TOKEN is required"

```
Railway Dashboard → Variables
BOT_TOKEN را اضافه کنید
Restart project
```

### خطا: "Connection refused"

- اینترنت را چک کنید
- API موجود است؟
- Deployment log را بررسی کنید

### خطا: "ModuleNotFoundError"

```bash
pip install -r requirements.txt
```

## 💰 هزینه

| بخش | قیمت |
|-----|------|
| **Termux** | رایگان |
| **Railway** | رایگان (500 ساعت/ماه) |
| **Bot Token** | رایگان |

**جمع کل**: ✅ **رایگان**

## 📝 نکات

- تمام قیمت‌ها بر اساس ریال ایران است
- برای معاملات واقعی منابع رسمی را بررسی کنید
- ربات 24/7 اجرا می‌شود
- بدون نیاز به database یا پایگاه داده

## 🔗 منابع

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [TGJU API](https://tgju.org/api/v1/latest)
- [Railway Docs](https://docs.railway.app)
- [GitHub](https://github.com)

## 📄 لایسنس

MIT License - آزاد برای استفاده شخصی

## 👨‍💻 نویسنده

ساخته‌شده برای اجرای ساده و بدون هزینه

---

## 🎯 مراحل شروع

1. **Bot Token دریافت کنید**
   - @BotFather / /newbot

2. **Repository clone کنید**
   ```bash
   git clone https://github.com/YOUR_USERNAME/telegram-price-bot.git
   ```

3. **تنظیمات**
   - BOT_TOKEN را جایگزین کنید
   - requirements نصب کنید

4. **اجرا**
   ```bash
   python3 Price.py
   ```

5. **ربات را test کنید**
   - تلگرام / /start

---

**موفق باشید! 🚀**

