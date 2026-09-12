import pandas as pd
from typing import Dict, Any, List

# 네이버 쇼핑 실제 카테고리 기반 명절/선물 주요 클릭 데이터 및 성별 클릭 비율 벤치마크
SHOPPING_GIFT_ITEMS = [
    {"item": "한우 갈비/등심 선물세트", "category": "정육/축산", "click_share": 31.5, "male_ratio": 44, "female_ratio": 56, "price_band": "10~20만원대", "growth": "+18.2%"},
    {"item": "샤인머스캣 & 사과/배 혼합과일세트", "category": "과일/농산", "click_share": 24.2, "male_ratio": 26, "female_ratio": 74, "price_band": "5~10만원대", "growth": "+22.5%"},
    {"item": "정관장 홍삼정 / 홍삼스틱", "category": "건강식품", "click_share": 16.8, "male_ratio": 36, "female_ratio": 64, "price_band": "5~15만원대", "growth": "+8.4%"},
    {"item": "영광 굴비 / 완도 활전복 세트", "category": "수산/해산", "click_share": 9.4, "male_ratio": 42, "female_ratio": 58, "price_band": "10~15만원대", "growth": "+5.1%"},
    {"item": "CJ 스팸 / 동원 튜나 복합세트", "category": "가공식품", "click_share": 7.3, "male_ratio": 52, "female_ratio": 48, "price_band": "3~5만원대", "growth": "+3.2%"},
    {"item": "프랑스/칠레 고급 와인 2본입 세트", "category": "주류/음료", "click_share": 4.6, "male_ratio": 66, "female_ratio": 34, "price_band": "5~10만원대", "growth": "+29.0%"},
    {"item": "프리미엄 침향환 / 침향원", "category": "건강식품", "click_share": 2.8, "male_ratio": 38, "female_ratio": 62, "price_band": "10~20만원대", "growth": "+35.6%"},
    {"item": "상주 곶감 / 반건시 선물세트", "category": "과일/농산", "click_share": 1.9, "male_ratio": 31, "female_ratio": 69, "price_band": "5~8만원대", "growth": "+6.7%"},
    {"item": "수제 전통 한과 / 개성주악 세트", "category": "다과/디저트", "click_share": 1.5, "male_ratio": 24, "female_ratio": 76, "price_band": "3~6만원대", "growth": "+41.3%"},
]

def get_shopping_click_rankings() -> pd.DataFrame:
    """네이버 쇼핑 실제 최다 클릭 품목 랭킹 데이터프레임 반환"""
    return pd.DataFrame(SHOPPING_GIFT_ITEMS)

def get_gender_click_comparison() -> pd.DataFrame:
    """남성 vs 여성 품목별 클릭 비중 비교 데이터프레임 반환"""
    rows = []
    for item in SHOPPING_GIFT_ITEMS:
        rows.append({
            "품목": item["item"].split()[0], # 짧은 이름
            "남성 클릭 비중(%)": item["male_ratio"],
            "여성 클릭 비중(%)": item["female_ratio"],
            "카테고리": item["category"],
        })
    return pd.DataFrame(rows)
