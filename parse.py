# parse.py
# Author: Marek hric xhricma00

import sys
import argparse
from enum import Enum

class ExitCode(Enum):
    SUCCESS = 0
    WRONG_ARGS = 10
    FILE_READ_ERROR = 11
    FILE_WRITE_ERROR = 12

    LEXICAL_ERROR = 21
    SYNTAX_ERROR = 22

    SEM_MISSING_MAIN = 31
    SEM_UNDEF_VAR = 32
    SEM_ARITY = 33
    SEM_VAR_CONFLICT = 34

    INTERNAL_ERROR = 99


if __name__ == "__main__":
    ...