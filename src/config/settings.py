import os
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 위치 로드 (루트 디렉토리 기준)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

class Settings:
    @property
    def NAVER_CLIENT_ID(self) -> str:
        load_dotenv(dotenv_path=ENV_PATH, override=True)
        return os.getenv("NAVER_CLIENT_ID", "").strip()

    @property
    def NAVER_CLIENT_SECRET(self) -> str:
        load_dotenv(dotenv_path=ENV_PATH, override=True)
        return os.getenv("NAVER_CLIENT_SECRET", "").strip()

    # NAVER API HUB (네이버 클라우드 플랫폼 NCP) 엔드포인트
    NCP_API_HUB_BASE: str = "https://naverapihub.apigw.ntruss.com"
    NCP_SEARCH_ENDPOINTS = {
        "news": "https://naverapihub.apigw.ntruss.com/search/v1/news",
        "blog": "https://naverapihub.apigw.ntruss.com/search/v1/blog",
        "webkr": "https://naverapihub.apigw.ntruss.com/search/v1/webkr",
        "image": "https://naverapihub.apigw.ntruss.com/search/v1/image",
        "kin": "https://naverapihub.apigw.ntruss.com/search/v1/kin",
        "local": "https://naverapihub.apigw.ntruss.com/search/v1/local",
        "cafearticle": "https://naverapihub.apigw.ntruss.com/search/v1/cafearticle",
        "encyc": "https://naverapihub.apigw.ntruss.com/search/v1/encyc",
    }
    NCP_DATALAB_TREND_ENDPOINT = "https://naveropenapi.apigw.ntruss.com/datalab/v1/search"

    # 기존 네이버 개발자 센터(openapi.naver.com) 엔드포인트
    DEV_SEARCH_ENDPOINTS = {
        "news": "https://openapi.naver.com/v1/search/news.json",
        "blog": "https://openapi.naver.com/v1/search/blog.json",
        "webkr": "https://openapi.naver.com/v1/search/webkr.json",
        "image": "https://openapi.naver.com/v1/search/image",
        "kin": "https://openapi.naver.com/v1/search/kin.json",
        "local": "https://openapi.naver.com/v1/search/local.json",
        "cafearticle": "https://openapi.naver.com/v1/search/cafearticle.json",
        "encyc": "https://openapi.naver.com/v1/search/encyc.json",
    }
    DEV_DATALAB_TREND_ENDPOINT = "https://openapi.naver.com/v1/datalab/search"

    # 기본 검색 엔드포인트
    SEARCH_ENDPOINTS = NCP_SEARCH_ENDPOINTS
    DATALAB_TREND_ENDPOINT = NCP_DATALAB_TREND_ENDPOINT

    # 서비스 한국어 명칭 매핑
    SERVICE_NAMES = {
        "news": "뉴스",
        "blog": "블로그",
        "webkr": "웹문서",
        "image": "이미지",
        "kin": "지식iN",
        "local": "지역/플레이스",
        "cafearticle": "카페글",
        "encyc": "백과사전",
    }

    DEFAULT_DISPLAY: int = 50
    MAX_DISPLAY: int = 100
    REQUEST_TIMEOUT: int = 10

settings = Settings()
