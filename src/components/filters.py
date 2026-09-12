from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
import streamlit as st
from src.config.settings import settings

def render_sidebar_filters() -> Dict[str, Any]:
    """사이드바 입력 필터 및 파라미터 제어 컴포넌트"""
    st.sidebar.markdown(
        """
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:1rem;">
            <div class="naver-badge">NAVER OPEN API</div>
            <span style="font-weight:700; font-size:1.1rem; color:#F8FAFC;">마켓 인사이트</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. API 인증 및 모드 설정
    with st.sidebar.expander("🔑 API 인증 설정 (.env)", expanded=False):
        client_id_env = settings.NAVER_CLIENT_ID
        client_secret_env = settings.NAVER_CLIENT_SECRET
        
        client_id = st.text_input(
            "Client ID",
            value=client_id_env,
            type="password",
            placeholder="발급받은 Client ID 입력",
            help=".env 파일에 NAVER_CLIENT_ID로 저장하면 자동으로 불러옵니다.",
        )
        client_secret = st.text_input(
            "Client Secret",
            value=client_secret_env,
            type="password",
            placeholder="발급받은 Client Secret 입력",
            help=".env 파일에 NAVER_CLIENT_SECRET로 저장하면 자동으로 불러옵니다.",
        )

        has_keys = bool(client_id and client_secret)
        if has_keys:
            st.success("✅ API 키가 설정되었습니다.")
        else:
            st.warning("⚠️ API 키가 없습니다. 아래 데모 모드로 체험 가능합니다.")

    # 데모 모드 스위치
    is_demo_mode = False
    if not (client_id and client_secret):
        is_demo_mode = True
        st.sidebar.info("💡 API 키가 미등록되어 **체험용 데모 모드**로 동작합니다.")
    else:
        is_demo_mode = st.sidebar.checkbox("🎮 체험용 데모 모드로 실행", value=False)

    st.sidebar.divider()

    # 2. 검색어 및 기간 입력
    st.sidebar.markdown("### 🔍 검색 및 기간 설정")
    
    keyword_input = st.sidebar.text_input(
        "검색어 (쉼표 `,`로 구분)",
        value="생성형AI, 챗GPT, 클로드",
        help="비교 분석할 키워드를 쉼표로 구분하여 최대 5개까지 입력하세요.",
    )
    
    # 쉼표 구분 리스트 정제
    keywords = [k.strip() for k in keyword_input.split(",") if k.strip()]
    if len(keywords) > 5:
        st.sidebar.warning("⚠️ 데이터랩 트렌드는 최대 5개 키워드까지 비교 가능합니다. 상위 5개만 적용됩니다.")
        keywords = keywords[:5]

    # 기간 설정 (기본값: 최근 3개월)
    today = datetime.today()
    default_start = today - timedelta(days=90)
    
    date_cols = st.sidebar.columns(2)
    with date_cols[0]:
        start_date = st.date_input("시작일", value=default_start, max_value=today)
    with date_cols[1]:
        end_date = st.date_input("종료일", value=today, min_value=start_date, max_value=today)

    # 3. 데이터랩 상세 필터
    time_unit = st.sidebar.selectbox(
        "트렌드 분석 구간 단위",
        options=["date", "week", "month"],
        format_func=lambda x: {"date": "📅 일간 (Daily)", "week": "📆 주간 (Weekly)", "month": "🗓️ 월간 (Monthly)"}.get(x, x),
        index=0,
    )

    with st.sidebar.expander("⚙️ 세부 필터 (디바이스 / 성별)", expanded=False):
        device_opt = st.selectbox(
            "기기 구분",
            options=["", "pc", "mo"],
            format_func=lambda x: {"": "전체 (PC+모바일)", "pc": "🖥️ PC", "mo": "📱 모바일"}.get(x, x),
        )
        gender_opt = st.selectbox(
            "성별 구분",
            options=["", "m", "f"],
            format_func=lambda x: {"": "전체 (남녀 모두)", "m": "👨 남성", "f": "👩 여성"}.get(x, x),
        )

    # 4. 검색 수집 옵션
    with st.sidebar.expander("📦 검색 채널 및 수집 설정", expanded=False):
        display_count = st.slider("채널당 수집 건수 (Display)", min_value=10, max_value=100, value=50, step=10)
        sort_order = st.radio("정렬 방식", options=["sim", "date"], format_func=lambda x: "정확도/관련도순 (sim)" if x == "sim" else "최신순 (date)", index=0)
        
        selected_services = []
        st.markdown("**수집 대상 채널 선택:**")
        service_cols = st.columns(2)
        for idx, (svc_key, svc_name) in enumerate(settings.SERVICE_NAMES.items()):
            col = service_cols[idx % 2]
            with col:
                if st.checkbox(svc_name, value=True, key=f"svc_chk_{svc_key}"):
                    selected_services.append(svc_key)

    st.sidebar.divider()
    search_clicked = st.sidebar.button("🚀 마켓 인사이트 분석 실행", type="primary", use_container_width=True)

    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "is_demo_mode": is_demo_mode,
        "keywords": keywords,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "time_unit": time_unit,
        "device": device_opt or None,
        "gender": gender_opt or None,
        "display_count": display_count,
        "sort_order": sort_order,
        "selected_services": selected_services,
        "search_clicked": search_clicked,
    }
