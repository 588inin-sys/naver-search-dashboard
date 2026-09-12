import streamlit as st

def apply_custom_styles():
    """대시보드 전체에 현대적인 글래스모피즘 및 네이버 브랜드 컬러 기반 커스텀 스타일 적용"""
    st.markdown(
        """
        <style>
        /* Pretendard 웹폰트 로드 */
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

        html, body, [class*="css"] {
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, 'Helvetica Neue', 'Segoe UI', 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif;
        }

        /* 메인 컨테이너 패딩 조절 */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1400px;
        }

        /* 글래스모피즘 KPI 카드 (라이트/다크 모드 적응형) */
        .kpi-card {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(0, 0, 0, 0.08);
            border-radius: 16px;
            padding: 1.25rem 1.5rem;
            margin-bottom: 1rem;
            transition: all 0.25s ease-in-out;
            box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.05);
        }

        /* 다크 모드일 때 카드 배경 */
        @media (prefers-color-scheme: dark) {
            .kpi-card {
                background: rgba(30, 41, 59, 0.7);
                border-color: rgba(255, 255, 255, 0.1);
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
            }
        }

        .kpi-card:hover {
            transform: translateY(-3px);
            border-color: rgba(3, 199, 90, 0.5);
            box-shadow: 0 10px 30px 0 rgba(3, 199, 90, 0.15);
        }

        .kpi-title {
            font-size: 0.8rem;
            color: #64748B;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.35rem;
        }

        .kpi-value {
            font-size: 1.75rem;
            font-weight: 800;
            color: #0F172A;
            letter-spacing: -0.02em;
        }

        @media (prefers-color-scheme: dark) {
            .kpi-value {
                color: #F8FAFC;
            }
            .kpi-title {
                color: #94A3B8;
            }
        }

        .kpi-sub {
            font-size: 0.8rem;
            color: #03C75A;
            font-weight: 500;
            margin-top: 0.25rem;
        }

        /* 네이버 시그니처 뱃지 */
        .naver-badge {
            display: inline-block;
            background: linear-gradient(135deg, #03C75A 0%, #00B048 100%);
            color: white;
            font-weight: 700;
            font-size: 0.75rem;
            padding: 3px 10px;
            border-radius: 20px;
            letter-spacing: 0.02em;
            box-shadow: 0 2px 8px rgba(3, 199, 90, 0.3);
        }

        /* 데모 모드 알림 뱃지 */
        .demo-badge {
            display: inline-block;
            background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
            color: white;
            font-weight: 700;
            font-size: 0.75rem;
            padding: 3px 10px;
            border-radius: 20px;
            letter-spacing: 0.02em;
        }

        /* 결과 카드 */
        .result-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 1rem 1.25rem;
            margin-bottom: 0.75rem;
            transition: all 0.2s ease;
        }

        .result-card:hover {
            background: rgba(255, 255, 255, 0.06);
            border-color: rgba(255, 255, 255, 0.2);
            transform: translateX(4px);
        }

        .result-title {
            font-size: 1.05rem;
            font-weight: 700;
            color: #38BDF8;
            text-decoration: none;
            margin-bottom: 0.4rem;
            display: block;
        }

        .result-title:hover {
            color: #03C75A;
            text-decoration: underline;
        }

        .result-desc {
            font-size: 0.9rem;
            color: #CBD5E1;
            line-height: 1.5;
            margin-bottom: 0.5rem;
        }

        .result-meta {
            font-size: 0.78rem;
            color: #64748B;
            display: flex;
            gap: 12px;
            align-items: center;
        }

        /* 탭 스타일링 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .stTabs [data-baseweb="tab"] {
            padding: 8px 16px;
            border-radius: 8px 8px 0 0;
            font-weight: 600;
        }

        /* 다운로드 버튼 스타일 */
        .stDownloadButton button {
            border-radius: 10px;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def render_kpi_card(title: str, value: str, subtext: str = "", badge_color: str = "#03C75A"):
    """HTML 기반 글래스모피즘 KPI 메트릭 카드 렌더링"""
    sub_html = f'<div class="kpi-sub" style="color: {badge_color};">{subtext}</div>' if subtext else ""
    html_code = f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        {sub_html}
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)
