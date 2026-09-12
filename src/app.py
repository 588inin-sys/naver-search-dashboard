import sys
from pathlib import Path

# 프로젝트 루트 경로를 sys.path에 추가하여 'src' 모듈 임포트 지원
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
from datetime import datetime

from src.config.settings import settings
from src.api.search_client import NaverSearchClient
from src.api.datalab_client import NaverDataLabClient
from src.api.mock_data import generate_mock_datalab_trend, generate_mock_search_results
from src.analysis.eda_engine import MarketInsightEDAEngine
from src.analysis.text_mining import (
    get_word_frequencies,
    get_ngrams,
    generate_wordcloud_dict,
    extract_product_entities,
    extract_target_relations,
)
from src.analysis.shopping_insight import get_shopping_click_rankings, get_gender_click_comparison
from src.components.styling import apply_custom_styles, render_kpi_card
from src.components.filters import render_sidebar_filters
from src.components.charts import (
    plot_datalab_trend,
    plot_channel_volume_comparison,
    plot_channel_share_donut,
    plot_word_frequency_bar,
    plot_ngram_bar,
    plot_product_items_bar,
    plot_target_relations_donut,
    plot_shopping_click_ranking,
    plot_gender_divergence_bar,
    create_wordcloud_figure,
)
from src.components.detail_views import (
    render_news_cards,
    render_blog_cards,
    render_image_gallery,
    render_local_cards,
    render_cafe_cards,
    render_kin_cards,
    render_webkr_cards,
    render_encyc_cards,
)
from src.utils.exporter import to_csv_bytes, to_excel_bytes, to_json_bytes

# 페이지 설정
st.set_page_config(
    page_title="네이버 마켓 인사이트 EDA 대시보드",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 커스텀 테마 스타일 적용
apply_custom_styles()

def fetch_market_data(filter_params: dict):
    """API 또는 모의 데이터로부터 검색 및 트렌드 데이터 수집"""
    keywords = filter_params["keywords"]
    is_demo = filter_params["is_demo_mode"]
    start_date = filter_params["start_date"]
    end_date = filter_params["end_date"]
    time_unit = filter_params["time_unit"]
    device = filter_params["device"]
    gender = filter_params["gender"]
    display_count = filter_params["display_count"]
    sort_order = filter_params["sort_order"]
    selected_services = filter_params["selected_services"]
    client_id = filter_params["client_id"]
    client_secret = filter_params["client_secret"]

    if not keywords:
        st.warning("검색어를 1개 이상 입력해 주세요.")
        return None, None

    # 1. 데이터랩 트렌드 데이터 수집
    trend_data = None
    if is_demo:
        trend_data = generate_mock_datalab_trend(keywords, start_date, end_date, time_unit)
    else:
        try:
            datalab_client = NaverDataLabClient(client_id, client_secret)
            trend_data = datalab_client.get_search_trend(
                keywords=keywords,
                start_date=start_date,
                end_date=end_date,
                time_unit=time_unit,
                device=device,
                gender=gender,
            )
        except Exception:
            # 트렌드 API 권한 미체크 시 모의 트렌드로 부드럽게 대체
            trend_data = generate_mock_datalab_trend(keywords, start_date, end_date, time_unit)
            trend_data["is_partial_fallback"] = True

    # 2. 8개 검색 서비스 데이터 수집
    keyword_results = {}
    if is_demo:
        keyword_results = generate_mock_search_results(keywords, display=display_count)
    else:
        search_client = NaverSearchClient(client_id, client_secret)
        for kw in keywords:
            try:
                res = search_client.search_all_services(
                    query=kw,
                    display=display_count,
                    sort=sort_order,
                    selected_services=selected_services,
                )
                keyword_results[kw] = res
            except Exception as e:
                st.error(f"⚠️ '{kw}' 검색 수집 중 오류: {e}")

    return trend_data, keyword_results


def main():
    # 사이드바 필터 렌더링
    filter_params = render_sidebar_filters()

    # 상단 헤더
    header_cols = st.columns([0.7, 0.3])
    with header_cols[0]:
        st.title("🟢 네이버 마켓 인사이트 EDA 대시보드")
        st.caption("네이버 오픈 API(검색 8개 채널 + 데이터랩 트렌드) 기반 시장 반응 및 키워드 탐색적 데이터 분석")
    with header_cols[1]:
        st.write("")
        if filter_params["is_demo_mode"]:
            st.markdown('<div style="text-align:right;"><span class="demo-badge">🎮 데모 체험 모드 활성</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align:right;"><span class="naver-badge">⚡ LIVE API 연동</span></div>', unsafe_allow_html=True)

    # 초기 로드 또는 검색 버튼 클릭 시 데이터 수집 및 세션 저장
    if filter_params["search_clicked"] or "cached_data" not in st.session_state:
        with st.spinner("네이버 API에서 마켓 인사이트 데이터를 수집 및 분석 중입니다..."):
            trend_data, keyword_results = fetch_market_data(filter_params)
            if keyword_results:
                st.session_state["cached_data"] = {
                    "trend_data": trend_data,
                    "keyword_results": keyword_results,
                    "filter_params": filter_params,
                }

    if "cached_data" not in st.session_state or not st.session_state["cached_data"]["keyword_results"]:
        st.info("👈 좌측 사이드바에서 검색어를 입력하고 **'마켓 인사이트 분석 실행'** 버튼을 클릭하세요.")
        return

    data = st.session_state["cached_data"]
    trend_data = data["trend_data"]
    keyword_results = data["keyword_results"]
    keywords = list(keyword_results.keys())

    # 데이터 분석 가공
    df_long = MarketInsightEDAEngine.build_channel_volume_long(keyword_results)
    df_matrix = MarketInsightEDAEngine.build_channel_volume_matrix(keyword_results)
    kpis = MarketInsightEDAEngine.calculate_overview_kpis(keyword_results, trend_data)
    combined_items_df = MarketInsightEDAEngine.get_combined_items_df(keyword_results)

    # 상단 KPI 메트릭 카드 4종
    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        render_kpi_card("총 시장 검색량 (Total Results)", f"{kpis['total_mentions']:,} 건", f"조사 키워드 {kpis['keyword_count']}개 합산")
    with kpi_cols[1]:
        render_kpi_card("최다 언급 키워드 (Top Volume)", str(kpis["top_keyword"]), "8개 채널 합산 1위", "#38BDF8")
    with kpi_cols[2]:
        render_kpi_card("최대 점유 채널 (Main Channel)", str(kpis["top_service"]), "가장 많은 콘텐츠 누적", "#F59E0B")
    with kpi_cols[3]:
        render_kpi_card("검색 트렌드 정점 (Peak Date)", str(kpis["peak_trend"]), "데이터랩 최대 검색 지수", "#EC4899")

    st.markdown("<br>", unsafe_allow_html=True)

    # 메인 대시보드 탭 구성
    tab1, tab2, tab_shop, tab3, tab4, tab5 = st.tabs([
        "📊 종합 개요 (Overview)",
        "📈 데이터랩 트렌드 (Trend)",
        "🛒 쇼핑 클릭 인사이트 (Shopping Click)",
        "🔤 텍스트 마이닝 & 마켓 품목 (Semantic EDA)",
        "📑 8개 채널별 세부 탐색 (Channel Explorer)",
        "💾 데이터 내보내기 (Export)",
    ])

    # ---------------- TAB 1: 종합 개요 ----------------
    with tab1:
        st.subheader("📊 키워드별 마켓 관심도 및 채널 점유율 현황")
        
        # 상단 트렌드 라인 차트
        if trend_data and "df" in trend_data and not trend_data["df"].empty:
            st.plotly_chart(plot_datalab_trend(trend_data["df"]), use_container_width=True)

        row_cols = st.columns([0.6, 0.4])
        with row_cols[0]:
            st.plotly_chart(plot_channel_volume_comparison(df_long), use_container_width=True)
        with row_cols[1]:
            kw_select_donut = st.selectbox("점유율 분석 키워드 선택", options=["전체 (All)"] + keywords, index=0)
            st.plotly_chart(plot_channel_share_donut(df_long, kw_select_donut), use_container_width=True)

        # 채널별 수치 요약 테이블
        with st.expander("📋 키워드 x 채널별 검색 결과량 매트릭스 표", expanded=False):
            st.dataframe(df_matrix.style.format(thousands=","), use_container_width=True)

    # ---------------- TAB 2: 데이터랩 트렌드 ----------------
    with tab2:
        st.subheader("📈 네이버 데이터랩(DataLab) 검색어 트렌드 심층 분석")
        if trend_data and trend_data.get("is_partial_fallback"):
            st.caption("ℹ️ 현재 트렌드 그래프는 예시 데이터로 표시 중입니다. (NCP 콘솔의 Application 설정에서 DataLab API를 켜시면 실제 데이터로 자동 전환됩니다)")
        if trend_data and "df" in trend_data and not trend_data["df"].empty:
            trend_df = trend_data["df"]
            st.plotly_chart(plot_datalab_trend(trend_df, f"기간: {filter_params['start_date']} ~ {filter_params['end_date']} (단위: {filter_params['time_unit']})"), use_container_width=True)

            # 트렌드 통계 지표 요약
            stats = trend_data.get("summary_stats", {})
            if stats:
                st.markdown("#### 📌 키워드별 트렌드 요약 통계")
                stat_rows = []
                for kw, s in stats.items():
                    stat_rows.append({
                        "키워드": kw,
                        "최대 검색량 지수 (Max)": f"{s['max_ratio']:.1f}",
                        "평균 검색량 지수 (Avg)": f"{s['avg_ratio']:.1f}",
                        "최고조 시점 (Peak Date)": s["peak_date"],
                        "데이터 포인트 수": s["total_data_points"],
                    })
                st.table(pd.DataFrame(stat_rows))
        else:
            st.info("데이터랩 트렌드 데이터가 없습니다.")

    # ---------------- TAB SHOP: 쇼핑 클릭 인사이트 ----------------
    with tab_shop:
        st.subheader("🛒 네이버 쇼핑 실제 최다 클릭 품목 & 남성/여성 선호도 EDA")
        st.caption("소비자들이 네이버에서 검색한 후 '실제 쇼핑 상품을 가장 많이 클릭하고 탐색한 품목 비중'과 '성별 클릭 선호 지수' 분석입니다.")

        df_shop_ranks = get_shopping_click_rankings()
        df_gender_clicks = get_gender_click_comparison()

        # 쇼핑 요약 지표 카드 3종
        scols = st.columns(3)
        with scols[0]:
            render_kpi_card("1위 최다 클릭 품목", "한우 선물세트 (31.5%)", "전체 명절 쇼핑 클릭 1위", "#03C75A")
        with scols[1]:
            render_kpi_card("여성 압도적 선호 1위", "과일/디저트세트 (74%)", "샤인머스캣/사과/한과", "#F43F5E")
        with scols[2]:
            render_kpi_card("남성 상대적 선호 1위", "고급 와인/주류 (66%)", "위스키 및 프리미엄 주류", "#38BDF8")

        st.markdown("<br>", unsafe_allow_html=True)

        shop_chart_cols = st.columns([0.55, 0.45])
        with shop_chart_cols[0]:
            st.plotly_chart(plot_shopping_click_ranking(df_shop_ranks, "네이버 쇼핑 실제 최다 클릭 품목 TOP 9"), use_container_width=True)
        with shop_chart_cols[1]:
            st.plotly_chart(plot_gender_divergence_bar(df_gender_clicks, "품목별 남성 vs 여성 클릭 비중 비교"), use_container_width=True)

        st.markdown("#### 📋 품목별 가격대 및 전년 대비 클릭 증가율")
        st.dataframe(
            df_shop_ranks.rename(columns={
                "item": "선물 품목",
                "category": "카테고리",
                "click_share": "클릭 점유율(%)",
                "male_ratio": "남성 비중(%)",
                "female_ratio": "여성 비중(%)",
                "price_band": "주요 가격대",
                "growth": "전년 대비 클릭 증가율",
            }),
            use_container_width=True,
            hide_index=True,
        )

    # ---------------- TAB 3: 텍스트 마이닝 ----------------
    with tab3:
        st.subheader("🔤 텍스트 마이닝 & 마켓 품목 탐색 (Semantic EDA)")
        
        mining_cols = st.columns([0.35, 0.65])
        with mining_cols[0]:
            target_kw = st.selectbox("분석 대상 키워드", options=["전체 키워드"] + keywords, index=0)
            custom_stop = st.text_input("추가 불용어 (쉼표로 구분)", placeholder="예: 할인, 이벤트, 매장")
            stopword_list = [s.strip() for s in custom_stop.split(",") if s.strip()]

        # 텍스트 데이터 추출
        if target_kw == "전체 키워드":
            corpus_df = combined_items_df
        else:
            corpus_df = combined_items_df[combined_items_df["query"] == target_kw]

        if not corpus_df.empty:
            titles_and_descs = (corpus_df["title"].fillna("") + " " + corpus_df["description"].fillna("")).tolist()
            
            # 1. 구체적인 인기 품목 및 선물 타겟 엔티티 추출
            df_products = extract_product_entities(titles_and_descs)
            df_targets = extract_target_relations(titles_and_descs)

            st.markdown("---")
            st.markdown("### 🎁 1. 실제 언급된 구체적 인기 품목/아이템 랭킹")
            st.caption("수집된 뉴스/블로그/카페/지식iN 본문에서 정육, 과일, 건강식품, 수산, 주류 등 실질 품목명만 자동 추출한 순위입니다.")
            
            prod_cols = st.columns([0.65, 0.35])
            with prod_cols[0]:
                if not df_products.empty:
                    st.plotly_chart(plot_product_items_bar(df_products, f"'{target_kw}' 인기 선물 품목 TOP 15"), use_container_width=True)
                else:
                    st.info("추출된 품목 데이터가 없습니다.")
            with prod_cols[1]:
                if not df_targets.empty:
                    st.plotly_chart(plot_target_relations_donut(df_targets, "선물 대상 (시댁/부모님/직장 등)"), use_container_width=True)
                else:
                    st.info("추출된 대상 데이터가 없습니다.")

            # 2. 일반 단어 빈도 및 연관어 N-gram
            st.markdown("---")
            st.markdown("### 🔤 2. 핵심 연관 단어 & 동시 출현 어휘 분석")
            
            # 검색어 자체는 빈도 목록에서 제외하여 유의미한 수식어/키워드만 남김
            search_terms_to_filter = keywords if target_kw == "전체 키워드" else [target_kw]
            df_freq = get_word_frequencies(titles_and_descs, top_n=25, custom_stopwords=stopword_list, filter_search_terms=search_terms_to_filter)
            df_ngram = get_ngrams(titles_and_descs, n=2, top_n=15, custom_stopwords=stopword_list, filter_search_terms=search_terms_to_filter)
            word_dict = generate_wordcloud_dict(titles_and_descs, max_words=80, custom_stopwords=stopword_list, filter_search_terms=search_terms_to_filter)

            tcols = st.columns(2)
            with tcols[0]:
                st.plotly_chart(plot_word_frequency_bar(df_freq, f"'{target_kw}' 핵심 연관 단어 (조사/일반어 제외)"), use_container_width=True)
            with tcols[1]:
                st.plotly_chart(plot_ngram_bar(df_ngram, f"'{target_kw}' 연관 단어 페어 (Bi-gram)"), use_container_width=True)

            # 3. 정제된 워드클라우드
            st.markdown("---")
            st.markdown("### ☁️ 3. 정제된 워드클라우드 (Word Cloud)")
            fig_wc = create_wordcloud_figure(word_dict)
            if fig_wc:
                st.pyplot(fig_wc, use_container_width=True)
            else:
                st.info("워드클라우드를 생성할 충분한 텍스트 데이터가 없습니다.")
        else:
            st.info("분석할 텍스트 콘텐츠가 없습니다.")

    # ---------------- TAB 4: 채널별 상세 탐색 ----------------
    with tab4:
        st.subheader("📑 네이버 8대 검색 서비스별 상세 수집 결과")
        
        detail_kw = st.selectbox("조회할 검색어 선택", options=keywords, index=0, key="detail_kw_selector")
        kw_data = keyword_results.get(detail_kw, {})
        items_by_svc = kw_data.get("items_by_service", {})

        # 채널 서브탭 생성
        svc_keys = list(settings.SEARCH_ENDPOINTS.keys())
        svc_tabs = st.tabs([f"📌 {settings.SERVICE_NAMES.get(k, k)} ({len(items_by_svc.get(k, []))})" for k in svc_keys])

        for idx, svc_key in enumerate(svc_keys):
            with svc_tabs[idx]:
                svc_items = items_by_svc.get(svc_key, [])
                
                # 내부 검색 필터
                sub_filter = st.text_input(f"'{settings.SERVICE_NAMES[svc_key]}' 내 검색어 필터링", key=f"filter_{svc_key}")
                if sub_filter:
                    svc_items = [it for it in svc_items if sub_filter.lower() in it.get("title", "").lower() or sub_filter.lower() in it.get("description", "").lower()]

                if svc_key == "news":
                    render_news_cards(svc_items)
                elif svc_key == "blog":
                    render_blog_cards(svc_items)
                elif svc_key == "image":
                    render_image_gallery(svc_items)
                elif svc_key == "local":
                    render_local_cards(svc_items)
                elif svc_key == "cafearticle":
                    render_cafe_cards(svc_items)
                elif svc_key == "kin":
                    render_kin_cards(svc_items)
                elif svc_key == "webkr":
                    render_webkr_cards(svc_items)
                elif svc_key == "encyc":
                    render_encyc_cards(svc_items)

    # ---------------- TAB 5: 데이터 내보내기 ----------------
    with tab5:
        st.subheader("💾 수집 데이터 확인 및 파일 내보내기 (Export)")
        
        if not combined_items_df.empty:
            st.markdown(f"총 **{len(combined_items_df):,}건**의 검색 데이터가 수집되었습니다.")
            
            # 컬럼 정리
            preview_cols = ["query", "service_name", "title", "description", "date", "link"]
            existing_cols = [c for c in preview_cols if c in combined_items_df.columns]
            st.dataframe(combined_items_df[existing_cols], use_container_width=True, height=400)

            # 다운로드 버튼
            st.markdown("#### 📥 파일 형식별 다운로드")
            down_cols = st.columns(3)

            with down_cols[0]:
                csv_bytes = to_csv_bytes(combined_items_df)
                st.download_button(
                    label="📄 CSV 파일 다운로드 (한글 Excel 호환)",
                    data=csv_bytes,
                    file_name=f"naver_market_insight_{datetime.today().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            with down_cols[1]:
                # 채널별 시트 분리 Excel 생성
                excel_dict = {"전체_통합": combined_items_df}
                for s_key in settings.SEARCH_ENDPOINTS.keys():
                    s_name = settings.SERVICE_NAMES.get(s_key, s_key)
                    s_df = combined_items_df[combined_items_df["service"] == s_key]
                    if not s_df.empty:
                        excel_dict[s_name] = s_df
                
                excel_bytes = to_excel_bytes(excel_dict)
                st.download_button(
                    label="📑 Excel (.xlsx) 시트별 다운로드",
                    data=excel_bytes,
                    file_name=f"naver_market_insight_{datetime.today().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

            with down_cols[2]:
                # JSON 직렬화를 위해 DataFrame 제외 순수 데이터만 추출
                clean_json_data = {}
                for kw, kw_info in keyword_results.items():
                    clean_json_data[kw] = {
                        "query": kw_info.get("query"),
                        "total_counts": kw_info.get("total_counts"),
                        "items_by_service": kw_info.get("items_by_service"),
                        "all_items": kw_info.get("all_items"),
                    }
                json_bytes = to_json_bytes(clean_json_data)
                st.download_button(
                    label="📦 JSON 원본 데이터 다운로드",
                    data=json_bytes,
                    file_name=f"naver_market_insight_{datetime.today().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    use_container_width=True,
                )
        else:
            st.info("내보낼 데이터가 없습니다.")

if __name__ == "__main__":
    main()
