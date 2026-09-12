import io
import json
from datetime import datetime, date
import pandas as pd
from typing import Dict, Any, List

def to_csv_bytes(df: pd.DataFrame) -> bytes:
    """한국어 엑셀 호환을 위해 utf-8-sig 인코딩으로 CSV 바이트 반환"""
    return df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

def to_excel_bytes(dfs: Dict[str, pd.DataFrame]) -> bytes:
    """여러 데이터프레임을 시트별로 묶어 Excel xlsx 바이너리 바이트로 반환"""
    import re
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for sheet_name, df in dfs.items():
            # 엑셀 시트 이름에서 유효하지 않은 특수문자(/, \, ?, *, :, [, ]) 제거 및 31자 제한
            safe_sheet_name = re.sub(r'[/\\?*:[\]]', '_', str(sheet_name))[:30]
            if not df.empty:
                df.to_excel(writer, sheet_name=safe_sheet_name, index=False)
            else:
                pd.DataFrame({"알림": ["데이터가 없습니다."]}).to_excel(writer, sheet_name=safe_sheet_name, index=False)
    return output.getvalue()

def json_default_serializer(obj: Any) -> Any:
    """JSON 직렬화 불가능한 타입(DataFrame, Timestamp, Set, ndarray 등) 변환 핸들러"""
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="records")
    elif isinstance(obj, pd.Timestamp) or isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, set):
        return list(obj)
    elif hasattr(obj, "tolist"):
        return obj.tolist()
    elif hasattr(obj, "__dict__"):
        return obj.__dict__
    return str(obj)

def to_json_bytes(data: Any) -> bytes:
    """JSON 포맷 바이트 반환 (DataFrame 및 각종 객체 자동 직렬화)"""
    return json.dumps(data, ensure_ascii=False, indent=2, default=json_default_serializer).encode("utf-8")
