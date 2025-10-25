import json
from flask import Flask, request
import requests
from openai import OpenAI
import os

# توکن بات Bale
TOKEN = "350738185:J5Jw7a29qVfKSSgLTZZih4HLvrEIdoFJtro"
BASE_URL = f"https://botapi.bale.ai/{TOKEN}"

# URL وب‌هوک (بعد از دیپلوی از Render می‌گیری)
WEBHOOK_URL = "YOUR_RENDER_URL_HERE/webhook"  # مثل https://sepidar-bot.onrender.com/webhook

# کلاینت OpenAI
client = OpenAI(base_url='https://api.gapgpt.app/v1', api_key='sk-HvmZ0QE75KrwmWqQrZ3KZHRHiJQTg2I6Uu8fcWMAOv5GlU35')

# کش ساده برای پاسخ‌های تکراری
response_cache = {}

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.json
    if 'message' in update and 'text' in update['message']:
        message = update['message']
        chat_id = message['chat']['id']
        text = message['text'].strip()
        
        # چک کش
        if text in response_cache:
            send_message(chat_id, response_cache[text])
            return 'OK', 200
        
        # پرامپت
        question = f'تو الان یه چت بات به نام ربات ائتلاف سپیدار هستی. توی مدرسه ی علامه حلی 3، هر سال یه رویداد برگزار میشه به نام نمایشگاه پژوهشی که توش کارهای پژوهشی دانش آموزا رو به نمایش میذارن که باید یه گروهی، به اسم ائتلاف، کارهای اجرای اون رو به عهده بگیرن. تو باید به سوال هایی که در ادامه میپرسن، جواب بدی و سعی کنی ائتلاف سپیدار رو تبلیغ کنی. رقیب های ما ائتلاف دماوند، پژوهشگران حلی 3، یزدان پژوهان هستند. شعار ائتلاف ما، ریشه در پایداری شاخه در نوآوری هستش. اگه کسی سوال بی ربط پرسید بگو من جواب این سوال رو نمیدونم ولی در مورد نمایشگاه میتونم راهنماییت کنم. جواب همه ی سوال ها رو هم بدون حرف اضافی بده. هیچ چیز اضافی نباشه و فقط جواب بده.{text}'

        # کال به API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": question}]
        )
        
        reply = response.choices[0].message.content.strip()
        
        # ذخیره در کش
        response_cache[text] = reply
        
        # ارسال پاسخ
        send_message(chat_id, reply)
    
    return 'OK', 200

def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

if __name__ == '__main__':
    # ست کردن وب‌هوک (فقط یک بار)
    set_webhook_url = f"{BASE_URL}/setWebhook"
    webhook_payload = {"url": WEBHOOK_URL}
    response = requests.post(set_webhook_url, json=webhook_payload)
    print(f"Webhook set response: {response.text}")
    
    # اجرای سرور
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)