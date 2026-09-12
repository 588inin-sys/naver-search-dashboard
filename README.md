# 🟢 네이버 마켓 인사이트 EDA 대시보드 (Naver Market Insight Dashboard)

네이버 오픈 API(검색 API 8종 + 데이터랩 검색어 트렌드 API)를 활용하여 다중 검색어와 기간별 시장 반응, 채널 점유율, 시계열 트렌드 및 의미론적 텍스트 마이닝을 수행하는 **탐색적 데이터 분석(EDA) Streamlit 대시보드**입니다.

---

## 🚀 빠른 시작 (Quick Start with `uv`)

본 프로젝트는 초고속 파이썬 패키지 관리자 **`uv`**를 사용하여 구동됩니다.

### 1. 가상환경 생성 및 패키지 설치
```bash
# 가상환경 생성
python -m uv venv .venv

# 가상환경 활성화 (Windows PowerShell)
.\.venv\Scripts\activate

# 의존성 패키지 설치
python -m uv pip install -r pyproject.toml
```

### 2. 네이버 API 키 설정 (.env)
1. [네이버 개발자 센터](https://developers.naver.com/apps/#/register)에서 애플리케이션 등록
2. 사용 API 항목에서 **'검색'** 및 **'데이터랩(검색어트렌드)'** 권한 추가
3. 프로젝트 루트의 `.env` 파일에 발급받은 키 입력:

```env
NAVER_CLIENT_ID=your_actual_client_id
NAVER_CLIENT_SECRET=your_actual_client_secret
```

> 💡 **API 키가 없거나 테스트 목적일 경우**: API 키 없이도 대시보드 내 **'🎮 체험용 데모 모드'**를 통해 모든 시각화 및 EDA 기능을 즉시 체험할 수 있습니다.

### 3. 대시보드 서버 실행
```bash
.\.venv\Scripts\streamlit run src/app.py
```
브라우저에서 `http://localhost:8501`로 접속합니다.

---

## 📂 프로젝트 폴더 구조 (책임별 분리)

```text
naver-search-dashboard/
├── .env.example              # 환경변수 템플릿
├── .env                      # 실제 API Key 저장 파일
├── pyproject.toml            # uv 프로젝트 의존성 명세
├── README.md                 # 프로젝트 가이드
├── src/
│   ├── app.py                # Streamlit 메인 애플리케이션
│   ├── config/               # 설정 및 환경변수 로더
│   │   ├── __init__.py
│   │   └── settings.py       # API URL 및 상수 정의
│   ├── api/                  # 네이버 API 통신 계층
│   │   ├── __init__.py
│   │   ├── base_client.py    # 공통 HTTP 요청 및 에러 핸들러
│   │   ├── search_client.py  # 8대 검색 API (뉴스/블로그/웹/이미지/지식iN/지역/카페/백과)
│   │   ├── datalab_client.py # 데이터랩 검색어 트렌드 API
│   │   └── mock_data.py      # 데모 체험용 모의 데이터 생성기
│   ├── analysis/             # EDA 및 텍스트 마이닝 통계 엔진
│   │   ├── __init__.py
│   │   ├── eda_engine.py     # 채널 점유율, 매트릭스 집계, KPI 연산
│   │   └── text_mining.py    # 한국어 형태소/명사 빈도, N-gram, 워드클라우드 사전
│   ├── components/           # UI 컴포넌트 및 시각화 차트
│   │   ├── __init__.py
│   │   ├── styling.py        # 글래스모피즘 CSS 및 KPI 카드
│   │   ├── filters.py        # 사이드바 입력 폼 (키워드/기간/기기/성별/채널)
│   │   ├── charts.py         # Plotly 인터랙티브 차트 (트렌드, 도넛, 바, 워드클라우드)
│   │   └── detail_views.py   # 8개 채널별 특화 결과 뷰어 (이미지 갤러리, 지도 등)
│   └── utils/                # 유틸리티
│       ├── __init__.py
│       ├── text_cleaner.py   # HTML 태그 제거 및 날짜 정규화
│       └── exporter.py       # CSV, Excel(.xlsx), JSON 내보내기
```

---

## 🎯 주요 분석 및 시각화 기능

1. **📊 종합 개요 (Overview & KPIs)**:
   - 총 시장 검색량, 최다 언급 키워드, 최다 점유 채널, 트렌드 피크 시점 4종 KPI 카드
   - 시계열 검색어 트렌드 라인 차트 & 채널별 검색량 비교 바 차트 & 점유율 도넛 차트
2. **📈 데이터랩 트렌드 (Trend Deep Dive)**:
   - 다중 키워드 시계열 상대 검색량(0~100) 비교
   - 일간/주간/월간 단위 및 기기(PC/모바일), 성별 세부 필터링
   - 키워드별 피크 시점 및 평균 지수 통계 테이블
3. **🔤 텍스트 마이닝 & 연관어 EDA**:
   - 제목 및 본문 요약문 기반 고빈도 키워드 TOP 20
   - 동시 출현 연관어 쌍(Bi-gram) 분석
   - 반응형 워드클라우드 (Word Cloud) 시각화
4. **📑 8대 검색 채널 상세 탐색**:
   - 뉴스, 블로그, 웹문서, 이미지(4열 갤러리), 지식iN, 지역(지도/주소/전화번호), 카페글, 백과사전
   - 서비스별 실시간 텍스트 필터링 및 원문 바로가기 링크
5. **💾 다형식 데이터 내보내기 (Export)**:
   - 한글 Excel 완벽 호환 `CSV (UTF-8-SIG)`
   - 채널별 시트 분리 `Excel (.xlsx)`
   - 계층형 `JSON` 파일 다운로드 지원
