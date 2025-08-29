# K-NCT (Korean Non-native Corpus with Tags)

한국어 비원어민 말뭉치 데이터를 처리하는 Python 라이브러리입니다.

## 주요 기능

### 1. JSON 데이터 로드 및 검증
- `load_dataset()`: JSON 파일을 로드하고 pydantic을 사용하여 데이터 검증
- 자동 타입 검사 및 필수 필드 검증
- 데이터 구조 무결성 보장

### 2. 오류 태그 파싱
- `parse_errors()`: `<eN>...</eN>` 형태의 오류 태그를 파싱
- 정제된 텍스트와 오류 정보를 구조화된 형태로 반환

## Pydantic 모델

### KNCTEntry
개별 데이터 항목을 나타내는 모델:
- `index`: 데이터 인덱스
- `error_sentence`: 오류가 포함된 문장
- `correct_sentence`: 정정된 문장
- `domain`: 도메인
- `style`: 스타일
- `syllable`: 음절 수
- `phrase`: 구문 수
- `number_of_error`: 오류 개수
- `error_type`: 오류 타입

### ErrorInfo
오류 정보를 구조화하는 모델:
- `text`: 오류 텍스트
- `start`: 시작 인덱스
- `end`: 종료 인덱스
- `type`: 오류 타입

## 사용 예시

```python
from knct import load_dataset, parse_errors

# 데이터 로드 및 검증
data = load_dataset('data/K-NCT_v1.5.json')

# 오류 파싱
clean_text, errors = parse_errors(data[0])
print(f"정제된 텍스트: {clean_text}")
print(f"오류 정보: {[e.dict() for e in errors]}")
```

## 데이터 검증

pydantic을 사용하여 다음과 같은 검증을 수행합니다:
- 필수 필드 존재 여부
- 데이터 타입 정확성
- 데이터 구조 무결성
- 스키마 일치성

## 요구사항

- Python 3.7+
- pydantic

## 설치

```bash
pip install pydantic
```
