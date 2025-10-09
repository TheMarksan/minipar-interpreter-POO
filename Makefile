# Makefile para MiniPar Interpreter
# Uso: make test1 [--ast] [--tokens] [--table]

# Variáveis
PYTHON = python3
INTERPRETER = src/main.py
TESTS_DIR = tests

# Cores
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
RED = \033[0;31m
NC = \033[0m

# Programas de teste
PROGRAMA1 = $(TESTS_DIR)/programa1_cliente_servidor.minipar
PROGRAMA2 = $(TESTS_DIR)/programa2_threads.minipar
PROGRAMA3 = $(TESTS_DIR)/programa3_neuronio.minipar
PROGRAMA4 = $(TESTS_DIR)/programa4_xor.minipar
PROGRAMA5 = $(TESTS_DIR)/programa5_recomendacao.minipar
PROGRAMA6 = $(TESTS_DIR)/programa6_quicksort.minipar
HELLO = $(TESTS_DIR)/hello_world.minipar

# Processa flags opcionais
FLAGS =
ifeq (--tokens,$(filter --tokens,$(MAKECMDGOALS)))
	FLAGS += --show-tokens
endif
ifeq (--ast,$(filter --ast,$(MAKECMDGOALS)))
	FLAGS += --show-ast
endif
ifeq (--table,$(filter --table,$(MAKECMDGOALS)))
	FLAGS += --show-symbols
endif

# Dummy targets para as flags (evita erro "No rule to make target")
--tokens:
	@:
--ast:
	@:
--table:
	@:

.PHONY: help clean test-all test1 test2 test3 test4 test5 test6 hello \
        --tokens --ast --table

# Target padrão
.DEFAULT_GOAL := help

## help: Mostra ajuda
help:
	@echo "$(BLUE)═══════════════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)         MiniPar Interpreter - Sistema de Build            $(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(GREEN)Uso:$(NC) make <test> [--ast] [--tokens] [--table]"
	@echo ""
	@echo "$(YELLOW)Testes Disponíveis:$(NC)"
	@echo "  test1        - Cliente-Servidor com Calculadora"
	@echo "  test2        - Threads (Fatorial e Fibonacci)"
	@echo "  test3        - Neurônio (Orientação a Objetos)"
	@echo "  test4        - XOR"
	@echo "  test5        - Sistema de Recomendação"
	@echo "  test6        - Quicksort"
	@echo "  hello        - Hello World"
	@echo "  test-all     - Executa todos os testes"
	@echo ""
	@echo "$(YELLOW)Flags Opcionais:$(NC)"
	@echo "  --tokens     - Mostra tokens (análise léxica)"
	@echo "  --ast        - Mostra AST (análise sintática)"
	@echo "  --table      - Mostra tabela de símbolos (análise semântica)"
	@echo ""
	@echo "$(BLUE)Exemplos:$(NC)"
	@echo "  make test1                    $(GREEN)# Apenas executa$(NC)"
	@echo "  make test1 --ast              $(GREEN)# Executa e mostra AST$(NC)"
	@echo "  make test2 --tokens           $(GREEN)# Executa e mostra tokens$(NC)"
	@echo "  make test3 --table            $(GREEN)# Executa e mostra símbolos$(NC)"
	@echo "  make test1 --ast --tokens     $(GREEN)# Executa com AST e tokens$(NC)"
	@echo "  make test2 --ast --table      $(GREEN)# Executa com AST e símbolos$(NC)"
	@echo ""
	@echo "$(YELLOW)Outros:$(NC)"
	@echo "  clean        - Remove arquivos temporários"
	@echo "  help         - Mostra esta mensagem"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════$(NC)"

## test1: Executa programa1
test1:
	@echo "$(GREEN)═══════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)  Programa 1: Cliente-Servidor com Calculadora$(NC)"
	@echo "$(GREEN)═══════════════════════════════════════════════════════════$(NC)"
	@$(PYTHON) $(INTERPRETER) $(PROGRAMA1) $(FLAGS)

## test2: Executa programa2
test2:
	@echo "$(GREEN)═══════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)  Programa 2: Threads (Fatorial e Fibonacci)$(NC)"
	@echo "$(GREEN)═══════════════════════════════════════════════════════════$(NC)"
	@$(PYTHON) $(INTERPRETER) $(PROGRAMA2) $(FLAGS)

## test3: Executa programa3
test3:
	@echo "$(GREEN)═══════════════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)  Programa 3: Neurônio (Orientação a Objetos)$(NC)"
	@echo "$(GREEN)═══════════════════════════════════════════════════════════$(NC)"
	@$(PYTHON) $(INTERPRETER) $(PROGRAMA3) $(FLAGS)

## test4: Executa programa4
test4:
	@if [ -f "$(PROGRAMA4)" ]; then \
		echo "$(GREEN)═══════════════════════════════════════════════════════════$(NC)"; \
		echo "$(GREEN)  Programa 4: XOR$(NC)"; \
		echo "$(GREEN)═══════════════════════════════════════════════════════════$(NC)"; \
		$(PYTHON) $(INTERPRETER) $(PROGRAMA4) $(FLAGS); \
	else \
		echo "$(RED)Programa 4 não encontrado: $(PROGRAMA4)$(NC)"; \
	fi

## test5: Executa programa5
test5:
	@if [ -f "$(PROGRAMA5)" ]; then \
		echo "$(GREEN)═══════════════════════════════════════════════════════════$(NC)"; \
		echo "$(GREEN)  Programa 5: Sistema de Recomendação$(NC)"; \
		echo "$(GREEN)═══════════════════════════════════════════════════════════$(NC)"; \
		$(PYTHON) $(INTERPRETER) $(PROGRAMA5) $(FLAGS); \
	else \
		echo "$(RED)Programa 5 não encontrado: $(PROGRAMA5)$(NC)"; \
	fi

## test6: Executa programa6
test6:
	@if [ -f "$(PROGRAMA6)" ]; then \
		echo "$(GREEN)═══════════════════════════════════════════════════════════$(NC)"; \
		echo "$(GREEN)  Programa 6: Quicksort$(NC)"; \
		echo "$(GREEN)═══════════════════════════════════════════════════════════$(NC)"; \
		$(PYTHON) $(INTERPRETER) $(PROGRAMA6) $(FLAGS); \
	else \
		echo "$(RED)Programa 6 não encontrado: $(PROGRAMA6)$(NC)"; \
	fi

## hello: Executa Hello World
hello:
	@if [ -f "$(HELLO)" ]; then \
		echo "$(GREEN)═══════════════════════════════════════════════════════════$(NC)"; \
		echo "$(GREEN)  Hello World$(NC)"; \
		echo "$(GREEN)═══════════════════════════════════════════════════════════$(NC)"; \
		$(PYTHON) $(INTERPRETER) $(HELLO) $(FLAGS); \
	else \
		echo "$(RED)Arquivo não encontrado: $(HELLO)$(NC)"; \
	fi

## test-all: Executa todos os programas
test-all:
	@echo "$(BLUE)═══════════════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)         Executando Todos os Programas de Teste$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@$(MAKE) test1 || true
	@echo ""
	@$(MAKE) test2 || true
	@echo ""
	@$(MAKE) test3 || true
	@echo ""
	@$(MAKE) test4 || true
	@echo ""
	@$(MAKE) test5 || true
	@echo ""
	@$(MAKE) test6 || true
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)         Todos os Testes Concluídos$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════$(NC)"

## clean: Remove arquivos temporários
clean:
	@echo "$(YELLOW)Limpando arquivos temporários...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name "*~" -delete 2>/dev/null || true
	@find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@echo "$(GREEN)Limpeza concluída!$(NC)"
