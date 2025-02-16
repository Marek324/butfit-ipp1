# parse.py
# Author: Marek hric xhricma00

import sys
from lark import Lark, Transformer, UnexpectedCharacters, UnexpectedToken, UnexpectedEOF

# Exit codes
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
    """
    Parses command line arguments.

    Returns:
        None if the arguments are correct.

    Exits:
        WRONG_ARGS if the number of arguments is incorrect or the argument is invalid.
    """
    if len(sys.argv) > 2:
        print("Wrong number of arguments", file=sys.stderr)
        sys.exit(WRONG_ARGS)
    elif len(sys.argv) == 2:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("usage: parse.py [-h]\n\nParser for SOL25\n\noptions:\n-h, --help  show this help message and exit")
            sys.exit(SUCCESS)
        else:
            print("Wrong argument", file=sys.stderr)
            sys.exit(WRONG_ARGS)

grammar = """
?start: program

program: class program? 
class: "class" term_cid ":" term_cid "{" method "}"
method: selector block method?

selector: term_id | term_id_ selector_tail
selector_tail: term_id_ selector_tail?

block: "[" block_par "|" block_stat "]"
block_par: term__id block_par?
block_stat: term_id ":=" expr "." block_stat?

expr: expr_base expr_tail
expr_tail: term_id | expr_sel
expr_sel: term_id_ expr_base expr_sel?
expr_base: term_int 
        | term_str 
        | term_id 
        | term_cid 
        | block 
        | "(" expr ")"


term_int: /["+"|"-"][1-9]+/
term_str: /''/
term_id: /a/
term_id_: /b/
term__id: /c/
term_cid: /d/


COMMENT: /"([^"]*)"/

%import common.WS
%ignore WS
%ignore COMMENT
"""

parser = Lark(grammar, start="start", parser="lalr")

# Lark transformer
class TreeToAST(Transformer):
    ...

def parse_code(code):
    """
    Performs lexical and syntactic analysis of input code.

    Args:
        code: The input code as a string.

    Returns:
        The Abstract Syntax Tree (AST) if parsing is successful.

    Exits:
        LEXICAL_ERROR if a lexical error occurs.
        SYNTAX_ERROR if a syntactic error occurs.
        INTERNAL_ERROR if an internal error occurs.
    """
    ...

def analyze_semantics(ast):
    """
    Performs semantic analysis of the AST.

    Args:
        ast: AST.
    
    Returns:
        AST if semantic analysis is successful.

    Exits:
        SEM_MISSING_MAIN if the main function is missing.
        SEM_UNDEF_VAR if an undefined variable is used.
        SEM_ARITY if a function is called with the wrong number of arguments.
        SEM_VAR_CONFLICT if a variable is redefined.
        INTERNAL_ERROR if an internal error occurs.
    """
    ...

def print_ast_as_xml(ast):
    """
    Prints the AST in XML format.

    Args:
        ast: AST.
    """
    ...

def main():
    parse_args()
    code = sys.stdin.read()
    ast = parse_code(code)
    ast = analyze_semantics(ast)
    print_ast_as_xml(ast)


if __name__ == "__main__":
    main()
