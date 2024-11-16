import termios
import tty
import sys
import random
import atexit
import os
import logging
from datetime import datetime


GREEN = "\033[32m"  # ]
RED = "\033[31m"  # ]
WORD_LEN_MIN = 3
WORD_LEN_MAX = 10


def to_color(text: str, color: str) -> str:
    """Wraps text in a color and resets it after"""
    # return text + color = "\033[0m" # ]
    return f"{text}{color}\033[0m"  # ]


def clear_screen(do_flush=True):
    """Clears the screen and optionally does a screen refresh"""
    sys.stdout.write("\033[H\033[J")  # ]]
    if do_flush:
        sys.stdout.flush()


def calculate_wpm(num_characters: int, seconds: float) -> float:
    return (num_characters / 5) / (seconds / 60)


class TypingTest:
    def __init__(self, word_bank: list[str], word_count: int = 10) -> None:
        self.word_bank = word_bank
        self.word_count: int = word_count
        self.match_index: int = 0
        self.text_for_test: str | None = None
        self.start_time: datetime | None = None
        self.text_for_user: str = ""

    def start_game(self):
        # setup game
        self.match_index = 0
        self.text_for_test = " ".join(random.sample(self.word_bank, self.word_count))

        # print words to write
        sys.stdout.write(self.text_for_test)
        sys.stdout.write("\033[H")  # ]
        sys.stdout.flush()

        # game loop
        is_first_character = True
        while self.match_index < len(self.text_for_test):
            byte = os.read(sys.stdin.fileno(), 1)
            char = chr(byte[0]).lower()
            logging.debug(f"Pressed byte: `{byte}`")
            if char == "\x03":  # Ctrl+C to exit
                clear_screen()
                print("C-c hit exiting program!")
                return
            if is_first_character:
                self.start_time = datetime.now()
                is_first_character = False
            self.handle_char(char)

        self.end_game()

    def handle_char(self, char: str):
        assert self.text_for_test is not None
        if char == "\x7f":  # Backspace
            logging.debug(
                f"Processing backspace rewriting and moving cursor: `{self.text_for_test[self.match_index]}`"
            )
            self.text_for_user = self.text_for_user[:-1]
            self.match_index = max(self.match_index - 1, 0)
            sys.stdout.write("\033[1D")  # ] move back 1 character
            sys.stdout.write(self.text_for_test[self.match_index])
            sys.stdout.write("\033[1D")  # ]
            sys.stdout.flush()
            return

        # handle random characters not in our typing test
        if not char.isalnum() and (not char == " "):
            logging.debug(f"Processed non ascii chracter (skipping): `{char}`")
            return

        # regular character handling
        logging.debug(f"Process ascii: `{char}`")
        char_to_match = self.text_for_test[self.match_index]
        self.match_index += 1
        self.text_for_user += char
        logging.debug(
            f"Matching pressed to expected: `{char}` to `{char_to_match}` => {char == char_to_match}"
        )
        if char_to_match == char:
            sys.stdout.write(to_color(GREEN, char))
        else:
            sys.stdout.write(
                to_color(RED, char_to_match if char_to_match != " " else "-")
            )
        # do to flush to but the input buffer to the stdout
        #    (would flush only on Enter)
        sys.stdout.flush()

    def end_game(self):
        assert self.start_time is not None
        assert self.text_for_test is not None
        difference = datetime.now() - self.start_time
        num_of_chars = 0
        num_of_correct_chars = 0
        for user_char, test_char in zip(self.text_for_user, self.text_for_test):
            if test_char == " ":
                continue
            num_of_chars += 1
            if user_char == test_char:
                num_of_correct_chars += 1
        adjusted_wpm = calculate_wpm(num_of_correct_chars, difference.total_seconds())
        raw_wpm = calculate_wpm(num_of_chars, difference.total_seconds())
        clear_screen(False)
        sys.stdout.write(
            f"Finished the test in {difference.total_seconds():.2f} seconds at {adjusted_wpm:.2f} adjusted wpm and {raw_wpm:.2f} raw wpm"
        )


def main():
    words = []
    with open("word_bank.txt") as word_file:
        for word in word_file.readlines():
            if len(word) >= WORD_LEN_MIN and len(word) <= WORD_LEN_MAX:
                words.append(word.strip().lower())
    typing_test = TypingTest(words, 10)
    typing_test.start_game()


if __name__ == "__main__":
    logging.basicConfig(
        filename="typing.log",
        level=logging.DEBUG,
        filemode="w",
        # format="%(asctime)s - %(levelname)s - %(message)s", -- example other fields
        format="%(message)s",
    )
    old_settings = termios.tcgetattr(sys.stdin)
    # set the program to raw mode io
    tty.setraw(sys.stdin)
    atexit.register(
        lambda: termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    )

    clear_screen()
    main()
