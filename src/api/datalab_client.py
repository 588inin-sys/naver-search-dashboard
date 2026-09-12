from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pandas as pd
from src.api.base_client import BaseApiClient, NaverApiError
from src.config.settings import settings
from src.utils.text_cleaner import sanitize_keyword

class NaverDataLabClient(BaseApiClient):
    """네이버 데이터랩(DataLab) 검색어 트렌드 API 클라이언트"""

    def get_search_trend(
        self,
        keywords: List[str],
        start_date: str,
        end_date: str,
        time_unit: str = "date",
        device: Optional[str] = None,
        gender: Optional[str] = None,
        ages: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        네이버 데이터랩 통합 검색어 트렌드 조회
        """
        if not keywords:
            raise ValueError("검색어를 1개 이상 입력해야 합니다.")

        clean_keywords = [sanitize_keyword(k) for k in keywords if sanitize_keyword(k)][:5]
        keyword_groups = [
            {"groupName": kw, "keywords": [kw]} for kw in clean_keywords
        ]

        payload: Dict[str, Any] = {
            "startDate": start_date,
            "endDate": end_date,
            "timeUnit": time_unit,
            "keywordGroups": keyword_groups,
        }

        if device in ["pc", "mo"]:
            payload["device"] = device
        if gender in ["m", "f"]:
            payload["gender"] = gender
        if ages:
            payload["ages"] = ages

        # 1차로 NCP DataLab 엔드포인트 시도 후, 실패 시 Developers 엔드포인트 시도
        endpoints_to_try = [
            settings.NCP_DATALAB_TREND_ENDPOINT,
            settings.DEV_DATALAB_TREND_ENDPOINT,
        ]
        
        last_err = None
        for ep in endpoints_to_try:
            try:
                raw_response = self.post(ep, json_data=payload)
                return self._parse_trend_response(raw_response)
            except Exception as e:
                last_err = e

        raise last_err or NaverApiError("데이터랩 트렌드 API 조회에 실패했습니다.")

    def _parse_trend_response(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """데이터랩 응답을 시각화에 적합한 Tidy DataFrame 및 통계로 변환"""
        results = raw.get("results", [])
        rows = []
        summary_stats = {}

        for group in results:
            title = group.get("title", "")
            data_points = group.get("data", [])
            
            group_ratios = []
            for dp in data_points:
                period = dp.get("period")
                ratio = float(dp.get("ratio", 0.0))
                group_ratios.append(ratio)
                rows.append({
                    "date": period,
                    "keyword": title,
                    "search_ratio": ratio,
                })

            if group_ratios:
                max_ratio = max(group_ratios)
                avg_ratio = sum(group_ratios) / len(group_ratios)
                peak_date = next((dp["period"] for dp in data_points if float(dp.get("ratio", 0)) == max_ratio), "")
                summary_stats[title] = {
                    "max_ratio": max_ratio,
                    "avg_ratio": round(avg_ratio, 2),
                    "peak_date": peak_date,
                    "total_data_points": len(group_ratios),
                }

        df_trend = pd.DataFrame(rows)
        if not df_trend.empty:
            df_trend["date"] = pd.to_datetime(df_trend["date"])
            df_trend = df_trend.sort_values(by=["date", "keyword"])

        return {
            "startDate": raw.get("startDate"),
            "endDate": raw.get("endDate"),
            "timeUnit": raw.get("timeUnit"),
            "raw_results": results,
            "df": df_trend,
            "summary_stats": summary_stats,
        }
