import requests
from bs4 import BeautifulSoup
import os
from google import genai

# API KEY
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

# 모델 fallback 리스트
models = [
    "gemini-2.5-flash",
    "gemini-2.0-flash-exp",
    "gemini-1.5-flash"
]

def call_gemini(prompt):

    for model in models:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"{model} 실패 → 다음 모델 시도")

    return "모든 모델 호출 실패"

# 뉴스 크롤링
url = "https://finance.naver.com/news/news_list.naver?mode=LSS2D&section_id=101&section_id2=258"

res = requests.get(url)
soup = BeautifulSoup(res.text, "html.parser")

titles = []
for a in soup.select(".articleSubject a")[:5]:
    titles.append(a.text.strip())

news_text = "\n".join(titles)

prompt = f"""
다음 한국 증시 뉴스를 요약해줘.

{news_text}
"""

summary = call_gemini(prompt)

print(summary)
