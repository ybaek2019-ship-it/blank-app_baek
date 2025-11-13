import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats
import io
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="성적 데이터 시각화 분석기",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
<style>
    h1 { color: #1f77b4; text-align: center; padding: 20px 0; }
    h2 { color: #1f77b4; margin-top: 30px; }
    .insight-box { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin: 10px 0; }
    .recommendation-box { background: #e8f4f8; padding: 15px; border-left: 4px solid #00aacc; border-radius: 4px; margin: 10px 0; }
    .warning-box { background: #fff3cd; padding: 15px; border-left: 4px solid #ff9800; border-radius: 4px; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

# ==================== AI 기반 분석 함수 ====================
def analyze_grades(df_data, score_cols, student_name=None):
    """
    성적 데이터를 분석하고 비판적 해석 및 추천을 제공합니다.
    """
    analysis = {}
    
    if student_name and student_name in df_data['이름'].values:
        # 개인별 분석
        student = df_data[df_data['이름'] == student_name].iloc[0]
        student_scores = student[score_cols].values
        student_avg = student_scores.mean()
        class_avg = df_data[score_cols].mean().mean()
        
        analysis['type'] = '개인'
        analysis['name'] = student_name
        analysis['avg'] = student_avg
        analysis['class_avg'] = class_avg
        analysis['strengths'] = score_cols[np.argsort(student_scores)[-2:]]  # 상위 2개 과목
        analysis['weaknesses'] = score_cols[np.argsort(student_scores)[:2]]  # 하위 2개 과목
        analysis['scores'] = dict(zip(score_cols, student_scores))
        analysis['percentile'] = (df_data[score_cols].mean(axis=1) < student_avg).sum() / len(df_data) * 100
        
    else:
        # 반 전체 분석
        analysis['type'] = '반전체'
        analysis['avg'] = df_data[score_cols].values.mean()
        analysis['max'] = df_data[score_cols].values.max()
        analysis['min'] = df_data[score_cols].values.min()
        analysis['std'] = df_data[score_cols].values.std()
        analysis['scores_by_subject'] = df_data[score_cols].mean().to_dict()
        
        # 강점/약점 과목
        subject_means = df_data[score_cols].mean()
        analysis['best_subject'] = subject_means.idxmax()
        analysis['worst_subject'] = subject_means.idxmin()
        analysis['best_avg'] = subject_means.max()
        analysis['worst_avg'] = subject_means.min()
    
    return analysis

def generate_insights(analysis):
    """분석 결과로부터 비판적 해석을 생성합니다."""
    insights = []
    
    if analysis['type'] == '개인':
        # 개인별 해석
        avg = analysis['avg']
        class_avg = analysis['class_avg']
        diff = avg - class_avg
        
        # 성과 평가
        if avg >= 90:
            insights.append(f"🌟 **최우수 성적**: {analysis['name']} 학생은 {avg:.1f}점의 우수한 성적을 기록했습니다. 이는 반 평균({class_avg:.1f}점)보다 {diff:+.1f}점 높습니다.")
        elif avg >= 80:
            insights.append(f"✅ **우수한 성적**: {analysis['name']} 학생은 {avg:.1f}점으로 양호한 수준입니다. (반 평균: {class_avg:.1f}점, 상위 {analysis['percentile']:.0f}%)")
        elif avg >= 70:
            insights.append(f"📊 **중상 수준**: {analysis['name']} 학생은 {avg:.1f}점으로 평균 수준입니다. (반 평균과의 격차: {diff:+.1f}점)")
        else:
            insights.append(f"⚠️ **주의 필요**: {analysis['name']} 학생은 {avg:.1f}점으로 학습 지원이 필요합니다. (반 평균: {class_avg:.1f}점)")
        
        # 과목별 분석
        strengths_str = ", ".join(analysis['strengths'])
        weaknesses_str = ", ".join(analysis['weaknesses'])
        insights.append(f"\n📚 **과목별 성과**:\n- ✨ 강점: {strengths_str}\n- 📌 개선 필요: {weaknesses_str}")
        
    else:
        # 반 전체 분석
        avg = analysis['avg']
        std = analysis['std']
        
        insights.append(f"📈 **반 전체 성적 분석**:\n- 평균: {avg:.1f}점\n- 최고: {analysis['max']:.0f}점 / 최저: {analysis['min']:.0f}점\n- 표준편차: {std:.2f}")
        insights.append(f"\n🎯 **과목별 성과**:\n- 최강점: {analysis['best_subject']} ({analysis['best_avg']:.1f}점)\n- 개선필요: {analysis['worst_subject']} ({analysis['worst_avg']:.1f}점)\n- 격차: {analysis['best_avg'] - analysis['worst_avg']:.1f}점")
        
        # 학력 분포 평가
        if std < 5:
            insights.append(f"\n⚖️ **학력 분포**: 표준편차가 작아(σ={std:.2f}) 학생들의 성적 편차가 적습니다. (균등한 수준)")
        else:
            insights.append(f"\n⚖️ **학력 분포**: 표준편차가 크므로(σ={std:.2f}) 학생별 학력 격차가 큼을 시사합니다.")
    
    return insights

def generate_recommendations(analysis, df_data, score_cols):
    """데이터 기반 행동 연결 추천을 생성합니다."""
    recommendations = []
    
    if analysis['type'] == '개인':
        avg = analysis['avg']
        class_avg = analysis['class_avg']
        scores = analysis['scores']
        
        # 점수대별 추천
        if avg >= 90:
            recommendations.append({
                'title': '🏆 현재 성과 유지 및 심화',
                'actions': [
                    '현재 학습 방법 지속 - 효과적인 학습 습관 유지',
                    '심화 학습 시작 - 상위권 대학 진학 준비',
                    '피어 튜터링 - 다른 학생들 지도를 통한 심화 이해',
                    '과학고/영재반 도전 검토'
                ]
            })
        elif avg >= 80:
            recommendations.append({
                'title': '✅ 점진적 성과 향상',
                'actions': [
                    '약점 과목 집중 학습 - 특히 ' + ", ".join(analysis['weaknesses']) + ' 강화',
                    '그룹 스터디 참여 - 협력 학습으로 이해도 증진',
                    '주 3~4회 복습 일정 수립',
                    '월 1회 성적 점검 및 학습 계획 수정'
                ]
            })
        elif avg >= 70:
            recommendations.append({
                'title': '📚 적극적인 학습 지원 필요',
                'actions': [
                    '개인 튜터링 - 특히 ' + analysis['weaknesses'][0] + ' 과목 집중',
                    '교과서 기본 개념 재학습 - 고등학교 내용 선행 학습',
                    '매일 학습 일정 수립 (최소 2시간)',
                    '학교 보충수업 필수 참여'
                ]
            })
        else:
            recommendations.append({
                'title': '🆘 긴급 학습 지원 필요',
                'actions': [
                    '전담 튜터 배정 또는 학습 컨설팅 상담',
                    '심리 상담 - 학습 동기 부족 원인 파악',
                    '기초 학력 진단 및 맞춤형 프로그램 시작',
                    '학부모 면담 - 가정 지원 방안 논의',
                    '진로 적성 검사 - 학습 목표 재설정'
                ]
            })
        
        # 약점 과목 맞춤 추천
        weakest_subject = analysis['weaknesses'][0]
        weak_score = scores[weakest_subject]
        
        if weak_score < 70:
            recommendations.append({
                'title': f'🎯 {weakest_subject} 과목 집중 개선 전략',
                'actions': [
                    f'문제점 진단 - {weakest_subject} 단원별 이해도 파악',
                    f'기초 개념 강화 - 선행 학습 내용 복습',
                    f'주 2회 과외 또는 온라인 강의 수강 고려',
                    f'매주 연습 문제 10문제 이상 풀이',
                    f'월말 진도율 점검'
                ]
            })
    
    else:
        # 반 전체 추천
        best_subject = analysis['best_subject']
        worst_subject = analysis['worst_subject']
        gap = analysis['best_avg'] - analysis['worst_avg']
        
        if gap > 10:
            recommendations.append({
                'title': '⚠️ 과목별 학력 격차 해소 필요',
                'actions': [
                    f'{worst_subject} 과목에 추가 교육 자원 배분',
                    f'{worst_subject} 과목 보충수업 운영 (주 2회)',
                    f'우수 학생 피어 튜터 배치',
                    f'{best_subject} 성공 사례 공유 및 학습법 전수',
                    f'월 1회 진도율 및 성과 모니터링'
                ]
            })
        
        recommendations.append({
            'title': '📊 전체 학력 향상 전략',
            'actions': [
                f'반 전체 평균 {analysis["avg"]:.1f}점 → 85점 목표 설정',
                '주 1회 전체 팀 미팅으로 학습 현황 공유',
                '월 2회 모의고사 실시 및 오답 분석',
                f'저성취 학생({analysis["min"]:.0f}점 이하) 집중 관리',
                '학습 동기 강화를 위한 인센티브 제도 도입'
            ]
        })
    
    return recommendations

st.title("📊 성적 데이터 시각화 분석기")
st.markdown("""
성적 CSV 파일을 업로드하면 다양한 시각화와 통계 분석을 제공합니다.
- 📈 점수 분포, 등급 분포 확인
- 🎯 과목별 성과 비교
- 📍 개인별/반 전체 성적 분석
- 💡 AI 기반 비판적 해석 및 행동 추천
- 💾 필터링된 데이터 다운로드
""")

# ==================== CSV 업로드 ====================
st.header("1️⃣ 성적 데이터 업로드")
uploaded_file = st.file_uploader(
    "CSV 파일을 선택하세요 (예: 학번, 이름, 국어, 영어, 수학, 과학, 사회)",
    type=['csv'],
    help="학생 성적 데이터를 담은 CSV 파일을 업로드하세요"
)

if uploaded_file is None:
    st.info("💡 CSV 파일을 업로드하여 시작하세요!")
    
    # 샘플 데이터 생성 옵션
    if st.button("📋 샘플 데이터로 시작하기"):
        np.random.seed(42)
        sample_data = {
            '학번': [f'S{i:03d}' for i in range(1, 31)],
            '이름': [f'학생{i}' for i in range(1, 31)],
            '국어': np.random.randint(70, 100, 30),
            '영어': np.random.randint(70, 100, 30),
            '수학': np.random.randint(60, 100, 30),
            '과학': np.random.randint(70, 100, 30),
            '사회': np.random.randint(70, 100, 30),
        }
        st.session_state.df = pd.DataFrame(sample_data)
        st.success("✅ 샘플 데이터 로드됨!")

else:
    # CSV 파일 로드
    df = pd.read_csv(uploaded_file)
    st.session_state.df = df
    st.success(f"✅ 파일 로드 완료! ({len(df)}명 학생)")
    
    # 데이터 미리보기
    with st.expander("📄 데이터 미리보기"):
        st.dataframe(df.head(10), use_container_width=True)

# ==================== 데이터 확인 및 필터링 ====================
if 'df' in st.session_state:
    df = st.session_state.df
    
    # 성적 컬럼 자동 감지
    score_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if '학번' in score_cols:
        score_cols.remove('학번')
    
    st.header("2️⃣ 데이터 필터링 및 통계")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📚 총 학생 수", len(df))
    with col2:
        st.metric("📖 과목 수", len(score_cols))
    with col3:
        avg_score = df[score_cols].values.mean()
        st.metric("⭐ 평균 점수", f"{avg_score:.1f}")
    
    # 필터링 옵션
    with st.expander("🔍 필터링 옵션"):
        col1, col2 = st.columns(2)
        with col1:
            min_score = st.slider("최소 점수", 0, 100, 0)
        with col2:
            max_score = st.slider("최대 점수", 0, 100, 100)
        
        if '이름' in df.columns:
            selected_student = st.multiselect("학생 선택 (선택 없으면 전체)", df['이름'].unique())
            if selected_student:
                df_filtered = df[df['이름'].isin(selected_student)]
            else:
                df_filtered = df
        else:
            df_filtered = df
        
        # 점수 범위 필터
        df_filtered = df_filtered[
            (df_filtered[score_cols].mean(axis=1) >= min_score) & 
            (df_filtered[score_cols].mean(axis=1) <= max_score)
        ]
    
    st.write(f"**필터링 결과: {len(df_filtered)}명 학생**")
    
    # ==================== 시각화 1: 점수 분포 (히스토그램) ====================
    st.header("3️⃣ 시각화 분석")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 전체 점수 분포",
        "📈 과목별 비교",
        "🏆 등급 분포",
        "👤 개인별 분석",
        "📉 통계 요약",
        "💡 AI 기반 해석 및 추천"
    ])
    
    with tab1:
        st.subheader("전체 점수 분포 (히스토그램)")
        st.markdown("**기능**: 마우스를 올리면 구간별 학생 수 확인, 더블클릭하면 특정 범위 확대")
        
        all_scores = df_filtered[score_cols].values.flatten()
        
        fig = px.histogram(
            x=all_scores,
            nbins=20,
            title="전체 학생 점수 분포",
            labels={'x': '점수', 'count': '학생 수'},
            color_discrete_sequence=['#1f77b4']
        )
        fig.update_xaxes(range=[0, 105])
        fig.add_vline(x=np.mean(all_scores), line_dash="dash", line_color="red", annotation_text=f"평균: {np.mean(all_scores):.1f}")
        fig.add_vline(x=np.median(all_scores), line_dash="dot", line_color="green", annotation_text=f"중앙값: {np.median(all_scores):.1f}")
        st.plotly_chart(fig, use_container_width=True)
        
        # 통계 정보
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("최고점", f"{np.max(all_scores):.0f}")
        with col2:
            st.metric("최저점", f"{np.min(all_scores):.0f}")
        with col3:
            st.metric("평균", f"{np.mean(all_scores):.1f}")
        with col4:
            st.metric("표준편차", f"{np.std(all_scores):.1f}")
    
    with tab2:
        st.subheader("과목별 점수 비교")
        st.markdown("**기능**: 각 과목별 성과 비교, 과목별 평균값 확인")
        
        # 과목별 평균
        subject_avg = df_filtered[score_cols].mean()
        
        # 박스 플롯
        fig = go.Figure()
        for col in score_cols:
            fig.add_trace(go.Box(
                y=df_filtered[col],
                name=col,
                boxmean='sd'
            ))
        fig.update_layout(
            title="과목별 점수 분포 (박스 플롯)",
            yaxis_title="점수",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 과목별 평균 표시
        st.write("**과목별 평균 점수**")
        cols = st.columns(len(score_cols))
        
        for i, col in enumerate(score_cols):
            cols[i].metric(col, f"{subject_avg[col]:.1f}")
    
    with tab3:
        st.subheader("등급 분포")
        st.markdown("**기능**: A/B/C/D/F 등급별 학생 수 파악, 성적대별 학생 분류")
        
        # 평균 점수 기준 등급 분류
        def get_grade(score):
            if score >= 90: return 'A'
            elif score >= 80: return 'B'
            elif score >= 70: return 'C'
            elif score >= 60: return 'D'
            else: return 'F'
        
        df_filtered['평균'] = df_filtered[score_cols].mean(axis=1)
        df_filtered['등급'] = df_filtered['평균'].apply(get_grade)
        
        grade_counts = df_filtered['등급'].value_counts().sort_index(ascending=False)
        
        fig = px.bar(
            x=grade_counts.index,
            y=grade_counts.values,
            title="등급별 학생 분포",
            labels={'x': '등급', 'y': '학생 수'},
            color=grade_counts.index,
            color_discrete_map={'A': '#00cc66', 'B': '#0066cc', 'C': '#ffcc00', 'D': '#ff6600', 'F': '#cc0000'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 등급별 상세
        st.write("**등급별 학생 명단**")
        for grade in ['A', 'B', 'C', 'D', 'F']:
            if grade in df_filtered['등급'].values:
                students = df_filtered[df_filtered['등급'] == grade]
                st.write(f"**{grade} 등급 ({len(students)}명)**: {', '.join(students['이름'].values) if '이름' in students.columns else 'N/A'}")
    
    with tab4:
        st.subheader("개인별 상세 분석")
        st.markdown("**기능**: 특정 학생의 과목별 성적 비교, 전체 평균과 개인 성적 비교")
        
        if '이름' in df_filtered.columns:
            student_name = st.selectbox("학생 선택", df_filtered['이름'].values)
            student_data = df_filtered[df_filtered['이름'] == student_name].iloc[0]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                avg = student_data[score_cols].mean()
                st.metric("개인 평균", f"{avg:.1f}")
            with col2:
                overall_avg = df_filtered[score_cols].mean().mean()
                st.metric("반 평균", f"{overall_avg:.1f}")
            with col3:
                diff = avg - overall_avg
                st.metric("평가", f"{diff:+.1f}", delta="상위" if diff > 0 else "하위")
            
            # 과목별 성적 비교
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=[student_data[col] for col in score_cols],
                theta=score_cols,
                fill='toself',
                name=student_name
            ))
            fig.add_trace(go.Scatterpolar(
                r=[df_filtered[col].mean() for col in score_cols],
                theta=score_cols,
                fill='toself',
                name='반 평균'
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                title=f"{student_name} 학생 성적 분석",
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("이름 컬럼이 없습니다.")
    
    with tab5:
        st.subheader("통계 요약")
        st.markdown("**기능**: 전체 학생 성적의 통계적 분석")
        
        # 통계표
        stats_df = pd.DataFrame({
            '과목': score_cols,
            '평균': df_filtered[score_cols].mean().values,
            '중앙값': df_filtered[score_cols].median().values,
            '표준편차': df_filtered[score_cols].std().values,
            '최고점': df_filtered[score_cols].max().values,
            '최저점': df_filtered[score_cols].min().values,
        })
        
        st.dataframe(stats_df.style.format({'평균': '{:.2f}', '중앙값': '{:.2f}', '표준편차': '{:.2f}', '최고점': '{:.0f}', '최저점': '{:.0f}'}), use_container_width=True)
        
        # 상관관계 히트맵
        st.write("**과목 간 상관관계**")
        corr_matrix = df_filtered[score_cols].corr()
        
        fig = px.imshow(
            corr_matrix,
            text_auto='.2f',
            color_continuous_scale='RdBu_r',
            zmin=-1, zmax=1,
            title="과목 간 상관관계 분석"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # ==================== 데이터 다운로드 ====================
    st.header("4️⃣ 데이터 다운로드")
    
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 분석된 데이터 다운로드 (CSV)",
        data=csv,
        file_name="grades_analysis.csv",
        mime="text/csv"
    )

