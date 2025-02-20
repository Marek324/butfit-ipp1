from tests.utils_tests import run_test

def test_missing_colon(monkeypatch):
    run_test("""
        class Main Object { 
            run [ | x := 5. ]
        }
        """,
        22, monkeypatch)
    
def test_invalid_class_id1(monkeypatch):
    run_test("""
        class main : Object { 
            run [ | x := 5. ]
        }
        """,
        22, monkeypatch)
    
def test_invalid_class_id2(monkeypatch):
    run_test("""
        class Main : object { 
            run [ | x := 5. ]
        }
        """,
        22, monkeypatch)
    
def test_unterminated_block(monkeypatch):
    run_test("""
        class Main Object { 
            run [ | x := 5.
        }
        """,
        22, monkeypatch)
    
def test_block_missing_pipe(monkeypatch):
    run_test("""
        class Main Object { 
            run [ x := 5. ]
        }
        """,
        22, monkeypatch)
    
def test_missing_dot(monkeypatch):
    run_test("""
        class Main Object { 
            run [ | x := 5 ]
        }
        """,
        22, monkeypatch)
    
def test_unterminated_class(monkeypatch):
    run_test("""
        class Main Object { 
            run [ | x := 5. ]
        """,
        22, monkeypatch)
    
def test_missing_class(monkeypatch):
    run_test("""
        Main : Object { 
            run [ | x := 5. ]
        }
        """,
        22, monkeypatch)
    
def test_missing_class_id(monkeypatch):
    run_test("""
        class : Object { 
            run [ | x := 5. ]
        }
        """,
        22, monkeypatch)
    
def test_missing_class_body(monkeypatch):
    run_test("""
        class Main: Object 
        """,
        22, monkeypatch)

def test_invalid_parameter1(monkeypatch):
    run_test("""
        class Main Object { 
            run [ x := 5. | ]
        }
        """,
        22, monkeypatch)
    
def test_invalid_parameter2(monkeypatch):
    run_test("""
        class Main Object { 
            run [ x := 5. | y ]
        }
        """,
        22, monkeypatch)
    
def test_invalid_parameter3(monkeypatch):
    run_test("""
        class Main : Object {
            run [
                :Main |
                x := 5.
            ]
        }
        """, 
        22, monkeypatch)
    
def test_invalid_parameter4(monkeypatch):
    run_test("""
        class Main : Object {
            run [
                Main |
                x := 5.
            ]
        }
        """, 
        22, monkeypatch)
    

def test_unclosed_parentheses(monkeypatch):
    run_test("""
        class Main : Object { 
            run [ | x := (5. ]
        }
        """,
        22, monkeypatch)
    
def test_invalid_send(monkeypatch):
    run_test("""
        class Main : Object { 
            run [ | x := 5 timesRepeat:. ]
        }
        """,
        22, monkeypatch)

def test_selector1(monkeypatch):
    run_test("""
        class Main : Object { 
            Integer [ | x := 5.  ]
        }
        """,
        22, monkeypatch)
    
def test_selector2(monkeypatch):
    run_test("""
        class Main : Object { 
            I_run [ | x := 5.  ]
        }
        """,
        22, monkeypatch)
    
def test_selector3(monkeypatch):
    run_test("""
        class Main : Object { 
            :run [ | x := 5.  ]
        }
        """,
        22, monkeypatch)
    
def test_selector4(monkeypatch):
    run_test("""
        class Main : Object { 
            run: a [ | x := 5.  ]
        }
        """,
        22, monkeypatch)
    
def test_selector5(monkeypatch):
    run_test("""
        class Main : Object { 
            run: a: b [ | x := 5.  ]
        }
        """,
        22, monkeypatch)