"""
Gerador de Código de Três Endereços (Three-Address Code - TAC)
Para o interpretador MiniPar 2025.1

O TAC é uma representação intermediária onde cada instrução tem no máximo
três operandos, facilitando otimização e geração de código de máquina.
"""

from typing import List, Tuple, Optional, Any
from parser.AST import *


class TACInstruction:
    """Representa uma instrução de código de três endereços"""
    
    def __init__(self, op: str, arg1=None, arg2=None, result=None):
        self.op = op          # Operação: +, -, *, /, =, goto, if, call, etc
        self.arg1 = arg1      # Primeiro argumento
        self.arg2 = arg2      # Segundo argumento
        self.result = result  # Resultado/destino
    
    def __str__(self):
        if self.op == 'label':
            return f"{self.result}:"
        elif self.op == 'goto':
            return f"    goto {self.result}"
        elif self.op == 'ifFalse':
            return f"    if !{self.arg1} goto {self.result}"
        elif self.op == 'ifTrue':
            return f"    if {self.arg1} goto {self.result}"
        elif self.op == 'if':
            return f"    if {self.arg1} {self.arg2} goto {self.result}"
        elif self.op == 'param':
            return f"    param {self.arg1}"
        elif self.op == 'call':
            if self.result:
                return f"    {self.result} = call {self.arg1}, {self.arg2}"
            return f"    call {self.arg1}, {self.arg2}"
        elif self.op == 'return':
            if self.arg1:
                return f"    return {self.arg1}"
            return f"    return"
        elif self.op == '=':
            return f"    {self.result} = {self.arg1}"
        elif self.op == '[]':
            return f"    {self.result} = {self.arg1}[{self.arg2}]"
        elif self.op == '[]=':
            return f"    {self.result}[{self.arg1}] = {self.arg2}"
        elif self.op == 'new':
            return f"    {self.result} = new {self.arg1}()"
        elif self.op == '.':
            return f"    {self.result} = {self.arg1}.{self.arg2}"
        elif self.op == '.=':
            return f"    {self.arg1}.{self.arg2} = {self.result}"
        elif self.op == 'method_call':
            if self.result:
                return f"    {self.result} = {self.arg1}.{self.arg2}"
            return f"    {self.arg1}.{self.arg2}"
        elif self.op == 'nop':
            return f"    nop"
        elif self.op in ['+', '-', '*', '/', '==', '!=', '<', '>', '<=', '>=', '&&', '||']:
            return f"    {self.result} = {self.arg1} {self.op} {self.arg2}"
        elif self.op == 'neg':
            return f"    {self.result} = -{self.arg1}"
        elif self.op == 'not':
            return f"    {self.result} = !{self.arg1}"
        else:
            return f"    {self.op} {self.arg1} {self.arg2} {self.result}"
    
    def __repr__(self):
        return self.__str__()


class TACGenerator:
    """Gerador de Código de Três Endereços a partir da AST"""
    
    def __init__(self):
        self.instructions: List[TACInstruction] = []
        self.temp_count = 0
        self.label_count = 0
        self.current_function = None
        self.string_literals = {}  # Armazena strings literais
        self.string_count = 0
    
    def new_temp(self) -> str:
        """Gera uma nova variável temporária"""
        temp = f"t{self.temp_count}"
        self.temp_count += 1
        return temp
    
    def new_label(self) -> str:
        """Gera um novo rótulo"""
        label = f"L{self.label_count}"
        self.label_count += 1
        return label
    
    def emit(self, op: str, arg1=None, arg2=None, result=None):
        """Emite uma instrução TAC"""
        instruction = TACInstruction(op, arg1, arg2, result)
        self.instructions.append(instruction)
        return instruction
    
    def get_string_literal(self, value: str) -> str:
        """Registra e retorna identificador para string literal"""
        if value not in self.string_literals:
            str_id = f"str_{self.string_count}"
            self.string_literals[value] = str_id
            self.string_count += 1
        return self.string_literals[value]
    
    def generate(self, ast: ProgramNode) -> List[TACInstruction]:
        """Gera TAC para todo o programa"""
        self.instructions = []
        
        # Comentário inicial
        self.emit('label', result='# MiniPar TAC Code')
        self.emit('nop')
        
        # Processa declarações globais
        for child in ast.children:
            self.visit(child)
        
        return self.instructions
    
    def visit(self, node) -> Optional[str]:
        """Visita um nó da AST e retorna o temporário com resultado (se houver)"""
        if node is None:
            return None
        
        # Mapeia tipo do nó para método visitor
        node_type = type(node).__name__
        method_name = f'visit_{node_type}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node):
        """Visitor genérico para nós não implementados"""
        print(f"AVISO: Nó {type(node).__name__} não tem visitor específico")
        return None
    
    # ==================== DECLARAÇÕES ====================
    
    def visit_FunctionNode(self, node: FunctionNode):
        """Gera TAC para declaração de função"""
        func_name = node.name
        self.current_function = func_name
        
        # Label da função
        self.emit('label', result=f"\n# Function: {func_name}")
        self.emit('label', result=f"{func_name}")
        
        # Parâmetros
        for param in node.parameters:
            param_name = param.identifier if hasattr(param, 'identifier') else str(param)
            self.emit('param', arg1=param_name)
        
        # Corpo da função
        for stmt in node.body:
            self.visit(stmt)
        
        # Return implícito se void
        if not any(isinstance(stmt, ReturnNode) for stmt in node.body):
            self.emit('return')
        
        self.current_function = None
        self.emit('nop')
        return None
    
    def visit_ClassNode(self, node: ClassNode):
        """Gera TAC para declaração de classe"""
        class_name = node.name
        
        self.emit('label', result=f"\n# Class: {class_name}")
        
        # Se tem herança
        if node.parent:
            self.emit('label', result=f"# extends {node.parent}")
        
        # Atributos (apenas documentação)
        if node.attributes:
            self.emit('label', result=f"# Attributes:")
            for attr in node.attributes:
                self.emit('label', result=f"#   {attr.type_name} {attr.name}")
        
        # Métodos
        if node.methods:
            self.emit('label', result=f"# Methods:")
            for method in node.methods:
                self.visit(method)
        
        self.emit('nop')
        return None
    
    def visit_MethodNode(self, node: MethodNode):
        """Gera TAC para método de classe"""
        # Métodos são tratados como funções com prefixo da classe
        return self.visit_FunctionNode(node)
    
    def visit_VariableDeclarationNode(self, node):
        """Gera TAC para declaração de variável"""
        var_name = node.identifier
        
        # Se tem inicialização
        if hasattr(node, 'initial_value') and node.initial_value:
            value_temp = self.visit(node.initial_value)
            if value_temp:
                self.emit('=', arg1=value_temp, result=var_name)
        
        return var_name
    
    def visit_DeclarationNode(self, node):
        """Gera TAC para declaração de variável (alias)"""
        return self.visit_VariableDeclarationNode(node)
    
    # ==================== STATEMENTS ====================
    
    def visit_AssignmentNode(self, node):
        """Gera TAC para atribuição"""
        var_name = node.identifier
        value_temp = self.visit(node.expression)
        
        if value_temp:
            self.emit('=', arg1=value_temp, result=var_name)
        
        return None
    
    def visit_ArrayAssignmentNode(self, node):
        """Gera TAC para atribuição em array"""
        array_name = node.array_name
        index_temp = self.visit(node.index)
        value_temp = self.visit(node.expression)
        
        # array[index] = value
        self.emit('[]=', arg1=index_temp, arg2=value_temp, result=array_name)
        
        return None
    
    def visit_IfNode(self, node):
        """Gera TAC para if/else"""
        # Avalia condição
        cond_temp = self.visit(node.condition)
        
        label_else = self.new_label()
        label_end = self.new_label()
        
        # if !cond goto else
        self.emit('ifFalse', arg1=cond_temp, result=label_else)
        
        # Bloco then
        for stmt in node.then_body:
            self.visit(stmt)
        
        # goto end
        self.emit('goto', result=label_end)
        
        # Label else
        self.emit('label', result=label_else)
        
        # Bloco else (se houver)
        if node.else_body:
            for stmt in node.else_body:
                self.visit(stmt)
        
        # Label end
        self.emit('label', result=label_end)
        
        return None
    
    def visit_WhileNode(self, node):
        """Gera TAC para while"""
        label_start = self.new_label()
        label_end = self.new_label()
        
        # Label start
        self.emit('label', result=label_start)
        
        # Avalia condição
        cond_temp = self.visit(node.condition)
        
        # if !cond goto end
        self.emit('ifFalse', arg1=cond_temp, result=label_end)
        
        # Corpo do loop
        for stmt in node.body:
            self.visit(stmt)
        
        # goto start
        self.emit('goto', result=label_start)
        
        # Label end
        self.emit('label', result=label_end)
        
        return None
    
    def visit_ForNode(self, node):
        """Gera TAC para for loop"""
        # Inicialização
        self.visit(node.init_expr)
        
        label_start = self.new_label()
        label_end = self.new_label()
        
        # Label start
        self.emit('label', result=label_start)
        
        # Condição
        cond_temp = self.visit(node.condition)
        self.emit('ifFalse', arg1=cond_temp, result=label_end)
        
        # Corpo
        for stmt in node.body:
            self.visit(stmt)
        
        # Incremento
        self.visit(node.increment)
        
        # goto start
        self.emit('goto', result=label_start)
        
        # Label end
        self.emit('label', result=label_end)
        
        return None
    
    def visit_ReturnNode(self, node):
        """Gera TAC para return"""
        if node.expression:
            value_temp = self.visit(node.expression)
            self.emit('return', arg1=value_temp)
        else:
            self.emit('return')
        
        return None
    
    def visit_PrintNode(self, node):
        """Gera TAC para print"""
        value_temp = self.visit(node.expression)
        
        # param value
        self.emit('param', arg1=value_temp)
        
        # call print, 1
        self.emit('call', arg1='print', arg2=1)
        
        return None
    
    def visit_InputNode(self, node):
        """Gera TAC para input"""
        result_temp = self.new_temp()
        
        # Se tem prompt
        if hasattr(node, 'prompt') and node.prompt:
            prompt_temp = self.visit(node.prompt)
            self.emit('param', arg1=prompt_temp)
            self.emit('call', arg1='input', arg2=1, result=result_temp)
        else:
            self.emit('call', arg1='input', arg2=0, result=result_temp)
        
        return result_temp
    
    # ==================== BLOCOS PAR/SEQ ====================
    
    def visit_BlockNode(self, node):
        """Gera TAC para bloco genérico"""
        block_type = node.block_type if hasattr(node, 'block_type') else 'BLOCK'
        
        self.emit('label', result=f"\n# {block_type} block start")
        
        for stmt in node.statements:
            self.visit(stmt)
        
        self.emit('label', result=f"# {block_type} block end")
        return None
    
    def visit_ParallelBlockNode(self, node):
        """Gera TAC para bloco PAR"""
        self.emit('label', result=f"\n# PAR block start")
        
        for stmt in node.statements:
            self.visit(stmt)
        
        self.emit('label', result=f"# PAR block end")
        return None
    
    def visit_SequentialBlockNode(self, node):
        """Gera TAC para bloco SEQ"""
        self.emit('label', result=f"\n# SEQ block start")
        
        for stmt in node.statements:
            self.visit(stmt)
        
        self.emit('label', result=f"# SEQ block end")
        return None
    
    # ==================== EXPRESSÕES ====================
    
    def visit_BinaryOpNode(self, node):
        """Gera TAC para operação binária"""
        left_temp = self.visit(node.left)
        right_temp = self.visit(node.right)
        result_temp = self.new_temp()
        
        # result = left op right
        self.emit(node.operator, arg1=left_temp, arg2=right_temp, result=result_temp)
        
        return result_temp
    
    def visit_UnaryOpNode(self, node):
        """Gera TAC para operação unária"""
        operand_temp = self.visit(node.operand)
        result_temp = self.new_temp()
        
        if node.operator == '-':
            self.emit('neg', arg1=operand_temp, result=result_temp)
        elif node.operator == '!':
            self.emit('not', arg1=operand_temp, result=result_temp)
        
        return result_temp
    
    def visit_NumberNode(self, node):
        """Gera TAC para número literal"""
        temp = self.new_temp()
        self.emit('=', arg1=node.value, result=temp)
        return temp
    
    def visit_StringNode(self, node):
        """Gera TAC para string literal"""
        str_id = self.get_string_literal(node.value)
        temp = self.new_temp()
        self.emit('=', arg1=str_id, result=temp)
        return temp
    
    def visit_IdentifierNode(self, node):
        """Retorna o nome da variável"""
        return node.name
    
    def visit_ArrayAccessNode(self, node):
        """Gera TAC para acesso a array"""
        array_name = node.array_name
        index_temp = self.visit(node.index)
        result_temp = self.new_temp()
        
        # result = array[index]
        self.emit('[]', arg1=array_name, arg2=index_temp, result=result_temp)
        
        return result_temp
    
    def visit_FunctionCallNode(self, node):
        """Gera TAC para chamada de função"""
        func_name = node.name
        arguments = node.arguments if node.arguments else []
        
        # Avalia argumentos e gera param
        for arg in arguments:
            arg_temp = self.visit(arg)
            self.emit('param', arg1=arg_temp)
        
        # Chamada
        result_temp = self.new_temp()
        num_args = len(arguments)
        self.emit('call', arg1=func_name, arg2=num_args, result=result_temp)
        
        return result_temp
    
    def visit_MethodCallNode(self, node):
        """Gera TAC para chamada de método"""
        obj_name = node.object_name
        method_name = node.method_name
        arguments = node.arguments if node.arguments else []
        
        # Avalia argumentos
        for arg in arguments:
            arg_temp = self.visit(arg)
            self.emit('param', arg1=arg_temp)
        
        # Chamada de método
        result_temp = self.new_temp()
        num_args = len(arguments)
        method_call = f"{method_name}, {num_args}"
        self.emit('method_call', arg1=obj_name, arg2=method_call, result=result_temp)
        
        return result_temp
    
    def visit_AttributeAccessNode(self, node):
        """Gera TAC para acesso a atributo"""
        obj_name = node.object_name
        attr_name = node.attribute_name
        result_temp = self.new_temp()
        
        # result = obj.attr
        self.emit('.', arg1=obj_name, arg2=attr_name, result=result_temp)
        
        return result_temp
    
    def visit_InstantiationNode(self, node):
        """Gera TAC para instanciação de objeto"""
        class_name = node.class_name
        var_name = node.var_name
        result_temp = self.new_temp()
        
        # temp = new ClassName()
        self.emit('new', arg1=class_name, result=result_temp)
        
        # var = temp
        self.emit('=', arg1=result_temp, result=var_name)
        
        return result_temp
    
    # ==================== CANAIS ====================
    
    def visit_SendNode(self, node):
        """Gera TAC para send em canal"""
        channel_name = node.channel
        values = node.values if hasattr(node, 'values') else []
        
        # Avalia valores a enviar
        for value in values:
            value_temp = self.visit(value)
            self.emit('param', arg1=value_temp)
        
        # call channel.send, n
        num_values = len(values)
        self.emit('method_call', arg1=channel_name, arg2=f"send, {num_values}")
        
        return None
    
    def visit_ReceiveNode(self, node):
        """Gera TAC para receive em canal"""
        channel_name = node.channel
        variables = node.variables if hasattr(node, 'variables') else []
        
        # Prepara variáveis para receber
        for var in variables:
            self.emit('param', arg1=var)
        
        # call channel.receive, n
        num_vars = len(variables)
        self.emit('method_call', arg1=channel_name, arg2=f"receive, {num_vars}")
        
        return None
    
    # ==================== UTILITÁRIOS ====================
    
    def print_tac(self):
        """Imprime o código TAC gerado"""
        print("\n" + "="*80)
        print("THREE-ADDRESS CODE (TAC)")
        print("="*80)
        
        # Imprime strings literais
        if self.string_literals:
            print("\n# String Literals:")
            for value, str_id in self.string_literals.items():
                print(f'    {str_id} = "{value}"')
        
        print("\n# Code:")
        for instruction in self.instructions:
            print(instruction)
        
        print("\n" + "="*80)
    
    def to_string(self) -> str:
        """Retorna o TAC como string"""
        lines = []
        
        # Strings literais
        if self.string_literals:
            lines.append("# String Literals:")
            for value, str_id in self.string_literals.items():
                lines.append(f'    {str_id} = "{value}"')
            lines.append("")
        
        # Instruções
        lines.append("# Code:")
        for instruction in self.instructions:
            lines.append(str(instruction))
        
        return "\n".join(lines)
    
    def save_to_file(self, filename: str):
        """Salva o TAC em arquivo"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# MiniPar Three-Address Code (TAC)\n")
            f.write("# Generated automatically\n\n")
            f.write(self.to_string())
        
        print(f"TAC salvo em: {filename}")
