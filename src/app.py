from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sys
import os
import traceback

# Caminhos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, "src"))

# Imports principais
from lexer.Lexer import Lexer
from parser.Parser import Parser
from parser.AST import DeclarationNode
from runtime.Interpreter import Interpreter
from utils.ast_printer import print_ast
import semantic.SemanticAnalyzer as Sa
from codegen.TACGenerator import TACGenerator

# Cria app
app = FastAPI(title="MiniPar 2025.1 API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir o frontend
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# Modelo de entrada
class CodigoEntrada(BaseModel):
    codigo: str

# Função auxiliar para gerar saída textual do AST
def get_ast_string(ast):
    from io import StringIO
    import contextlib
    s = StringIO()
    with contextlib.redirect_stdout(s):
        print_ast(ast)
    return s.getvalue().strip()

# Função auxiliar para imprimir tokens
def get_tokens_string(tokens):
    lines = []
    for token in tokens:
        type_name = token.type.name if hasattr(token.type, 'name') else str(token.type)
        lines.append(f"Token({type_name}, {repr(token.lexeme)}, {token.line})")
    return "\n".join(lines)

@app.post("/interpretar")
async def interpretar(dados: CodigoEntrada):
    codigo = dados.codigo

    try:
        # --- 1️⃣ Análise Léxica ---
        lexer = Lexer(codigo)
        tokens = lexer.tokenize()
        tokens_str = get_tokens_string(tokens)

        # --- 2️⃣ Análise Sintática / AST ---
        parser = Parser(tokens)
        ast = parser.parse()
        ast_str = get_ast_string(ast)

        # --- 3️⃣ Análise Semântica ---
        analyzer = Sa.SemanticAnalyzer()
        errors = analyzer.analyze(ast)

        if errors:
            semantica = "❌ Erros semânticos encontrados:\n" + "\n".join(f"- {e}" for e in errors)
        else:
            semantica = "✅ Nenhum erro semântico encontrado!"

        # --- 4️⃣ Execução / Interpretação ---
        interpreter = Interpreter()
        exec_output = []
        try:
            import io
            import contextlib
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                interpreter.interpret(ast)
            exec_output = buf.getvalue().strip()
        except Exception as e:
            exec_output = f"Erro de execução: {e}"

        # --- 5️⃣ Retorno JSON ---
        return {
            "tokens": tokens_str,
            "ast": ast_str,
            "semantico": semantica,
            "execucao": exec_output
        }

    except Exception as e:
        traceback_str = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        return {"erro": str(e), "traceback": traceback_str}

# Página principal
@app.get("/")
async def root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
