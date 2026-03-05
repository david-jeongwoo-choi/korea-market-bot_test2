import os
import feedparser
import requests
from bs4 import BeautifulSoup
from google import genai

# 환경변수
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Gemini 클라이언트
client = genai.Client(api_key=GEMINI_API_KEY)

# 투자 키워드
SECTOR_KEYWORDS = [
    "M&A","인수","매각","투자","IPO","상장",
    "반도체","AI","배터리","전기차",
    "금리","인플레이션","구조조정",
    "사모펀드","PE","VC","지배구조",
    "상법","자본시장법","삼성전자","삼성",
    "현대차","현대자동차","로봇","한화","SK", "국민연금", "의결권", "경영권"
]

RSS_FEEDS = [
    "https://rss.hankyung.com/new/news_section/economy",
    "https://rss.hankyung.com/new/news_section/finance",
    "https://rss.hankyung.com/new/news_section/stock",
    "https://www.mk.co.kr/rss/economy/",
    "https://www.sedaily.com/rss/News",
    "https://www.fnnews.com/rss/economy",
    "https://www.chosun.com/economy/rss/",
    "https://rss.joins.com/joins_money_list.xml",
    "https://rss.donga.com/total.xml",
]

MODEL = "gemini-1.5-chat"  # 안정적 무료 모델

def clean_html(text):
    return BeautifulSoup(text, "html.parser").get_text()

def get_news():
    news_list = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:50]:
            title = clean_html(entry.title)
            link = entry.link
            summary = clean_html(getattr(entry, "summary", ""))
            if any(k in title or k in summary for k in SECTOR_KEYWORDS):
                news_list.append({"title": title, "link": link})
    return news_list[:15]  # 최소 15개

def summarize_news(news_item):
    prompt = f"""
너는 글로벌 헤지펀드 전략가다.
아래 뉴스 제목과 링크를 보고 투자 관점에서 **3줄 요약**만 작성해라.
- 숫자, 기업명, 투자 포인트 중심
- 3줄 이상 작성 금지

뉴스 제목: {news_item['title']}
뉴스 링크: {news_item['link']}
"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        summary = response.choices[0].message.content.strip()
        if summary:
            return summary
    except Exception as e:
        print(f"요약 실패: {e}")
    return f"요약 생성 실패\n{news_item['title']}\n{news_item['link']}"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    r = requests.post(url, data=data)
    if r.status_code != 200:
        print(f"텔레그램 전송 실패: {r.text}")

def run():
    news = get_news()
    messages = []
    for n in news:
        summary = summarize_news(n)
        messages.append(f"🔹 {n['title']}\n{summary}\n링크: {n['link']}")
    final_message = "📊 Korea Market Hedge Fund Style News\n\n" + "\n\n".join(messages)
    send_telegram(final_message)

if __name__ == "__main__":
    run()
