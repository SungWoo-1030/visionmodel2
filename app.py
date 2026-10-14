"""제조 품질 현황 대시보드 (Streamlit 샘플 앱)

실행 방법:  streamlit run app.py
"""

import numpy as np
import pandas as pd
import streamlit as st

# ------------------------------------------------------------
# 1. 기본 설정
# ------------------------------------------------------------
st.set_page_config(page_title="제조 품질 현황 대시보드", page_icon="🏭", layout="wide")

REQUIRED_COLUMNS = ["inspection_date", "product_id", "result", "defect_type", "confidence"]


# ------------------------------------------------------------
# 2. 데이터 준비 함수
# ------------------------------------------------------------
def make_sample_data():
    """CSV를 올리지 않아도 테스트할 수 있는 샘플 데이터를 만든다."""
    rng = np.random.default_rng(42)  # 시드를 고정해서 항상 같은 데이터가 나오게 한다
    n = 300
    dates = pd.date_range("2026-10-01", periods=14)  # 14일치

    df = pd.DataFrame(
        {
            "inspection_date": rng.choice(dates, size=n),
            "product_id": rng.choice(["P001", "P002", "P003", "P004", "P005"], size=n),
            "result": rng.choice(["OK", "NG"], size=n, p=[0.88, 0.12]),
        }
    )
    df = df.sort_values("inspection_date").reset_index(drop=True)

    # NG일 때만 불량 유형을 넣고, OK이면 "None"으로 둔다
    defect_choices = rng.choice(["Scratch", "Crack", "Dent", "Stain"], size=n)
    df["defect_type"] = np.where(df["result"] == "NG", defect_choices, "None")

    # 정상은 신뢰도 높게, 불량은 조금 낮게
    df["confidence"] = np.where(
        df["result"] == "OK",
        rng.uniform(0.92, 0.99, size=n),
        rng.uniform(0.80, 0.95, size=n),
    ).round(2)
    return df


def read_uploaded_csv(uploaded_file):
    """업로드된 CSV를 읽는다. 한글 윈도우 엑셀 CSV(cp949)도 읽을 수 있게 처리."""
    try:
        return pd.read_csv(uploaded_file, encoding="utf-8-sig")
    except UnicodeDecodeError:
        uploaded_file.seek(0)
        return pd.read_csv(uploaded_file, encoding="cp949")


def clean_data(df):
    """컬럼 형식을 정리한다."""
    df = df.copy()
    df["inspection_date"] = pd.to_datetime(df["inspection_date"], errors="coerce")
    df = df.dropna(subset=["inspection_date"])  # 날짜가 잘못된 행은 제외
    df["result"] = df["result"].astype(str).str.strip().str.upper()
    # pandas는 "None" 글자를 빈 값(NaN)으로 읽는 경우가 있어서 다시 채워준다
    df["defect_type"] = df["defect_type"].fillna("None").astype(str).str.strip()
    df.loc[df["defect_type"] == "", "defect_type"] = "None"
    return df


# ------------------------------------------------------------
# 3. 제목
# ------------------------------------------------------------
st.title("🏭 제조 품질 현황 대시보드")
st.caption("AI 비전검사 PoC 준비를 위한 품질 데이터 모니터링")

# ------------------------------------------------------------
# 4. 사이드바: CSV 업로드와 필터
# ------------------------------------------------------------
st.sidebar.header("데이터 / 필터")
uploaded = st.sidebar.file_uploader("CSV 파일 업로드", type=["csv"])

data = None
if uploaded is not None:
    raw = read_uploaded_csv(uploaded)
    missing = [c for c in REQUIRED_COLUMNS if c not in raw.columns]
    if missing:
        st.sidebar.error(f"필수 컬럼이 없습니다: {', '.join(missing)}")
    else:
        data = clean_data(raw)
        st.sidebar.success(f"업로드 데이터 사용 중 ({len(data)}행)")

if data is None:
    data = clean_data(make_sample_data())
    st.sidebar.info("샘플 데이터를 사용 중입니다.")

if data.empty:
    st.warning("사용할 수 있는 데이터가 없습니다. CSV 내용을 확인해 주세요.")
    st.stop()

# 날짜 필터
min_date = data["inspection_date"].min().date()
max_date = data["inspection_date"].max().date()
date_range = st.sidebar.date_input(
    "검사 날짜", value=(min_date, max_date), min_value=min_date, max_value=max_date
)
# 날짜를 하나만 고른 경우(튜플 길이 1)에도 오류가 나지 않게 처리
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range[0] if isinstance(date_range, tuple) else date_range

# 제품 필터
product_options = sorted(data["product_id"].astype(str).unique())
selected_products = st.sidebar.multiselect("제품", product_options, default=product_options)

# 검사 결과 필터
result_options = sorted(data["result"].unique())
selected_results = st.sidebar.multiselect("검사 결과", result_options, default=result_options)

# 필터 적용
dates_only = data["inspection_date"].dt.date
filtered = data[
    (dates_only >= start_date)
    & (dates_only <= end_date)
    & (data["product_id"].astype(str).isin(selected_products))
    & (data["result"].isin(selected_results))
]

if filtered.empty:
    st.warning("선택한 조건에 해당하는 데이터가 없습니다. 필터를 조정해 주세요.")
    st.stop()

# ------------------------------------------------------------
# 5. 상단: KPI 카드
# ------------------------------------------------------------
total = len(filtered)
ok_count = int((filtered["result"] == "OK").sum())
ng_count = int((filtered["result"] == "NG").sum())
defect_rate = ng_count / total * 100

c1, c2, c3, c4 = st.columns(4)
c1.metric("전체 검사", f"{total:,} 건")
c2.metric("정상 (OK)", f"{ok_count:,} 건")
c3.metric("불량 (NG)", f"{ng_count:,} 건")
c4.metric("불량률", f"{defect_rate:.1f} %")

st.divider()

# ------------------------------------------------------------
# 6. 중단: 그래프 2개
# ------------------------------------------------------------
left, right = st.columns(2)

with left:
    st.subheader("날짜별 검사 현황")
    daily = (
        filtered.assign(date=filtered["inspection_date"].dt.date)
        .groupby("date")
        .agg(검사건수=("result", "size"), 불량건수=("result", lambda s: (s == "NG").sum()))
    )
    st.line_chart(daily)

with right:
    st.subheader("불량 유형별 건수")
    defects = filtered[(filtered["result"] == "NG") & (filtered["defect_type"] != "None")]
    if defects.empty:
        st.info("표시할 불량 데이터가 없습니다.")
    else:
        st.bar_chart(defects["defect_type"].value_counts())

st.divider()

# ------------------------------------------------------------
# 7. 하단: 최근 검사 결과 10건 (OK/NG 색으로 구분)
# ------------------------------------------------------------
st.subheader("최근 검사 데이터 (10건)")

recent = filtered.sort_values("inspection_date", kind="stable").tail(10).iloc[::-1].copy()
recent["inspection_date"] = recent["inspection_date"].dt.strftime("%Y-%m-%d")
recent = recent[REQUIRED_COLUMNS].reset_index(drop=True)


def color_result(column):
    """result 컬럼: OK는 초록, NG는 빨강 배경으로 표시"""
    return [
        "background-color: #d4edda; color: #155724" if v == "OK"
        else "background-color: #f8d7da; color: #721c24" if v == "NG"
        else ""
        for v in column
    ]


st.dataframe(recent.style.apply(color_result, subset=["result"]))

# ------------------------------------------------------------
# 8. 업로드 데이터 미리보기 (맨 아래, 펼치기)
# ------------------------------------------------------------
with st.expander("현재 사용 중인 전체 데이터 미리보기"):
    st.dataframe(data.head(50))
