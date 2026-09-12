import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pandas as pd
from src.config.settings import settings
from src.utils.text_cleaner import sanitize_keyword

def generate_mock_datalab_trend(
    keywords: List[str],
    start_date: str,
    end_date: str,
    time_unit: str = "date",
) -> Dict[str, Any]:
    """네이버 데이터랩 트렌드 모의 데이터 생성"""
    clean_kws = [sanitize_keyword(k) for k in keywords if sanitize_keyword(k)][:5]
    if not clean_kws:
        clean_kws = ["AI", "데이터분석"]

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    
    # 주기별 날짜 간격
    step_days = 1
    if time_unit == "week":
        step_days = 7
    elif time_unit == "month":
        step_days = 30

    date_list = []
    curr = start_dt
    while curr <= end_dt:
        date_list.append(curr.strftime("%Y-%m-%d"))
        curr += timedelta(days=step_days)

    rows = []
    summary_stats = {}

    for idx, kw in enumerate(clean_kws):
        base_seed = hash(kw) % 1000
        random.seed(base_seed)
        
        base_val = 30 + (idx * 15) % 40
        group_ratios = []
        data_points = []
        
        for i, dt_str in enumerate(date_list):
            # 주기적인 사인파 곡선 + 노이즈로 자연스러운 트렌드 생성
            wave = math.sin((i + idx * 3) / 5.0) * 20
            noise = random.uniform(-10, 15)
            # 특정 시점에 스파이크 발생
            spike = 30 if (i % 14 == 7) else 0
            val = max(5.0, min(100.0, base_val + wave + noise + spike))
            val = round(val, 1)
            group_ratios.append(val)
            data_points.append({"period": dt_str, "ratio": val})
            rows.append({
                "date": dt_str,
                "keyword": kw,
                "search_ratio": val,
            })

        max_ratio = max(group_ratios)
        avg_ratio = sum(group_ratios) / len(group_ratios)
        peak_date = next((dp["period"] for dp in data_points if dp["ratio"] == max_ratio), "")

        summary_stats[kw] = {
            "max_ratio": max_ratio,
            "avg_ratio": round(avg_ratio, 2),
            "peak_date": peak_date,
            "total_data_points": len(group_ratios),
        }

    df_trend = pd.DataFrame(rows)
    if not df_trend.empty:
        df_trend["date"] = pd.to_datetime(df_trend["date"])

    return {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": time_unit,
        "is_mock": True,
        "df": df_trend,
        "summary_stats": summary_stats,
    }

def generate_mock_search_results(
    keywords: List[str],
    display: int = 30,
) -> Dict[str, Dict[str, Any]]:
    """네이버 8개 검색 서비스 모의 데이터 생성"""
    all_keyword_results = {}

    for kw in keywords:
        kw = sanitize_keyword(kw)
        if not kw:
            continue
        
        random.seed(hash(kw) % 10000)
        items_by_service = {}
        total_counts = {}
        all_flattened = []

        for service in settings.SEARCH_ENDPOINTS.keys():
            service_name = settings.SERVICE_NAMES.get(service, service)
            total = random.randint(1500, 850000)
            total_counts[service] = total
            
            sample_items = []
            for i in range(1, display + 1):
                date_offset = random.randint(0, 90)
                pub_date = (datetime.now() - timedelta(days=date_offset)).strftime("%Y-%m-%d")
                
                title = f"[{service_name}] '{kw}' 최신 트렌드 및 마켓 분석 리포트 #{i}"
                desc = f"{kw} 관련 최신 시장 동향, 사용자 반응 및 인사이트를 다각도로 조사한 결과입니다. {kw}의 활용 사례와 향후 전망에 대해 심도 있는 데이터를 제공합니다."
                link = f"https://search.naver.com/search.naver?query={kw}"

                item = {
                    "id": f"{service}_{i}",
                    "query": kw,
                    "service": service,
                    "service_name": service_name,
                    "title": title,
                    "description": desc,
                    "link": link,
                    "date": pub_date,
                    "raw_date": pub_date,
                }

                if service == "image":
                    # Unsplash 더미 이미지 URL
                    item["thumbnail"] = f"https://picsum.photos/seed/{hash(kw + str(i)) % 1000}/300/200"
                    item["sizeheight"] = "200"
                    item["sizewidth"] = "300"
                elif service == "local":
                    item["category"] = f"전문점 > {kw} 관련"
                    item["telephone"] = f"02-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
                    item["address"] = f"서울특별시 강남구 테헤란로 {random.randint(10, 500)}"
                    item["roadAddress"] = f"서울특별시 강남구 테헤란로 {random.randint(10, 500)}길"
                elif service == "blog":
                    item["bloggername"] = f"{kw} 매니아 블로그"
                    item["bloggerlink"] = f"https://blog.naver.com/sample_{i}"
                elif service == "cafearticle":
                    item["cafename"] = f"{kw} 공식 커뮤니티"
                    item["cafeurl"] = f"https://cafe.naver.com/sample_{i}"

                sample_items.append(item)
                all_flattened.append(item)

            items_by_service[service] = sample_items

        all_keyword_results[kw] = {
            "query": kw,
            "total_counts": total_counts,
            "items_by_service": items_by_service,
            "all_items": all_flattened,
            "df_all": pd.DataFrame(all_flattened),
            "is_mock": True,
        }

    return all_keyword_results
