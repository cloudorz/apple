# coding: utf-8

import random

def generate_password():
    return ''.join(random.sample("abcdefghijkmnpqrstuvwxyz23456789", 6))
