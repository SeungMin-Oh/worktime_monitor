import requests
from bs4 import BeautifulSoup

import argparse

# 명령줄 인수 파서 설정
parser = argparse.ArgumentParser(description="Tmax SSO Login Script")
parser.add_argument("username", help="Your username")
parser.add_argument("password", help="Your password")
parser.add_argument("company", choices=["TS", "TD", "TO"], help="Company code (TS, TD, TO)")

args = parser.parse_args()

# 세션 시작
session = requests.Session()

# 첫 번째 단계: 초기 로그인 요청 보내기
login_url = "https://otims.tmax.co.kr/checkUserInfo.tmv?tmaxsso_nsso=yes"
login_data = {
    "userId": args.username,
    "passwd": args.password,
    "company": args.company
}
# 로그인 요청 보내기
login_response = session.post(login_url, data=login_data)

# 로그인 성공 여부 확인
if login_response.status_code == 200 and "tmaxsso_tokn" in login_response.text:
    print("첫 번째 단계 로그인 성공!")

    # BeautifulSoup을 사용하여 HTML 파싱
    soup = BeautifulSoup(login_response.text, 'html.parser')

    # SSO 서버에 필요한 데이터 추출
    sso_url = soup.find('form')['action']
    sso_data = {tag['name']: tag['value'] for tag in soup.find_all('input')}

    # 두 번째 단계: SSO 서버에 인증 토큰 등록
    sso_response = session.post(sso_url, data=sso_data)

    # 최종 로그인 성공 여부 확인
    if sso_response.status_code == 200:
        print("SSO 인증 및 최종 로그인 성공!")

        # 중간 페이지 요청 보내기
        middle_page_url = "https://otims.tmax.co.kr/frame.screen"
        middle_page_data = {
            "accessMode": "2",
            "goUrl": "/frame.screen",
            "survey_popup": "T"
        }

        middle_page_response = session.post(middle_page_url, data=middle_page_data)

        # 중간 페이지 성공 여부 확인
        if middle_page_response.status_code == 200:
            print("중간 페이지 요청 성공!")
            
	    # BeautifulSoup을 사용하여 HTML 파싱
            soup = BeautifulSoup(middle_page_response.text, 'html.parser')
            form = soup.find('form')
            if form:
                action_url = form['action']
                form_data = {tag['name']: tag['value'] for tag in form.find_all('input')}

                # 최종 페이지 요청 보내기
                final_response = session.post(action_url, data=form_data)
                
                if final_response.status_code == 200:
                    print("최종 페이지 요청 성공!")
                    print(final_response.text)
                else:
                    print(f"최종 페이지 요청 실패: {final_response.status_code}")
                    print(final_response.text)
            else:
                print("폼을 찾을 수 없습니다. 메인 페이지가 이미 로드되었을 수 있습니다.")
                print(middle_page_response.text)

        else:
            print(f"중간 페이지 요청 실패: {middle_page_response.status_code}")
            print(middle_page_response.text)
    else:
        print(f"SSO 인증 실패: {sso_response.status_code}")
        print(sso_response.text)
else:
    print(f"로그인 실패: {login_response.status_code}")
    print(login_response.text)

