import pytest
import sys
import io
from parse import main

def run_arg_test(args, expected_code):
    sys.argv = ['parse.py'] + args
    with pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == expected_code

def run_test(input, expected_code, monkeypatch):
    sys.argv = ['parse.py']
    monkeypatch.setattr(sys, 'stdin', io.StringIO(input))
    with pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == expected_code
