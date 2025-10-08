class ASTNode:
    pass


class ProgramNode(ASTNode):
    def __init__(self):
        self.children = []


class CommentNode(ASTNode):
    def __init__(self, text):
        self.text = text


class ClassNode(ASTNode):
    def __init__(self, name, parent, attributes, methods):
        self.name = name
        self.parent = parent
        self.attributes = attributes
        self.methods = methods


class AttributeNode(ASTNode):
    def __init__(self, type_name, name, is_array=False, array_size=None, is_2d_array=False, array_dimensions=None):
        self.type_name = type_name
        self.name = name
        self.is_array = is_array
        self.array_size = array_size
        self.is_2d_array = is_2d_array
        self.array_dimensions = array_dimensions


class MethodNode(ASTNode):
    def __init__(self, return_type, name, parameters, body):
        self.return_type = return_type
        self.name = name
        self.parameters = parameters
        self.body = body


class FunctionNode(ASTNode):
    def __init__(self, return_type, name, parameters, body):
        self.return_type = return_type
        self.name = name
        self.parameters = parameters
        self.body = body


class BlockNode(ASTNode):
    def __init__(self, block_type, statements):
        self.block_type = block_type
        self.statements = statements


class AssignmentNode(ASTNode):
    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.expression = expression


class IfNode(ASTNode):
    def __init__(self, condition, then_body, else_body=None):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body


class WhileNode(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body


class ForNode(ASTNode):
    def __init__(self, var, init_expr, condition, increment, body):
        self.var = var
        self.init_expr = init_expr
        self.condition = condition
        self.increment = increment
        self.body = body


class InstantiationNode(ASTNode):
    def __init__(self, type_name, var_name, class_name):
        self.type_name = type_name
        self.var_name = var_name
        self.class_name = class_name


class NewExpressionNode(ASTNode):
    def __init__(self, class_name):
        self.class_name = class_name


class ArrayElementMethodCallNode(ASTNode):
    def __init__(self, array_access, method_name, arguments=None):
        self.array_access = array_access
        self.method_name = method_name
        self.arguments = arguments if arguments else []


class ArrayElementAttributeAssignmentNode(ASTNode):
    def __init__(self, array_access, attribute_name, value):
        self.array_access = array_access
        self.attribute_name = attribute_name
        self.value = value


class ArrayElementAttributeAccessNode(ASTNode):
    def __init__(self, array_access, attribute_name):
        self.array_access = array_access
        self.attribute_name = attribute_name


class ArrayAccessWithObjectNode(ASTNode):
    def __init__(self, object_attr_access, index, index2=None):
        self.object_attr_access = object_attr_access
        self.index = index
        self.index2 = index2


class ObjectAttributeArrayAssignmentNode(ASTNode):
    def __init__(self, object_name, attr_name, index, value, index2=None):
        self.object_name = object_name
        self.attr_name = attr_name
        self.index = index
        self.value = value
        self.index2 = index2


class MethodCallNode(ASTNode):
    def __init__(self, object_name, method_name, arguments=None):
        self.object_name = object_name
        self.method_name = method_name
        self.arguments = arguments or []


class FunctionCallNode(ASTNode):
    def __init__(self, name, arguments=None):
        self.name = name
        self.arguments = arguments or []


class PrintNode(ASTNode):
    def __init__(self, expression):
        self.expression = expression


class InputNode(ASTNode):
    def __init__(self, identifier, prompt=None):
        self.identifier = identifier
        self.prompt = prompt


class SendNode(ASTNode):
    def __init__(self, channel, values):
        self.channel = channel
        self.values = values


class ReceiveNode(ASTNode):
    def __init__(self, channel, variables):
        self.channel = channel
        self.variables = variables


class ReturnNode(ASTNode):
    def __init__(self, expression):
        self.expression = expression


class BinaryOpNode(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right


class UnaryOpNode(ASTNode):
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand


class NumberNode(ASTNode):
    def __init__(self, value):
        self.value = value


class StringNode(ASTNode):
    def __init__(self, value):
        self.value = value


class IdentifierNode(ASTNode):
    def __init__(self, name):
        self.name = name


class AttributeAccessNode(ASTNode):
    def __init__(self, object_name, attribute_name):
        self.object_name = object_name
        self.attribute_name = attribute_name


class AttributeAssignmentNode(ASTNode):
    def __init__(self, object_name, attribute_name, expression):
        self.object_name = object_name
        self.attribute_name = attribute_name
        self.expression = expression


class ConditionNode(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right


class DeclarationNode(ASTNode):
    def __init__(self, type_name, identifier, initial_value=None, is_array=False, array_size=None, is_2d_array=False, array_dimensions=None):
        self.type_name = type_name
        self.identifier = identifier
        self.initial_value = initial_value
        self.is_array = is_array
        self.array_size = array_size
        self.is_2d_array = is_2d_array
        self.array_dimensions = array_dimensions  # [rows, cols] para arrays 2D


class ArrayAccessNode(ASTNode):
    def __init__(self, array_name, index, index2=None):
        self.array_name = array_name
        self.index = index
        self.index2 = index2  # Para arrays 2D


class ArrayAssignmentNode(ASTNode):
    def __init__(self, array_name, index, expression, index2=None):
        self.array_name = array_name
        self.index = index
        self.expression = expression
        self.index2 = index2  # Para arrays 2D


class ArrayInitNode(ASTNode):
    def __init__(self, elements):
        self.elements = elements


class BraceInitNode(ASTNode):
    def __init__(self, values):
        self.values = values  # Lista de valores para inicialização com {}
