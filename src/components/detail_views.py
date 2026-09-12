from typing import List, Dict, Any
import streamlit as st

def render_news_cards(items: List[Dict[str, Any]]):
    """뉴스 검색 결과 카드 렌더링"""
    if not items:
        st.info("수집된 뉴스 데이터가 없습니다.")
        return

    for item in items:
        title = item.get("title", "")
        desc = item.get("description", "")
        link = item.get("link") or item.get("originallink", "#")
        date = item.get("date") or item.get("raw_date", "")

        st.markdown(
            f"""
            <div class="result-card">
                <a class="result-title" href="{link}" target="_blank">📰 {title}</a>
                <div class="result-desc">{desc}</div>
                <div class="result-meta">
                    <span>📅 {date}</span>
                    <span>🔗 <a href="{link}" target="_blank" style="color: #64748B;">원문 보기</a></span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

def render_blog_cards(items: List[Dict[str, Any]]):
    """블로그 검색 결과 카드 렌더링"""
    if not items:
        st.info("수집된 블로그 데이터가 없습니다.")
        return

    for item in items:
        title = item.get("title", "")
        desc = item.get("description", "")
        link = item.get("link", "#")
        blogger = item.get("bloggername", "네이버 블로거")
        date = item.get("date", "")

        st.markdown(
            f"""
            <div class="result-card">
                <a class="result-title" href="{link}" target="_blank">✍️ {title}</a>
                <div class="result-desc">{desc}</div>
                <div class="result-meta">
                    <span>👤 {blogger}</span>
                    <span>📅 {date}</span>
                    <span>🔗 <a href="{link}" target="_blank" style="color: #64748B;">블로그 바로가기</a></span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

def render_image_gallery(items: List[Dict[str, Any]]):
    """이미지 검색 결과 그리드 갤러리 렌더링 (4열 그리드)"""
    if not items:
        st.info("수집된 이미지 데이터가 없습니다.")
        return

    cols = st.columns(4)
    for idx, item in enumerate(items):
        col = cols[idx % 4]
        thumb = item.get("thumbnail") or item.get("link")
        title = item.get("title", f"이미지 #{idx+1}")
        link = item.get("link", "#")
        
        with col:
            if thumb:
                st.image(thumb, use_container_width=True, caption=title[:30] + ("..." if len(title) > 30 else ""))
            st.markdown(f"<a href='{link}' target='_blank' style='font-size:0.75rem; color:#38BDF8;'>원본 링크 ↗</a>", unsafe_allow_html=True)

def render_local_cards(items: List[Dict[str, Any]]):
    """지역/플레이스 검색 결과 카드 렌더링"""
    if not items:
        st.info("수집된 지역/플레이스 데이터가 없습니다.")
        return

    for item in items:
        title = item.get("title", "")
        category = item.get("category", "")
        road_addr = item.get("roadAddress") or item.get("address", "")
        tel = item.get("telephone", "전화번호 미등록")
        link = item.get("link") or f"https://map.naver.com/v5/search/{title}"

        st.markdown(
            f"""
            <div class="result-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <a class="result-title" href="{link}" target="_blank">📍 {title}</a>
                    <span style="background: rgba(99, 102, 241, 0.2); color:#A5B4FC; padding:2px 8px; border-radius:12px; font-size:0.75rem;">{category}</span>
                </div>
                <div class="result-desc" style="margin-top:0.3rem;">
                    🏠 {road_addr}<br>
                    📞 {tel}
                </div>
                <div class="result-meta">
                    <span>🗺️ <a href="{link}" target="_blank" style="color: #03C75A; font-weight:600;">네이버 지도에서 보기 ↗</a></span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

def render_cafe_cards(items: List[Dict[str, Any]]):
    """카페글 검색 결과 카드 렌더링"""
    if not items:
        st.info("수집된 카페 데이터가 없습니다.")
        return

    for item in items:
        title = item.get("title", "")
        desc = item.get("description", "")
        link = item.get("link", "#")
        cafe_name = item.get("cafename", "네이버 카페")

        st.markdown(
            f"""
            <div class="result-card">
                <a class="result-title" href="{link}" target="_blank">☕ {title}</a>
                <div class="result-desc">{desc}</div>
                <div class="result-meta">
                    <span>👥 {cafe_name}</span>
                    <span>🔗 <a href="{link}" target="_blank" style="color: #64748B;">카페글 보기</a></span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

def render_kin_cards(items: List[Dict[str, Any]]):
    """지식iN 검색 결과 카드 렌더링"""
    if not items:
        st.info("수집된 지식iN 데이터가 없습니다.")
        return

    for item in items:
        title = item.get("title", "")
        desc = item.get("description", "")
        link = item.get("link", "#")

        st.markdown(
            f"""
            <div class="result-card">
                <a class="result-title" href="{link}" target="_blank">💡 Q. {title}</a>
                <div class="result-desc">A. {desc}</div>
                <div class="result-meta">
                    <span>🔗 <a href="{link}" target="_blank" style="color: #64748B;">지식iN 질문/답변 전체보기</a></span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

def render_webkr_cards(items: List[Dict[str, Any]]):
    """웹문서 검색 결과 카드 렌더링"""
    if not items:
        st.info("수집된 웹문서 데이터가 없습니다.")
        return

    for item in items:
        title = item.get("title", "")
        desc = item.get("description", "")
        link = item.get("link", "#")

        st.markdown(
            f"""
            <div class="result-card">
                <a class="result-title" href="{link}" target="_blank">🌐 {title}</a>
                <div class="result-desc">{desc}</div>
                <div class="result-meta">
                    <span>🔗 <a href="{link}" target="_blank" style="color: #64748B;">{link}</a></span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

def render_encyc_cards(items: List[Dict[str, Any]]):
    """백과사전 검색 결과 카드 렌더링"""
    if not items:
        st.info("수집된 백과사전 데이터가 없습니다.")
        return

    for item in items:
        title = item.get("title", "")
        desc = item.get("description", "")
        link = item.get("link", "#")
        thumb = item.get("thumbnail")

        st.markdown(
            f"""
            <div class="result-card">
                <a class="result-title" href="{link}" target="_blank">📚 {title}</a>
                <div class="result-desc">{desc}</div>
                <div class="result-meta">
                    <span>🔗 <a href="{link}" target="_blank" style="color: #64748B;">지식백과 정의 보기</a></span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
