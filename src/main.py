import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from lexer.Lexer import Lexer
from parser.Parser import Parser
from parser.AST import DeclarationNode
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
        print("Uso: python main.py <arquivo.minipar> [--show-tokens] [--show-ast] [--show-symbols] [--emit-tac] [--save-tac <arquivo>]")
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
    
    # Parse optional channel mappings from CLI:
    # --channel-bind name=host:port   (can repeat)
    # --channel-connect name=host:port (can repeat)
    # --node-id ID                     (this process identifier)
    # --channel-map id=host:port       (map node id -> host:port) (can repeat)
    channel_bind = {}
    channel_connect = {}
    channel_map = {}
    node_id = None

    for i, arg in enumerate(sys.argv):
        if arg == "--channel-bind" and i + 1 < len(sys.argv):
            pair = sys.argv[i + 1]
            if '=' in pair:
                name, hp = pair.split('=', 1)
                channel_bind[name] = hp
        if arg == "--channel-connect" and i + 1 < len(sys.argv):
            pair = sys.argv[i + 1]
            if '=' in pair:
                name, hp = pair.split('=', 1)
                channel_connect[name] = hp
        if arg == "--node-id" and i + 1 < len(sys.argv):
            node_id = sys.argv[i + 1]
        if arg == "--channel-map" and i + 1 < len(sys.argv):
            pair = sys.argv[i + 1]
            if '=' in pair:
                nid, hp = pair.split('=', 1)
                channel_map[nid] = hp

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
        
        # If program declares channels, offer an interactive prompt per channel
        # asking whether this machine will RECEIVE (bind/listen) or SEND (connect).
        # Only offer interactive network role prompts if the channel declaration
        # includes pairing ids (i.e., was written as: c_channel name id1 id2).
        declared_channels = [
            child for child in ast.children
            if isinstance(child, DeclarationNode) and child.type_name.lower() == 'c_channel' and getattr(child, 'channel_info', None)
        ]

        if declared_channels and not channel_bind and not channel_connect:
            print("\nDetectado(s) declaração(ões) de canal com ids (par para rede):")
            for decl in declared_channels:
                name = decl.identifier
                info = getattr(decl, 'channel_info', None)
                print(f" - {name} (ids: {', '.join(info)})")
            try:
                cont = input("Deseja configurar papéis de rede para esses canais agora? [S/n]: ").strip().lower()
            except EOFError:
                cont = 'n'

            if cont == '' or cont.startswith(('s', 'y')):
                for decl in declared_channels:
                    name = decl.identifier
                    info = getattr(decl, 'channel_info', None)
                    # If channel_info present, show the two ids and ask which this node is
                    if info and len(info) >= 2:
                        print(f"Canal '{name}' pareamento: {info[0]} (servidor) <-> {info[1]} (cliente)")
                        try:
                            sel = input(f"Qual id representa ESTA máquina para o canal '{name}'? (deixe vazio para pular): ").strip()
                        except EOFError:
                            sel = ''
                        if sel == info[0]:
                            # Perguntar apenas a porta; bind em todas as interfaces
                            port = input(f"Informe a PORTA para BIND (escutar) para o id servidor '{sel}' (ex: 9000): ").strip()
                            if port:
                                channel_bind[name] = f"0.0.0.0:{port}"
                        elif sel == info[1]:
                            # Perguntar IP do servidor (opcional) e porta. Se IP vazio, assume localhost
                            server_ip = input(f"Informe o IP do servidor para conectar ao canal '{name}' (deixe vazio para 127.0.0.1): ").strip()
                            if server_ip == '':
                                server_ip = '127.0.0.1'
                            port = input(f"Informe a PORTA para conectar ao canal '{name}' (ex: 9000): ").strip()
                            if port:
                                channel_connect[name] = f"{server_ip}:{port}"
                        else:
                            print("Nenhum id válido selecionado para este canal; mapeamento interativo ignorado.")

        print("=" * 50)
        print("EXECUÇÃO")
        print("=" * 50)
        interpreter = Interpreter(channel_bind=channel_bind, channel_connect=channel_connect, node_id=node_id, channel_map=channel_map)
        interpreter.interpret(ast)
        print()

        if show_symbols:
            print("=" * 50)
            print("TABELA DE SÍMBOLOS")
            print("=" * 50)
            interpreter.symbol_table.print_table()
            print()

    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

