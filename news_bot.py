import os
import feedparser
import requests
from google import genai

# 환경변수
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Gemini 설정
client = genai.Client(api_key=GEMINI_API_KEY)

def get_news():
    url = "https://news.google.com/rss/search?q=한국+증시&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(url)

    news_list = []
    for entry in feed.entries[:5]:
        news_list.append(entry.title)

    return news_list


def summarize(news):

    prompt = f"""
다음 한국 증시 뉴스를 투자 관점에서 5줄로 요약해줘.

뉴스:
{news}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"모델 호출 실패: {e}"


def send_telegram(message):

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    requests.post(url, data=data)


def run():

    news = get_news()

    news_text = "\n".join(news)

    summary = summarize(news_text)

    message = f"📈 오늘의 한국 증시 뉴스\n\n{summary}"

    send_telegram(message)


if __name__ == "__main__":
    run()
