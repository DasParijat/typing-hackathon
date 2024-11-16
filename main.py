import random

with open("word_bank.txt") as file:
    random_words = random.sample(file.readlines(), 10)
    stripped_random_words = []
    for random_word in random_words:
        stripped_random_words.append(random_word.strip())
    print(stripped_random_words)
