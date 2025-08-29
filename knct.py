import json
import re
from typing import List, Dict, Any
from pydantic import BaseModel, Field

# Pydantic 모델 정의
class KNCTEntry(BaseModel):
    """K-NCT 데이터의 개별 항목을 나타내는 모델"""
    index: int = Field(..., description="데이터 인덱스")
    error_sentence: str = Field(..., description="오류가 포함된 문장")
    correct_sentence: str = Field(..., description="정정된 문장")
    domain: str = Field(..., description="도메인")
    style: str = Field(..., description="스타일")
    syllable: int = Field(..., description="음절 수")
    phrase: int = Field(..., description="구문 수")
    number_of_error: int = Field(..., alias="number of error", description="오류 개수")
    error_type: Dict[str, str] = Field(..., description="오류 타입")
    
    class Config:
        allow_population_by_field_name = True

class KNCTSchema(BaseModel):
    """K-NCT 스키마를 나타내는 모델"""
    fields: List[Dict[str, Any]]
    primaryKey: List[str]
    pandas_version: str = Field(..., alias="pandas_version")

class KNCTDataset(BaseModel):
    """K-NCT 전체 데이터셋을 나타내는 모델"""
    dataset_schema: KNCTSchema = Field(..., alias="schema")
    data: List[KNCTEntry]

class GrammarError(BaseModel):
    """문법 오류 정보를 나타내는 모델"""
    text: str = Field(..., description="오류 텍스트")
    start: int = Field(..., description="clean_text 상에서의 시작 인덱스")
    end: int = Field(..., description="clean_text 상에서의 종료 인덱스 (exclusive)")
    type: str = Field(..., description="오류 타입")

def load_dataset(filepath='K-NCT_v1.5.json') -> List[KNCTEntry]:
    """
    JSON 파일을 로드하고 pydantic을 사용해서 validation을 수행합니다.
    
    Returns:
        List[KNCTEntry]: 검증된 데이터 리스트
    """
    try:
        # JSON 파일 로드
        with open(filepath, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        raise

    try:        
        # Pydantic 모델로 validation 수행
        validated_data = KNCTDataset(**raw_data)
        
        print(f'{len(validated_data.data)} sentences are loaded and validated successfully.')
        
        return validated_data.data
        
    except Exception as e:
        print(f"Error validating the data: {e}")
        raise

def parse_errors(entry: KNCTEntry) -> tuple[str, List[GrammarError]]:
    """
    <eN>…</eN> 형태의 오류 태그가 포함된 문장을 파싱하여
    - clean_text: 태그가 제거된 순수 문장
    - errors: GrammarError 객체들의 리스트
    를 반환한다.
    """
    sentence = entry.error_sentence
    error_type = entry.error_type
    
    # 오류 태그 전용 정규표현식: <eN>…</eN>
    tag_pattern = re.compile(r'<(e\d+)>(.*?)</\1>')
    
    errors: List[GrammarError] = []
    clean_parts: List[str] = []
    last_index = 0
    clean_index = 0  # clean_text 상의 누적 길이

    # 순회하며 태그와 태그 사이 텍스트 처리
    for m in tag_pattern.finditer(sentence):
        tag_name = m.group(1)       # e1, e2, ...
        error_text = m.group(2)     # 태그 내부의 실제 오류 텍스트
        span_start, span_end = m.span()

        # 태그 앞의 순수 텍스트 추가
        prefix = sentence[last_index:span_start]
        clean_parts.append(prefix)
        clean_index += len(prefix)

        # 오류 텍스트만 clean_text 에 추가
        clean_parts.append(error_text)

        # 오류 정보 기록 (clean_text 상의 인덱스 기준)
        error_info = GrammarError(
            text=error_text,
            start=clean_index,
            end=clean_index + len(error_text),            
            type=error_type[tag_name]
        )
        errors.append(error_info)
        clean_index += len(error_text)

        last_index = span_end

    # 마지막 태그 뒤 남은 텍스트 추가
    suffix = sentence[last_index:]
    clean_parts.append(suffix)

    clean_text = ''.join(clean_parts)

    return clean_text, errors
