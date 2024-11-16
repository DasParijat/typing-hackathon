import random
from datetime import datetime


GREEN = "\033[32m"  # ]
RED = "\033[31m"  # ]
LOOK_AHEAD = 2


def to_color(text: str, color: str) -> str:
    """Wraps text in a color and resets it after"""
    # return text + color = "\033[0m" # ]
    return f"{color}{text}\033[0m"  # ]


with open("word_bank.txt") as file:
    random_words = random.sample(file.readlines(), 5)
    stripped_random_words = []
    for random_word in random_words:
        stripped_random_words.append(random_word.strip())

    start_time = datetime.now()
    amount_correct_chars = 0
    for i in range(len(stripped_random_words)):
        word = stripped_random_words[i]
        words = stripped_random_words[
            i : min(len(stripped_random_words), i + LOOK_AHEAD + 1)
        ]
        print(" ".join(words))
        user_word = input()
        word = word + "#" * (len(user_word) - len(word))
        user_word = user_word + "#" * (len(word) - len(user_word))
        for i in range(len(user_word)):
            user_char = user_word[i]
            matching_char = word[i]
            if user_char == matching_char:
                amount_correct_chars += 1
                print(to_color(matching_char, GREEN), end="")
            else:
                print(to_color(matching_char, RED), end="")
        print()
    end_time = datetime.now()
    difference = end_time - start_time

    adjusted_wpm = (amount_correct_chars / 5) / (difference.total_seconds() / 60)
    raw_wpm = (sum(map(len, stripped_random_words)) / 5) / (
        difference.total_seconds() / 60
    )

    print(f"Your adjusted raw wpm is {adjusted_wpm:.2f}")
    print(f"Your raw wpm is {raw_wpm:.2f}")
