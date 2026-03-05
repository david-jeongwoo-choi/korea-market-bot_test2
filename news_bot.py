import feedparser
import requests
import datetime
import os
import google.generativeai as genai

# ======================
# API KEY
# ======================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

genai.configure(api_key=GEMINI_API_KEY)

# ======================
# 뉴스 RSS
# ======================

RSS_FEEDS = [

"https://www.hankyung.com/feed/economy",
"https://www.mk.co.kr/rss/30000001/",
"https://feeds.reuters.com/reuters/businessNews",
"https://rss.nytimes.com/services/xml/rss/nyt/Business.xml"

]

# ======================
# 뉴스 수집
# ======================

def collect_news():

    news = []

    for url in RSS_FEEDS:

        feed = feedparser.parse(url)

        for entry in feed.entries[:5]:

            title = entry.title
            link = entry.link

            news.append(f"{title}\n{link}")

    return news


# ======================
# Gemini 분석
# ======================

def analyze_news(news):

    model = genai.GenerativeModel("gemini-2.5-flash-lite")

    prompt = f"""
You are a hedge fund analyst.

Summarize these news into a Korea market briefing.

For each news provide:

Title
3 line summary
Market impact

News:
{news}
"""

    response = model.generate_content(prompt)

    return response.text


# ======================
# 텔레그램 전송
# ======================

def send_telegram(message):

    url=f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    data={
        "chat_id":CHAT_ID,
        "text":message
    }

    requests.post(url,data=data)


# ======================
# 실행
# ======================

def run():

    news = collect_news()

    report = analyze_news(news)

    send_telegram(report)


if __name__ == "__main__":

    run()
