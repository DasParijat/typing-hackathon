import random

GREEN = "\033[32m"  # ]
RED = "\033[31m"  # ]


def to_color(text: str, color: str) -> str:
    """Wraps text in a color and resets it after"""
    # return text + color = "\033[0m" # ]
    return f"{color}{text}\033[0m"  # ]


with open("word_bank.txt") as file:
    random_words = random.sample(file.readlines(), 10)
    stripped_random_words = []
    for random_word in random_words:
        stripped_random_words.append(random_word.strip())
    for word in stripped_random_words:
        print(word)
        user_word = input()
        for i in range(len(user_word)):
            user_char = user_word[i]
            matching_char = word[i]
            if user_char == matching_char:
                print(to_color(matching_char, GREEN), end="")
            else:
                print(to_color(matching_char, RED), end="")
        print()
