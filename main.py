import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import subprocess
import threading
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 예약 가능 시 재생할 소리 파일 경로 (wav 또는 mp3 형식 권장)
SOUND_FILE = "/Users/petersong/code/f-lab/catch-table-reservation/notification.wav"

# 예약 확인을 위한 URL (로그인 후 접근할 예약 페이지 URL을 입력하세요)
TARGET_URL = "https://app.catchtable.co.kr"

# ChromeDriver 경로 (chromedriver가 PATH에 있다면 생략 가능)
CHROME_DRIVER_PATH = "/Users/petersong/code/f-lab/catch-table-reservation/chromedriver"

def play_sound():
    """macOS의 afplay를 사용하여 소리를 재생합니다."""
    try:
        subprocess.call(["afplay", SOUND_FILE])
    except Exception as e:
        print(f"소리 재생 중 오류 발생: {e}")

def show_notification():
    """macOS 시스템 알림을 표시합니다."""
    try:
        notification = 'display notification "예약 가능!" with title "캐치테이블 알림"'
        subprocess.call(["osascript", "-e", notification])
    except Exception as e:
        print(f"알림 표시 중 오류 발생: {e}")

def alert_user():
    """소리와 시스템 알림을 동시에 실행합니다."""
    threading.Thread(target=play_sound).start()
    threading.Thread(target=show_notification).start()

def main():
    # Selenium WebDriver 설정
    service = Service(CHROME_DRIVER_PATH)
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  # 브라우저 최대화
    driver = webdriver.Chrome(service=service, options=options)

    # 예약 페이지로 이동
    driver.get(TARGET_URL)

    print("브라우저가 열렸습니다. 수동으로 로그인 해주세요.")
    print("로그인이 완료되면 Enter 키를 눌러 예약 확인을 시작합니다.")
    input()
    print("예약 확인을 시작합니다. 1분마다 페이지를 새로고침하며 예약 가능 여부를 확인합니다.")

    try:
        reservation_available = False  # 예약 가능 상태 플래그
        while True:
            driver.refresh()
            time.sleep(5)  # 페이지 로딩 대기 시간

            # 예약 상태를 나타내는 모든 요소를 XPath를 사용하여 찾습니다.
            reservation_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'q9ov9u9')]")

            # 예약 가능한 날짜들을 저장할 리스트
            available_dates = []

            for element in reservation_elements:
                try:
                    # 날짜와 상태를 가져옵니다.
                    date_element = element.find_element(By.XPATH, ".//div[1]")
                    status_element = element.find_element(By.XPATH, ".//div[2]")

                    date_text = date_element.text.strip()
                    status_text = status_element.text.strip()

                    # 날짜와 상태가 빈 문자열인 경우 건너뜁니다.
                    if not date_text or not status_text:
                        continue

                    # 날짜 출력 (디버깅 용도)
                    print(f"날짜: {date_text}, 상태: {status_text}")

                    # 예약 가능 여부 체크
                    if status_text == "예약 가능":
                        available_dates.append(date_text)
                except Exception as e:
                    print(f"요소를 찾는 중 오류 발생: {e}")
                    continue

            if available_dates:
                print("예약 가능한 날짜가 있습니다:")
                for date in available_dates:
                    print(f"- {date}")
                if not reservation_available:
                    # 예약 가능 시 알림 음성 재생 등 추가 동작 실행
                    alert_user()
                    print("예약을 진행하려면 브라우저에서 직접 예약을 진행해주세요.")
                    reservation_available = True  # 예약 가능 상태로 플래그 설정
                # 예약 가능 시 time.sleep을 1시간으로 설정하여 브라우저를 유지합니다.
                time.sleep(3600)
            else:
                print("현재 모든 날짜가 예약 마감 상태입니다.")
                # 다음 확인을 위해 일정 시간 대기
                time.sleep(60)  # 1분마다 확인
    except KeyboardInterrupt:
        print("사용자에 의해 중단되었습니다.")
    finally:
        # 예약 가능한 상태에서 브라우저를 종료하지 않도록 합니다.
        if not reservation_available:
            driver.quit()

if __name__ == "__main__":
    main()