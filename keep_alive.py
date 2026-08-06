from flask import Flask
from threading import Thread
import time
import requests
import os

app = Flask('')

@app.route('/')
def home():
    return "Bot is active and running!"

def run():
    # جلب الرابط الخاص بالمشروع تلقائياً أو وضع رابط افتراضي
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def self_ping():
    # انتظر قليلاً حتى يشتغل السيرفر تماماً
    time.sleep(10)
    # استبدل هذا الرابط برابط مشروعك الفعلي إذا لزم الأمر، أو دع البوت يحاول الاتصال محلياً
    url = f"http://127.0.0.1:{os.environ.get('PORT', 8080)}/"
    while True:
        try:
            requests.get(url)
        except Exception:
            pass
        # يكرر العملية كل 4 دقائق (240 ثانية) ليضمن عدم سكون الاستضافة
        time.sleep(240)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
    
    p = Thread(target=self_ping)
    p.daemon = True
    p.start()
