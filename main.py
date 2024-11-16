import termios
import tty
import sys
import random
import atexit
import os
import logging
import time
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


def get_char() -> str:
    byte = os.read(sys.stdin.fileno(), 1)
    logging.debug(f"Pressed byte: `{byte}`")
    char = chr(byte[0]).lower()
    if char == "\x03":  # Ctrl+C to exit
        clear_screen()
        print("C-c hit exiting program!")
        sys.exit(0)
    return char


class TypingTest:
    def __init__(self, word_bank: list[str], word_count: int = 10) -> None:
        self.word_bank = word_bank
        self.word_count: int = word_count
        self.match_index: int = 0
        self.text_for_test: str | None = None
        self.start_time: datetime | None = None
        self.text_for_user: str = ""
        self.max_adjusted_wpm: float = 0
        self.key_presses: list[tuple[str, datetime]] = []

    def start_session(self):
        while True:
            self.start_game()
            print("Press 1 for new game, 2 to replay,and 3 to end")
            sys.stdout.write("\r")
            char = None
            while char not in ["1", "2", "3"]:
                char = get_char()
            if char == "2":
                self.replay_game()
            if char == "3":
                print("Goodbye!")
                break

    def replay_game(self):
        assert self.text_for_test is not None
        self.match_index = 0
        self.text_for_user = ""
        clear_screen(False)
        sys.stdout.write(self.text_for_test)
        sys.stdout.write("\033[H")  # ]
        sys.stdout.flush()
        logging.debug(self.key_presses)
        self.handle_char(self.key_presses[0][0])
        for i in range(len(self.key_presses) - 1):
            _, time1 = self.key_presses[i]
            char2, time2 = self.key_presses[i + 1]
            difference = time2 - time1
            time.sleep(difference.total_seconds())
            self.handle_char(char2)
        time.sleep(0.2)

    def start_game(self):
        clear_screen(False)
        # setup game
        self.match_index = 0
        self.text_for_user = ""
        self.text_for_test = " ".join(random.sample(self.word_bank, self.word_count))
        self.key_presses = []

        # print words to write
        sys.stdout.write(self.text_for_test)
        sys.stdout.write("\033[H")  # ]
        sys.stdout.flush()

        # game loop
        is_first_character = True
        while self.match_index < len(self.text_for_test):
            char = get_char()
            current_time = datetime.now()
            if is_first_character:
                self.start_time = current_time
                is_first_character = False
            self.key_presses.append((char, current_time))
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
        self.max_adjusted_wpm = max(adjusted_wpm, self.max_adjusted_wpm)
        raw_wpm = calculate_wpm(num_of_chars, difference.total_seconds())
        clear_screen(False)
        sys.stdout.write(
            f"Finished the test in {difference.total_seconds():.2f} seconds at {adjusted_wpm:.2f} adjusted wpm and {raw_wpm:.2f} raw wpm\n\r"
            + f"Best adjusted wpm this session: {self.max_adjusted_wpm:.2f}\n\r"
        )
        sys.stdout.flush()


def main():
    words = []
    with open("word_bank.txt") as word_file:
        for word in word_file.readlines():
            if len(word) >= WORD_LEN_MIN and len(word) <= WORD_LEN_MAX:
                words.append(word.strip().lower())
    typing_test = TypingTest(words, 10)
    typing_test.start_session()


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

    main()
