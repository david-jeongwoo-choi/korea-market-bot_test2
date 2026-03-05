import os
import requests
import feedparser
from google import genai

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

RSS_FEEDS = [
"https://news.google.com/rss/search?q=한국+경제&hl=ko&gl=KR&ceid=KR:ko",
"https://news.google.com/rss/search?q=Korea+economy&hl=en-US&gl=US&ceid=US:en",
"https://news.google.com/rss/search?q=semiconductor+industry&hl=en-US&gl=US&ceid=US:en",
"https://news.google.com/rss/search?q=AI+industry&hl=en-US&gl=US&ceid=US:en",
"https://news.google.com/rss/search?q=Korea+M&A&hl=en-US&gl=US&ceid=US:en"
]

KEYWORDS = [
"M&A","인수","매각","투자","IPO","상장","반도체","AI",
"배터리","전기차","금리","인플레이션","구조조정",
"펀드","사모펀드","PE","VC","지배구조","상법","자본시장법",
"삼성전자","삼성","현대차","현대자동차","SK","한화","로봇"
]

def get_news():

    articles = []

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)

        for entry in feed.entries[:10]:
            title = entry.title
            link = entry.link

            if any(k.lower() in title.lower() for k in KEYWORDS):
                articles.append(f"{title} - {link}")

    return list(set(articles))[:20]


def analyze_news(news):

    if len(news) == 0:
        return "오늘 중요한 경제 뉴스 없음"

    prompt = f"""
다음 뉴스들을 헤지펀드 투자자 관점에서 분석해줘.

각 뉴스마다
- 제목
- 3줄 요약
- 시장 영향

형식으로 정리.

뉴스 목록:
{news}
"""

    models = [
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro-latest"
    ]

    for model in models:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )
            return response.text

        except Exception as e:
            print(f"{model} 실패 → 다음 모델 시도")

    return "AI 뉴스 분석 실패 (모델 호출 실패)"


def send_telegram(message):

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    requests.post(url, data=payload)


def run():

    news = get_news()

    report = analyze_news(news)

    today = __import__("datetime").date.today()

    message = f"""
📊 Korea Market Intelligence
{today}

{report}

(Automated Market Bot)
"""

    send_telegram(message)


if __name__ == "__main__":
    run()
