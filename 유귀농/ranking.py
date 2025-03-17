import requests
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict

# 빅카인즈 API 설정
API_KEY = "#기간만료#"
BIGKINDS_URL = "#기간만료#"

# 검색 키워드 및 지역 리스트
KEYWORDS = ["귀농 지원 정책", "귀농 지원 혜택", "귀농 지원금"]
REGIONS = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종", "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]
POLICY_KEYWORDS = ["정책", "혜택", "지원금", "토지 저금리 대출"]

# 뉴스 데이터 가져오기
def fetch_news(keyword, region):
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
    for region in REGIONS:
        for keyword in KEYWORDS:
            articles = fetch_news(keyword, region)
            for article in articles:
                news_data.append({
                    "region": region,
                    "title": article.get("title", ""),
                    "content": article.get("content", "")
                })
    return pd.DataFrame(news_data)

# TF-IDF 기반 핵심 문장 추출
def extract_key_sentences(df):
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(df['content'].fillna(""))
    feature_names = vectorizer.get_feature_names_out()
    scores = np.array(tfidf_matrix.sum(axis=1)).flatten()
    df['tfidf_score'] = scores
    return df.sort_values(by='tfidf_score', ascending=False)

# 정책 가중치 부여
def apply_policy_weights(df):
    df['policy_score'] = df['content'].apply(lambda x: sum([x.count(word) for word in POLICY_KEYWORDS]))
    df['final_score'] = df['tfidf_score'] + df['policy_score']
    return df

# 지역별 점수 집계 및 정렬
def rank_regions(df):
    region_scores = df.groupby('region')['final_score'].sum().reset_index()
    return region_scores.sort_values(by='final_score', ascending=False)

# 실행 코드
news_df = collect_news_data()
news_df = extract_key_sentences(news_df)
news_df = apply_policy_weights(news_df)
ranked_regions = rank_regions(news_df)

import ace_tools as tools
tools.display_dataframe_to_user(name="Ranked Regions", dataframe=ranked_regions)
