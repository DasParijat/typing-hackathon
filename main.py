import random
from datetime import datetime
import time
import sys


GREEN = "\033[32m"  # ]
RED = "\033[31m"  # ]
START_SAMPLE_SIZE = 5

def to_color(text: str, color: str) -> str:
    """Wraps text in a color and resets it after"""
    # return text + color = "\033[0m" # ]
    return f"{color}{text}\033[0m"  # ]

def set_test(sample_size):
    """Reads a word bank file fo typing tst"""
    with open("word_bank.txt") as file:
        random_words = random.sample(file.readlines(), int(sample_size))
        typing_test = TypingTest(random_words)
    return typing_test


class TypingTest:
    def __init__(self, words: list[str], look_ahead=2) -> None:
        self.words: list[str] = words
        self.look_ahead: int = look_ahead

    def start_test(self):
        # init variables for test
        random_words = random.sample(self.words, 5)
        self.test_words: list[str] = list(map(str.strip, random_words))
        self.amount_correct_chars: int = 0
        self.start_time: datetime = datetime.now()
        self.word_inputs: list[tuple[str, datetime]] = []

        self.do_test()
        self.end_test()

    def do_test(self):
        for i in range(len(self.test_words)):
            match_word = self.test_words[i]
            words = self.test_words[
                i : min(len(self.test_words), i + self.look_ahead + 1)
            ]

            print(" ".join(words))
            user_word = input()
            self.process_word(match_word, user_word)
            print()

    def end_test(self):
        end_time = datetime.now()
        difference = end_time - self.start_time

        adjusted_wpm = (self.amount_correct_chars / 5) / (
            difference.total_seconds() / 60
        )
        raw_wpm = (sum(map(len, self.test_words)) / 5) / (
            difference.total_seconds() / 60
        )

        print(f"Your adjusted raw wpm is {adjusted_wpm:.2f}")
        print(f"Your raw wpm is {raw_wpm:.2f}")

    def do_replay(self):
        these_word_inputs = self.word_inputs.copy()
        self.word_inputs = []
        self.amount_correct_chars: int = 0
        previous_time = self.start_time
        for i, (user_word, finish_time) in enumerate(these_word_inputs):
            words = self.test_words[
                i : min(len(self.test_words), i + self.look_ahead + 1)
            ]
            print(" ".join(words))
            difference = finish_time - previous_time
            previous_time = finish_time
            seconds_word_took = difference.total_seconds()
            for char in user_word:
                print(char, end="")
                sys.stdout.flush()
                time.sleep(seconds_word_took / len(user_word))
            print()
            self.process_word(self.test_words[i], user_word)
            print()

    def process_word(self, match_word: str, user_word: str):
        self.word_inputs.append((user_word, datetime.now()))

        match_word = match_word + "#" * (len(user_word) - len(match_word))
        user_word = user_word + "#" * (len(match_word) - len(user_word))
        
        for i in range(len(user_word)):
            user_char = user_word[i]
            matching_char = match_word[i]
        
            if user_char == matching_char:
                self.amount_correct_chars += 1
                print(to_color(matching_char, GREEN), end="")
            else:
                print(to_color(matching_char, RED), end="")

def main():
    sample_size = START_SAMPLE_SIZE
    typing_test = set_test(sample_size)
    user_input = None

    while user_input not in ["q"]:
        user_input = input(
            f"\nType:\n'q' to quit\n'c' to change sample of words\n's' to change size of sample (currently {sample_size})\n'r' to replay\n'' to play"
        ).lower()

        match (user_input):
            case "r":
                typing_test.do_replay()
            case "c":
                typing_test = set_test(sample_size)
                print("Sample of words changed!")
            case "s":
                sample_size = input("New sample size: ")
                print("Sample size changed!\nType 'c' to restart sample to desired size")
            case _:
                typing_test.start_test()


    print("Goodbye !")


if __name__ == "__main__":
    main()
