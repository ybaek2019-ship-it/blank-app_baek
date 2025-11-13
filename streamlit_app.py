import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from PIL import Image
import io
import datetime


# 페이지 설정
st.set_page_config(
    page_title="Streamlit 요소 예시 가이드",
    page_icon="🎈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS로 스타일 개선
st.markdown("""
<style>
    /* 헤더 스타일 */
    h1 {
        color: #0066cc;
        text-align: center;
        padding-bottom: 20px;
        border-bottom: 3px solid #0066cc;
    }
    
    /* 서브헤더 스타일 */
    h2 {
        color: #0066cc;
        margin-top: 30px;
    }
    
    /* 각주 섹션 */
    .footnote {
        background-color: #f0f8ff;
        padding: 15px;
        border-left: 4px solid #0066cc;
        margin: 10px 0;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# 각주를 수집할 리스트
footnotes = []

def add_footnote(text: str) -> int:
    """각주를 추가하고 번호를 반환합니다."""
    footnotes.append(text)
    return len(footnotes)


# --- 페이지 상단 ---
st.title("🎈 Streamlit 요소 예시 가이드")
st.markdown("""
이 페이지는 Streamlit에서 사용할 수 있는 다양한 UI 요소를 소개하는 인터랙티브 가이드입니다.
각 요소 옆의 위첨자 번호를 클릭하거나 페이지 하단의 각주 섹션에서 자세한 설명을 확인하세요.
""")

# Header 예시
num = add_footnote("""
**`st.header`** — 섹션 제목을 표시합니다.
- 마크다운 형식으로 텍스트 서식 지원
- 앵커(anchor)를 자동 생성하여 목차 작성 가능
- 예: `st.header("제목", divider="blue")`
""")
st.header(f"기본 헤더 예시 [{num}]", divider="blue")

# Markdown 블록
num = add_footnote("""
**`st.markdown`** — 마크다운 형식의 텍스트를 렌더링합니다.
- 굵게, 기울임꼴, 코드, 링크, 표 등 마크다운 문법 지원
- `unsafe_allow_html=True`로 HTML 태그 포함 가능
- LaTeX 수식 지원 가능
""")
st.markdown(f"**마크다운 예시** [{num}]: _이 텍스트는 마크다운으로 작성되었습니다._")

# 입력 위젯: 텍스트 입력 + 버튼
num = add_footnote("""
**`st.text_input`, `st.button`** — 사용자 입력을 받고 액션을 트리거합니다.
- `text_input`: 한 줄 텍스트 입력 필드
- `button`: 클릭할 수 있는 버튼 (True 반환)
- `key` 파라미터로 상태 관리 가능
""")
name = st.text_input(f"이름을 입력하세요 [{num}]", value="홍길동", key="name_input")
if st.button("인사하기"):
    st.success(f"안녕하세요, {name}님! 👋")

# 슬라이더와 숫자 입력
num = add_footnote("""
**`st.slider`, `st.number_input`** — 수치 입력 컨트롤입니다.
- `slider`: 범위 내에서 값을 선택 (마우스 드래그)
- `number_input`: 정확한 수치 입력 필드 (텍스트 타입, 스핀 버튼)
- 범위, 단계(step), 기본값 설정 가능
""")
col1, col2 = st.columns(2)
with col1:
    age = st.slider(f"나이 선택 [{num}]", 0, 120, 30)
with col2:
    score = st.number_input(f"점수 입력 [{num}]", min_value=0, max_value=100, value=75)
st.write(f"선택된 나이: {age}, 점수: {score}")

# 선택형 입력들
num = add_footnote("""
**`st.selectbox`, `st.multiselect`, `st.checkbox`, `st.radio`** — 다양한 선택형 위젯입니다.
- `selectbox`: 드롭다운 목록에서 단일 선택
- `multiselect`: 여러 개 선택 가능
- `checkbox`: 체크박스 (True/False)
- `radio`: 라디오 버튼 (한 번에 하나만 선택)
""")
option = st.selectbox(f"옵션 선택 [{num}]", ["옵션 A", "옵션 B", "옵션 C"])
multi = st.multiselect("다중 선택", ["빨강", "초록", "파랑"], default=["빨강"]) 
agree = st.checkbox("동의합니다")
st.write("선택:", option, multi, "동의:", agree)

# 데이터프레임 / 테이블 / 차트
num = add_footnote("""
**`st.dataframe`, `st.table`, `st.altair_chart`, `st.line_chart`** — 데이터 표시와 시각화입니다.
- `dataframe`: 인터랙티브 테이블 (정렬, 필터링 가능)
- `table`: 정적 테이블
- `altair_chart`: Altair 라이브러리 기반 선언형 차트
- `line_chart`: 간단한 라인 차트 (내장)
""")
df = pd.DataFrame({"x": np.arange(10), "y": np.random.randn(10).cumsum()})
st.subheader(f"데이터 프레임 및 차트 [{num}]")
st.dataframe(df, use_container_width=True)
st.table(df.head())
chart = alt.Chart(df).mark_bar().encode(x="x:O", y="y:Q")
st.altair_chart(chart, use_container_width=True)
st.line_chart(df.set_index('x'))

# 지도 예시 (무작위 좌표)
num = add_footnote("""
**`st.map`** — 위도/경도 데이터를 간단히 시각화합니다.
- 데이터프레임에서 'lat', 'lon' 컬럼 자동 인식
- Mapbox 기반 인터랙티브 지도
- 줌(zoom), 패닝 지원
""")
map_data = pd.DataFrame({
    "lat": 37.5 + np.random.randn(50) * 0.02, 
    "lon": 127.0 + np.random.randn(50) * 0.02
})
st.subheader(f"지도 예시 [{num}]")
st.map(map_data)

# 이미지 표시 (PIL로 생성)
num = add_footnote("""
**`st.image`** — 이미지를 표시합니다.
- PIL Image, NumPy 배열, 파일 경로, URL 지원
- `caption`: 이미지 아래 설명 텍스트
- `width`, `use_column_width` 로 크기 조정 가능
""")
img = Image.new("RGB", (300, 150), color=(73, 109, 137))
buf = io.BytesIO()
img.save(buf, format="PNG")
buf.seek(0)
st.image(buf, caption=f"샘플 이미지 (300x150px) [{num}]", use_column_width=False)

# 파일 업로더
num = add_footnote("""
**`st.file_uploader`** — 사용자가 파일을 업로드하도록 합니다.
- `type` 파라미터로 파일 형식 제한 (예: ['csv', 'xlsx'])
- 업로드된 파일은 메모리 내 `UploadedFile` 객체
- 자동으로 세션이 변경되면 초기화
""")
uploaded = st.file_uploader(f"파일 업로드 (CSV/TXT) [{num}]", type=['csv', 'txt'])
if uploaded is not None:
    st.write(f"업로드됨: **{uploaded.name}** (크기: {uploaded.size} bytes)")

# 확장 영역(Expander)과 코드 블록
num = add_footnote("""
**`st.expander`, `st.code`** — 보조 정보나 코드를 표시합니다.
- `expander`: 클릭하면 펼쳐지는 아코디언 섹션
- `code`: 구문 강조(syntax highlighting)가 있는 코드 블록
- `language` 파라미터로 프로그래밍 언어 지정 가능
""")
with st.expander(f"숨겨진 정보 보기 [{num}]"):
    st.write("여기에 더 자세한 설명이나 예시를 넣을 수 있습니다.")
    st.code("import streamlit as st\nst.write('Hello, Streamlit!')", language="python")

# 컬럼 레이아웃과 메트릭
num = add_footnote("""
**`st.columns`, `st.metric`** — 대시보드 레이아웃 구성입니다.
- `columns(n)`: n개의 동일 너비 컬럼 생성
- `metric`: KPI(핵심지표) 표시 (제목, 값, 변화)
- 대시보드, 카드형 UI 구성에 유용
""")
st.subheader(f"대시보드 예시 [{num}]")
col_a, col_b, col_c = st.columns(3)
col_a.metric("매출", "$12.4k", "+5%")
col_b.metric("활성 사용자", "1,204", "-2%")
col_c.metric("전환율", "3.2%", "+0.2%")

# 사이드바 예시
num = add_footnote("""
**`st.sidebar`** — 보조 컨트롤을 사이드바에 배치합니다.
- 필터, 네비게이션, 설정 등 보조 인터페이스 배치
- 메인 콘텐츠와 독립적으로 관리 가능
- 모바일에서는 햄버거 메뉴로 변환
""")
with st.sidebar:
    st.header(f"사이드바 [{num}]")
    sidebar_option = st.selectbox("사이드 옵션", ["옵션 1", "옵션 2", "옵션 3"]) 
    st.write("선택됨:", sidebar_option)

# 진행 상태 표시기
num = add_footnote("""
**`st.progress`, `st.spinner`** — 긴 작업 동안 피드백을 제공합니다.
- `progress`: 0~100% 진행률 표시
- `spinner`: 로딩 중 메시지 표시
- 함께 사용하여 사용자 경험 향상
""")
st.subheader(f"진행 상태 표시 [{num}]")
if st.button("긴 작업 시뮬레이션 실행"):
    with st.spinner("작업 중입니다..."):
        import time
        progress = st.progress(0)
        for i in range(1, 101):
            time.sleep(0.02)
            progress.progress(i)
    st.success("작업 완료! ✓")

# 다운로드 버튼 예시
num = add_footnote("""
**`st.download_button`** — 사용자가 데이터를 파일로 받을 수 있게 합니다.
- `data`: 바이너리 또는 문자열 데이터
- `file_name`: 다운로드 파일명
- `mime`: MIME 타입 (예: 'text/csv', 'application/json')
""")
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label=f"샘플 CSV 다운로드 [{num}]", 
    data=csv, 
    file_name="sample_data.csv", 
    mime="text/csv"
)

# 날짜 입력 예시
num = add_footnote("""
**`st.date_input`** — 날짜 선택 위젯입니다.
- `value`: 기본값 (datetime.date 객체)
- 캘린더 UI 제공
- 범위 선택도 가능 (`min_value`, `max_value`)
""")
today = st.date_input(f"날짜 선택 [{num}]", value=datetime.date.today())
st.write(f"선택된 날짜: **{today}**")


# 하단: 각주 출력
st.markdown("---")
st.subheader("📌 각주 및 상세 설명 (Footnotes & Details)")
st.markdown("위의 각 요소 [번호]에 해당하는 자세한 설명입니다:")
for i, note in enumerate(footnotes, start=1):
    st.markdown(f"**[{i}]** {note}")
