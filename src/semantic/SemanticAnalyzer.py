from symbol_table.SymbolTable import SymbolTable
from typing import List, Optional

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors: List[str] = []
        self.current_function: Optional[str] = None
        self.return_type_stack: List[str] = []
        self.functions = {}  # Dicionário adicional para armazenar funções

    def analyze(self, ast) -> List[str]:
        """Analisa a árvore AST (objeto) e retorna uma lista de erros semânticos"""
        print("=== INICIANDO ANÁLISE SEMÂNTICA ===")
        self.errors = []
        self.functions = {}

        try:
            # Primeira passada: coletar declarações globais
            self.collect_global_declarations(ast)

            # Segunda passada: análise semântica completa
            if hasattr(ast, 'children'):
                self.analyze_children(ast.children)
            elif hasattr(ast, 'declarations'):
                self.analyze_children(ast.declarations)
            else:
                self.analyze_node(ast)

            print("✅ Análise semântica concluída!")

        except Exception as e:
            self.errors.append(f"Erro durante análise: {str(e)}")
            print(f"Erro durante análise: {e}")
            import traceback
            traceback.print_exc()

        return self.errors

    def collect_global_declarations(self, ast):
        """Coleta declarações globais da AST"""
        children = []
        if hasattr(ast, 'children'):
            children = ast.children
        elif hasattr(ast, 'declarations'):
            children = ast.declarations

        for child in children:
            # Declarações de variáveis globais (canais)
            if self.is_variable_declaration(child):
                type_name = getattr(child, 'type_name', getattr(child, 'type', None))
                identifier = getattr(child, 'identifier', None)

                if not type_name or not identifier:
                    continue

                if not self.is_valid_type(type_name):
                    self.errors.append(f"Erro: Tipo '{type_name}' não é válido")
                    continue

                # Verifica se a variável já foi declarada no escopo atual
                if self.symbol_table_exists_current_scope(identifier):
                    self.errors.append(f"Erro: Variável '{identifier}' já declarada")
                else:
                    self.symbol_table.define(identifier, type_name)
                    print(f"✓ Variável global declarada: {identifier} : {type_name}")

            # Declarações de funções
            elif self.is_function_declaration(child):
                func_name = getattr(child, 'name', getattr(child, 'identifier', None))
                if func_name:
                    self.functions[func_name] = child  # Armazena no dicionário local
                    print(f"✓ Função declarada: {func_name}")

    def analyze_children(self, children):
        """Analisa uma lista de children da AST"""
        for child in children:
            self.analyze_node(child)

    def analyze_node(self, node):
        """Analisa um nó individual da AST"""
        if self.is_variable_declaration(node):
            self.analyze_variable_declaration(node)
        elif self.is_function_declaration(node):
            self.analyze_function_declaration(node)
        elif self.is_assignment(node):
            self.analyze_assignment(node)
        elif self.is_expression_statement(node):
            self.analyze_expression_statement(node)
        elif self.is_channel_operation(node):
            self.analyze_channel_operation(node)
        elif self.is_if_statement(node):
            self.analyze_if_statement(node)
        elif self.is_block_statement(node):
            self.analyze_block_statement(node)
        elif self.is_function_call(node):
            self.analyze_function_call(node)
        elif hasattr(node, 'children'):
            self.analyze_children(node.children)
        elif hasattr(node, 'declarations'):
            self.analyze_children(node.declarations)
        elif hasattr(node, 'statements'):
            self.analyze_children(node.statements)

    def is_variable_declaration(self, node) -> bool:
        """Verifica se é uma declaração de variável"""
        return (hasattr(node, 'type_name') or hasattr(node, 'type')) and hasattr(node, 'identifier') and not hasattr(node, 'return_type')

    def is_function_declaration(self, node) -> bool:
        """Verifica se é uma declaração de função"""
        return (hasattr(node, 'return_type') and
                (hasattr(node, 'name') or hasattr(node, 'identifier')) and
                (hasattr(node, 'body') or hasattr(node, 'children')))

    def is_assignment(self, node) -> bool:
        """Verifica se é uma atribuição"""
        return hasattr(node, 'identifier') and hasattr(node, 'expression')

    def is_expression_statement(self, node) -> bool:
        """Verifica se é um statement de expressão"""
        return hasattr(node, 'expression')

    def is_channel_operation(self, node) -> bool:
        """Verifica se é uma operação de canal"""
        return hasattr(node, 'channel')

    def is_if_statement(self, node) -> bool:
        """Verifica se é uma estrutura if"""
        return hasattr(node, 'condition') and hasattr(node, 'then_body')

    def is_block_statement(self, node) -> bool:
        """Verifica se é um bloco"""
        return hasattr(node, 'block_type') and hasattr(node, 'statements')

    def is_function_call(self, node) -> bool:
        """Verifica se é uma chamada de função"""
        return hasattr(node, 'name') and hasattr(node, 'arguments')

    def analyze_variable_declaration(self, node):
        """Analisa declaração de variável"""
        type_name = getattr(node, 'type_name', getattr(node, 'type', None))
        identifier = getattr(node, 'identifier', None)

        if not type_name or not identifier:
            self.errors.append("Erro: Declaração de variável incompleta")
            return

        # Verifica se o tipo é válido
        if not self.is_valid_type(type_name):
            self.errors.append(f"Erro: Tipo '{type_name}' não é válido")
            return

        # Verifica se a variável já foi declarada no escopo atual
        # Mas ignora se já foi declarada na fase de coleta global
        existing = self.symbol_table.lookup(identifier)
        if existing and self.symbol_table_exists_current_scope(identifier):
            # Só reporta erro se realmente for redeclaração no mesmo escopo
            # e não for uma variável global já coletada
            if self.symbol_table.current_scope.scope_level > 0:
                self.errors.append(f"Erro: Variável '{identifier}' já declarada neste escopo")
        else:
            # Registra a variável apenas se ainda não existe
            if not existing:
                self.symbol_table.define(identifier, type_name)
                print(f"  ✓ Variável declarada: {identifier} : {type_name}")

    def analyze_function_declaration(self, node):
        """Analisa declaração de função"""
        func_name = getattr(node, 'name', getattr(node, 'identifier', None))
        return_type = getattr(node, 'return_type', None)
        parameters = getattr(node, 'parameters', [])
        body = getattr(node, 'body', getattr(node, 'children', []))

        if not func_name:
            self.errors.append("Erro: Função sem nome")
            return

        print(f"Analisando função: {func_name}")

        # Verifica tipo de retorno
        if return_type and not self.is_valid_type(return_type):
            self.errors.append(f"Erro: Tipo de retorno '{return_type}' inválido")

        self.current_function = func_name
        if return_type:
            self.return_type_stack.append(return_type)
        else:
            self.return_type_stack.append("VOID")

        # Entra em novo escopo para a função
        self.symbol_table.enter_scope()

        try:
            # Registra parâmetros
            for param in parameters:
                if hasattr(param, 'type') and hasattr(param, 'identifier'):
                    param_type = param.type
                    param_name = param.identifier
                    if not self.is_valid_type(param_type):
                        self.errors.append(f"Erro: Tipo de parâmetro '{param_type}' inválido")
                    self.symbol_table.define(param_name, param_type)
                    print(f"    ✓ Parâmetro: {param_name} : {param_type}")

            # Analisa corpo da função
            self.analyze_children(body)

        finally:
            if self.return_type_stack:
                self.return_type_stack.pop()
            self.symbol_table.exit_scope()
            self.current_function = None

    def analyze_assignment(self, node):
        """Analisa atribuição"""
        identifier = getattr(node, 'identifier', None)
        expression = getattr(node, 'expression', None)

        if not identifier:
            self.errors.append("Erro: Atribuição sem identificador")
            return

        # Verifica se a variável foi declarada
        var_info = self.symbol_table.lookup(identifier)
        if not var_info:
            self.errors.append(f"Erro: Variável '{identifier}' não declarada")
            return

        var_type = var_info.symbol_type
        expr_type = self.get_expression_type(expression)

        if expr_type is None:
            self.errors.append(f"Erro: Expressão inválida na atribuição para '{identifier}'")
        elif not self.are_types_compatible(var_type, expr_type):
            self.errors.append(f"Erro: Não é possível atribuir {expr_type} a '{identifier}' do tipo {var_type}")

    def analyze_expression_statement(self, node):
        """Analisa statement de expressão"""
        expression = getattr(node, 'expression', None)
        if expression:
            # Apenas verifica se a expressão é válida
            self.get_expression_type(expression)

    def analyze_channel_operation(self, node):
        """Analisa operação de canal (send/receive)"""
        channel_name = getattr(node, 'channel', None)

        if not channel_name:
            self.errors.append("Erro: Operação de canal sem nome")
            return

        # Verifica se o canal existe
        channel_info = self.symbol_table.lookup(channel_name)
        if not channel_info:
            self.errors.append(f"Erro: Canal '{channel_name}' não declarado")
            return

        channel_type = channel_info.symbol_type
        if channel_type != "C_CHANNEL":
            self.errors.append(f"Erro: '{channel_name}' não é um canal (tipo: {channel_type})")
            return

        # Verifica operação de send (values)
        if hasattr(node, 'values'):
            values = node.values
            for value in values:
                # Verifica se as variáveis existem
                if hasattr(value, 'name'):
                    var_name = value.name
                    if not self.symbol_table.lookup(var_name):
                        self.errors.append(f"Erro: Variável '{var_name}' não declarada para envio pelo canal")

        # Verifica operação de receive (variables)
        if hasattr(node, 'variables'):
            variables = node.variables
            for var in variables:
                if hasattr(var, 'name'):
                    var_name = var.name
                    if not self.symbol_table.lookup(var_name):
                        self.errors.append(f"Erro: Variável '{var_name}' não declarada para recebimento do canal")

    def analyze_if_statement(self, node):
        """Analisa estrutura if"""
        condition = getattr(node, 'condition', None)
        then_body = getattr(node, 'then_body', [])
        else_body = getattr(node, 'else_body', [])

        # Verifica condição
        condition_type = self.get_expression_type(condition)
        if condition_type != "BOOL":
            self.errors.append("Erro: Condição do if deve ser booleana")

        # Analisa then_body
        self.symbol_table.enter_scope()
        self.analyze_children(then_body)
        self.symbol_table.exit_scope()

        # Analisa else_body se existir
        if else_body:
            self.symbol_table.enter_scope()
            self.analyze_children(else_body)
            self.symbol_table.exit_scope()

    def analyze_block_statement(self, node):
        """Analisa bloco (seq/par)"""
        block_type = getattr(node, 'block_type', None)
        statements = getattr(node, 'statements', [])

        print(f"  Analisando bloco {block_type.upper()}")

        # Para blocos paralelos, verifica se as funções chamadas existem
        if block_type == "par":
            for stmt in statements:
                if self.is_function_call(stmt):
                    func_name = getattr(stmt, 'name', None)
                    if not self.lookup_function(func_name):
                        self.errors.append(f"Erro: Função '{func_name}' não declarada no bloco paralelo")

        self.symbol_table.enter_scope()
        try:
            self.analyze_children(statements)
        finally:
            self.symbol_table.exit_scope()

    def analyze_function_call(self, node):
        """Analisa chamada de função"""
        func_name = getattr(node, 'name', None)
        arguments = getattr(node, 'arguments', [])

        if not func_name:
            self.errors.append("Erro: Chamada de função sem nome")
            return None

        # Verifica se a função existe
        function = self.lookup_function(func_name)
        if not function:
            self.errors.append(f"Erro: Função '{func_name}' não declarada")
            return None

        # Verifica número de argumentos
        expected_params = getattr(function, 'parameters', [])
        if len(arguments) != len(expected_params):
            self.errors.append(f"Erro: Número incorreto de argumentos para '{func_name}' (esperado: {len(expected_params)}, recebido: {len(arguments)})")

        # Verifica tipos dos argumentos
        for i, (arg, expected_param) in enumerate(zip(arguments, expected_params)):
            arg_type = self.get_expression_type(arg)
            expected_type = getattr(expected_param, 'type', None)

            if arg_type and expected_type and not self.are_types_compatible(arg_type, expected_type):
                self.errors.append(f"Erro: Argumento {i+1} de '{func_name}' esperava {expected_type}, recebeu {arg_type}")

        return getattr(function, 'return_type', "VOID")

    def get_expression_type(self, expr) -> Optional[str]:
        """Obtém o tipo de uma expressão"""
        if not expr:
            return None

        # Expressão literal
        if hasattr(expr, 'value'):
            value = expr.value
            if isinstance(value, int):
                return "INT"
            elif isinstance(value, float):
                return "FLOAT"
            elif isinstance(value, str):
                # Tenta inferir o tipo da string
                if value.isdigit():
                    return "INT"
                try:
                    float(value)
                    return "FLOAT"
                except ValueError:
                    return "STRING"
            elif isinstance(value, bool):
                return "BOOL"
            else:
                return "STRING"  # Default para strings

        # Expressão binária
        elif hasattr(expr, 'left') and hasattr(expr, 'operator') and hasattr(expr, 'right'):
            left_type = self.get_expression_type(expr.left)
            right_type = self.get_expression_type(expr.right)
            operator = expr.operator

            if left_type is None or right_type is None:
                return None

            # Tabela de compatibilidade de operadores
            operator_compatibility = {
                '+': {
                    'INT': {'INT': 'INT', 'FLOAT': 'FLOAT'},
                    'FLOAT': {'INT': 'FLOAT', 'FLOAT': 'FLOAT'},
                    'STRING': {'STRING': 'STRING', 'INT': 'STRING', 'FLOAT': 'STRING'}  # Coerção implícita
                },
                '-': {
                    'INT': {'INT': 'INT', 'FLOAT': 'FLOAT'},
                    'FLOAT': {'INT': 'FLOAT', 'FLOAT': 'FLOAT'}
                },
                '*': {
                    'INT': {'INT': 'INT', 'FLOAT': 'FLOAT'},
                    'FLOAT': {'INT': 'FLOAT', 'FLOAT': 'FLOAT'}
                },
                '/': {
                    'INT': {'INT': 'FLOAT', 'FLOAT': 'FLOAT'},
                    'FLOAT': {'INT': 'FLOAT', 'FLOAT': 'FLOAT'}
                },
                '==': {'ANY': {'ANY': 'BOOL'}},
                '!=': {'ANY': {'ANY': 'BOOL'}},
                '<': {
                    'INT': {'INT': 'BOOL', 'FLOAT': 'BOOL'},
                    'FLOAT': {'INT': 'BOOL', 'FLOAT': 'BOOL'}
                },
                '>': {
                    'INT': {'INT': 'BOOL', 'FLOAT': 'BOOL'},
                    'FLOAT': {'INT': 'BOOL', 'FLOAT': 'BOOL'}
                }
            }

            if operator in operator_compatibility:
                if left_type in operator_compatibility[operator]:
                    if right_type in operator_compatibility[operator][left_type]:
                        return operator_compatibility[operator][left_type][right_type]
                    elif 'ANY' in operator_compatibility[operator][left_type]:
                        return operator_compatibility[operator][left_type]['ANY']
                elif 'ANY' in operator_compatibility[operator]:
                    return operator_compatibility[operator]['ANY']['ANY']

            self.errors.append(f"Erro: Operador '{operator}' não pode ser aplicado aos tipos {left_type} e {right_type}")
            return None

        # Identificador (variável)
        elif hasattr(expr, 'name'):
            var_name = expr.name
            var_info = self.symbol_table.lookup(var_name)
            if var_info:
                return var_info.symbol_type
            else:
                self.errors.append(f"Erro: Variável '{var_name}' não declarada")
                return None

        # Chamada de função
        elif self.is_function_call(expr):
            return self.analyze_function_call(expr)

        return None

    def is_valid_type(self, type_name: str) -> bool:
        """Verifica se um tipo é válido"""
        valid_types = ["INT", "FLOAT", "STRING", "BOOL", "VOID", "C_CHANNEL"]
        return type_name in valid_types

    def are_types_compatible(self, type1: str, type2: str) -> bool:
        """Verifica se dois tipos são compatíveis"""
        if type1 == type2:
            return True
        if type1 in ["INT", "FLOAT"] and type2 in ["INT", "FLOAT"]:
            return True
        return False

    # Métodos auxiliares para trabalhar com a SymbolTable existente

    def symbol_table_exists_current_scope(self, name: str) -> bool:
        """Verifica se um símbolo existe no escopo atual (sem modificar SymbolTable)"""
        try:
            # Acessa o escopo atual diretamente e verifica se o símbolo existe
            current_scope = self.symbol_table.current_scope
            return current_scope.exists(name)
        except:
            # Fallback: verifica se existe em qualquer escopo
            return self.symbol_table.exists(name)

    def lookup_function(self, name: str):
        """Busca uma função no registro local (sem modificar SymbolTable)"""
        return self.functions.get(name)

    def register_function(self, name: str, function_node):
        """Registra uma função no registro local (sem modificar SymbolTable)"""
        self.functions[name] = function_node

    def print_symbol_table(self):
        """Imprime o estado atual da tabela de símbolos"""
        print("\n" + "="*50)
        print("TABELA DE SÍMBOLOS - ESTADO FINAL")
        print("="*50)
        self.symbol_table.print_table()

    def print_functions(self):
        """Imprime as funções registradas"""
        print("\n" + "="*50)
        print("FUNÇÕES REGISTRADAS")
        print("="*50)
        for func_name, func_node in self.functions.items():
            return_type = getattr(func_node, 'return_type', 'VOID')
            params = getattr(func_node, 'parameters', [])
            param_str = ", ".join([f"{p.type} {p.identifier}" for p in params if hasattr(p, 'type') and hasattr(p, 'identifier')])
            print(f"  {func_name} : {return_type} ({param_str})")