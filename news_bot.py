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

# 섹터 키워드 (투자용)
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

# 글로벌 + 국내 RSS
RSS_FEEDS = [
    "https://news.google.com/rss/search?q=한국+증시&hl=ko&gl=KR&ceid=KR:ko",
    "https://feeds.reuters.com/reuters/businessNews",
    "https://www.bloomberg.com/feed/podcast/etf-report.xml",
    "https://rss.hankyung.com/new/news_section/economy"
]

# 뉴스 수집
def get_news():
    news_list = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            title = entry.title
            # 키워드 필터링
            if any(k in title for k in SECTOR_KEYWORDS):
                news_list.append(title)
    return news_list

# 뉴스 점수화 (헤지펀드 스타일)
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

def filter_news(news):
    scored = [(n, score_news(n)) for n in news]
    scored = [n for n, s in scored if s >= 2]
    return scored[:7]  # 최대 7개 뉴스

# Gemini AI 분석
def analyze_news(news):
    if not news:
        return "오늘 중요한 경제 뉴스 없음"

    news_text = "\n".join(news)
    prompt = f"""
너는 글로벌 헤지펀드 매크로 전략가다.

다음 뉴스들을 분석해서 아래 형식으로 정리해라.

1️⃣ 핵심 이벤트 (3개)
2️⃣ 시장 영향 (코스피 / 반도체 / 자동차 / AI)
3️⃣ 투자 인사이트 (롱/숏 아이디어)
4️⃣ 3줄 요약

뉴스:
{news_text}
"""

    for model in MODELS:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )
            return response.text if response.text else "AI 응답 없음"
        except Exception as e:
            print(f"{model} 실패 → 다음 모델 시도: {e}")

    return "모든 모델 호출 실패"

# 텔레그램 발송
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    r = requests.post(url, data=data)
    if r.status_code != 200:
        print(f"텔레그램 전송 실패: {r.text}")

# 메인 실행
def run():
    news = get_news()
    filtered_news = filter_news(news)
    summary = analyze_news(filtered_news)
    message = f"📊 Korea Market Intelligence\n\n{summary}"
    send_telegram(message)

if __name__ == "__main__":
    run()
