import string
import random

def get_random_string():
    s = string.ascii_lowercase
    s += "0123456789"
    return ''.join(random.choice(s) for i in range(40))