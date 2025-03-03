Documentation of Project Implementation for IPP 2024/2025 \
Name and surname: Marek Hric \
Login: xhricma00

## Implementation design

The project implements a parser for the SOL25 language, performing lexical, syntactic, and semantic analysis. The `parse.py` script takes SOL25 code as input, validates it, and outputs an XML representation of the code's structure. The implementation uses the Lark parsing library for grammar definition and parsing, and the `xml.etree.ElementTree` library for XML generation. The script includes error handling for various stages of the parsing process.

## Argument parsing

The `parse_args()` function handles command-line argument parsing. It checks for the `--help` or `-h` arguments to display a help message and exits. The script expects no arguments (reading from standard input) or the `--help` argument. Incorrect numbers or invalid arguments result in an error message to standard error and exit with an error code 10.

## Lexical and syntax analysis (Lark)

The Lark library handles the core of the parsing process. The `grammar` variable defines the SOL25 language's grammar using Lark's syntax. The `parser` object is initialized with this grammar, and the `parse_code()` function uses it to parse the input code. The `parse_code()` function catches and handles lexical errors, exiting with error code 21 and syntax errors, exiting with error code 22. 

## Semantical analysis

Semantic analysis is performed by the `SemanticAnalyzer` class, which inherits from Lark's `Visitor`. The `analyze_semantics()` function instantiates the analyzer and initiates the semantic checks. The analyzer checks for:
- The existence of a `Main` class with a `run` method in the `Main` class (error code 31 if they don't exist).
- Usage of undefined variables, formal parameters, classes, and class methods (error code 32).
- Wrong block arity (error code 33).
- Redefinition of the variable or formal parameter (error code 34).
- Redefinition of class, built-in class or method in one class, block parameters with the same name (error code 35).


## XML generation

The `tree_to_xml()` function converts the parse tree into an XML representation. It creates an XML structure that reflects the structure of the SOL25 code, including classes, methods, blocks, and expressions. The `add_classes()`, `add_methods_blocks()`, `add_assigns()`, and `add_expr()` functions recursively build the XML tree. The `xml_as_str()` function post-processes the XML to ensure proper formatting and escaping of special characters before printing the XML to standard output.

## Testing

I have created my [tests](https://github.com/Marek324/IPP-1-tests) to test this script and distributed it to other students.