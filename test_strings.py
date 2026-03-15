from luz.lexer import Lexer
from luz.parser import Parser
from luz.interpreter import Interpreter

def test_luz_strings():
    interpreter = Interpreter()
    
    # 1. Asignación y concatenación
    lexer = Lexer('saludo = "hola" + " mundo"')
    ast = Parser(lexer.get_tokens()).parse()
    assert interpreter.visit(ast) == "hola mundo"
    
    # 2. Multiplicación de strings
    lexer = Lexer('risa = "ja" * 3')
    ast = Parser(lexer.get_tokens()).parse()
    assert interpreter.visit(ast) == "jajaja"
    
    # 3. Comparación de strings
    lexer = Lexer('if "luz" == "luz" { resultado = "si" }')
    ast = Parser(lexer.get_tokens()).parse()
    interpreter.visit(ast)
    assert interpreter.symbol_table['resultado'] == "si"

    # 4. Error en resta de strings
    try:
        lexer = Lexer('"hola" - "mundo"')
        ast = Parser(lexer.get_tokens()).parse()
        interpreter.visit(ast)
        assert False, "Debería haber lanzado una excepción"
    except Exception as e:
        assert "no soportada para strings" in str(e)

    print("¡Pruebas de strings pasaron con éxito!")

if __name__ == "__main__":
    test_luz_strings()
