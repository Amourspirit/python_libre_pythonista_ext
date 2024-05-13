from typing import Callable

# https://www.oreilly.com/library/view/python-cookbook/0596001673/ch09s02.html


class Command:
    """Class for passing commands"""

    def __init__(self, callback: Callable, *args, **kwargs):
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        return self.callback(*self.args, *self.kwargs)
