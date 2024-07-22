import requests
from bs4 import BeautifulSoup
import argparse
import datetime
import pandas as pd

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
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Referer': 'https://otims.tmax.co.kr/frame.screen',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


# 로그인 요청 보내기
login_response = session.post(login_url, data=login_data, headers = headers)

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

        # 메인 페이지로 이동
        main_page_url = "https://otims.tmax.co.kr/frame.screen"
        main_page_response = session.get(main_page_url)

        if main_page_response.status_code == 200:
            print("메인 페이지 접근 성공")

            # BeautifulSoup을 사용하여 HTML 파싱
            soup = BeautifulSoup(main_page_response.text, 'html.parser')

            # 근태기록 조회 페이지로 이동
            attendance_url = "https://otims.tmax.co.kr/insa/attend/findAttdDailyConfirm.screen"
            today = datetime.datetime.today().strftime('%Y%m%d')
            start_date = '20240712'
            end_date = '20240722'
            attendance_data = {
                'attdKind': '',
                'stDate': start_date,
                'edDate': end_date,
                'status': '',
                'deptCd': '2600',
                'hier': 'Y',
                'empNm': '',
                'empCls': '',
                'isAdmin': 'false',
                'retStDate': start_date,
                'retEdDate': end_date,
            }

            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': 'https://otims.tmax.co.kr/frame.screen',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            attendance_page_response = session.post(attendance_url, data=attendance_data, headers=headers)

            if attendance_page_response.status_code == 200:
                print("근태기록 조회 페이지 접근 성공")

                # 근태기록 데이터 추출
                attendance_soup = BeautifulSoup(attendance_page_response.text, 'html.parser')
                attendance_records = []
                table = attendance_soup.find('table', {'id': 'listTable'})
                if table:
                    for row in table.find_all('tr')[1:]:  # 헤더 행 제외
                        cols = row.find_all('td')
                        if len(cols) > 15:  # 데이터 행인지 확인
                            record = {
                                "company": cols[1].text.strip(),
                                "department": cols[2].text.strip(),
                                "emp_id": cols[3].text.strip(),
                                "name": cols[4].text.strip(),
                                "position": cols[5].text.strip(),
                                "date": cols[7].text.strip(),
                                "work_start": cols[10].text.strip(),
                                "work_end": cols[11].text.strip(),
                                "late_time": cols[14].text.strip(),
                                "work_time": cols[15].text.strip()
                            }
                            attendance_records.append(record)

                # 데이터프레임으로 변환
                df = pd.DataFrame(attendance_records)

                # 시간 계산을 위해 데이터 변환
                def convert_to_minutes(time_str):
                    if ':' in time_str:
                        hours, minutes = map(int, time_str.split(':'))
                        return hours * 60 + minutes
                    return 0

                df['late_time_minutes'] = df['late_time'].apply(convert_to_minutes)
                df['work_time_minutes'] = df['work_time'].apply(convert_to_minutes)

                # 인원별 평균 근태 시간 계산
                avg_late_time = df.groupby('name')['late_time_minutes'].mean()
                avg_work_time = df.groupby('name')['work_time_minutes'].mean()

                avg_late_time_df = avg_late_time.reset_index()
                avg_work_time_df = avg_work_time.reset_index()

                # 평균 시간 결과 출력
                print("인원별 평균 지각 시간 (분):")
                print(avg_late_time_df)
                
                print("\n인원별 평균 근무 시간 (분):")
                print(avg_work_time_df)
            else:
                print("근태기록 조회 페이지 접근 실패")
                print(f"상태 코드: {attendance_page_response.status_code}")
                print(attendance_page_response.text)
        else:
            print(f"메인 페이지 접근 실패: {main_page_response.status_code}")
            print(main_page_response.text)
    else:
        print(f"SSO 인증 실패: {sso_response.status_code}")
        print(sso_response.text)
else:
    print(f"로그인 실패: {login_response.status_code}")
    print(login_response.text)

