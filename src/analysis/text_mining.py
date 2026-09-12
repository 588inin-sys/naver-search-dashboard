import re
from collections import Counter
from typing import List, Tuple, Dict, Any, Optional, Set
import pandas as pd

# 1. 확장된 한국어 불용어 및 일상/조사/질문형 어휘 목록
KOREAN_STOPWORDS = {
    # 기본 조사/접속사/대명사
    "이", "그", "저", "것", "수", "등", "및", "를", "을", "에", "의", "가", "은", "는", "로", "으로",
    "에서", "와", "과", "도", "하다", "있다", "되다", "대한", "통해", "위해", "관련", "이번", "올해",
    "더", "잘", "못", "때", "곳", "년", "월", "일", "개", "명", "위", "건", "중", "전", "후",
    
    # 검색/포털/홍보 관련 일반어
    "네이버", "검색", "조회", "결과", "제공", "사진", "뉴스", "블로그", "카페", "지식", "출처",
    "보기", "더보기", "안내", "문의", "바로가기", "클릭", "이용", "사용", "확인", "소개", "글",
    "내용", "포스팅", "업로드", "관련", "정보", "최신", "인기", "방법", "정리", "후기", "리뷰",
    
    # 질문/의견/감정/수식어 (명절/쇼핑 데이터에서 품목을 가리는 불용어)
    "너무", "정말", "진짜", "많이", "가장", "어떤", "어떻게", "좋은", "좋을까요", "어떨까요",
    "추천", "부탁", "질문", "답변", "고민", "생각", "준비", "보낼", "드릴", "하는", "하는데",
    "해서", "해주세요", "알려주세요", "있을까요", "좋겠어요", "할지", "다들", "어디", "지금",
    "오늘", "내일", "요즘", "같은", "다른", "있는", "없는", "많은", "적은", "이런", "저런",
    "우리", "저희", "제가", "무엇", "혹시", "얼마", "가격", "비용", "구입", "구매", "선택",
    "어르신", "가족", "사람", "분들", "모두", "하나", "두개", "세트", "선물세트", "선물", "추석",
    "명절", "설날", "한가위", "추석선물", "명절선물", "설선물"
}

# 2. 마켓/선물/소비재 핵심 품목 및 브랜드 사전
MARKET_PRODUCT_CATALOG = {
    # 정육 / 축산
    "한우": ["한우", "소고기", "갈비", "LA갈비", "꽃등심", "불고기", "안심", "채끝", "살치살", "우족", "사골", "한우세트", "갈비세트", "정육"],
    "돼지고기": ["돼지고기", "삼겹살", "목살", "돈육", "이베리코"],
    
    # 과일 / 농산
    "과일": ["과일", "사과", "배", "샤인머스캣", "샤인머스켓", "망고", "애플망고", "멜론", "머스크멜론", "감", "곶감", "반건시", "복숭아", "자두", "포도", "과일세트", "혼합과일"],
    "견과/버섯/특산품": ["견과류", "견과", "호두", "아몬드", "버섯", "표고버섯", "송이버섯", "상황버섯", "더덕", "도라지", "인삼", "수삼", "참기름", "들기름", "꿀", "벌꿀"],
    
    # 수산 / 해산물
    "수산/해산물": ["굴비", "영광굴비", "보리굴비", "전복", "옥돔", "갈치", "멸치", "김", "곱창김", "새우", "대하", "게장", "간장게장", "연어", "참치회", "수산물"],
    
    # 건강기능식품 / 영양제 / 한방
    "건강식품/홍삼": ["홍삼", "정관장", "수삼", "흑삼", "침향", "침향원", "녹용", "공진단", "경옥고", "컴파운드케이", "도라지청", "배도라지", "생강청", "흑마늘", "비타민", "유산균", "오메가3", "영양제", "프로폴리스", "콜라겐", "루테인", "건강식품", "건강기능식품"],
    
    # 가공식품 / 조미료 / 커피/티
    "가공식품/오일": ["스팸", "리챔", "참치", "동원참치", "식용유", "카놀라유", "올리브유", "아보카도유", "트러플오일", "햄", "통조림", "조미료", "장류", "고추장", "된장"],
    "디저트/다과/음료": ["한과", "약과", "떡", "화과자", "수제쿠키", "쿠키", "양갱", "베이커리", "커피", "원두", "더치커피", "차", "티세트", "전통차", "홍차", "녹차"],
    
    # 주류 / 주류세트
    "주류/와인": ["와인", "레드와인", "화이트와인", "위스키", "싱글몰트", "꼬냑", "전통주", "막걸리", "소주", "사케", "증류주", "주류세트"],
    
    # 생활/뷰티/바디/리빙
    "생활/뷰티/바디": ["화장품", "설화수", "스킨케어", "에센스", "바디워시", "바디세트", "샴푸", "샴푸세트", "치약세트", "핸드크림", "향수", "디퓨저", "수건", "타올", "주방용품", "식기", "냄비"],
    
    # 현금/상품권/기타
    "상품권/용돈": ["상품권", "백화점상품권", "온누리상품권", "신세계상품권", "롯데상품권", "용돈", "용돈박스", "플라워박스", "현금", "기프티콘"],
}

# 3. 대상/관계 키워드 사전
TARGET_RELATION_CATALOG = {
    "시댁/시부모님": ["시댁", "예비시댁", "시부모님", "시아버지", "시어머니", "시가"],
    "부모님/친정": ["부모님", "친정", "친정부모님", "아버지", "어머니", "엄마", "아빠"],
    "직장/거래처": ["거래처", "직장", "회사", "상사", "동료", "직원", "고객", "바이어", "선생님", "교수님"],
    "연인/예비배우자": ["남친", "여친", "남자친구", "여자친구", "예비신랑", "예비신부", "상견례"],
    "친척/지인": ["친척", "이모", "삼촌", "고모", "조카", "친구", "지인", "이웃"]
}

def clean_korean_token(word: str) -> str:
    """한국어 단어 끝에 붙은 조사/어미를 분리 및 정제"""
    word = word.strip()
    # 2글자 단어는 보존
    if len(word) <= 2:
        return word
    
    # 대표적인 조사/어미 패턴 제거 (예: 추석선물로 -> 추석선물, 시댁에 -> 시댁, 한우를 -> 한우)
    suffix_pattern = r"(에서|으로|에게|한테|께서|보다|처럼|마다|이나|이랑|하고|이며|로서|로써|라고|까지|부터|을|를|에|의|가|은|는|로|와|과|도|만|라|네|다|요|죠|할|된|할지|하는|했던|해서)$"
    cleaned = re.sub(suffix_pattern, "", word)
    return cleaned if len(cleaned) >= 2 else word

def extract_tokens(
    text: str,
    min_len: int = 2,
    custom_stopwords: Optional[List[str]] = None,
    filter_search_terms: Optional[List[str]] = None,
) -> List[str]:
    """한글/영문 텍스트에서 품사/조사 정제 후 의미 있는 키워드 토큰 추출"""
    if not text:
        return []
    
    stopwords = KOREAN_STOPWORDS.union(set(custom_stopwords or []))
    if filter_search_terms:
        for st in filter_search_terms:
            stopwords.add(st.strip())
            for sub in st.strip().split():
                stopwords.add(sub)

    # 한글, 영문, 숫자 단어 단위 추출
    raw_words = re.findall(r"[가-힣a-zA-Z0-9]+", text)
    
    tokens = []
    for w in raw_words:
        if w.isdigit() or len(w) < min_len:
            continue
        
        # 소문자화 및 조사 정제
        w_cleaned = clean_korean_token(w.lower())
        
        if len(w_cleaned) < min_len or w_cleaned in stopwords:
            continue
        tokens.append(w_cleaned)
        
    return tokens

def extract_product_entities(texts: List[str]) -> pd.DataFrame:
    """
    수집된 본문/제목 텍스트 전체에서 실제 '구체적인 선물 품목/아이템'만 핀포인트 추출 및 집계
    """
    category_counts = Counter()
    specific_item_counts = Counter()
    item_to_category = {}

    # 검색 사전 인덱싱
    flat_items = []
    for cat, items in MARKET_PRODUCT_CATALOG.items():
        for it in items:
            flat_items.append((it, cat))
            item_to_category[it] = cat

    for text in texts:
        if not text:
            continue
        text_lower = text.lower()
        
        for it, cat in flat_items:
            # 단어가 텍스트에 포함되어 있는지 탐색 (단어 등장 횟수 카운트)
            occurrences = len(re.findall(re.escape(it), text_lower))
            if occurrences > 0:
                specific_item_counts[it] += occurrences
                category_counts[cat] += occurrences

    rows = []
    for it, count in specific_item_counts.most_common(30):
        rows.append({
            "item": it,
            "category": item_to_category.get(it, "기타"),
            "count": count,
        })

    df = pd.DataFrame(rows)
    return df

def extract_target_relations(texts: List[str]) -> pd.DataFrame:
    """
    수집된 텍스트에서 '선물 대상 / 타겟 관계(시댁, 부모님, 거래처 등)' 추출 및 집계
    """
    target_counts = Counter()
    for text in texts:
        if not text:
            continue
        for group, keywords in TARGET_RELATION_CATALOG.items():
            for kw in keywords:
                cnt = len(re.findall(re.escape(kw), text))
                if cnt > 0:
                    target_counts[group] += cnt

    rows = [{"target": t, "count": c} for t, c in target_counts.most_common(10)]
    return pd.DataFrame(rows)

def get_word_frequencies(
    texts: List[str],
    top_n: int = 30,
    min_len: int = 2,
    custom_stopwords: Optional[List[str]] = None,
    filter_search_terms: Optional[List[str]] = None,
) -> pd.DataFrame:
    """단어별 출현 빈도수 데이터프레임 생성 (조사 정제 및 불용어 제거)"""
    counter = Counter()

    for text in texts:
        tokens = extract_tokens(
            text,
            min_len=min_len,
            custom_stopwords=custom_stopwords,
            filter_search_terms=filter_search_terms,
        )
        counter.update(tokens)

    most_common = counter.most_common(top_n)
    if not most_common:
        return pd.DataFrame(columns=["word", "frequency"])
    
    df = pd.DataFrame(most_common, columns=["word", "frequency"])
    return df

def get_ngrams(
    texts: List[str],
    n: int = 2,
    top_n: int = 20,
    custom_stopwords: Optional[List[str]] = None,
    filter_search_terms: Optional[List[str]] = None,
) -> pd.DataFrame:
    """연관 단어 쌍 (N-gram / Collocation) 빈도 분석"""
    ngram_counter = Counter()

    for text in texts:
        tokens = extract_tokens(
            text,
            custom_stopwords=custom_stopwords,
            filter_search_terms=filter_search_terms,
        )
        if len(tokens) < n:
            continue
        for i in range(len(tokens) - n + 1):
            ngram = " + ".join(tokens[i : i + n])
            ngram_counter[ngram] += 1

    most_common = ngram_counter.most_common(top_n)
    if not most_common:
        return pd.DataFrame(columns=["ngram", "frequency"])
    
    df = pd.DataFrame(most_common, columns=["ngram", "frequency"])
    return df

def generate_wordcloud_dict(
    texts: List[str],
    max_words: int = 100,
    custom_stopwords: Optional[List[str]] = None,
    filter_search_terms: Optional[List[str]] = None,
) -> Dict[str, int]:
    """워드클라우드용 {단어: 빈도} 딕셔너리 생성 (의미 있는 실질 명사 위주)"""
    counter = Counter()

    for text in texts:
        tokens = extract_tokens(
            text,
            custom_stopwords=custom_stopwords,
            filter_search_terms=filter_search_terms,
        )
        counter.update(tokens)

    return dict(counter.most_common(max_words))
