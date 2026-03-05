import requests
from bs4 import BeautifulSoup
from google import genai
import os

# ================================
# 환경변수
# ================================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ================================
# Gemini 설정
# ================================

client = genai.Client(api_key=GEMINI_API_KEY)

# ================================
# 키워드
# ================================

KEYWORDS = [
"M&A","인수","매각","투자","IPO","상장",
"반도체","AI","배터리","전기차",
"금리","인플레이션",
"구조조정","펀드","사모펀드","PE","VC",
"지배구조","상법","자본시장법",
"삼성전자","삼성","현대차","현대자동차",
"로봇","한화","SK"
]

# ================================
# 뉴스 사이트
# ================================

NEWS_SITES = [

"https://www.hankyung.com/economy",
"https://www.hankyung.com/finance",
"https://www.mk.co.kr/news/economy",
"https://www.mk.co.kr/news/stock",
"https://www.ft.com/markets",
"https://www.reuters.com/markets",
"https://www.bloomberg.com/markets"
]

# ================================
# 뉴스 크롤링
# ================================

def get_news():

    articles = []

    for site in NEWS_SITES:

        try:

            res = requests.get(site,timeout=10)
            soup = BeautifulSoup(res.text,"html.parser")

            links = soup.find_all("a")

            for link in links:

                title = link.get_text().strip()

                if len(title) < 15:
                    continue

                for k in KEYWORDS:
                    if k in title:

                        articles.append(title)
                        break

        except:
            pass

    return list(set(articles))[:20]

# ================================
# AI 분석
# ================================

def analyze_news(news):

    text = "\n".join(news)

    prompt = f"""
너는 헤지펀드 매크로 전략가다.

다음 뉴스 기반으로
한국 및 글로벌 시장에 중요한 뉴스만 선별해라.

각 뉴스는

- 제목
- 3줄 요약
- 시장 영향

형식으로 작성해라.

뉴스:

{text}
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    return response.text


# ================================
# 텔레그램 전송
# ================================

def send_telegram(msg):

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg
    }

    requests.post(url,data=data)


# ================================
# 실행
# ================================

def run():

    news = get_news()

    if not news:
        return

    report = analyze_news(news)

    final = f"""
📊 Korea Market Intelligence
{report}

(AI Hedge Fund Briefing)
"""

    send_telegram(final)


if __name__ == "__main__":
    run()
