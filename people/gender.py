import random


def gender():
    gender = random.choices(["Male", "Female"], weights=[9767, 10000])
    return gender
