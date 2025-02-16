import pytest
import sys
from parse import parse_args

def test_arg_empty():
    sys.argv = ['parse.py']
    assert parse_args() == None

def test_arg_help():
    sys.argv = ['parse.py', '--help']
    with pytest.raises(SystemExit) as e:
        parse_args()
    assert e.value.code == 0

def test_arg_help_short():
    sys.argv = ['parse.py', '-h']
    with pytest.raises(SystemExit) as e:
        parse_args()
    assert e.value.code == 0

def test_arg_wrong():
    sys.argv = ['parse.py', 'wrong']
    with pytest.raises(SystemExit) as e:
        parse_args()
    assert e.value.code == 10

def test_arg_too_many():
    sys.argv = ['parse.py', 'too', 'many']
    with pytest.raises(SystemExit) as e:
        parse_args()
    assert e.value.code == 10

def test_arg_wrong_and_help():
    sys.argv = ['parse.py', 'wrong', '--help']
    with pytest.raises(SystemExit) as e:
        parse_args()
    assert e.value.code == 10

def test_arg_help_and_wrong():
    sys.argv = ['parse.py', '--help', 'wrong']
    with pytest.raises(SystemExit) as e:
        parse_args()
    assert e.value.code == 10

def test_arg_help_and_help():
    sys.argv = ['parse.py', '--help', '--help']
    with pytest.raises(SystemExit) as e:
        parse_args()
    assert e.value.code == 10

