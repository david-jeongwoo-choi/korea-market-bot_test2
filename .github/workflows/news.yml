import requests
import feedparser
import os
import google.generativeai as genai

# 환경변수
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini 설정
genai.configure(api_key=GEMINI_API_KEY)

# 뉴스 RSS
RSS_FEEDS = [

"https://news.google.com/rss/search?q=한국+경제&hl=ko&gl=KR&ceid=KR:ko",
"https://news.google.com/rss/search?q=Korea+economy&hl=en-US&gl=US&ceid=US:en",
"https://news.google.com/rss/search?q=삼성전자&hl=ko&gl=KR&ceid=KR:ko",
"https://news.google.com/rss/search?q=AI+semiconductor&hl=en-US&gl=US&ceid=US:en"

]


def get_news():

    news = []

    for url in RSS_FEEDS:

        feed = feedparser.parse(url)

        for entry in feed.entries[:5]:

            news.append(entry.title)

    return news


def analyze_news(news):

    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
다음 뉴스들을 보고 한국 투자자 관점에서 중요한 뉴스만 정리해줘.

각 뉴스는

제목
3줄 요약
시장 영향

뉴스 목록
{news}
"""

    response = model.generate_content(prompt)

    return response.text


def send_telegram(msg):

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    data = {

        "chat_id": CHAT_ID,
        "text": msg

    }

    requests.post(url, data=data)


def run():

    news = get_news()

    report = analyze_news(news)

    send_telegram(report)


if __name__ == "__main__":

    run()
