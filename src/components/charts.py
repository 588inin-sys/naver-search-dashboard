import os
from typing import Dict, Any, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# 다크 모드 및 모던 차트 테마 색상 팔레트
CHART_COLORS = [
    "#03C75A",  # Naver Green
    "#6366F1",  # Indigo
    "#06B6D4",  # Cyan
    "#F43F5E",  # Rose
    "#F59E0B",  # Amber
    "#8B5CF6",  # Violet
    "#10B981",  # Emerald
    "#EC4899",  # Pink
]

def get_korean_font_path() -> Optional[str]:
    """시스템 내 한글 폰트 경로 탐색 (Windows Malgun Gothic 등)"""
    candidate_paths = [
        "C:/Windows/Fonts/malgun.ttf",
        "C:/Windows/Fonts/gulim.ttc",
        "C:/Windows/Fonts/batang.ttc",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    ]
    for path in candidate_paths:
        if os.path.exists(path):
            return path
    return None

def plot_datalab_trend(df_trend: pd.DataFrame, title: str = "네이버 데이터랩 검색어 트렌드 추이") -> go.Figure:
    """데이터랩 검색어 트렌드 시계열 라인 차트"""
    if df_trend.empty:
        fig = go.Figure()
        fig.update_layout(title="트렌드 데이터가 없습니다.")
        return fig

    fig = px.line(
        df_trend,
        x="date",
        y="search_ratio",
        color="keyword",
        color_discrete_sequence=CHART_COLORS,
        labels={"date": "날짜", "search_ratio": "상대 검색량 (0~100)", "keyword": "검색어"},
        title=f"📈 {title}",
        markers=True,
    )

    fig.update_traces(
        line=dict(width=2.5),
        marker=dict(size=5),
        hovertemplate="<b>%{data.name}</b><br>날짜: %{x|%Y-%m-%d}<br>검색량 지수: <b>%{y:.1f}</b><extra></extra>",
    )

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=50, b=20),
        hovermode="x unified",
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", range=[0, 105]),
    )
    return fig

def plot_channel_volume_comparison(df_long: pd.DataFrame) -> go.Figure:
    """검색어별 8개 서비스 채널 검색 결과량 비교 바 차트"""
    if df_long.empty:
        return go.Figure()

    fig = px.bar(
        df_long,
        x="service_name",
        y="count",
        color="keyword",
        barmode="group",
        color_discrete_sequence=CHART_COLORS,
        labels={"service_name": "검색 서비스", "count": "총 검색 결과 수", "keyword": "검색어"},
        title="📊 채널별 검색 결과량 비교 (Volume EDA)",
        text_auto=".2s",
    )

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)"),
    )
    return fig

def plot_channel_share_donut(df_long: pd.DataFrame, selected_keyword: Optional[str] = None) -> go.Figure:
    """채널 점유율 도넛 차트"""
    if df_long.empty:
        return go.Figure()

    filtered_df = df_long
    title = "🍩 전체 채널별 언급 비중"
    if selected_keyword and selected_keyword != "전체 (All)":
        filtered_df = df_long[df_long["keyword"] == selected_keyword]
        title = f"🍩 '{selected_keyword}' 채널별 언급 비중"

    agg_df = filtered_df.groupby("service_name")["count"].sum().reset_index()

    fig = px.pie(
        agg_df,
        values="count",
        names="service_name",
        hole=0.55,
        color_discrete_sequence=CHART_COLORS,
        title=title,
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>결과 수: %{value:,}건<br>비중: <b>%{percent}</b><extra></extra>",
    )

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
    )
    return fig

def plot_word_frequency_bar(df_freq: pd.DataFrame, title: str = "주요 키워드 출현 빈도 TOP 20") -> go.Figure:
    """상위 빈도 단어 수평 바 차트"""
    if df_freq.empty:
        return go.Figure()

    top_df = df_freq.head(20).iloc[::-1]  # 높은 순이 위로 오도록 역순 정렬

    fig = px.bar(
        top_df,
        x="frequency",
        y="word",
        orientation="h",
        color="frequency",
        color_continuous_scale=["#0284C7", "#03C75A"],
        labels={"frequency": "출현 빈도", "word": "단어"},
        title=f"🔤 {title}",
        text="frequency",
    )

    fig.update_traces(textposition="outside")

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)"),
        yaxis=dict(showgrid=False),
    )
    return fig

def plot_ngram_bar(df_ngram: pd.DataFrame, title: str = "연관어 쌍 (Bi-gram) TOP 15") -> go.Figure:
    """연관어 쌍(N-gram) 수평 바 차트"""
    if df_ngram.empty:
        return go.Figure()

    top_df = df_ngram.head(15).iloc[::-1]

    fig = px.bar(
        top_df,
        x="frequency",
        y="ngram",
        orientation="h",
        color="frequency",
        color_continuous_scale=["#6366F1", "#EC4899"],
        labels={"frequency": "동시 출현 빈도", "ngram": "연관어 조합"},
        title=f"🔗 {title}",
        text="frequency",
    )

    fig.update_traces(textposition="outside")

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)"),
        yaxis=dict(showgrid=False),
    )
    return fig

def plot_product_items_bar(df_products: pd.DataFrame, title: str = "실시간 인기 품목/아이템 TOP 15") -> go.Figure:
    """수집된 문서에서 추출된 구체적 선물 품목 랭킹 바 차트"""
    if df_products.empty:
        return go.Figure()

    top_df = df_products.head(15).iloc[::-1]

    fig = px.bar(
        top_df,
        x="count",
        y="item",
        color="category",
        orientation="h",
        labels={"count": "언급 횟수", "item": "구체적 품목명", "category": "카테고리"},
        title=f"🎁 {title}",
        text="count",
    )

    fig.update_traces(textposition="outside")

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)"),
        yaxis=dict(showgrid=False),
    )
    return fig

def plot_target_relations_donut(df_targets: pd.DataFrame, title: str = "선물 대상/타겟 비중") -> go.Figure:
    """선물 대상/관계 비중 도넛 차트"""
    if df_targets.empty:
        return go.Figure()

    fig = px.pie(
        df_targets,
        values="count",
        names="target",
        hole=0.5,
        color_discrete_sequence=CHART_COLORS,
        title=f"👥 {title}",
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>언급 수: %{value:,}건<br>비중: <b>%{percent}</b><extra></extra>",
    )

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig

def plot_shopping_click_ranking(df_shop: pd.DataFrame, title: str = "네이버 쇼핑 최다 클릭 품목 랭킹 TOP") -> go.Figure:
    """네이버 쇼핑 최다 클릭 품목 수평 바 차트"""
    if df_shop.empty:
        return go.Figure()

    top_df = df_shop.iloc[::-1]

    fig = px.bar(
        top_df,
        x="click_share",
        y="item",
        color="category",
        orientation="h",
        labels={"click_share": "클릭 점유율 (%)", "item": "선물 품목명", "category": "카테고리"},
        title=f"🛒 {title}",
        text="click_share",
    )

    fig.update_traces(texttemplate="%{x:.1f}%", textposition="outside")

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", range=[0, 38]),
        yaxis=dict(showgrid=False),
    )
    return fig

def plot_gender_divergence_bar(df_gender: pd.DataFrame, title: str = "남성 vs 여성 품목별 클릭 선호도 비교") -> go.Figure:
    """남성 vs 여성 품목별 클릭 비중 비교 그룹 바 차트"""
    if df_gender.empty:
        return go.Figure()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df_gender["품목"],
        x=df_gender["남성 클릭 비중(%)"],
        name="👨 남성 클릭 비중",
        orientation="h",
        marker=dict(color="#38BDF8"),
        text=df_gender["남성 클릭 비중(%)"].apply(lambda v: f"{v}%"),
        textposition="inside",
    ))
    fig.add_trace(go.Bar(
        y=df_gender["품목"],
        x=df_gender["여성 클릭 비중(%)"],
        name="👩 여성 클릭 비중",
        orientation="h",
        marker=dict(color="#F43F5E"),
        text=df_gender["여성 클릭 비중(%)"].apply(lambda v: f"{v}%"),
        textposition="inside",
    ))

    fig.update_layout(
        title=f"👫 {title}",
        barmode="stack",
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", range=[0, 105]),
        yaxis=dict(showgrid=False),
    )
    return fig

def create_wordcloud_figure(word_dict: Dict[str, int]) -> Optional[plt.Figure]:
    """워드클라우드 Matplotlib Figure 생성"""
    if not word_dict:
        return None

    font_path = get_korean_font_path()
    
    wc_kwargs = {
        "width": 900,
        "height": 450,
        "background_color": "#0F172A",
        "colormap": "viridis",
        "max_words": 100,
        "prefer_horizontal": 0.85,
    }
    if font_path:
        wc_kwargs["font_path"] = font_path

    try:
        wc = WordCloud(**wc_kwargs).generate_from_frequencies(word_dict)
        fig, ax = plt.subplots(figsize=(10, 5), facecolor="#0F172A")
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        plt.tight_layout(pad=0)
        return fig
    except Exception:
        return None
