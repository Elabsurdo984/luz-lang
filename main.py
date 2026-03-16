import sys
from luz.lexer import Lexer
from luz.parser import Parser
from luz.interpreter import Interpreter

def run(text, interpreter):
    try:
        lexer = Lexer(text)
        tokens = lexer.get_tokens()
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        result = interpreter.visit(ast)
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    interpreter = Interpreter()
    
    # Si se pasa un argumento, intentar ejecutar ese archivo
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                code = f.read()
                run(code, interpreter)
        except FileNotFoundError:
            print(f"Error: El archivo '{filename}' no existe.")
        except Exception as e:
            print(f"Error al leer el archivo: {e}")
    
    # De lo contrario, iniciar el REPL
    else:
        print("Intérprete de Luz v1.1 - Escribe 'salir' para finalizar")
        while True:
            try:
                text = input("Luz > ")
                if text.strip().lower() == "salir":
                    break
                if not text.strip():
                    continue
                    
                result = run(text, interpreter)
                if result is not None:
                    print(result)
                    
            except KeyboardInterrupt:
                print("\nSaliendo...")
                break
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    main()
