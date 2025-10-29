import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from lexer.Lexer import Lexer
from parser.Parser import Parser
from runtime.Interpreter import Interpreter
from utils.ast_printer import print_ast
import semantic.SemanticAnalyzer as Sa
from codegen.TACGenerator import TACGenerator


def print_tokens(tokens):
    print("=" * 50)
    print("TOKENS")
    print("=" * 50)
    for token in tokens:
        type_name = token.type.name if hasattr(token.type, 'name') else str(token.type)
        print(f"Token({type_name}, {repr(token.lexeme)}, {token.line})")
    print("=" * 50)
    print()


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <minipar_file> [--show-tokens] [--show-ast] [--show-symbols] [--emit-tac] [--save-tac <file>]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    show_tokens_flag = "--show-tokens" in sys.argv
    show_ast_flag = "--show-ast" in sys.argv
    show_symbols = "--show-symbols" in sys.argv
    emit_tac = "--emit-tac" in sys.argv
    save_tac = None
    
    # Verifica se deve salvar TAC em arquivo
    if "--save-tac" in sys.argv:
        try:
            idx = sys.argv.index("--save-tac")
            if idx + 1 < len(sys.argv):
                save_tac = sys.argv[idx + 1]
        except (ValueError, IndexError):
            print("Error: --save-tac requires a filename")
            sys.exit(1)
    
    if not Path(file_path).exists():
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
    
    with open(file_path, 'r') as f:
        source_code = f.read()
    
    try:
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        if show_tokens_flag:
            print_tokens(tokens)
        
        parser = Parser(tokens)
        ast = parser.parse()
        # analyzer = Sa.SemanticAnalyzer()
        # errors = analyzer.analyze(ast)
        # if errors:
        #     print("❌ ERROS ENCONTRADOS:")
        #     for error in errors:
        #         print(f"  - {error}")
        #     print(f"\nTotal: {len(errors)} erro(s)")
        # else:
        #     print("✅ Nenhum erro semântico encontrado!")
        
        if show_ast_flag:
            print("=" * 50)
            print("ÁRVORE DE SINTAXE ABSTRATA (AST)")
            print("=" * 50)
            print_ast(ast)
            print()
        
        # Gera TAC se solicitado
        if emit_tac or save_tac:
            tac_gen = TACGenerator()
            tac_gen.generate(ast)
            
            if emit_tac:
                tac_gen.print_tac()
            
            if save_tac:
                tac_gen.save_to_file(save_tac)
        
        print("=" * 50)
        print("EXECUÇÃO")
        print("=" * 50)
        interpreter = Interpreter()
        interpreter.interpret(ast)
        print()
        
        if show_symbols:
            print("=" * 50)
            print("TABELA DE SÍMBOLOS")
            print("=" * 50)
            interpreter.symbol_table.print_table()
            print()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

