import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from konlpy.tag import Okt
from wordcloud import WordCloud  

# 빅카인즈 API 설정
API_KEY = "#기간만료#"
BIGKINDS_URL = "#기간만료#"

# 검색 키워드
KEYWORDS = ["농산물", "농업", "작물 재배", "농업 기술"]

# 불용어 리스트를 파일에서 불러오기
def load_stopwords(file_path="korean_stopwords.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            stopwords = set(f.read().splitlines())
        return stopwords
    except FileNotFoundError:
        print("파일을 찾을 수 없습니다.")
        return set()

# 한국어 불용어 로드
KOREAN_STOPWORDS = load_stopwords()

# 뉴스 데이터 가져오기
def fetch_news(keyword):
    payload = {
        "access_key": API_KEY,
        "query": keyword,
        "provider": "",
        "category": "",
        "date_from": "20240101",
        "date_to": "20240317",
        "sort": "view",
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
                "content": article.get("content", ""),
                "views": article.get("view_count", 0)
            })
    return pd.DataFrame(news_data)

# 한국어 불용어 제거 함수
def remove_stopwords(text):
    okt = Okt()
    tokens = okt.morphs(text)
    filtered_tokens = [word for word in tokens if word not in KOREAN_STOPWORDS]
    return " ".join(filtered_tokens)

# 농산물 관련 데이터 추출 (재배 조건, 병충해 저항성, 예상 수익성)
def extract_farm_data(df):
    df["cleaned_content"] = df["content"].apply(remove_stopwords)
    df["cultivation_conditions"] = df["cleaned_content"].apply(lambda x: "재배 조건 정보 추출")
    df["pest_resistance"] = df["cleaned_content"].apply(lambda x: "병충해 저항성 분석")
    df["profitability"] = df["cleaned_content"].apply(lambda x: "예상 수익성 평가")
    return df

# 사용자 설문 데이터 처리
def get_user_preferences():
    user_info = {
        "climate_preference": input("선호하는 기후를 입력하세요: "),
        "labor_intensity": int(input("가능한 노동 강도를 1~10으로 입력하세요: ")),
        "income_target": int(input("희망 소득 목표(연간, 단위: 만원): ")),
        "farming_experience": int(input("농업 경험(년): ")),
        "capital_size": int(input("운영 가능한 자본 규모(만원): "))
    }
    return user_info

# 사용자 성향 및 농산물 매칭
def match_user_to_crops(df, user_info):
    df["score"] = df.apply(lambda row: 
        (1 if user_info["climate_preference"] in row["cultivation_conditions"] else 0) +
        (row["profitability"].count("높음") * user_info["income_target"]) +
        (row["pest_resistance"].count("강함") * user_info["farming_experience"]) -
        (abs(user_info["labor_intensity"] - 5) * 10), axis=1)
    return df.sort_values(by="score", ascending=False)


from collections import Counter

def generate_weighted_wordcloud(df):
    # 가중치가 적용된 단어 빈도수를 저장할 Counter 생성
    weighted_freq = Counter()
    
    for _, row in df.iterrows():
        tokens = row["cleaned_content"].split()
        # 조회수가 없는 키워드는 0으로 처리리
        view_count = row["views"] if row["views"] else 0
        # 단어 빈도 계산 후 조회수 가중치를 곱해서 누적
        freq = Counter(tokens)
        for word, count in freq.items():
            weighted_freq[word] += count * view_count

    font_path = "C:/Windows/Fonts/malgun.ttf"
    
    # 워드클라우드 생성
    wordcloud = WordCloud(
        font_path=font_path,
        width=800,
        height=400,
        background_color="white"
    ).generate_from_frequencies(weighted_freq)
    
    plt.figure(figsize=(15, 7.5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title("요즘 농부들의 HOT ISSUE!", fontsize=20)
    plt.show()

generate_weighted_wordcloud(news_df)

