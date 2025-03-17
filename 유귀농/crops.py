import requests
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict

# 빅카인즈 API 설정
API_KEY = "#기간만료#"
BIGKINDS_URL = "#기간만료#"

# 검색 키워드
KEYWORDS = ["작물", "종자"]
POSITIVE_KEYWORDS = ["성장", "수익", "인기", "호황", "혁신", "발전"]

# 뉴스 데이터 가져오기
def fetch_news(keyword):
    payload = {
        "access_key": API_KEY,
        "query": keyword,
        "provider": "",
        "category": "",
        "date_from": "20240101",
        "date_to": "20240317",
        "sort": "accuracy",
        "hilight": "100",
        "start": 0,
        "display": 50
    }
    response = requests.post(BIGKINDS_URL, json=payload)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []

# 뉴스 데이터를 수집하여 데이터프레임으로 저장
def collect_news_data():
    news_data = []
    for keyword in KEYWORDS:
        articles = fetch_news(keyword)
        for article in articles:
            news_data.append({
                "title": article.get("title", ""),
                "content": article.get("content", "")
            })
    return pd.DataFrame(news_data)

# 키워드 트렌드 분석
def analyze_trends(df):
    crop_counts = defaultdict(int)
    for _, row in df.iterrows():
        for word in POSITIVE_KEYWORDS:
            if word in row["content"]:
                crop_counts[row["title"]] += 1
    return pd.DataFrame(list(crop_counts.items()), columns=["Crop", "Positive Count"])

# 트렌드 시각화
def plot_trends(df):
    df = df.sort_values(by="Positive Count", ascending=False)[:10]
    plt.figure(figsize=(10, 5))
    plt.bar(df["Crop"], df["Positive Count"], color='skyblue')
    plt.xticks(rotation=45, ha='right')
    plt.xlabel("작물")
    plt.ylabel("긍정적 키워드 빈도")
    plt.title("최근 인기 작물 트렌드")
    plt.show()

# 실행 코드
news_df = collect_news_data()
trend_df = analyze_trends(news_df)
import ace_tools as tools

tools.display_dataframe_to_user(name="Trending Crops", dataframe=trend_df)
plot_trends(trend_df)
