# 🏭 제조 품질 현황 대시보드

AI 비전검사 PoC 준비를 위한 품질 데이터 모니터링 샘플 앱입니다.
(Streamlit + pandas 만 사용 / DB·로그인·외부 API 없음)

## 주요 기능

- CSV 업로드 (없으면 코드에서 만든 샘플 데이터 자동 사용)
- KPI 카드: 전체 검사 / 정상 / 불량 / 불량률
- 날짜별 검사·불량 건수 선그래프, 불량 유형별 막대그래프
- 최근 검사 10건 표 (OK=초록, NG=빨강)
- 사이드바 필터: 날짜 / 제품 / 검사 결과

## 파일 구조

```
quality-dashboard/
├── app.py            # 앱 전체 코드 (이 파일 하나가 전부)
├── requirements.txt  # 필요한 라이브러리
├── sample_data.csv   # 업로드 테스트용 샘플 CSV
├── README.md
└── .gitignore        # GitHub에 올리지 않을 파일 목록
```

## CSV 형식

아래 5개 컬럼이 **반드시** 있어야 합니다. (컬럼 이름은 영문 그대로)

| 컬럼 | 설명 | 예시 |
|---|---|---|
| inspection_date | 검사 날짜 | 2026-10-01 |
| product_id | 제품 ID | P001 |
| result | 검사 결과 (OK 또는 NG) | NG |
| defect_type | 불량 유형 (정상이면 None) | Scratch |
| confidence | 모델 신뢰도 (0~1) | 0.91 |

## 1. 내 컴퓨터(Windows 11)에서 실행하기

VS Code에서 프로젝트 폴더를 열고 **터미널(Terminal) → 새 터미널**을 엽니다.
(PowerShell 기준)

```powershell
# 1) 가상환경 만들기 (처음 한 번만)
python -m venv .venv

# 2) 가상환경 켜기
.venv\Scripts\Activate.ps1

# 3) 라이브러리 설치 (처음 한 번만)
pip install -r requirements.txt

# 4) 앱 실행
streamlit run app.py
```

브라우저가 자동으로 열리며 `http://localhost:8501` 에서 확인할 수 있습니다.
종료는 터미널에서 `Ctrl + C` 입니다.

> **2)에서 "스크립트 실행이 비활성화" 오류가 나면?**
> 아래 명령을 한 번 실행한 뒤 다시 시도하세요.
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
>
> **`python` 명령을 못 찾으면?** `py -m venv .venv` 처럼 `py`를 써 보세요.
> **`streamlit` 명령을 못 찾으면?** `python -m streamlit run app.py` 로 실행하세요.

## 2. GitHub에 올리기

1. https://github.com 에서 로그인 후 **New repository** 클릭
   - Repository name: `quality-dashboard`
   - **Public** 선택 (무료 Streamlit Cloud 배포는 보통 Public이 가장 쉽습니다)
   - README 추가 옵션은 체크하지 않기 (이미 파일이 있으므로)
2. VS Code 터미널에서 프로젝트 폴더 기준으로 실행합니다.
   (아래 `내아이디` 부분은 본인 GitHub 아이디로 바꾸세요)

```powershell
git init
git add .
git commit -m "first commit: quality dashboard"
git branch -M main
git remote add origin https://github.com/내아이디/quality-dashboard.git
git push -u origin main
```

처음 push 할 때 GitHub 로그인 창이 뜨면 로그인하면 됩니다.

> Git이 없다면 https://git-scm.com 에서 설치하거나,
> VS Code 왼쪽의 **소스 제어(Source Control)** 아이콘에서 "Publish to GitHub" 버튼을 써도 됩니다.

## 3. Streamlit Community Cloud에 배포하기

1. https://share.streamlit.io 접속 → **GitHub 계정으로 로그인**
2. 오른쪽 위 **Create app** (또는 **New app**) 클릭
3. 다음처럼 입력
   - Repository: `내아이디/quality-dashboard`
   - Branch: `main`
   - Main file path: `app.py`
4. **Deploy** 클릭 → 1~3분 정도 기다리면 `https://xxxx.streamlit.app` 주소가 생깁니다.

이후 코드를 수정하고 `git add . → git commit → git push` 하면 배포된 앱에 자동 반영됩니다.

## 문제 해결 체크리스트

| 증상 | 확인할 것 |
|---|---|
| 배포 시 `ModuleNotFoundError` | `requirements.txt`에 라이브러리 이름이 있는지, 파일이 저장소 맨 위에 있는지 |
| 한글이 깨져 보이는 CSV | 엑셀에서 "CSV UTF-8"로 저장 (cp949도 자동 지원) |
| "필수 컬럼이 없습니다" | CSV 첫 줄의 컬럼 이름이 위 표와 똑같은지 |
| 그래프가 비어 있음 | 사이드바 필터(날짜/제품/결과)가 너무 좁지 않은지 |
