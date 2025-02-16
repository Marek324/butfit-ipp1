# parse.py
# Author: Marek hric xhricma00

import sys
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


def parse_args():
    if len(sys.argv) > 2:
        print("Wrong number of arguments")
        sys.exit(ExitCode.WRONG_ARGS.value, file=sys.stderr)
    elif len(sys.argv) == 2:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("usage: parse.py [-h]\n\nParser for SOL25\n\noptions:\n-h, --help  show this help message and exit")
            sys.exit(ExitCode.SUCCESS.value)
        else:
            print("Wrong argument", file=sys.stderr)
            sys.exit(ExitCode.WRONG_ARGS.value)


if __name__ == "__main__":
    parse_args()

    
    

