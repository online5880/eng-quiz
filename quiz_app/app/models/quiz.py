import random
import pandas as pd
from pathlib import Path

class Quiz:
    def __init__(self):
        self.questions = self.load_questions()
        self.current_question = None
        self.answered_questions = set()
        self.correct_questions = set()
        self.current_combo = 0
        self.max_combo = 0

    def load_questions(self):
        try:
            # CSV 파일 경로 확인
            csv_path = Path(__file__).parent.parent.parent / 'data' / 'quiz_data.csv'
            print(f"CSV 파일 경로: {csv_path}")
            print(f"파일 존재 여부: {csv_path.exists()}")

            # CSV 파일 읽기
            df = pd.read_csv(csv_path)
            print("CSV 데이터 미리보기:")
            print(df.head())
            print("\n컬럼명:", df.columns.tolist())

            # 컬럼명 매핑
            df = df.rename(columns={
                'Lesson': 'lesson',
                '단어': 'word',
                '단어 뜻': 'meaning',
                '예문 (영어)': 'example_en',
                '예문 (한국어)': 'example_ko'
            })
            
            # index를 id로 추가
            df = df.reset_index()
            df = df.rename(columns={'index': 'id'})
            
            questions = df.to_dict('records')
            print("\n변환된 데이터 첫 번째 항목:", questions[0] if questions else "데이터 없음")
            
            return questions

        except Exception as e:
            print(f"Error loading quiz data: {e}")
            # 기본 테스트 데이터 반환
            return [
                {
                    "id": 0,
                    "lesson": "1",
                    "word": "apple",
                    "meaning": "사과",
                    "example_en": "I eat an apple every day.",
                    "example_ko": "나는 매일 사과를 먹는다."
                }
            ]

    def get_random_question(self):
        if not self.questions:
            print("문제 데이터가 없습니다!")
            return None
            
        available_questions = [q for q in self.questions 
                             if q.get('id') not in self.answered_questions]
        
        if not available_questions:
            self.answered_questions.clear()
            available_questions = self.questions

        self.current_question = random.choice(available_questions)
        print("선택된 문제:", self.current_question)
        return self.current_question

    def check_answer(self, answer):
        if not self.current_question:
            return False
        
        is_correct = answer.lower().strip() == self.current_question['meaning'].lower().strip()
        question_id = self.current_question['id']
        
        # 이미 맞춘 문제는 다시 체크하지 않음
        if question_id not in self.answered_questions:
            self.answered_questions.add(question_id)
            if is_correct:
                self.correct_questions.add(question_id)
                self.current_combo += 1
                self.max_combo = max(self.max_combo, self.current_combo)
            else:
                self.current_combo = 0
        
        return is_correct

    def get_progress(self):
        total_questions = len(self.questions)
        answered_questions = len(self.answered_questions)
        return {
            'answered': answered_questions,
            'total': total_questions,
            'percentage': (answered_questions / total_questions) * 100 if total_questions > 0 else 0
        }

    def get_current_question_details(self):
        """현재 문제의 모든 세부 정보를 반환"""
        if not self.current_question:
            return None
        return {
            'correct_answer': self.current_question['meaning'],
            'example_en': self.current_question.get('example_en', ''),
            'example_ko': self.current_question.get('example_ko', ''),
            'lesson': self.current_question.get('lesson', '')
        }

    def get_stats(self):
        """현재 학습 통계 반환"""
        total_attempted = len(self.answered_questions)
        total_correct = len(self.correct_questions)
        accuracy = (total_correct / total_attempted * 100) if total_attempted > 0 else 0
        
        return {
            'total_attempts': total_attempted,
            'correct_answers': total_correct,
            'accuracy': round(accuracy, 1),
            'current_combo': self.current_combo,
            'max_combo': self.max_combo
        }

    def to_dict(self):
        """현재 상태를 딕셔너리로 변환"""
        return {
            'answered_questions': list(self.answered_questions),
            'correct_questions': list(self.correct_questions),
            'current_combo': self.current_combo,
            'max_combo': self.max_combo
        }

    def load_state(self, state_dict):
        """상태 딕셔너리로부터 상태 복원"""
        if state_dict:
            self.answered_questions = set(state_dict.get('answered_questions', []))
            self.correct_questions = set(state_dict.get('correct_questions', []))
            self.current_combo = state_dict.get('current_combo', 0)
            self.max_combo = state_dict.get('max_combo', 0)
