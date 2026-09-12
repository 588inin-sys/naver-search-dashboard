from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from src.config.settings import settings

class MarketInsightEDAEngine:
    """네이버 검색 및 트렌드 데이터에 대한 탐색적 데이터 분석(EDA) 엔진"""

    @staticmethod
    def build_channel_volume_matrix(keyword_results: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
        """
        키워드별 x 채널별 검색 총 결과 수(Total Count) 매트릭스 생성
        """
        rows = []
        for kw, res in keyword_results.items():
            total_counts = res.get("total_counts", {})
            row = {"keyword": kw}
            for service, count in total_counts.items():
                service_name = settings.SERVICE_NAMES.get(service, service)
                row[service_name] = count
            rows.append(row)
        
        df = pd.DataFrame(rows)
        return df

    @staticmethod
    def build_channel_volume_long(keyword_results: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
        """
        Plotly 차트 렌더링을 위한 Long-format 채널별 데이터프레임 생성
        """
        rows = []
        for kw, res in keyword_results.items():
            total_counts = res.get("total_counts", {})
            total_all = sum(total_counts.values()) or 1
            for service, count in total_counts.items():
                service_name = settings.SERVICE_NAMES.get(service, service)
                share = (count / total_all) * 100
                rows.append({
                    "keyword": kw,
                    "service": service,
                    "service_name": service_name,
                    "count": count,
                    "share_percent": round(share, 2),
                })
        return pd.DataFrame(rows)

    @staticmethod
    def calculate_overview_kpis(
        keyword_results: Dict[str, Dict[str, Any]],
        trend_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        대시보드 상단 주요 KPI 요약 지표 산출
        """
        total_market_mentions = 0
        keyword_totals = {}
        channel_totals = {s: 0 for s in settings.SEARCH_ENDPOINTS.keys()}

        for kw, res in keyword_results.items():
            total_counts = res.get("total_counts", {})
            kw_sum = sum(total_counts.values())
            keyword_totals[kw] = kw_sum
            total_market_mentions += kw_sum
            for s, c in total_counts.items():
                channel_totals[s] = channel_totals.get(s, 0) + c

        top_keyword = max(keyword_totals, key=keyword_totals.get) if keyword_totals else "-"
        top_service_code = max(channel_totals, key=channel_totals.get) if channel_totals else "news"
        top_service_name = settings.SERVICE_NAMES.get(top_service_code, top_service_code)

        # 트렌드 피크 정보
        peak_info = "-"
        if trend_data and "summary_stats" in trend_data:
            stats = trend_data["summary_stats"]
            if stats:
                highest_kw = max(stats, key=lambda k: stats[k].get("max_ratio", 0))
                peak_date = stats[highest_kw].get("peak_date", "")
                peak_info = f"{highest_kw} ({peak_date})"

        return {
            "total_mentions": total_market_mentions,
            "top_keyword": top_keyword,
            "top_service": top_service_name,
            "peak_trend": peak_info,
            "keyword_count": len(keyword_results),
            "channel_totals": channel_totals,
        }

    @staticmethod
    def get_combined_items_df(keyword_results: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
        """모든 키워드와 모든 채널의 수집 아이템을 단일 데이터프레임으로 병합"""
        dfs = []
        for kw, res in keyword_results.items():
            df = res.get("df_all")
            if df is not None and not df.empty:
                dfs.append(df)
        if dfs:
            return pd.concat(dfs, ignore_index=True)
        return pd.DataFrame()
