import os

use_powershell = False
try:
    import termios
except:
    use_powershell = True

import subprocess
import tty
import sys
import random
import logging


GREEN = "\033[32m"  # ]
RED = "\033[31m"  # ]
WORD_LEN_MIN = 3
WORD_LEN_MAX = 10
WORD_COUNT = 10


def to_color(text: str, color: str) -> str:
    """Wraps text in a color and resets it after"""
    # return text + color = "\033[0m" # ]
    return f"{text}{color}\033[0m"  # ]


def clear_screen(do_flush=True):
    """Clears the screen and optionally does a screen refresh"""
    sys.stdout.write("\033[H\033[J")  # ]]
    if do_flush:
        sys.stdout.flush()


def main():
    words = []
    with open("word_bank.txt") as word_file:
        for word in word_file.readlines():
            if len(word) >= WORD_LEN_MIN and len(word) <= WORD_LEN_MAX:
                words.append(word.strip().lower())

    text_for_test = " ".join(random.sample(words, WORD_COUNT))
    match_index = 0
    sys.stdout.write(text_for_test)
    sys.stdout.write("\033[H")  # ]
    sys.stdout.flush()
    while match_index < len(text_for_test):
        byte = os.read(sys.stdin.fileno(), 1)
        char = chr(byte[0]).lower()
        logging.debug(f"Pressed byte: `{byte}`")
        # special character handling
        if char == "\x03":  # Ctrl+C to exit
            clear_screen()
            print("C-c hit exiting program!")
            return
        elif char == "\x7f":  # Backspace
            logging.debug(
                f"Processing space rewriting and moving cursor: `{text_for_test[match_index]}`"
            )
            match_index = max(match_index - 1, 0)
            sys.stdout.write("\033[1D")  # ] move back 1 character
            sys.stdout.write(text_for_test[match_index])
            sys.stdout.write("\033[1D")  # ]
            sys.stdout.flush()
            continue
        # regular character handling
        # Convert byte to ASCII
        if not char.isalnum() and (not char == " "):
            logging.debug(f"Processed non ascii chracter (skipping): `{char}`")
            continue

        logging.debug(f"Process ascii: `{char}`")
        char_to_match = text_for_test[match_index]
        match_index += 1
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


if __name__ == "__main__":
    logging.basicConfig(
        filename="typing.log",
        level=logging.DEBUG,
        filemode="w",
        # format="%(asctime)s - %(levelname)s - %(message)s", -- example other fields
        format="%(message)s",
    )
    if use_powershell:
        subprocess.run("Get-Content -Path C:\example.txt -Raw")
    else:
        old_settings = termios.tcgetattr(sys.stdin)  # pyright: ignore
        # set the program to raw mode io
        tty.setraw(sys.stdin)
    try:
        clear_screen()
        main()
    finally:
        # ensure if there a bug in the program to still reset the stdin
        if use_powershell:
            subprocess.run("Get-Content -Path C:\example.txt")
        else:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)  # pyright: ignore
