import re
import html
from datetime import datetime
from typing import Optional

def clean_html(text: Optional[str]) -> str:
    """HTML 태그(<b>, </b> 등) 및 HTML 엔티티를 정제하여 순수 텍스트로 변환"""
    if not text:
        return ""
    # HTML 엔티티 언이스케이프 (&quot;, &amp;, &lt;, &gt;, &#39; 등)
    text = html.unescape(text)
    # HTML 태그 제거
    text = re.sub(r"<[^>]+>", "", text)
    # 다중 공백 단일화 및 양끝 공백 제거
    text = re.sub(r"\s+", " ", text).strip()
    return text

def parse_naver_date(date_str: Optional[str]) -> Optional[str]:
    """
    네이버 API가 반환하는 다양한 날짜 포맷을 'YYYY-MM-DD' 또는 'YYYY-MM-DD HH:MM'으로 정규화
    - 뉴스/지식iN/블로그/카페: 'Wed, 19 May 2021 15:30:00 +0900' (RFC 822)
    - 블로그/카페 postdate: '20210519' (YYYYMMDD)
    - 백과사전/웹문서 등 기타 포맷
    """
    if not date_str:
        return None
    
    date_str = date_str.strip()
    
    # 1. '20230519' 포맷
    if len(date_str) == 8 and date_str.isdigit():
        try:
            dt = datetime.strptime(date_str, "%Y%m%d")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    # 2. RFC 822 포맷 (예: 'Wed, 19 May 2021 15:30:00 +0900')
    try:
        # 시간대 offset 처리 (+0900 등)
        dt = datetime.strptime(date_str[:25], "%a, %d %b %Y %H:%M:%S")
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        pass

    # 3. 'YYYY-MM-DD' 형태 이미 되어 있는 경우
    if re.match(r"^\d{4}-\d{2}-\d{2}", date_str):
        return date_str[:10]

    return date_str

def sanitize_keyword(keyword: str) -> str:
    """검색어 전처리 (앞뒤 공백 제거 및 중복 공백 정제)"""
    return re.sub(r"\s+", " ", keyword.strip())
