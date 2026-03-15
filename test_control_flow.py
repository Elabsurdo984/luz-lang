from luz.lexer import Lexer
from luz.parser import Parser
from luz.interpreter import Interpreter

def test_luz_control_flow():
    interpreter = Interpreter()
    
    cases = [
        ("if 10 == 10 { x = 1 }", 1.0),
        ("x", 1.0),
        ("if 5 > 10 { y = 1 } elif 5 == 5 { y = 2 } else { y = 3 }", 2.0),
        ("y", 2.0),
        ("if 5 > 10 { z = 1 } else { z = 3 }", 3.0),
        ("z", 3.0),
        ("a = 10; b = 20; if a < b { res = 100 } else { res = 200 }", 100.0), # Aunque el REPL actual no soporta ';' fácilmente, el lexer lo ignorará como error si no lo definimos, o fallará. 
    ]
    
    # Nota: El parser actual espera EOF, así que procesaremos cada línea independientemente en el test.
    
    # Caso 1
    lexer = Lexer("if 10 == 10 { x = 1 }")
    ast = Parser(lexer.get_tokens()).parse()
    assert interpreter.visit(ast) == 1.0
    assert interpreter.symbol_table['x'] == 1.0
    
    # Caso 2: Elif
    lexer = Lexer("if 5 > 10 { y = 1 } elif 5 == 5 { y = 2 } else { y = 3 }")
    ast = Parser(lexer.get_tokens()).parse()
    assert interpreter.visit(ast) == 2.0
    assert interpreter.symbol_table['y'] == 2.0

    # Caso 3: Else
    lexer = Lexer("if 5 > 10 { z = 1 } else { z = 3 }")
    ast = Parser(lexer.get_tokens()).parse()
    assert interpreter.visit(ast) == 3.0
    assert interpreter.symbol_table['z'] == 3.0

    print("¡Pruebas de flujo de control pasaron con éxito!")

if __name__ == "__main__":
    test_luz_control_flow()
