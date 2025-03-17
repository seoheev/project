import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

# 빅카인즈 API 설정
API_KEY = "#기간만료#"
BIGKINDS_URL = "#기간만료#"
DICT_API = "http://www.law.go.kr/DRF/lawSearch.do?OC=test&target=lstrm&query=자동차&type=HTML" # 법제처 국가법령정보 OPEN API

# 검색 키워드
KEYWORDS = ["귀농 법률", "농업 지원 법 개정", "농촌 정책 변경"]

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

# 법제처 API를 이용한 법률 용어 해석
def explain_legal_terms(text):
    words = text.split()
    explained_text = []
    for word in words:
        response = requests.get(f"{DICT_API}{word}&type=HTML")
        if response.status_code == 200:
            definition = response.text  # 법제처 API가 HTML을 반환하므로 직접 파싱 필요
            explained_text.append(f"{word} ({definition[:100]}...)")  # 100자까지만 표시
        else:
            explained_text.append(word)
    return " ".join(explained_text)

# 뉴스 데이터에 법률 용어 설명 추가
def enhance_news_with_explanations(df):
    df["explained_content"] = df["content"].apply(explain_legal_terms)
    return df

# 실행 코드
news_df = collect_news_data()
news_df = enhance_news_with_explanations(news_df)

import ace_tools as tools

tools.display_dataframe_to_user(name="Simplified Legal News", dataframe=news_df)
