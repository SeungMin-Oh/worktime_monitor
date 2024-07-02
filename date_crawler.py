import requests
from bs4 import BeautifulSoup

# 세션 시작
session = requests.Session()

# 로그인 URL과 로그인 폼 데이터 설정
login_url = "https://otims.tmax.co.kr/login"  # 실제 로그인 URL로 변경
login_data = {
    "username": "your_username",  # 실제 폼 필드 이름과 값으로 변경
    "password": "your_password"   # 실제 폼 필드 이름과 값으로 변경
}

# 로그인 요청 보내기
login_response = session.post(login_url, data=login_data)

# 로그인 성공 여부 확인
if login_response.status_code == 200:
    # 로그인 성공 시, 근태 정보 조회 요청 보내기
    fetch_url = "https://otims.tmax.co.kr/insa/attend/findAttdDailyConfirm.screen"
    fetch_data = {
        "gbWork": "",
        "attdKind": "newAttdKind",
        "status": "newStatus",
        "deptCd": "newDeptCd",
        "hier": "newHier",
        "empNm": "newEmpNm",
        "stDate": "20240601",
        "edDate": "20240702"
    }

    fetch_response = session.post(fetch_url, data=fetch_data)

    # 요청 성공 여부 확인
    if fetch_response.status_code == 200:
        print("요청 성공!")
        print(fetch_response.text)
    else:
        print(f"요청 실패: {fetch_response.status_code}")
        print(fetch_response.text)
else:
    print(f"로그인 실패: {login_response.status_code}")
    print(login_response.text)

