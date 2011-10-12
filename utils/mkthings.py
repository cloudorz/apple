# coding: utf-8

import random

def generate_password():
    return ''.join(random.sample("abcdefghijkmnpqrstuvwxyz23456789", 6))

class QDict(dict):
    """A dict that allows for object-like property access syntax."""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

# singleton decorator

 def singleton(aClass):
    instance = []

    def onCall(*args, **kwargs):
        if not instance:
            instance[0] = aClass(*args, **kwargs)
        return instance[0]

    return onCall
