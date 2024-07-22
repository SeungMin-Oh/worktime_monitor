import requests
from bs4 import BeautifulSoup
import argparse
import datetime

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

        # 근태기록 조회 페이지로 이동
        attendance_url = "https://otims.tmax.co.kr/corp/kor/attendance/findAttdDailyConfirm.screen"
        today = datetime.datetime.today().strftime('%Y%m%d')
        start_date = '20240712'
        end_date = '20240722'
        attendance_data = {
            'attdKind': '',  # 필요한 경우 적절히 변경
            'stDate': start_date,
            'edDate': end_date,
            'status': '',
            'deptCd': '2600',
            'hier': 'Y',
            'empNm': '',
            'empCls': '',
            'isAdmin': 'false',
            'retStDate': start_date,
            'retEdDate': end_date
        }

        attendance_page_response = session.post(attendance_url, data=attendance_data)

        if attendance_page_response.status_code == 200:
            print("근태기록 조회 페이지 접근 성공")

            # 근태기록 데이터 추출 (필요한 데이터 구조에 맞게 수정 필요)
            attendance_soup = BeautifulSoup(attendance_page_response.text, 'html.parser')
            attendance_records = []
            table = attendance_soup.find('table', {'id': 'listTable'})
            if table:
                for row in table.find_all('tr')[1:]:  # 헤더 행 제외
                    cols = row.find_all('td')
                    record = {
                        "date": cols[0].text.strip(),
                        "status": cols[1].text.strip(),
                        # 필요한 다른 데이터 항목들
                    }
                    attendance_records.append(record)

            # 추출된 데이터 출력 또는 처리
            for record in attendance_records:
                print(record)
        else:
            print("근태기록 조회 페이지 접근 실패")
    else:
        print(f"SSO 인증 실패: {sso_response.status_code}")
        print(sso_response.text)
else:
    print(f"로그인 실패: {login_response.status_code}")
    print(login_response.text)

