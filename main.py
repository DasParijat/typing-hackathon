import termios
import tty
import sys
import random
import atexit
import os
import logging


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


class TypingTest:
    def __init__(self, word_bank: list[str], word_count: int = 10) -> None:
        self.word_bank = word_bank
        self.word_count: int = word_count
        self.match_index: int = 0
        self.text_for_test: str | None = None

    def start_game(self):
        # setup game
        self.match_index = 0
        self.text_for_test = " ".join(random.sample(self.word_bank, self.word_count))

        # print words to write
        sys.stdout.write(self.text_for_test)
        sys.stdout.write("\033[H")  # ]
        sys.stdout.flush()

        # game loop
        while self.match_index < len(self.text_for_test):
            byte = os.read(sys.stdin.fileno(), 1)
            char = chr(byte[0]).lower()
            logging.debug(f"Pressed byte: `{byte}`")
            if char == "\x03":  # Ctrl+C to exit
                clear_screen()
                print("C-c hit exiting program!")
                return
            self.handle_char(char)

    def handle_char(self, char: str):
        assert self.text_for_test is not None
        if char == "\x7f":  # Backspace
            logging.debug(
                f"Processing backspace rewriting and moving cursor: `{self.text_for_test[self.match_index]}`"
            )
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


def main():
    words = []
    with open("word_bank.txt") as word_file:
        for word in word_file.readlines():
            if len(word) >= WORD_LEN_MIN and len(word) <= WORD_LEN_MAX:
                words.append(word.strip().lower())
    typing_test = TypingTest(words)
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
