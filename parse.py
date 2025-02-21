# parse.py
# Author: Marek hric xhricma00

import sys, re
from lark import Lark, Visitor, UnexpectedCharacters, UnexpectedToken, UnexpectedEOF
from lark.tree import pydot__tree_to_png
import xml.etree.ElementTree as ET


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
        SUCCESS if the help message is printed.
        WRONG_ARGS if the number of arguments is incorrect or the argument is invalid.
    """
    if len(sys.argv) > 2:
        print("Wrong number of arguments", file=sys.stderr)
        sys.exit(WRONG_ARGS)
    elif len(sys.argv) == 2:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("usage: parse.py [-h | --help]\n\nParser for SOL25\nOutputs XML representation\n\noptions:\n-h, --help  show this help message and exit")
            sys.exit(SUCCESS)
        else:
            print("Wrong argument", file=sys.stderr)
            sys.exit(WRONG_ARGS)

grammar = """
?start: program?

program: class program? 
class: "class" term_cid ":" term_cid "{" method? "}"
method: selector block method?

selector: term_id | term_sel_id selector_tail?
selector_tail: term_sel_id selector_tail?

block: "[" block_par? "|" block_stat? "]"
block_par: term_block_par_id block_par?
block_stat: term_id ":=" expr "." block_stat?

expr: expr_base expr_tail
expr_tail: term_id | expr_sel?
expr_sel: term_sel_id expr_base expr_sel?
expr_base: term_int 
        | term_str 
        | term_id 
        | term_cid 
        | block 
        | "(" expr ")"


term_int: /[+\-]?[0-9]+/
term_str: /'([^'\\\\\n]|\\\\['n\\\\])*\'/x
term_id: /[a-z_][a-zA-Z0-9_]*/
term_sel_id: /[a-z_][a-zA-Z0-9_]*:/ 
term_block_par_id: /:[a-z_][a-zA-Z0-9_]*/ 
term_cid: /[A-Z][a-zA-Z0-9]*/


COMMENT: /"([^"]*)"/

%import common.WS
%ignore WS
%ignore COMMENT
"""

def save_description(token):
    """
    Callback function to save first comment as description.
    """
    global description
    comment = token.value
    if description is None:
        description = re.sub(r"[\n\r]+", "&nbsp;", comment)
        return ""
    else:
        return ""

parser = Lark(grammar, start="start", parser="lalr", lexer_callbacks={"COMMENT": save_description})
language = "SOL25"
description = None

def parse_code(code):
    """
    Performs lexical and syntactic analysis of input code.

    Args:
        code: The input code as a string.

    Returns:
        The parse tree if parsing is successful.

    Exits:
        LEXICAL_ERROR if a lexical error occurs.
        SYNTAX_ERROR if a syntactic error occurs.
        INTERNAL_ERROR if an internal error occurs.
    """
    try:
        tree = parser.parse(code)
        # pydot__tree_to_png(tree, "parse_tree.png")
        # print(description)
        print(tree.pretty())
        return tree
    except UnexpectedCharacters as e:
        print("Lexical error: " + str(e), file=sys.stderr)
        sys.exit(LEXICAL_ERROR)
    except UnexpectedToken as e:
        print("Syntax error: " + str(e), file=sys.stderr)
        sys.exit(SYNTAX_ERROR)
    except UnexpectedEOF as e:
        print("Syntax error: " + str(e), file=sys.stderr)
        sys.exit(SYNTAX_ERROR)
    except Exception as e:
        print("Internal error: " + str(e), file=sys.stderr)
        sys.exit(INTERNAL_ERROR)

# Lark transformer
class SemanticAnalyzer(Visitor):
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.current_function = None
    ...

def analyze_semantics(tree):
    """
    Performs semantic analysis of the parse tree using lark Visitor.

    Args:
        tree: lark parse tree.
    
    Returns:
        tree: lark parse tree with semantic analysis.

    Exits: 
        SEM_MISSING_MAIN if the main function is missing.
        SEM_UNDEF_VAR if an undefined variable is used.
        SEM_ARITY if a function is called with the wrong number of arguments.
        SEM_VAR_CONFLICT if a variable is redefined.
        INTERNAL_ERROR if an internal error occurs.
    """
    return SemanticAnalyzer().visit_topdown(tree)

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
    tree = parse_code(code)
    tree = analyze_semantics(tree)
    print_ast_as_xml(tree)

if __name__ == "__main__":
    main()
