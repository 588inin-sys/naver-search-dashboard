import requests
from typing import Dict, Any, Optional
from src.config.settings import settings

class NaverApiError(Exception):
    """네이버 API 요청 관련 커스텀 예외"""
    def __init__(self, message: str, status_code: Optional[int] = None, error_code: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code

class BaseApiClient:
    """NAVER API HUB (NCP) 및 네이버 오픈 API 통신을 위한 기본 클라이언트"""

    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        self.client_id = (client_id or settings.NAVER_CLIENT_ID).strip()
        self.client_secret = (client_secret or settings.NAVER_CLIENT_SECRET).strip()
        self.timeout = settings.REQUEST_TIMEOUT

    @property
    def is_configured(self) -> bool:
        """API 인증 정보가 입력되었는지 확인"""
        return bool(self.client_id and self.client_secret)

    def _get_headers(self) -> Dict[str, str]:
        """NAVER API HUB(NCP) 및 기존 Open API 인증 헤더 동시 제공"""
        if not self.is_configured:
            raise NaverApiError("네이버 API 클라이언트 ID 또는 시크릿이 설정되지 않았습니다. .env 파일이나 사이드바를 확인해 주세요.", status_code=401)
        return {
            # NAVER Cloud Platform (NAVER API HUB) 헤더
            "X-NCP-APIGW-API-KEY-ID": self.client_id,
            "X-NCP-APIGW-API-KEY": self.client_secret,
            # 네이버 개발자 센터 (Legacy Open API) 헤더
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret,
            "Content-Type": "application/json",
            "User-Agent": "NaverMarketInsightDashboard/1.0",
        }

    def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """GET 요청 실행 (엔드포인트 자동 폴백 지원)"""
        headers = self._get_headers()
        try:
            response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
            return self._handle_response(response, url)
        except requests.exceptions.Timeout:
            raise NaverApiError("API 요청 시간이 초과되었습니다 (Timeout). 잠시 후 다시 시도해 주세요.")
        except requests.exceptions.ConnectionError:
            raise NaverApiError("네트워크 연결에 실패했습니다. 인터넷 연결 상태를 확인해 주세요.")
        except Exception as e:
            if isinstance(e, NaverApiError):
                raise e
            raise NaverApiError(f"API 요청 중 예기치 않은 오류가 발생했습니다: {str(e)}")

    def post(self, url: str, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """POST 요청 실행"""
        headers = self._get_headers()
        try:
            response = requests.post(url, headers=headers, json=json_data, timeout=self.timeout)
            return self._handle_response(response, url)
        except requests.exceptions.Timeout:
            raise NaverApiError("API 요청 시간이 초과되었습니다 (Timeout). 잠시 후 다시 시도해 주세요.")
        except requests.exceptions.ConnectionError:
            raise NaverApiError("네트워크 연결에 실패했습니다. 인터넷 연결 상태를 확인해 주세요.")
        except Exception as e:
            if isinstance(e, NaverApiError):
                raise e
            raise NaverApiError(f"API 요청 중 예기치 않은 오류가 발생했습니다: {str(e)}")

    def _handle_response(self, response: requests.Response, url: str = "") -> Dict[str, Any]:
        """응답 상태 코드 검증 및 JSON 파싱"""
        if response.status_code == 200:
            try:
                return response.json()
            except Exception:
                raise NaverApiError("응답 데이터(JSON)를 파싱할 수 없습니다.")
        
        # 에러 메시지 추출
        error_msg = f"HTTP {response.status_code}"
        try:
            err_json = response.json()
            if isinstance(err_json, dict):
                error_msg = (
                    err_json.get("errorMessage")
                    or err_json.get("message")
                    or (err_json.get("error", {}).get("message") if isinstance(err_json.get("error"), dict) else None)
                    or response.text
                )
        except Exception:
            error_msg = response.text or error_msg

        if response.status_code == 401:
            raise NaverApiError(f"인증 또는 권한 오류 (401): {error_msg} (NCP 콘솔에서 해당 API가 활성화되어 있는지 확인해 주세요)", status_code=401)
        elif response.status_code == 403:
            raise NaverApiError(f"권한 없음 (403): {error_msg}", status_code=403)
        elif response.status_code == 429:
            raise NaverApiError("호출 한도 초과 (429): API 일일/월간 호출 한도를 초과했습니다.", status_code=429)
        else:
            raise NaverApiError(f"API 요청 실패 ({response.status_code}): {error_msg}", status_code=response.status_code)
