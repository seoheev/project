import folium
from folium.plugins import Figure
from folium import CustomIcon
import requests
from bs4 import BeautifulSoup

# 지도 생성
fig = Figure(width=505, height=350)
m = folium.Map(location=[35.65440, 129.22861], zoom_start=14)

fig.add_child(m)
folium.Marker(
    [35.65440, 129.22861],
    popup='<b>subway</b>',
    tooltip='<i>부산역</i>'
).add_to(m)

# 데이터프레임에서 좌표 리스트 생성
list_ = df[['LATITUDE', 'LONGITUDE']].values.tolist()
fig = Figure(width=550, height=350)

center = list_[0]
m = folium.Map(location=center, zoom_start=10)
fig.add_child(m)

# 폴리라인 추가
folium.PolyLine(locations=list_).add_to(m)

# 커스텀 아이콘 마커 추가
icon = CustomIcon("/markerpink.png", icon_size=(20, 20))

# row 변수 예시
row = {
    'geometry': type('', (), {'y': 35.65440, 'x': 129.22861})()
}

folium.Marker(
    location=[row.geometry.y, row.geometry.x],
    icon=icon,
    popup="Popup Text",
    tooltip="Tooltip Text"
).add_to(m)


# 일정 관리 함수
def add_task(task):
    with open('tasks.txt', 'a', encoding='utf-8') as file:
        file.write(task + '\n')
    print(f"일정이 '{task}' 추가되었습니다!")


def show_tasks():
    print("오늘의 일정:")
    try:
        with open('tasks.txt', 'r', encoding='utf-8') as file:
            tasks = file.readlines()
            if tasks:
                for i, task in enumerate(tasks, start=1):
                    print(f"{i}. {task.strip()}")
            else:
                print("아직 아무 일정이 없어요.")
    except FileNotFoundError:
        print("일정 없음")


def main():
    print("Klanner에 오신 걸 환영합니다!")
    while True:
        print("\n1. 일정을 추가할게요.")
        print("2. 일정들을 보여주세요.")
        print("3. 끝")
        choice = input("원하는 업무의 숫자를 입력해주세요: ")
        if choice == '1':
            task = input("당신의 일정: ")
            add_task(task)
        elif choice == '2':
            show_tasks()
        elif choice == '3':
            print("Klanner을 끝낼게요")
            break
        else:
            print("잘못된 접근입니다. 다시 입력해주세요")


if __name__ == "__main__":
    main()


# 리뷰 크롤링
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import time

# 크롬 드라이버 경로 설정 
chrome_driver_path = "/path/to/chromedriver"  # 본인의 크롬 드라이버 경로 입력
service = Service(chrome_driver_path)
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # 브라우저 창 없이 실행
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0")

# 브라우저 실행
driver = webdriver.Chrome(service=service, options=options)

# 네이버 지도 '이재모피자' 검색 페이지로 이동
naver_map_url = "https://map.naver.com/v5/search/이재모피자"
driver.get(naver_map_url)
time.sleep(3)  # 페이지 로딩 대기

# 프레임 전환 (네이버 지도는 iframe 내부에서 로딩됨)
driver.switch_to.frame("entryIframe")
time.sleep(2)

# 리뷰 스크롤 다운 (리뷰를 더 많이 로드하기 위함)
for _ in range(3):  # 3번 스크롤 (더 많이 가져오려면 숫자 늘리기)
    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
    time.sleep(2)

# 리뷰 텍스트 가져오기
review_elements = driver.find_elements(By.CSS_SELECTOR, ".place_section_content .zPfVt")
reviews = [review.text.strip() for review in review_elements if review.text.strip()]

# 결과 출력
if reviews:
    print("📌 이재모피자 네이버 지도 리뷰")
    for idx, review in enumerate(reviews[:5], start=1):  # 최대 5개만 출력
        print(f"{idx}. {review}")
else:
    print("리뷰를 찾을 수 없습니다.")

# 브라우저 종료
driver.quit()

