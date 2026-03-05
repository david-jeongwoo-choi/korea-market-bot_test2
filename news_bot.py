import os
import feedparser
import requests
from bs4 import BeautifulSoup

# 환경변수
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 국내외 주요 경제 RSS
RSS_FEEDS = [
    # 국내
    "https://rss.hankyung.com/new/news_section/economy",
    "https://rss.hankyung.com/new/news_section/finance",
    "https://rss.hankyung.com/new/news_section/stock",
    "https://www.mk.co.kr/rss/economy/",
    "https://www.sedaily.com/rss/News",
    "https://www.fnnews.com/rss/economy",
    "https://www.chosun.com/economy/rss/",
    "https://rss.joins.com/joins_money_list.xml",
    "https://rss.donga.com/total.xml",
    # 글로벌
    "https://feeds.reuters.com/reuters/businessNews",
    "https://feeds.bbci.co.uk/news/business/rss.xml",
    "https://www.bloomberg.com/feed/podcast/etf-report.xml",
    "https://www.cnbc.com/id/10001147/device/rss/rss.html",
    "https://www.ft.com/?format=rss",
]

SECTOR_KEYWORDS = [
    "M&A","인수","매각","투자","IPO","상장",
    "반도체","AI","배터리","전기차",
    "금리","인플레이션","구조조정",
    "사모펀드","PE","VC","지배구조",
    "상법","자본시장법","삼성전자","삼성",
    "현대차","현대자동차","로봇","한화","SK"
]

def clean_html(text):
    return BeautifulSoup(text, "html.parser").get_text()

# 뉴스 수집
def get_news(min_count=20):
    news_list = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = clean_html(entry.title)
            link = entry.link
            summary = clean_html(getattr(entry, "summary", ""))
            # 키워드 포함 뉴스만
            if any(k in title or k in summary for k in SECTOR_KEYWORDS):
                news_list.append({"title": title, "link": link})
            if len(news_list) >= min_count:
                break
        if len(news_list) >= min_count:
            break
    return news_list[:min_count]

# 텔레그램 발송
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    r = requests.post(url, data=data)
    if r.status_code != 200:
        print(f"텔레그램 전송 실패: {r.text}")

def run():
    news = get_news(min_count=20)
    messages = []
    for n in news:
        messages.append(f"🔹 {n['title']}\n링크: {n['link']}")
    final_message = "📊 Korea + Global Market News\n\n" + "\n\n".join(messages)
    send_telegram(final_message)

if __name__ == "__main__":
    run()
