"""Python 기초 퀴즈 게임. 실행: python quiz_game.py"""

import json
from pathlib import Path

try:
    BASE_DIR = Path(__file__).resolve().parent
except NameError:
    BASE_DIR = Path.cwd()

STATE_FILE = BASE_DIR / "state.json"


class Quiz:
    """문제, 네 개의 선택지, 1~4 사이 정답 번호를 관리한다."""

    def __init__(self, question, choices, answer):
        if not isinstance(question, str) or not question.strip():
            raise ValueError("문제는 빈 문자열일 수 없습니다.")
        if (not isinstance(choices, list) or len(choices) != 4
                or any(not isinstance(c, str) or not c.strip() for c in choices)):
            raise ValueError("선택지는 비어 있지 않은 문자열 4개여야 합니다.")
        if type(answer) is not int or not 1 <= answer <= 4:
            raise ValueError("정답 번호는 1~4의 정수여야 합니다.")
        self.question = question.strip()
        self.choices = [c.strip() for c in choices]
        self.answer = answer

    def display(self):
        print(f"\n{self.question}")
        for number, choice in enumerate(self.choices, 1):
            print(f"  {number}. {choice}")

    def check_answer(self, selected):
        return selected == self.answer

    def to_dict(self):
        return {"question": self.question, "choices": self.choices, "answer": self.answer}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise ValueError("퀴즈 데이터는 객체여야 합니다.")
        return cls(data["question"], data["choices"], data["answer"])


def default_quizzes():
    """Python 입문 학습자가 핵심 문법을 복습하도록 만든 기본 문제."""
    return [
        Quiz("Python에서 화면에 내용을 출력하는 함수는?", ["input()", "print()", "len()", "type()"], 2),
        Quiz("다음 중 Python의 리스트를 나타내는 것은?", ["(1, 2)", "{1, 2}", "[1, 2]", "'1, 2'"], 3),
        Quiz("len('hello')의 결과는?", ["4", "5", "6", "오류"], 2),
        Quiz("Python에서 주석을 시작하는 기호는?", ["//", "<!--", "#", "**"], 3),
        Quiz("3 // 2의 결과는?", ["1", "1.5", "2", "3"], 1),
        Quiz("다음 중 조건문에 사용하는 키워드는?", ["for", "def", "if", "import"], 3),
        Quiz("range(3)을 순회할 때 생성되는 값은?", ["1, 2, 3", "0, 1, 2", "0, 1, 2, 3", "3만"], 2),
    ]


class QuizGame:
    def __init__(self, state_file=STATE_FILE):
        self.state_file = Path(state_file)
        self.quizzes = default_quizzes()
        self.best_score = None  # 최고 정답 수
        self.best_total = None  # 해당 기록을 달성한 당시 문제 수
        self.load()

    def save(self):
        data = {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score,
            "best_total": self.best_total,
        }
        temporary = self.state_file.with_name(self.state_file.name + ".tmp")
        try:
            with temporary.open("w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
                file.write("\n")
            temporary.replace(self.state_file)
            return True
        except OSError as error:
            print(f"[저장 오류] 파일을 저장하지 못했습니다: {error}")
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
            return False

    def load(self):
        try:
            with self.state_file.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, dict) or not isinstance(data.get("quizzes"), list):
                raise ValueError("quizzes 항목이 올바르지 않습니다.")
            quizzes = [Quiz.from_dict(item) for item in data["quizzes"]]
            score = data.get("best_score")
            total = data.get("best_total")
            if score is not None and (type(score) is not int or score < 0):
                raise ValueError("best_score 값이 올바르지 않습니다.")
            if total is not None and (type(total) is not int or total < 0):
                raise ValueError("best_total 값이 올바르지 않습니다.")
            if (score is None) != (total is None):
                raise ValueError("최고 점수 기록이 불완전합니다.")
            if score is not None and (total == 0 or score > total):
                raise ValueError("최고 점수가 전체 문제 수보다 큽니다.")
            self.quizzes = quizzes
            self.best_score = score
            self.best_total = total
        except FileNotFoundError:
            print("[안내] 저장 파일이 없어 기본 퀴즈로 시작합니다.")
            self.save()
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError, KeyError, TypeError) as error:
            print(f"[안내] 데이터 파일을 읽을 수 없거나 손상되었습니다: {error}")
            print("[안내] 기본 퀴즈 데이터로 초기화합니다.")
            self.quizzes = default_quizzes()
            self.best_score = None
            self.best_total = None
            self.save()

    @staticmethod
    def read_number(prompt, minimum, maximum):
        while True:
            raw = input(prompt).strip()
            if not raw:
                print("[입력 오류] 빈 입력입니다. 다시 입력하세요.")
                continue
            try:
                value = int(raw)
            except ValueError:
                print("[입력 오류] 숫자를 입력하세요.")
                continue
            if not minimum <= value <= maximum:
                print(f"[입력 오류] {minimum}~{maximum} 사이의 숫자를 입력하세요.")
                continue
            return value

    @staticmethod
    def read_text(prompt):
        while True:
            value = input(prompt).strip()
            if value:
                return value
            print("[입력 오류] 빈 문자열은 사용할 수 없습니다.")

    @staticmethod
    def show_menu():
        print("\n========== Python 기초 퀴즈 ==========")
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 최고 점수 확인")
        print("5. 종료")
        print("======================================")

    def play(self):
        if not self.quizzes:
            print("[안내] 등록된 퀴즈가 없습니다.")
            return
        score = 0
        total = len(self.quizzes)
        for index, quiz in enumerate(self.quizzes, 1):
            print(f"\n--- {index}/{total}번 문제 ---")
            quiz.display()
            selected = self.read_number("정답 번호 (1~4): ", 1, 4)
            if quiz.check_answer(selected):
                score += 1
                print("정답입니다!")
            else:
                print(f"오답입니다. 정답은 {quiz.answer}번입니다.")
        print(f"\n[결과] {total}문제 중 {score}문제 정답 ({score / total * 100:.1f}점)")
        if self.best_score is None or score > self.best_score:
            self.best_score = score
            self.best_total = total
            print("축하합니다! 최고 기록을 갱신했습니다.")
        self.save()

    def add_quiz(self):
        print("\n--- 새 퀴즈 등록 ---")
        question = self.read_text("문제: ")
        choices = [self.read_text(f"{number}번 선택지: ") for number in range(1, 5)]
        answer = self.read_number("정답 번호 (1~4): ", 1, 4)
        self.quizzes.append(Quiz(question, choices, answer))
        if self.save():
            print("퀴즈가 추가되고 저장되었습니다.")
        else:
            print("퀴즈는 현재 실행에 추가되었지만 파일 저장에는 실패했습니다.")

    def list_quizzes(self):
        if not self.quizzes:
            print("[안내] 등록된 퀴즈가 없습니다.")
            return
        print(f"\n--- 퀴즈 목록 (총 {len(self.quizzes)}개) ---")
        for index, quiz in enumerate(self.quizzes, 1):
            print(f"\n[{index}번]")
            quiz.display()
            print(f"  정답: {quiz.answer}번")

    def show_best_score(self):
        if self.best_score is None:
            print("[안내] 아직 퀴즈를 푼 기록이 없습니다.")
        else:
            print(f"[최고 기록] {self.best_total}문제 중 {self.best_score}문제 정답 "
                  f"({self.best_score / self.best_total * 100:.1f}점)")

    def run(self):
        try:
            while True:
                self.show_menu()
                choice = self.read_number("메뉴 선택 (1~5): ", 1, 5)
                if choice == 1:
                    self.play()
                elif choice == 2:
                    self.add_quiz()
                elif choice == 3:
                    self.list_quizzes()
                elif choice == 4:
                    self.show_best_score()
                else:
                    print("게임을 종료합니다.")
                    break
        except (KeyboardInterrupt, EOFError):
            print("\n[안내] 입력이 중단되어 안전하게 종료합니다.")
        finally:
            self.save()


if __name__ == "__main__":
    QuizGame().run()

