# ============================================================================
# AST.py - Árvore de Sintaxe Abstrata (Abstract Syntax Tree)
# ============================================================================
# Define todos os nós da AST que representam as construções da linguagem MiniPar.
# Cada nó armazena informações sobre uma estrutura sintática específica.
# ============================================================================

class ASTNode:
    """Classe base para todos os nós da AST."""
    pass


class ProgramNode(ASTNode):
    """Nó raiz do programa - contém todas as classes, funções e blocos."""
    def __init__(self):
        self.children = []  # Lista de nós filhos (classes, funções, blocos)


class CommentNode(ASTNode):
    """Representa um comentário no código."""
    def __init__(self, text):
        self.text = text  # Texto do comentário


class ClassNode(ASTNode):
    """Representa uma definição de classe com herança opcional."""
    def __init__(self, name, parent, attributes, methods):
        self.name = name              # Nome da classe
        self.parent = parent          # Nome da classe pai (ou None)
        self.attributes = attributes  # Lista de AttributeNode
        self.methods = methods        # Lista de MethodNode


class AttributeNode(ASTNode):
    """Representa um atributo de classe (pode ser array 1D ou 2D)."""
    def __init__(self, type_name, name, is_array=False, array_size=None, is_2d_array=False, array_dimensions=None):
        self.type_name = type_name           # Tipo do atributo (int, real, string, etc.)
        self.name = name                     # Nome do atributo
        self.is_array = is_array             # True se for array 1D
        self.array_size = array_size         # Tamanho do array 1D
        self.is_2d_array = is_2d_array       # True se for array 2D
        self.array_dimensions = array_dimensions  # [linhas, colunas] para array 2D


class MethodNode(ASTNode):
    """Representa um método dentro de uma classe."""
    def __init__(self, return_type, name, parameters, body):
        self.return_type = return_type  # Tipo de retorno do método
        self.name = name                # Nome do método
        self.parameters = parameters    # Lista de (tipo, nome) dos parâmetros
        self.body = body                # Lista de statements do corpo


class FunctionNode(ASTNode):
    """Representa uma função global (fora de classes)."""
    def __init__(self, return_type, name, parameters, body):
        self.return_type = return_type  # Tipo de retorno da função
        self.name = name                # Nome da função
        self.parameters = parameters    # Lista de (tipo, nome) dos parâmetros
        self.body = body                # Lista de statements do corpo


class BlockNode(ASTNode):
    """Representa um bloco SEQ (sequencial) ou PAR (paralelo)."""
    def __init__(self, block_type, statements):
        self.block_type = block_type  # "seq" ou "par"
        self.statements = statements  # Lista de statements a executar


class AssignmentNode(ASTNode):
    """Representa uma atribuição simples: var = expressão."""
    def __init__(self, identifier, expression):
        self.identifier = identifier  # Nome da variável
        self.expression = expression  # Expressão a atribuir


class IfNode(ASTNode):
    """Representa uma estrutura IF-ELSE."""
    def __init__(self, condition, then_body, else_body=None):
        self.condition = condition    # Condição a avaliar
        self.then_body = then_body    # Statements do bloco IF
        self.else_body = else_body    # Statements do bloco ELSE (opcional)


class WhileNode(ASTNode):
    """Representa um loop WHILE."""
    def __init__(self, condition, body):
        self.condition = condition  # Condição do loop
        self.body = body            # Statements do corpo do loop


class ForNode(ASTNode):
    """Representa um loop FOR com inicialização, condição e incremento."""
    def __init__(self, var, init_expr, condition, increment, body):
        self.var = var                # Variável de controle
        self.init_expr = init_expr    # Expressão de inicialização
        self.condition = condition    # Condição de continuação
        self.increment = increment    # Expressão de incremento
        self.body = body              # Statements do corpo do loop


class InstantiationNode(ASTNode):
    """Representa a criação de um objeto: TipoVar nome = new Classe()."""
    def __init__(self, type_name, var_name, class_name):
        self.type_name = type_name    # Tipo da variável
        self.var_name = var_name      # Nome da variável
        self.class_name = class_name  # Nome da classe a instanciar


class NewExpressionNode(ASTNode):
    """Representa uma expressão 'new Classe()' (criação inline de objeto)."""
    def __init__(self, class_name):
        self.class_name = class_name  # Nome da classe a instanciar


class ArrayElementMethodCallNode(ASTNode):
    """Representa chamada de método em elemento de array: arr[i].metodo()."""
    def __init__(self, array_access, method_name, arguments=None):
        self.array_access = array_access  # Nó ArrayAccessNode
        self.method_name = method_name    # Nome do método
        self.arguments = arguments if arguments else []  # Argumentos do método


class ArrayElementAttributeAssignmentNode(ASTNode):
    """Representa atribuição a atributo de objeto em array: arr[i].attr = valor."""
    def __init__(self, array_access, attribute_name, value):
        self.array_access = array_access    # Nó ArrayAccessNode
        self.attribute_name = attribute_name  # Nome do atributo
        self.value = value                   # Valor a atribuir


class ArrayElementAttributeAccessNode(ASTNode):
    """Representa acesso a atributo de objeto em array: arr[i].attr."""
    def __init__(self, array_access, attribute_name):
        self.array_access = array_access    # Nó ArrayAccessNode
        self.attribute_name = attribute_name  # Nome do atributo


class ArrayAccessWithObjectNode(ASTNode):
    """Representa acesso a array que é atributo de objeto: obj.arr[i] ou this.arr[i]."""
    def __init__(self, object_attr_access, index, index2=None):
        self.object_attr_access = object_attr_access  # Nó AttributeAccessNode
        self.index = index      # Índice primário
        self.index2 = index2    # Índice secundário (para arrays 2D)


class ObjectAttributeArrayAssignmentNode(ASTNode):
    """Representa atribuição a elemento de array que é atributo: obj.arr[i] = valor."""
    def __init__(self, object_name, attr_name, index, value, index2=None):
        self.object_name = object_name  # Nome do objeto
        self.attr_name = attr_name      # Nome do atributo array
        self.index = index              # Índice primário
        self.value = value              # Valor a atribuir
        self.index2 = index2            # Índice secundário (para arrays 2D)


class MethodCallNode(ASTNode):
    """Representa chamada de método: objeto.metodo(args)."""
    def __init__(self, object_name, method_name, arguments=None):
        self.object_name = object_name  # Nome do objeto
        self.method_name = method_name  # Nome do método
        self.arguments = arguments or []  # Lista de argumentos


class FunctionCallNode(ASTNode):
    """Representa chamada de função: funcao(args)."""
    def __init__(self, name, arguments=None):
        self.name = name  # Nome da função
        self.arguments = arguments or []  # Lista de argumentos


class PrintNode(ASTNode):
    """Representa comando PRINT(expressão)."""
    def __init__(self, expression):
        self.expression = expression  # Expressão a imprimir


class InputNode(ASTNode):
    """Representa comando INPUT para leitura de dados do usuário."""
    def __init__(self, identifier, prompt=None):
        self.identifier = identifier  # Variável que receberá o valor
        self.prompt = prompt         # Mensagem opcional (prompt)


class SendNode(ASTNode):
    """Representa envio de dados por canal: canal.SEND(valores)."""
    def __init__(self, channel, values):
        self.channel = channel  # Nome do canal
        self.values = values    # Lista de valores a enviar


class ReceiveNode(ASTNode):
    """Representa recebimento de dados por canal: canal.RECEIVE(variáveis)."""
    def __init__(self, channel, variables):
        self.channel = channel      # Nome do canal
        self.variables = variables  # Lista de variáveis que receberão valores


class ReturnNode(ASTNode):
    """Representa comando RETURN em funções."""
    def __init__(self, expression):
        self.expression = expression  # Expressão a retornar


class BinaryOpNode(ASTNode):
    """Representa operação binária: left operador right (+, -, *, /, &&, ||)."""
    def __init__(self, left, operator, right):
        self.left = left          # Operando esquerdo
        self.operator = operator  # Operador (+, -, *, /, &&, ||)
        self.right = right        # Operando direito


class UnaryOpNode(ASTNode):
    """Representa operação unária: operador operando (ex: -5)."""
    def __init__(self, operator, operand):
        self.operator = operator  # Operador unário (-, !)
        self.operand = operand    # Operando


class NumberNode(ASTNode):
    """Representa um número literal (inteiro ou real)."""
    def __init__(self, value):
        self.value = value  # Valor numérico


class StringNode(ASTNode):
    """Representa uma string literal."""
    def __init__(self, value):
        self.value = value  # Valor da string


class IdentifierNode(ASTNode):
    """Representa um identificador (nome de variável, função, etc.)."""
    def __init__(self, name):
        self.name = name  # Nome do identificador


class AttributeAccessNode(ASTNode):
    """Representa acesso a atributo de objeto: objeto.atributo."""
    def __init__(self, object_name, attribute_name):
        self.object_name = object_name      # Nome do objeto
        self.attribute_name = attribute_name  # Nome do atributo


class AttributeAssignmentNode(ASTNode):
    """Representa atribuição a atributo: objeto.atributo = expressão."""
    def __init__(self, object_name, attribute_name, expression):
        self.object_name = object_name      # Nome do objeto
        self.attribute_name = attribute_name  # Nome do atributo
        self.expression = expression        # Expressão a atribuir


class ConditionNode(ASTNode):
    """Representa uma condição: left operador right (==, !=, <, >, <=, >=)."""
    def __init__(self, left, operator, right):
        self.left = left          # Lado esquerdo
        self.operator = operator  # Operador relacional
        self.right = right        # Lado direito


class DeclarationNode(ASTNode):
    """Representa declaração de variável com inicialização opcional."""
    def __init__(self, type_name, identifier, initial_value=None, is_array=False, array_size=None, is_2d_array=False, array_dimensions=None):
        self.type_name = type_name          # Tipo da variável
        self.identifier = identifier        # Nome da variável
        self.initial_value = initial_value  # Valor inicial (opcional)
        self.is_array = is_array            # True se for array 1D
        self.array_size = array_size        # Tamanho do array 1D
        self.is_2d_array = is_2d_array      # True se for array 2D
        self.array_dimensions = array_dimensions  # [linhas, colunas] para arrays 2D


class ArrayAccessNode(ASTNode):
    """Representa acesso a elemento de array: arr[i] ou arr[i][j]."""
    def __init__(self, array_name, index, index2=None):
        self.array_name = array_name  # Nome do array
        self.index = index            # Índice primário
        self.index2 = index2          # Índice secundário (para arrays 2D)


class ArrayAssignmentNode(ASTNode):
    """Representa atribuição a elemento de array: arr[i] = expr ou arr[i][j] = expr."""
    def __init__(self, array_name, index, expression, index2=None):
        self.array_name = array_name  # Nome do array
        self.index = index            # Índice primário
        self.expression = expression  # Expressão a atribuir
        self.index2 = index2          # Índice secundário (para arrays 2D)


class ArrayInitNode(ASTNode):
    """Representa inicialização de array com colchetes: [val1, val2, ...]."""
    def __init__(self, elements):
        self.elements = elements  # Lista de elementos


class BraceInitNode(ASTNode):
    """Representa inicialização com chaves: {val1, val2, ...}."""
    def __init__(self, values):
        self.values = values  # Lista de valores
