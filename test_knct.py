#!/usr/bin/env python3
"""
K-NCT 라이브러리 테스트 파일
pydantic validation, 데이터 로딩, 오류 파싱 등의 기능을 테스트합니다.
"""

import unittest
import tempfile
import json
import os
from knct import (
    KNCTEntry, KNCTSchema, KNCTDataset, GrammarError,
    load_dataset, parse_errors
)


class TestKNCTModels(unittest.TestCase):
    """Pydantic 모델 테스트"""
    
    def test_knct_entry_valid(self):
        """유효한 KNCTEntry 생성 테스트"""
        entry_data = {
            "index": 0,
            "error_sentence": "테스트 <e1>문장</e1>입니다.",
            "correct_sentence": "테스트 문장입니다.",
            "domain": "test",
            "style": "test",
            "syllable": 8,
            "phrase": 3,
            "number of error": 1,
            "error_type": {"e1": "test_error"}
        }
        
        entry = KNCTEntry(**entry_data)
        self.assertEqual(entry.index, 0)
        self.assertEqual(entry.error_sentence, "테스트 <e1>문장</e1>입니다.")
        self.assertEqual(entry.number_of_error, 1)
        self.assertEqual(entry.error_type["e1"], "test_error")
    
    def test_knct_entry_missing_field(self):
        """필수 필드 누락 테스트"""
        entry_data = {
            "index": 0,
            # "error_sentence" 필드 누락
            "correct_sentence": "테스트 문장입니다.",
            "domain": "test",
            "style": "test",
            "syllable": 8,
            "phrase": 3,
            "number of error": 1,
            "error_type": {"e1": "test_error"}
        }
        
        with self.assertRaises(Exception):
            KNCTEntry(**entry_data)
    
    def test_knct_entry_invalid_type(self):
        """잘못된 타입 테스트"""
        entry_data = {
            "index": "문자열인덱스",  # int가 아닌 str
            "error_sentence": "테스트 문장입니다.",
            "correct_sentence": "테스트 문장입니다.",
            "domain": "test",
            "style": "test",
            "syllable": 8,
            "phrase": 3,
            "number of error": 1,
            "error_type": {"e1": "test_error"}
        }
        
        with self.assertRaises(Exception):
            KNCTEntry(**entry_data)
    
    def test_grammar_error_valid(self):
        """유효한 GrammarError 생성 테스트"""
        error_info = GrammarError(
            text="테스트",
            start=0,
            end=3,
            type="test_error"
        )
        
        self.assertEqual(error_info.text, "테스트")
        self.assertEqual(error_info.start, 0)
        self.assertEqual(error_info.end, 3)
        self.assertEqual(error_info.type, "test_error")
    
    def test_knct_dataset_valid(self):
        """유효한 KNCTDataset 생성 테스트"""
        dataset_data = {
            "schema": {
                "fields": [{"name": "index", "type": "integer"}],
                "primaryKey": ["index"],
                "pandas_version": "0.20.0"
            },
            "data": [
                {
                    "index": 0,
                    "error_sentence": "테스트 문장",
                    "correct_sentence": "정정된 문장",
                    "domain": "test",
                    "style": "test",
                    "syllable": 5,
                    "phrase": 2,
                    "number of error": 1,
                    "error_type": {"e1": "test"}
                }
            ]
        }
        
        dataset = KNCTDataset(**dataset_data)
        self.assertEqual(len(dataset.data), 1)
        self.assertEqual(dataset.data[0].index, 0)


class TestLoadKNCTDataset(unittest.TestCase):
    """데이터 로딩 함수 테스트"""
    
    def test_load_valid_json(self):
        """유효한 JSON 파일 로딩 테스트"""
        # 임시 JSON 파일 생성
        temp_data = {
            "schema": {
                "fields": [{"name": "index", "type": "integer"}],
                "primaryKey": ["index"],
                "pandas_version": "0.20.0"
            },
            "data": [
                {
                    "index": 0,
                    "error_sentence": "테스트 <e1>문장</e1>",
                    "correct_sentence": "테스트 문장",
                    "domain": "test",
                    "style": "test",
                    "syllable": 4,
                    "phrase": 2,
                    "number of error": 1,
                    "error_type": {"e1": "test"}
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(temp_data, f)
            temp_file = f.name
        
        try:
            data = load_dataset(temp_file)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0].error_sentence, "테스트 <e1>문장</e1>")
        finally:
            os.unlink(temp_file)
    
    def test_load_invalid_json(self):
        """잘못된 JSON 파일 로딩 테스트"""
        # 잘못된 데이터 (필수 필드 누락)
        invalid_data = {
            "schema": {
                "fields": [{"name": "index", "type": "integer"}],
                "primaryKey": ["index"],
                "pandas_version": "0.20.0"
            },
            "data": [
                {
                    "index": 0,
                    # "error_sentence" 필드 누락
                    "correct_sentence": "테스트 문장",
                    "domain": "test",
                    "style": "test",
                    "syllable": 4,
                    "phrase": 2,
                    "number of error": 1,
                    "error_type": {"e1": "test"}
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_data, f)
            temp_file = f.name
        
        try:
            with self.assertRaises(Exception):
                load_dataset(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_load_nonexistent_file(self):
        """존재하지 않는 파일 로딩 테스트"""
        with self.assertRaises(FileNotFoundError):
            load_dataset("nonexistent_file.json")


class TestParseErrors(unittest.TestCase):
    """오류 파싱 함수 테스트"""
    
    def test_parse_single_error(self):
        """단일 오류 파싱 테스트"""
        entry = KNCTEntry(
            index=0,
            error_sentence="테스트 <e1>문장</e1>입니다.",
            correct_sentence="테스트 문장입니다.",
            domain="test",
            style="test",
            syllable=8,
            phrase=3,
            number_of_error=1,
            error_type={"e1": "test_error"}
        )
        
        clean_text, errors = parse_errors(entry)
        
        self.assertEqual(clean_text, "테스트 문장입니다.")
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].text, "문장")
        self.assertEqual(errors[0].start, 4)
        self.assertEqual(errors[0].end, 6)
        self.assertEqual(errors[0].type, "test_error")
    
    def test_parse_multiple_errors(self):
        """다중 오류 파싱 테스트"""
        entry = KNCTEntry(
            index=0,
            error_sentence="<e1>테스트</e1> <e2>문장</e2>입니다.",
            correct_sentence="테스트 문장입니다.",
            domain="test",
            style="test",
            syllable=8,
            phrase=3,
            number_of_error=2,
            error_type={"e1": "error1", "e2": "error2"}
        )
        
        clean_text, errors = parse_errors(entry)
        
        self.assertEqual(clean_text, "테스트 문장입니다.")
        self.assertEqual(len(errors), 2)
        
        # 첫 번째 오류
        self.assertEqual(errors[0].text, "테스트")
        self.assertEqual(errors[0].start, 0)
        self.assertEqual(errors[0].end, 3)
        self.assertEqual(errors[0].type, "error1")
        
        # 두 번째 오류
        self.assertEqual(errors[1].text, "문장")
        self.assertEqual(errors[1].start, 4)
        self.assertEqual(errors[1].end, 6)
        self.assertEqual(errors[1].type, "error2")
    
    def test_parse_no_errors(self):
        """오류가 없는 문장 파싱 테스트"""
        entry = KNCTEntry(
            index=0,
            error_sentence="테스트 문장입니다.",
            correct_sentence="테스트 문장입니다.",
            domain="test",
            style="test",
            syllable=8,
            phrase=3,
            number_of_error=0,
            error_type={}
        )
        
        clean_text, errors = parse_errors(entry)
        
        self.assertEqual(clean_text, "테스트 문장입니다.")
        self.assertEqual(len(errors), 0)
    
    def test_parse_consecutive_errors(self):
        """연속된 오류 파싱 테스트 - 실제 데이터셋에서 볼 수 있는 케이스"""
        entry = KNCTEntry(
            index=0,
            error_sentence="<e1>테스트</e1><e2>문장</e2>입니다.",
            correct_sentence="테스트문장입니다.",
            domain="test",
            style="test",
            syllable=8,
            phrase=3,
            number_of_error=2,
            error_type={"e1": "error1", "e2": "error2"}
        )
        
        clean_text, errors = parse_errors(entry)
        
        # 연속된 태그도 각각 독립적으로 파싱됨
        self.assertEqual(len(errors), 2)
        self.assertEqual(errors[0].text, "테스트")
        self.assertEqual(errors[0].type, "error1")
        self.assertEqual(errors[1].text, "문장")
        self.assertEqual(errors[1].type, "error2")
        self.assertEqual(clean_text, "테스트문장입니다.")


class TestIntegration(unittest.TestCase):
    """통합 테스트"""
    
    def test_full_workflow(self):
        """전체 워크플로우 테스트"""
        # 1. 데이터 생성
        entry = KNCTEntry(
            index=0,
            error_sentence="<e1>안녕하세요</e1> <e2>반갑습니다</e2>.",
            correct_sentence="안녕하세요 반갑습니다.",
            domain="daily",
            style="spoken",
            syllable=10,
            phrase=3,
            number_of_error=2,
            error_type={"e1": "greeting", "e2": "greeting"}
        )
        
        # 2. 오류 파싱
        clean_text, errors = parse_errors(entry)
        
        # 3. 결과 검증
        self.assertEqual(clean_text, "안녕하세요 반갑습니다.")
        self.assertEqual(len(errors), 2)
        self.assertEqual(errors[0].type, "greeting")
        self.assertEqual(errors[1].type, "greeting")
        
        # 4. 오류 정보 검증
        for error in errors:
            self.assertIsInstance(error, GrammarError)
            self.assertTrue(hasattr(error, 'text'))
            self.assertTrue(hasattr(error, 'start'))
            self.assertTrue(hasattr(error, 'end'))
            self.assertTrue(hasattr(error, 'type'))


if __name__ == '__main__':
    # 테스트 실행
    unittest.main(verbosity=2)
