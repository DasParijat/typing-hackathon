import random

with open("word_bank.txt") as file:
    print(random.sample(file.readlines(), 10))
