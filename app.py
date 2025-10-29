from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys, os


# 🧩 Importa seus módulos reais do MiniPar
from src.lexer import Lexer
from src.parser import Parser

app = FastAPI(title="MiniPar 2025.1 API")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# Libera acesso do front-end
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de entrada
class CodigoEntrada(BaseModel):
    codigo: str

@app.post("/interpretar")
async def interpretar(dados: CodigoEntrada):
    codigo = dados.codigo

    try:
        # --- 1️⃣ Análise Léxica ---
        lexer = Lexer(codigo)
        tokens = lexer.tokenize()  # ajuste conforme seu método

        # --- 2️⃣ Análise Sintática / AST ---
        parser = Parser(tokens)
        ast = parser.parse()  # ajuste conforme seu método

        # --- 3️⃣ Análise Semântica (se tiver) ---
        semantica = "Semântica OK"

        return {
            "lexica": "\n".join([str(t) for t in tokens]),
            "ast": str(ast),
            "semantica": semantica
        }

    except Exception as e:
        return {"erro": str(e)}
