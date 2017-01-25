import os
from contextlib import contextmanager


@contextmanager
def cd(directory):
    cwd = os.getcwd()
    os.chdir(os.path.expanduser(directory))
    try:
        yield
    finally:
        os.chdir(cwd)
