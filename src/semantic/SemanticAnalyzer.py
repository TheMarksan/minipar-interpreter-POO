# ============================================================================
# SemanticAnalyzer.py - Analisador Semântico Completo Corrigido
# ============================================================================

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from parser.AST import *
from symbol_table.SymbolTable import SymbolTable

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
        self.warnings = []
        self.current_class = None
        self.current_function = None
        self.current_method = None
        self.current_return_type = None
        self.declared_variables = set()
        self.used_variables = set()
        self.array_info = {}

    def analyze(self, ast_node):
        """Inicia a análise semântica do programa."""
        try:
            self._add_builtin_symbols()
            self.visit(ast_node)
            self._check_undeclared_variables()

            return {
                'success': len(self.errors) == 0,
                'errors': self.errors,
                'warnings': self.warnings,
                'statistics': {
                    'total_errors': len(self.errors),
                    'total_warnings': len(self.warnings),
                    'declared_variables': len(self.declared_variables),
                    'used_variables': len(self.used_variables)
                }
            }
        except Exception as e:
            self.errors.append(f"Erro fatal durante análise semântica: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'errors': self.errors,
                'warnings': self.warnings,
                'statistics': {
                    'total_errors': len(self.errors),
                    'total_warnings': len(self.warnings),
                    'declared_variables': len(self.declared_variables),
                    'used_variables': len(self.used_variables)
                }
            }

    def _add_builtin_symbols(self):
        """Adiciona símbolos built-in na tabela."""
        # Tipos básicos em maiúsculas e minúsculas
        builtin_types = ['int', 'float', 'string', 'bool', 'char', 'void',
                        'INT', 'FLOAT', 'STRING', 'BOOL', 'CHAR', 'VOID']
        for type_name in builtin_types:
            self.symbol_table.define(type_name, "type")

        # Funções built-in
        builtin_functions = [
            ('strlen', 'int', [('string', 'str')]),
            ('substr', 'string', [('string', 'str'), ('int', 'start'), ('int', 'length')]),
            ('charat', 'string', [('string', 'str'), ('int', 'index')]),
            ('indexof', 'int', [('string', 'str'), ('string', 'ch')]),
            ('parseint', 'int', [('string', 'str')]),
            ('print', 'void', [('string', 'message')]),
            ('input', 'string', [])
        ]

        for name, return_type, params in builtin_functions:
            self.symbol_table.define_function(name, return_type, params)

    def _check_undeclared_variables(self):
        """Verifica se há variáveis usadas mas não declaradas."""
        for var_name in self.used_variables:
            if (var_name not in self.declared_variables and
                not self._is_builtin_function(var_name) and
                not self.symbol_table.exists(var_name)):
                self.error(f"Variável '{var_name}' não declarada")

    def _is_builtin_function(self, name):
        """Verifica se é uma função built-in."""
        builtins = ['strlen', 'substr', 'charat', 'indexof', 'parseint', 'print', 'input']
        return name in builtins

    def visit(self, node):
        """Método principal de visitação dos nós da AST."""
        if node is None:
            return None

        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        print(f"DEBUG: Visitando {method_name}")
        return visitor(node)


    def generic_visit(self, node):
        """Visita genérica para nós sem método específico."""
        for attr_name in dir(node):
            if not attr_name.startswith('_'):
                attr_value = getattr(node, attr_name)
                if isinstance(attr_value, list):
                    for item in attr_value:
                        if isinstance(item, ASTNode):
                            self.visit(item)
                elif isinstance(attr_value, ASTNode):
                    self.visit(attr_value)
        return None

    def error(self, message, node=None):
        """Registra um erro semântico."""
        self.errors.append(f"ERRO SEMÂNTICO: {message}")

    def warning(self, message, node=None):
        """Registra um aviso semântico."""
        self.warnings.append(f"AVISO: {message}")

    def _normalize_type(self, type_name):
        """Normaliza nomes de tipos para minúsculas."""
        if type_name is None:
            return None
        return type_name.lower()

    def _is_valid_type(self, type_name):
        """Verifica se um tipo é válido."""
        if type_name is None:
            return False

        normalized_type = self._normalize_type(type_name)
        basic_types = ['int', 'float', 'string', 'bool', 'char', 'void']

        if normalized_type in basic_types:
            return True

        # Verificar se é uma classe
        symbol = self.symbol_table.lookup(type_name)
        if symbol and symbol.is_class:
            return True

        return False

    def _is_assignable(self, target_type, source_type):
        """Verifica se source_type pode ser atribuído a target_type."""
        if target_type is None or source_type is None:
            return True

        normalized_target = self._normalize_type(target_type)
        normalized_source = self._normalize_type(source_type)

        if normalized_target == normalized_source:
            return True

        # Conversões implícitas permitidas
        if normalized_target == 'float' and normalized_source == 'int':
            return True

        # String pode receber qualquer tipo (para concatenação)
        if normalized_target == 'string':
            return True

        # Verificar herança de classes
        if (self.symbol_table.exists(normalized_target) and
            self.symbol_table.exists(normalized_source)):
            target_symbol = self.symbol_table.lookup(normalized_target)
            source_symbol = self.symbol_table.lookup(normalized_source)
            if target_symbol and source_symbol and target_symbol.is_class and source_symbol.is_class:
                # Verificar se source é subtipo de target
                current = normalized_source
                while current:
                    class_symbol = self.symbol_table.lookup(current)
                    if not class_symbol or not class_symbol.is_class:
                        break
                    if class_symbol.value and class_symbol.value.get('parent') == normalized_target:
                        return True
                    current = class_symbol.value.get('parent') if class_symbol.value else None

        return False

    # ============================================================================
    # MÉTODOS DE VISITAÇÃO
    # ============================================================================

    def visit_ProgramNode(self, node):
        """Analisa o programa completo."""
        for child in node.children:
            self.visit(child)

    def visit_ClassNode(self, node):
        """Analisa declaração de classe."""
        if self.symbol_table.exists(node.name):
            self.error(f"Classe '{node.name}' já declarada", node)
            return

        # Adicionar classe à tabela de símbolos
        self.symbol_table.define_class(node.name, node.attributes, node.methods, node.parent)

        # Entrar no escopo da classe
        old_class = self.current_class
        self.current_class = node.name
        self.symbol_table.enter_scope()

        # Analisar atributos
        for attr in node.attributes:
            self.visit(attr)

        # Analisar métodos
        for method in node.methods:
            self.visit(method)

        # Sair do escopo da classe
        self.symbol_table.exit_scope()
        self.current_class = old_class

    def visit_AttributeNode(self, node):
        """Analisa atributo de classe."""
        if not self._is_valid_type(node.type_name):
            self.error(f"Tipo '{node.type_name}' não é válido", node)

        # Definir atributo na tabela de símbolos
        is_array = node.is_array or node.is_2d_array
        array_size = node.array_size

        if node.is_2d_array:
            self.array_info[node.name] = {
                'is_2d': True,
                'dimensions': node.array_dimensions
            }

        self.symbol_table.define(
            node.name,
            node.type_name,
            is_array=is_array,
            array_size=array_size
        )
        self.declared_variables.add(node.name)

    def visit_MethodNode(self, node):
        """Analisa método de classe."""
        if not self._is_valid_type(node.return_type):
            self.error(f"Tipo de retorno '{node.return_type}' não é válido", node)

        # Entrar no escopo do método
        old_function = self.current_function
        old_method = self.current_method
        old_return_type = self.current_return_type

        self.current_function = node.name
        self.current_method = node.name
        self.current_return_type = node.return_type
        self.symbol_table.enter_scope()

        # Adicionar parâmetros na tabela
        for param_type, param_name in node.parameters:
            if not self._is_valid_type(param_type):
                self.error(f"Tipo de parâmetro '{param_type}' não é válido", node)
            self.symbol_table.define(param_name, param_type)
            self.declared_variables.add(param_name)

        # Adicionar 'this' implícito para métodos
        if self.current_class:
            self.symbol_table.define('this', self.current_class)
            self.declared_variables.add('this')

        # Analisar corpo do método
        for statement in node.body:
            self.visit(statement)

        # Sair do escopo do método
        self.symbol_table.exit_scope()
        self.current_function = old_function
        self.current_method = old_method
        self.current_return_type = old_return_type

    def visit_FunctionNode(self, node):
        """Analisa função global."""
        if self.symbol_table.exists(node.name):
            self.error(f"Função '{node.name}' já declarada", node)
            return

        if not self._is_valid_type(node.return_type):
            self.error(f"Tipo de retorno '{node.return_type}' não é válido", node)

        # Adicionar função na tabela
        self.symbol_table.define_function(
            node.name,
            node.return_type,
            node.parameters
        )

        # Entrar no escopo da função
        old_function = self.current_function
        old_return_type = self.current_return_type

        self.current_function = node.name
        self.current_return_type = node.return_type
        self.symbol_table.enter_scope()

        # Adicionar parâmetros na tabela
        for param_type, param_name in node.parameters:
            if not self._is_valid_type(param_type):
                self.error(f"Tipo de parâmetro '{param_type}' não é válido", node)
            self.symbol_table.define(param_name, param_type)
            self.declared_variables.add(param_name)

        # Analisar corpo da função
        for statement in node.body:
            self.visit(statement)

        # Sair do escopo da função
        self.symbol_table.exit_scope()
        self.current_function = old_function
        self.current_return_type = old_return_type

    def visit_BlockNode(self, node):
        """Analisa bloco SEQ ou PAR."""
        self.symbol_table.enter_scope()
        for stmt in node.statements:
            self.visit(stmt)
        self.symbol_table.exit_scope()
        return None

    def visit_DeclarationNode(self, node):
        """Analisa declaração de variável."""
        if self.symbol_table.exists(node.identifier):
            self.error(f"Variável '{node.identifier}' já declarada", node)
            return

        # Registrar variável declarada
        self.declared_variables.add(node.identifier)

        # Verificar tipo
        if not self._is_valid_type(node.type_name):
            self.error(f"Tipo '{node.type_name}' não é válido", node)
            return

        # Definir variável
        is_array = node.is_array or node.is_2d_array
        array_size = node.array_size

        if node.is_2d_array:
            self.array_info[node.identifier] = {
                'is_2d': True,
                'dimensions': node.array_dimensions
            }

        self.symbol_table.define(
            node.identifier,
            node.type_name,
            is_array=is_array,
            array_size=array_size
        )

        # Verificar inicialização
        if node.initial_value:
            initial_type = self.visit(node.initial_value)
            if initial_type and not self._is_assignable(node.type_name, initial_type):
                self.error(f"Tipo incompatível na inicialização de '{node.identifier}'. Esperado: {node.type_name}, Encontrado: {initial_type}", node)

    def visit_AssignmentNode(self, node):
        """Analisa atribuição simples."""
        self.used_variables.add(node.identifier)

        # Verificar se variável existe
        var_symbol = self.symbol_table.lookup(node.identifier)
        if not var_symbol:
            self.error(f"Variável '{node.identifier}' não declarada", node)
            return None

        # Verificar tipo da expressão
        expr_type = self.visit(node.expression)
        if expr_type and not self._is_assignable(var_symbol.symbol_type, expr_type):
            # Se o alvo é string, permitir qualquer atribuição (para concatenação)
            if self._normalize_type(var_symbol.symbol_type) != 'string':
                self.error(f"Tipo incompatível na atribuição para '{node.identifier}'. Esperado: {var_symbol.symbol_type}, Encontrado: {expr_type}", node)

        return var_symbol.symbol_type

    def visit_ArrayAssignmentNode(self, node):
        """Analisa atribuição a array."""
        self.used_variables.add(node.array_name)

        # Verificar se array existe
        array_symbol = self.symbol_table.lookup(node.array_name)
        if not array_symbol:
            self.error(f"Array '{node.array_name}' não declarado", node)
            return None

        # Verificar índices
        index_type = self.visit(node.index)
        if index_type and not self._is_assignable('int', index_type):
            self.error(f"Índice do array deve ser inteiro, encontrado: {index_type}", node)

        if node.index2:
            index2_type = self.visit(node.index2)
            if index2_type and not self._is_assignable('int', index2_type):
                self.error(f"Segundo índice do array deve ser inteiro, encontrado: {index2_type}", node)

        # Verificar tipo da expressão
        expr_type = self.visit(node.expression)
        if expr_type and not self._is_assignable(array_symbol.symbol_type, expr_type):
            self.error(f"Tipo incompatível na atribuição ao array '{node.array_name}'. Esperado: {array_symbol.symbol_type}, Encontrado: {expr_type}", node)

        return array_symbol.symbol_type

    def visit_IfNode(self, node):
        """Analisa estrutura if-else."""
        # Verificar condição
        cond_type = self.visit(node.condition)
        if cond_type and not self._is_assignable('bool', cond_type):
            self.error(f"Condição do IF deve ser booleana, encontrado: {cond_type}", node)

        # Analisar bloco then
        self.symbol_table.enter_scope()
        for stmt in node.then_body:
            self.visit(stmt)
        self.symbol_table.exit_scope()

        # Analisar bloco else se existir
        if node.else_body:
            self.symbol_table.enter_scope()
            for stmt in node.else_body:
                self.visit(stmt)
            self.symbol_table.exit_scope()

    def visit_WhileNode(self, node):
        """Analisa loop while."""
        # Verificar condição
        cond_type = self.visit(node.condition)
        if cond_type and not self._is_assignable('bool', cond_type):
            self.error(f"Condição do WHILE deve ser booleana, encontrado: {cond_type}", node)

        # Analisar corpo
        self.symbol_table.enter_scope()
        for stmt in node.body:
            self.visit(stmt)
        self.symbol_table.exit_scope()

    def visit_ForNode(self, node):
        """Analisa loop for."""
        self.used_variables.add(node.var)

        # Verificar variável de controle
        if not self.symbol_table.exists(node.var):
            self.error(f"Variável de controle '{node.var}' não declarada", node)

        # Verificar expressão de inicialização
        init_type = self.visit(node.init_expr)

        # Verificar condição
        cond_type = self.visit(node.condition)
        if cond_type and not self._is_assignable('bool', cond_type):
            self.error(f"Condição do FOR deve ser booleana, encontrado: {cond_type}", node)

        # Verificar incremento
        self.visit(node.increment)

        # Analisar corpo
        self.symbol_table.enter_scope()
        for stmt in node.body:
            self.visit(stmt)
        self.symbol_table.exit_scope()

    def visit_InstantiationNode(self, node):
        """Analisa criação de objeto."""
        if node.type_name and not self._is_valid_type(node.type_name):
            self.error(f"Tipo '{node.type_name}' não é válido", node)

        if not self._is_valid_type(node.class_name):
            self.error(f"Classe '{node.class_name}' não declarada", node)

        self.declared_variables.add(node.var_name)

        # Definir a variável do objeto
        self.symbol_table.define(node.var_name, node.class_name)

        return node.class_name

    def visit_NewExpressionNode(self, node):
        """Analisa expressão 'new'."""
        if not self._is_valid_type(node.class_name):
            self.error(f"Classe '{node.class_name}' não declarada", node)

        return node.class_name

    def visit_MethodCallNode(self, node):
        """Analisa chamada de método."""
        self.used_variables.add(node.object_name)

        # Verificar se objeto existe
        obj_symbol = self.symbol_table.lookup(node.object_name)
        if not obj_symbol:
            self.error(f"Objeto '{node.object_name}' não declarado", node)
            return None

        # Buscar método na classe do objeto
        method_info = self._find_method(obj_symbol.symbol_type, node.method_name)
        if not method_info:
            self.error(f"Método '{node.method_name}' não encontrado no objeto '{node.object_name}'", node)
            return None

        # Verificar argumentos
        expected_params = method_info['parameters']
        if len(node.arguments) != len(expected_params):
            self.error(f"Número incorreto de argumentos para '{node.method_name}'. Esperado: {len(expected_params)}, Encontrado: {len(node.arguments)}", node)
        else:
            for i, (arg, (expected_type, param_name)) in enumerate(zip(node.arguments, expected_params)):
                arg_type = self.visit(arg)
                if arg_type and not self._is_assignable(expected_type, arg_type):
                    self.error(f"Tipo incompatível no argumento {i+1} de '{node.method_name}'. Esperado: {expected_type}, Encontrado: {arg_type}", node)

        return method_info['return_type']

    def visit_FunctionCallNode(self, node):
        """Analisa chamada de função."""
        self.used_variables.add(node.name)

        # Verificar se função existe
        func_symbol = self.symbol_table.lookup(node.name)
        if not func_symbol or not func_symbol.is_function:
            if not self._is_builtin_function(node.name):
                self.error(f"Função '{node.name}' não declarada", node)
            return None

        # Verificar argumentos
        expected_params = func_symbol.parameters
        if len(node.arguments) != len(expected_params):
            self.error(f"Número incorreto de argumentos para '{node.name}'. Esperado: {len(expected_params)}, Encontrado: {len(node.arguments)}", node)
        else:
            for i, (arg, (expected_type, param_name)) in enumerate(zip(node.arguments, expected_params)):
                arg_type = self.visit(arg)
                if arg_type and not self._is_assignable(expected_type, arg_type):
                    self.error(f"Tipo incompatível no argumento {i+1} de '{node.name}'. Esperado: {expected_type}, Encontrado: {arg_type}", node)

        return func_symbol.return_type

    def visit_PrintNode(self, node):
        """Analisa comando print."""
        self.visit(node.expression)
        return None

    def visit_InputNode(self, node):
        """Analisa comando input."""
        self.used_variables.add(node.identifier)

        # Verificar se variável existe
        var_symbol = self.symbol_table.lookup(node.identifier)
        if not var_symbol:
            self.error(f"Variável '{node.identifier}' não declarada", node)

        # Verificar prompt se existir
        if node.prompt:
            self.visit(node.prompt)

        return 'string'

    def visit_ReturnNode(self, node):
        """Analisa comando return."""
        if not self.current_function and not self.current_method:
            self.error("Comando RETURN fora de função/método", node)
            return

        if node.expression:
            expr_type = self.visit(node.expression)
            if expr_type and self.current_return_type and not self._is_assignable(self.current_return_type, expr_type):
                self.error(f"Tipo de retorno incompatível. Esperado: {self.current_return_type}, Encontrado: {expr_type}", node)
        elif self.current_return_type and not self._is_assignable(self.current_return_type, 'void'):
            self.error(f"Função/método deve retornar valor do tipo {self.current_return_type}", node)

    def visit_BinaryOpNode(self, node):
        """Analisa operação binária."""
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if not left_type or not right_type:
            return None

        left_normalized = self._normalize_type(left_type)
        right_normalized = self._normalize_type(right_type)

        # Operações aritméticas
        if node.operator in ['+', '-', '*', '/', '%']:
            # CORREÇÃO: Permitir string + qualquer tipo (concatenação)
            if node.operator == '+' and (left_normalized == 'string' or right_normalized == 'string'):
                return 'string'

            if left_normalized in ['int', 'float'] and right_normalized in ['int', 'float']:
                # Se um dos tipos é float, o resultado é float
                if 'float' in [left_normalized, right_normalized]:
                    return 'float'
                return 'int'
            else:
                self.error(f"Operação {node.operator} não suportada entre {left_type} e {right_type}", node)
                return None

        # Operações lógicas
        elif node.operator in ['&&', '||']:
            if left_normalized == 'bool' and right_normalized == 'bool':
                return 'bool'
            else:
                self.error(f"Operação {node.operator} requer booleanos, encontrado: {left_type} e {right_type}", node)
                return None

        # Operações de comparação
        elif node.operator in ['==', '!=', '<', '>', '<=', '>=']:
            if (left_normalized in ['int', 'float'] and right_normalized in ['int', 'float']) or \
               (left_normalized == 'string' and right_normalized == 'string' and node.operator in ['==', '!=']):
                return 'bool'
            else:
                self.error(f"Comparação {node.operator} não suportada entre {left_type} e {right_type}", node)
                return None

        return None

    def visit_UnaryOpNode(self, node):
        """Analisa operação unária."""
        operand_type = self.visit(node.operand)
        if not operand_type:
            return None

        operand_normalized = self._normalize_type(operand_type)

        if node.operator == '-':
            if operand_normalized in ['int', 'float']:
                return operand_type
            else:
                self.error(f"Operador unário '-' requer tipo numérico, encontrado: {operand_type}", node)
                return None
        elif node.operator == '!':
            if operand_normalized == 'bool':
                return 'bool'
            else:
                self.error(f"Operador unário '!' requer tipo booleano, encontrado: {operand_type}", node)
                return None

        return operand_type

    def visit_ConditionNode(self, node):
        """Analisa condição."""
        self.visit(node.left)
        self.visit(node.right)
        return 'bool'

    def visit_NumberNode(self, node):
        """Analisa número literal."""
        value_str = str(node.value)
        if '.' in value_str:
            return 'float'
        return 'int'

    def visit_StringNode(self, node):
        """Analisa string literal."""
        return 'string'

    def visit_IdentifierNode(self, node):
        """Analisa identificador."""
        self.used_variables.add(node.name)

        symbol = self.symbol_table.lookup(node.name)
        if not symbol:
            if not self._is_builtin_function(node.name):
                self.error(f"Identificador '{node.name}' não declarado", node)
            return None
        return symbol.symbol_type

    def visit_AttributeAccessNode(self, node):
        """Analisa acesso a atributo de objeto."""
        self.used_variables.add(node.object_name)

        # Verificar objeto
        obj_symbol = self.symbol_table.lookup(node.object_name)
        if not obj_symbol:
            self.error(f"Objeto '{node.object_name}' não declarado", node)
            return None

        # Buscar atributo na classe
        attribute_info = self._find_attribute(obj_symbol.symbol_type, node.attribute_name)
        if not attribute_info:
            self.error(f"Atributo '{node.attribute_name}' não encontrado no objeto '{node.object_name}'", node)
            return None

        return attribute_info['type']

    def visit_AttributeAssignmentNode(self, node):
        """Analisa atribuição a atributo."""
        self.used_variables.add(node.object_name)

        # Verificar objeto
        obj_symbol = self.symbol_table.lookup(node.object_name)
        if not obj_symbol:
            self.error(f"Objeto '{node.object_name}' não declarado", node)
            return None

        # Buscar atributo na classe
        attribute_info = self._find_attribute(obj_symbol.symbol_type, node.attribute_name)
        if not attribute_info:
            self.error(f"Atributo '{node.attribute_name}' não encontrado no objeto '{node.object_name}'", node)
            return None

        # Verificar tipo da expressão
        expr_type = self.visit(node.expression)
        if expr_type and not self._is_assignable(attribute_info['type'], expr_type):
            self.error(f"Tipo incompatível na atribuição ao atributo '{node.attribute_name}'. Esperado: {attribute_info['type']}, Encontrado: {expr_type}", node)

        return attribute_info['type']

    def visit_ArrayAccessNode(self, node):
        """Analisa acesso a elemento de array."""
        self.used_variables.add(node.array_name)

        # Verificar se array existe
        array_symbol = self.symbol_table.lookup(node.array_name)
        if not array_symbol:
            self.error(f"Array '{node.array_name}' não declarado", node)
            return None

        # Verificar índices
        index_type = self.visit(node.index)
        if index_type and not self._is_assignable('int', index_type):
            self.error(f"Índice do array deve ser inteiro, encontrado: {index_type}", node)

        if node.index2:
            index2_type = self.visit(node.index2)
            if index2_type and not self._is_assignable('int', index2_type):
                self.error(f"Segundo índice do array deve ser inteiro, encontrado: {index2_type}", node)

        # Retornar tipo base do array
        return array_symbol.symbol_type

    def visit_ArrayInitNode(self, node):
        """Analisa inicialização de array com colchetes."""
        if not node.elements:
            return 'array'

        # Verificar elementos
        for element in node.elements:
            self.visit(element)

        return 'array'

    def visit_BraceInitNode(self, node):
        """Analisa inicialização com chaves."""
        for value in node.values:
            self.visit(value)
        return 'object'

    # Métodos para acesso a array com objetos (simplificados)
    def visit_ArrayElementMethodCallNode(self, node):
        self.visit(node.array_access)
        for arg in node.arguments:
            self.visit(arg)
        return 'object'

    def visit_ArrayElementAttributeAssignmentNode(self, node):
        self.visit(node.array_access)
        self.visit(node.value)
        return 'object'

    def visit_ArrayElementAttributeAccessNode(self, node):
        self.visit(node.array_access)
        return 'object'

    def visit_ArrayAccessWithObjectNode(self, node):
        self.visit(node.object_attr_access)
        self.visit(node.index)
        if node.index2:
            self.visit(node.index2)
        return 'object'

    def visit_ObjectAttributeArrayAssignmentNode(self, node):
        self.used_variables.add(node.object_name)
        self.visit(node.index)
        if node.index2:
            self.visit(node.index2)
        self.visit(node.value)
        return 'object'

    def visit_SendNode(self, node):
        self.used_variables.add(node.channel)
        for value in node.values:
            self.visit(value)
        return None

    def visit_ReceiveNode(self, node):
        self.used_variables.add(node.channel)
        for var in node.variables:
            self.used_variables.add(var)
        return None

    # ============================================================================
    # MÉTODOS AUXILIARES
    # ============================================================================

    def _find_method(self, class_name, method_name):
        """Encontra um método em uma classe, considerando herança."""
        current_class = class_name
        while current_class:
            class_symbol = self.symbol_table.lookup(current_class)
            if not class_symbol or not class_symbol.is_class:
                break

            # Buscar método na classe atual
            for method in class_symbol.value['methods']:
                if method.name == method_name:
                    return {
                        'return_type': method.return_type,
                        'parameters': method.parameters
                    }

            # Buscar na classe pai
            current_class = class_symbol.value['parent']

        return None

    def _find_attribute(self, class_name, attribute_name):
        """Encontra um atributo em uma classe, considerando herança."""
        current_class = class_name
        while current_class:
            class_symbol = self.symbol_table.lookup(current_class)
            if not class_symbol or not class_symbol.is_class:
                break

            # Buscar atributo na classe atual
            for attr in class_symbol.value['attributes']:
                if attr.name == attribute_name:
                    return {
                        'type': attr.type_name,
                        'is_array': attr.is_array,
                        'is_2d_array': attr.is_2d_array
                    }

            # Buscar na classe pai
            current_class = class_symbol.value['parent']

        return None

    def print_analysis_report(self):
        """Imprime um relatório completo da análise semântica."""
        print("\n" + "="*60)
        print("RELATÓRIO DA ANÁLISE SEMÂNTICA")
        print("="*60)

        if self.warnings:
            print(f"\nAVISOS ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
        else:
            print("\n✅ Nenhum aviso encontrado.")

        if self.errors:
            print(f"\nERROS ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        else:
            print("\n✅ Nenhum erro semântico encontrado!")

        print(f"\n📊 Estatísticas:")
        print(f"   - Variáveis declaradas: {len(self.declared_variables)}")
        print(f"   - Variáveis utilizadas: {len(self.used_variables)}")
        print(f"   - Avisos: {len(self.warnings)}")
        print(f"   - Erros: {len(self.errors)}")

        print("\n" + "="*60)

    def get_analysis_report(self):
        """Retorna um dicionário com o relatório completo."""
        return {
            'success': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'statistics': {
                'total_errors': len(self.errors),
                'total_warnings': len(self.warnings),
                'declared_variables': len(self.declared_variables),
                'used_variables': len(self.used_variables)
            }
        }