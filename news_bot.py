import os
import feedparser
import requests
from google import genai

# 환경변수
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Gemini 클라이언트
client = genai.Client(api_key=GEMINI_API_KEY)

# 헤지펀드 스타일 투자 키워드
SECTOR_KEYWORDS = [
    "M&A","인수","매각","투자","IPO","상장",
    "반도체","AI","배터리","전기차",
    "금리","인플레이션","구조조정",
    "사모펀드","PE","VC","지배구조",
    "상법","자본시장법","삼성전자","삼성",
    "현대차","현대자동차","로봇","한화","SK"
]

# 모델 fallback
MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash-exp",
    "gemini-1.5-flash"
]

# 국내외 RSS
RSS_FEEDS = [
    "https://rss.hankyung.com/new/news_section/economy",
    "https://rss.hankyung.com/new/news_section/finance",
    "https://rss.hankyung.com/new/news_section/stock",
    "https://feeds.reuters.com/reuters/businessNews",
    "https://www.bloomberg.com/feed/podcast/etf-report.xml"
]

# 뉴스 수집
def get_news():
    news_list = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:50]:  # 최신 50개 뉴스 수집
            title = entry.title
            link = entry.link
            summary = getattr(entry, "summary", "")
            # 키워드 포함 뉴스만 우선 수집
            if any(k in title or k in summary for k in SECTOR_KEYWORDS):
                news_list.append({"title": title, "link": link})
    return news_list

# 뉴스 점수화
def score_news(title):
    score = 0
    for keyword in SECTOR_KEYWORDS:
        if keyword in title:
            score += 2
    if "M&A" in title or "인수" in title:
        score += 3
    if "금리" in title or "인플레이션" in title:
        score += 2
    return score

# 뉴스 필터링 + 최소 15개 확보
def filter_news(news):
    scored = [(n, score_news(n["title"])) for n in news]
    scored_priority = [n for n, s in scored if s >= 1]
    scored_priority.sort(key=lambda x: score_news(x["title"]), reverse=True)

    # 최소 15개 확보
    if len(scored_priority) < 15:
        remaining = [n for n in news if n not in scored_priority]
        scored_priority += remaining[:15 - len(scored_priority)]

    return scored_priority[:15]

# 뉴스별 3줄 요약
def summarize_news(news_item):
    prompt = f"""
너는 글로벌 헤지펀드 전략가다. 
아래 뉴스 제목과 링크를 보고 투자 관점에서 **3줄 요약**만 작성해라.

뉴스 제목: {news_item['title']}
뉴스 링크: {news_item['link']}
"""
    for model in MODELS:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )
            return response.text if response.text else "요약 없음"
        except Exception as e:
            print(f"{model} 실패 → 다음 모델 시도: {e}")
    return "모든 모델 호출 실패"

# 텔레그램 전송
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    r = requests.post(url, data=data)
    if r.status_code != 200:
        print(f"텔레그램 전송 실패: {r.text}")

# 메인
def run():
    news = get_news()
    filtered_news = filter_news(news)

    # 각 뉴스별 3줄 요약 + 링크
    messages = []
    for n in filtered_news:
        summary = summarize_news(n)
        messages.append(f"🔹 {n['title']}\n{summary}\n링크: {n['link']}")

    final_message = "📊 Korea Market Hedge Fund Style News\n\n" + "\n\n".join(messages)
    send_telegram(final_message)

if __name__ == "__main__":
    run()
