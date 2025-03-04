# parse.py
# Author: Marek hric xhricma00

import sys, re
from lark import Lark, Visitor, Token, UnexpectedCharacters, UnexpectedToken, UnexpectedEOF
import xml.etree.ElementTree as ET


# Exit codes
SUCCESS = 0
WRONG_ARGS = 10

LEXICAL_ERROR = 21
SYNTAX_ERROR = 22

SEM_MISSING_MAIN_RUN = 31
SEM_UNDEF = 32
SEM_ARITY = 33
SEM_VAR_CONFLICT = 34
SEM_OTHER = 35

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

program: class_ program? 
class_: "class" term_cid ":" term_cid "{" method? "}"
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

    Args:
        token: lark token with comment.
    """
    global description
    comment = token.value[1:-1]
    if description is None:
        description = comment

        return ""
    else:
        return ""

parser = Lark(grammar, start="start", parser="lalr", lexer_callbacks={"COMMENT": save_description})
LANGUAGE = "SOL25"
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

def get_selector(selector):
    """
    Recursively saves selector from definition.

    Args:
        selector: lark parse subtree with selector node as root.

    Returns:
        selector string.
    """
    sel = selector.children[0].children[0].value
    if len(selector.children) == 1:
        return sel
    else:
        return sel + get_selector(selector.children[1])
    
def get_methods(method, class_id):
    """
    Recursively saves class instance methods from definition.

    Args:
        method: lark parse subtree with method node as root.
        class_id: class name for error print.

    Returns:
        List of method names.

    Exits:
        SEM_OTHER if a method is defined more than once.
    """
    method_sel = get_selector(method.children[0])
    
    # method has 2 or 3 children: selector, block, method (if there is another method)
    if len(method.children) == 2:
        return [method_sel]
    
    methods = [method_sel] + get_methods(method.children[2], class_id)
    if len(methods) != len(set(methods)):
        print(f"Semantic error: Method {method_sel} redefinition in class {class_id}", file=sys.stderr)
        sys.exit(SEM_OTHER)
    
    return methods

def check_expr_o(def_vars, expr, analyzer):
    """
    Recursively checks for undefined variables and class methods in the expression.

    Args:
        def_vars: variables defined in the block.
        expr: lark parse subtree with expr node as root.
        analyzer: lark visitor instance.

    Exits:
        SEM_UNDEF if an undefined variable is used.
    """
    if isinstance(expr, Token):
        return
    
    for child in expr.children:
        if isinstance(child, Token):
            continue

        if child.data == "expr_base" or child.data == "expr_sel" or child.data == "expr":
            term = child.children[0]
            if term.data == "term_id":
                var_name = term.children[0].value
                if var_name not in def_vars:
                    print(f"Semantic error: Undefined variable {var_name}", file=sys.stderr)
                    sys.exit(SEM_UNDEF)
            if child.data != "block":
                check_expr_o(def_vars, child, analyzer)
        
        if child.data == "expr_tail" and len(child.children) > 0:
            if child.children[0].data == "term_id":
                sel = child.children[0].children[0].value
                if sel in analyzer.reserved_ids:
                    print(f"Syntax error: '{sel}' is a reserved keyword", file=sys.stderr)
                    sys.exit(SYNTAX_ERROR)
            if child.data != "block":
                check_expr_o(def_vars, child, analyzer)

def check_expr_base(def_vars, expr_base, analyzer):
    """
    Checks for undefined variables and class methods in the expression base.

    Args:
        def_vars: variables defined in the block.
        expr_base: lark parse subtree with expr_base node as root.
        analyzer: lark visitor instance.

    Exits:
        SEM_UNDEF if an undefined variable is used.
    """
    if (expr_base.children[0].data == "expr"):
        check_expr(def_vars, expr_base.children[0], analyzer)
    elif (expr_base.children[0].data == "term_id"):
        var_name = expr_base.children[0].children[0].value
        if var_name not in def_vars:
            print(f"Semantic error: Undefined variable {var_name}", file=sys.stderr)
            sys.exit(SEM_UNDEF)

def check_expr_sel(def_vars, expr_sel, analyzer):
    """
    Checks for undefined variables and class methods in the expression tail.

    Args:
        def_vars: variables defined in the block.
        expr_sel: lark parse subtree with expr_sel node as root.
        analyzer: lark visitor instance.

    Returns:
        selector string.

    Exits:
        SEM_UNDEF if an undefined variable is used..
    """
    check_expr_base(def_vars, expr_sel.children[1], analyzer)

    if len(expr_sel.children) == 2:
        return expr_sel.children[0].children[0].value
    else:
        return expr_sel.children[0].children[0].value + check_expr_sel(def_vars, expr_sel.children[2], analyzer)

def check_expr_tail(def_vars, expr_tail, analyzer):
    """
    Checks for undefined variables and class methods in the expression tail.

    Args:
        def_vars: variables defined in the block.
        expr_tail: lark parse subtree with expr_tail node as root.
        analyzer: lark visitor instance.

    Exits:
        SYNTAX_ERROR if an reserved keyword is used as selector.
    """
    if len(expr_tail.children) == 0:
        return
    
    if expr_tail.children[0].data == "term_id":
        sel = expr_tail.children[0].children[0].value
        if sel in analyzer.reserved_ids:
            print(f"Syntax error: '{sel}' is a reserved keyword", file=sys.stderr)
            sys.exit(SYNTAX_ERROR)
    elif expr_tail.children[0].data == "expr_sel":
        sel = check_expr_sel(def_vars, expr_tail.children[0], analyzer)
    else: 
        check_expr_base(def_vars, expr_tail.children[0].children[1], analyzer)

def check_expr(def_vars, expr, analyzer):
    """
    Recursively checks for undefined variables and class methods in the expression.

    Args:
        def_vars: variables defined in the block.
        expr: lark parse subtree with expr node as root.
        analyzer: lark visitor instance.

    Exits:
        SEM_UNDEF if an undefined class method is used.
    """
    base = expr.children[0].children[0]
    if base.data == 'expr' and len(expr.children[1].children) == 0:
        check_expr(def_vars, base, analyzer)
        return
    elif base.data == 'block':
        return
    elif base.data == 'term_cid':
        class_id = base.children[0].value
        if class_id not in analyzer.classes:
            analyzer.classes[class_id] = {"defined": False}

        if expr.children[1].children[0].data == 'expr_sel':
            sel = check_expr_sel(def_vars, expr.children[1].children[0], analyzer)
            if sel != "from:":
                print(f"Semantic error: Undefined class method {sel} in class {class_id}", file=sys.stderr)
                sys.exit(SEM_UNDEF)
        elif expr.children[1].children[0].data == 'term_id':
            sel = expr.children[1].children[0].children[0].value
            if sel == "read":
                analyzer.classes[class_id]["used_read"] = True
            elif sel != "new":
                print(f"Semantic error: Undefined class method {sel} in class {class_id}", file=sys.stderr)
                sys.exit(SEM_UNDEF)
            
    check_expr_base(def_vars, expr.children[0], analyzer)
    check_expr_tail(def_vars, expr.children[1], analyzer)


def check_assignements(block_params, def_vars, block_stat, analyzer):
    """
    Recursively check all assignements in the block.

    Args:
        block_params: block parameters
        def_vars: variables defined in the block.
        block_stat: lark parse subtree with block_stat node as root.
        analyzer: lark visitor instance.

    Exits:
        SEM_VAR_CONFLICT if a variable is redefined.
        SYNTAX_ERROR if an reserved keyword is used as variable name.
    """
    check_expr(def_vars, block_stat.children[1], analyzer)

    var_name = block_stat.children[0].children[0].value
    if var_name in block_params:
        print(f"Semantic error: Variable {var_name} redefinition", file=sys.stderr)
        sys.exit(SEM_VAR_CONFLICT)
    elif var_name in analyzer.reserved_ids:
        print(f"Syntax error: '{var_name}' is a reserved keyword", file=sys.stderr)
        sys.exit(SYNTAX_ERROR)
    
    def_vars.append(var_name)

    #Following assignement
    if len(block_stat.children) == 3:
        check_assignements(block_params, def_vars, block_stat.children[2], analyzer)
    
def get_block_params(block_par):
    """
    Recursively saves block parameters from definition.

    Args:
        block_par: lark parse subtree with block_par node as root.
    """
    param = block_par.children[0].children[0].value[1:]

    if len(block_par.children) == 1:
        return [param]
    
    methods = [param] + get_block_params(block_par.children[1])
    if len(methods) != len(set(methods)):
        print(f"Semantic error: Block parameters with the same name", file=sys.stderr)
        sys.exit(SEM_OTHER)
    
    return methods

def is_string_subclass(class_name, classes):
    """
    Checks if the class is a subclass of String.

    Args:
        class_name: class name.
        classes: class dictionary.

    Returns:
        True if the class is a subclass of String, False otherwise.
    """
    if class_name == "String":
        return True
    if classes[class_name]["parent"] is None:
        return False
    
    return is_string_subclass(classes[class_name]["parent"], classes)

# Lark visitor for semantic analysis
class SemanticAnalyzer(Visitor):
    def __init__(self):
        self.builtin_classes = ["Object", "Nil", "True", "False", "Integer", "String", "Block"]
        self.reserved_ids = ['self', 'super', 'true', 'false', 'nil'] # 'class' is checked separately
        self.classes = {}
        for builtin_class in self.builtin_classes:
            self.classes[builtin_class] = {"defined": True, "used_read": False}
            if builtin_class == "Object":
                self.classes[builtin_class]["parent"] = None
            else:
                self.classes[builtin_class]["parent"] = "Object"
        
    def class_(self, tree):
        class_id = tree.children[0].children[0].value
        class_parent = tree.children[1].children[0].value
        
        if class_id in self.builtin_classes:
            print(f"Semantic error: Builtin class {class_id} redefinition", file=sys.stderr)
            sys.exit(SEM_OTHER)

        if class_id in self.classes and self.classes[class_id]["defined"]:
            print(f"Semantic error: Class {class_id} redefinition", file=sys.stderr)
            sys.exit(SEM_OTHER)
        elif class_id in self.classes:
            self.classes[class_id]["defined"] = True
            self.classes[class_id]["parent"] = class_parent
            if "used_read" not in self.classes[class_id]:
                self.classes[class_id]["used_read"] = False
        else:
            self.classes[class_id]= {"defined": True, "parent": class_parent, "used_read": False}

            if len(tree.children) == 3:
                self.classes[class_id]["methods"] = get_methods(tree.children[2], class_id)
            else:
                self.classes[class_id]["methods"] = []

        if class_parent not in self.classes:
            self.classes[class_parent] = {"defined": False}

        return tree
    
    def method(self, tree):
        sel = get_selector(tree.children[0])
        args_n = len(sel.split(":")) - 1
        params_n = 0
        
        if len(tree.children[1].children) > 0:    
            if tree.children[1].children[0].data == "block_par":
                params_n = len(get_block_params(tree.children[1].children[0]))

        if params_n != args_n:
            print(f"Semantic error: Method {sel} has wrong number of arguments", file=sys.stderr)
            sys.exit(SEM_ARITY)
        
        return tree

    def block(self, tree):
        # Empty block
        if (len(tree.children) == 0):
            return tree
        
        stat_index = 0
        block_params = []
        def_vars = self.reserved_ids.copy()

        if tree.children[0].data == "block_par":
            stat_index = 1
            block_params = get_block_params(tree.children[0])
            def_vars.extend(block_params)

            if len(tree.children) != 2:
                return tree
            
        check_assignements(block_params, def_vars, tree.children[stat_index], self)

        return tree
    
    def expr_base(self, tree):            
        if tree.children[0].data == "term_cid":
            class_id = tree.children[0].children[0].value
            if class_id not in self.classes:
                self.classes[class_id] = {"defined": False}

        return tree
    
    def term_id(self, tree):
        id = tree.children[0].value
        if id == 'class':
            print("Syntax error: 'class' is a reserved keyword", file=sys.stderr)
            sys.exit(SYNTAX_ERROR)

        return tree

    def term_block_par_id(self, tree):
        id = tree.children[0].value[1:]
        if id == 'class' or id in self.reserved_ids:
            print(f"Syntax error: '{id}' is a reserved keyword", file=sys.stderr)
            sys.exit(SYNTAX_ERROR)
        
        return tree

    def final_check(self):
        if "Main" not in self.classes:
            print("Semantic error: Main class is missing", file=sys.stderr)
            sys.exit(SEM_MISSING_MAIN_RUN)

        if "run" not in self.classes["Main"]["methods"]:
            print("Semantic error: Main class is missing run method", file=sys.stderr)
            sys.exit(SEM_MISSING_MAIN_RUN)

        for class_name in self.classes:
            if self.classes[class_name]["defined"] == False:
                print(f"Semantic error: Class {class_name} is missing definition", file=sys.stderr)
                sys.exit(SEM_UNDEF)
            elif self.classes[class_name]["used_read"] == True and not is_string_subclass(class_name, self.classes):
                print(f"Semantic error: {class_name} does not have 'read' class method", file=sys.stderr)
                sys.exit(SEM_UNDEF)
                

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
    sem_analyzer = SemanticAnalyzer()
    sem_analyzer.visit_topdown(tree)
    sem_analyzer.final_check()

def add_expr_simple(expr, tree_exp):
    """
    Adds simple expression (literal, var, block) to the xml tree.

    Args:
        expr: xml tree node.
        tree_exp: lark parse subtree with expr_base first child node as root.
    """
    match tree_exp.data:
        case "term_int":
            ET.SubElement(expr, "literal", attrib={"class": "Integer", "value": tree_exp.children[0].value})
        case "term_str":
            ET.SubElement(expr, "literal", attrib={"class": "String", "value": tree_exp.children[0].value[1:-1]})
        case "term_cid":
            ET.SubElement(expr, "literal", attrib={"class": "class", "value": tree_exp.children[0].value})
        case "term_id":
            match tree_exp.children[0].value:
                case "true":
                    ET.SubElement(expr, "literal", attrib={"class": "True", "value": "true"})
                case "false":
                    ET.SubElement(expr, "literal", attrib={"class": "False", "value": "false"})
                case "nil":
                    ET.SubElement(expr, "literal", attrib={"class": "Nil", "value": "nil"})
                case _:
                    ET.SubElement(expr, "var", attrib={"name": tree_exp.children[0].value})
        case "block":
            block = ET.SubElement(expr, "block")
            param_n = 0
            for i in range(len(tree_exp.children)):
                if tree_exp.children[i].data == "block_par":
                    param_n = add_params(block, tree_exp.children[i])
                if tree_exp.children[i].data == "block_stat":
                    add_assigns(block, tree_exp.children[i])
                    
            block.set("arity", str(param_n))


def add_expr_send(send, tree_expr_sel, arg_n=1):
    """
    Adds send arguments to the xml tree.

    Args:
        send: xml send tree node.
        tree_exp_sel: lark parse subtree with expr node as root.
    """
    send.attrib["selector"] += tree_expr_sel.children[0].children[0].value
    arg = ET.SubElement(send, "arg", {"order": str(arg_n)})
    arg_expr = ET.SubElement(arg, "expr")
    
    if tree_expr_sel.children[1].children[0].data == "expr":
        add_expr(arg_expr, tree_expr_sel.children[1].children[0])
    else:
        add_expr_simple(arg_expr, tree_expr_sel.children[1].children[0])

    if len(tree_expr_sel.children) == 3:
        add_expr_send(send, tree_expr_sel.children[2], arg_n + 1)

    
def add_expr(expr, tree_expr):
    """
    Adds expression to the xml tree.

    Args:
        expr: xml expr tree node.
        tree_expr: lark parse subtree with expr node as root.
    """
    if tree_expr.children[0].children[0].data == 'expr' and len(tree_expr.children[1].children) == 0:
        add_expr(expr, tree_expr.children[0].children[0])
        return

    if len(tree_expr.children[1].children) > 0:
        send = ET.SubElement(expr, "send", attrib={"selector": ""})
        
        # receiver
        send_expr = ET.SubElement(send, "expr")
        if tree_expr.children[0].children[0].data == 'expr':
            add_expr(send_expr, tree_expr.children[0].children[0])
        else:
            add_expr_simple(send_expr, tree_expr.children[0].children[0])

        if tree_expr.children[1].children[0].data != 'expr_sel':
            send.attrib["selector"] = tree_expr.children[1].children[0].children[0].value
            return
        
        add_expr_send(send, tree_expr.children[1].children[0])
        return

    add_expr_simple(expr, tree_expr.children[0].children[0])

def add_assigns(block, tree_block_stat, order=1):
    """
    Recursively adds assignements to the xml tree.

    Args:
        block: xml block tree node.
        tree_block_stat: lark parse subtree with block_stat node as root.
        order: assignement order.
    """
    assign = ET.SubElement(block, "assign")
    assign.set("order", str(order))
    ET.SubElement(assign, "var", attrib={"name": tree_block_stat.children[0].children[0].value})
    expr = ET.SubElement(assign, "expr")
    
    add_expr(expr, tree_block_stat.children[1])

    if (len(tree_block_stat.children) == 3):
        add_assigns(block, tree_block_stat.children[2], order + 1)
    
def add_params(block, tree_block_par, order=1, param_n=1):
    """
    Recursively adds parameters to the xml tree.

    Args:
        block: xml block tree node.
        tree_block_par: lark parse subtree with block_par node as root.
        order: parameter order.
        param_n: parameter number.
    
    Returns:
        Number of parameters (used in block literals).
    """
    if len(tree_block_par.children) == 0:
        return 0
    
    param = ET.SubElement(block, "parameter")
    param.set("order", str(order))
    param.set("name", tree_block_par.children[0].children[0].value[1:])
    if  (len(tree_block_par.children) > 1):
        add_params(block, tree_block_par.children[1], order=(order + 1), param_n=(param_n + 1))

    return param_n
    
def add_methods_blocks(class_, tree_method):
    """
    Recursively adds methods to the xml tree.

    Args:
        class_: xml class tree node.
        tree_method: lark parse subtree with method node as root.
    """
    sel = get_selector(tree_method.children[0])
    method = ET.SubElement(class_, "method")
    method.set("selector", sel)
    
    block = ET.SubElement(method, "block")
    arity = len(sel.split(":")) - 1
    block.set("arity", str(arity))
    for i in range(len(tree_method.children[1].children)):
        if tree_method.children[1].children[i].data == "block_par":
            add_params(block, tree_method.children[1].children[i])
        if tree_method.children[1].children[i].data == "block_stat":
            add_assigns(block, tree_method.children[1].children[i])

    if len(tree_method.children) == 3:
        add_methods_blocks(class_, tree_method.children[2])

def add_classes(program, tree_prog):
    """
    Recursiively adds classes to the xml tree.

    Args:
        program: xml program tree node.
        tree_prog: lark parse subtree with program node as root
    """
    tree_c = tree_prog.children[0]
    class_ = ET.SubElement(program, "class")
    class_.set("name", tree_c.children[0].children[0].value)
    class_.set("parent", tree_c.children[1].children[0].value)
    if(len(tree_c.children) == 3):
        add_methods_blocks(class_, tree_c.children[2])
        
    if len(tree_prog.children) == 2:
        add_classes(program, tree_prog.children[1])
            
def tree_to_xml(tree):
    """
    Convert tree to xml representation.

    Args:
        tree: lark parse tree.
    
    Returns:
        xml representation of tree.
    """
    global description 
    root = ET.Element("program")
    root.set('language', LANGUAGE)
    if description is not None:
        root.set('description', description)

    add_classes(root, tree)

    xml_tree = ET.ElementTree(root)
    
    return xml_tree

def xml_as_str(xml):
    """
    Post-process xml tree and convert it to string.

    Args:
        xml: xml tree.

    Returns:
        xml string representation.
    """
    xml_str = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + ET.tostring(xml.getroot()).__str__()[2:-1]
    xml_str = re.sub(r"\\\\", r"\\", xml_str)
    xml_str = re.sub(r"\\\\'", r"\&apos;", xml_str)
    return xml_str

def main():
    parse_args()
    code = sys.stdin.read()
    tree = parse_code(code)
    analyze_semantics(tree)
    xml = tree_to_xml(tree)
    xml_str = xml_as_str(xml)
    print(xml_str)

if __name__ == "__main__":
    main()
