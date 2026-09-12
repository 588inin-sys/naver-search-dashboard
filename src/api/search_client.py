from typing import Dict, Any, List, Optional
import pandas as pd
from src.api.base_client import BaseApiClient, NaverApiError
from src.config.settings import settings
from src.utils.text_cleaner import clean_html, parse_naver_date, sanitize_keyword

class NaverSearchClient(BaseApiClient):
    """네이버 8개 검색 서비스 API 클라이언트"""

    def search_service(
        self,
        service: str,
        query: str,
        display: int = 50,
        start: int = 1,
        sort: str = "sim",
    ) -> Dict[str, Any]:
        """
        특정 서비스(news, blog, webkr, image, kin, local, cafearticle, encyc)에 대한 검색 실행
        """
        if service not in settings.SEARCH_ENDPOINTS:
            raise ValueError(f"지원하지 않는 검색 서비스입니다: {service}")

        endpoint = settings.SEARCH_ENDPOINTS[service]
        params = {
            "query": sanitize_keyword(query),
            "display": min(max(display, 1), settings.MAX_DISPLAY),
            "start": min(max(start, 1), 1000),
        }

        # 정렬 파라미터가 유효한 서비스 (news, blog, cafearticle, kin 등)
        if service in ["news", "blog", "cafearticle", "kin", "image", "local"]:
            params["sort"] = sort

        raw_response = self.get(endpoint, params=params)
        return self._normalize_search_response(service, query, raw_response)

    def search_all_services(
        self,
        query: str,
        display: int = 50,
        sort: str = "sim",
        selected_services: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        단일 키워드에 대해 선택된 모든 검색 서비스의 데이터를 병합 수집
        """
        services_to_search = selected_services or list(settings.SEARCH_ENDPOINTS.keys())
        results = {}
        total_counts = {}
        items_by_service = {}
        all_flattened_items = []

        for service in services_to_search:
            try:
                res = self.search_service(service, query, display=display, sort=sort)
                results[service] = res
                total_counts[service] = res.get("total", 0)
                items = res.get("items", [])
                items_by_service[service] = items
                all_flattened_items.extend(items)
            except Exception as e:
                # 개별 서비스 실패 시에도 대시보드가 죽지 않도록 에러 기록 후 계속 진행
                results[service] = {"error": str(e), "total": 0, "items": []}
                total_counts[service] = 0
                items_by_service[service] = []

        return {
            "query": query,
            "total_counts": total_counts,
            "items_by_service": items_by_service,
            "all_items": all_flattened_items,
            "df_all": pd.DataFrame(all_flattened_items) if all_flattened_items else pd.DataFrame(),
        }

    def _normalize_search_response(self, service: str, query: str, raw: Dict[str, Any]) -> Dict[str, Any]:
        """API 원본 응답을 통일된 스키마 구조로 정규화"""
        total = raw.get("total", 0)
        raw_items = raw.get("items", [])
        normalized_items = []

        for idx, item in enumerate(raw_items, 1):
            title = clean_html(item.get("title", ""))
            description = clean_html(item.get("description", ""))
            link = item.get("link") or item.get("originallink", "")
            
            # 날짜 파싱
            date_raw = item.get("pubDate") or item.get("postdate") or ""
            date_cleaned = parse_naver_date(date_raw)

            entry: Dict[str, Any] = {
                "id": f"{service}_{idx}",
                "query": query,
                "service": service,
                "service_name": settings.SERVICE_NAMES.get(service, service),
                "title": title,
                "description": description,
                "link": link,
                "date": date_cleaned,
                "raw_date": date_raw,
            }

            # 서비스별 특화 필드 추가
            if service == "news":
                entry["originallink"] = item.get("originallink", "")
            elif service == "blog":
                entry["bloggername"] = item.get("bloggername", "")
                entry["bloggerlink"] = item.get("bloggerlink", "")
            elif service == "image":
                entry["thumbnail"] = item.get("thumbnail", "")
                entry["sizeheight"] = item.get("sizeheight", "")
                entry["sizewidth"] = item.get("sizewidth", "")
            elif service == "local":
                entry["category"] = item.get("category", "")
                entry["telephone"] = item.get("telephone", "")
                entry["address"] = item.get("address", "")
                entry["roadAddress"] = item.get("roadAddress", "")
                entry["mapx"] = item.get("mapx", "")
                entry["mapy"] = item.get("mapy", "")
            elif service == "cafearticle":
                entry["cafename"] = item.get("cafename", "")
                entry["cafeurl"] = item.get("cafeurl", "")
            elif service == "encyc":
                entry["thumbnail"] = item.get("thumbnail", "")

            normalized_items.append(entry)

        return {
            "query": query,
            "service": service,
            "service_name": settings.SERVICE_NAMES.get(service, service),
            "total": total,
            "display": raw.get("display", len(normalized_items)),
            "start": raw.get("start", 1),
            "items": normalized_items,
            "df": pd.DataFrame(normalized_items) if normalized_items else pd.DataFrame(),
        }
