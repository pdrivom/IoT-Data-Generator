from random import randint

def gender():
    return 'male' if randint(0, 10) % 2 else 'female'
