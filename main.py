import os
import requests
import feedparser
import schedule
import time
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

RSS_FEEDS = [
    "https://www.artificialintelligence-news.com/feed/",
    "https://techcrunch.com/tag/artificial-intelligence/feed/",
]

def get_news():
    articles = []
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                title = entry.get("title", "")
                summary = entry.get("summary", "")[:500]
                articles.append("- " + title + ": " + summary)
        except Exception as e:
            print("خطأ في RSS: " + str(e))
    return "\n".join(articles[:10])

def summarize(news_text):
    today = datetime.now().strftime("%Y-%m-%d")
    prompt = "لخّص هذه الأخبار بالعربية:\n- ركّز فقط على أدوات الذكاء الاصطناعي الجديدة\n- تجاهل الأخبار العامة\n- صنّف كل خبر: عالي جدا / متوسط / ضعيف\n- لا تزد عن 5 أخبار\n\nالأخبار:\n" + news_text
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + GEMINI_API_KEY
    response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
    data = response.json()
    if "candidates" in data:
    return data["candidates"][0]["content"]["parts"][0]["text"]
else:
    return "⚠️ خطأ في Gemini: " + str(data)

def send_telegram(message):
    url = "https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message})

def daily_job():
    print("بدء المهمة اليومية...")
    news = get_news()
    if not news:
        print("لم يتم جلب أخبار")
        return
    summary = summarize(news)
    send_telegram(summary)
    print("تم الإرسال بنجاح!")

if __name__ == "__main__":
    print("البوت يعمل...")
    daily_job()
    schedule.every().day.at("02:00").do(daily_job)
    while True:
        schedule.run_pending()
        time.sleep(60)
