import sys
import os
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from parser.AST import *
from runtime.Channel import Channel
from runtime.ThreadManager import ThreadManager
from symbol_table.SymbolTable import SymbolTable


class ReturnException(Exception):
    def __init__(self, value):
        self.value = value


class ObjectInstance:
    def __init__(self, class_name, class_def, parent_classes=None):
        self.class_name = class_name
        self.class_def = class_def
        self.parent_classes = parent_classes or {}
        self.attributes = {}
        
        for attr in class_def.attributes:
            self.attributes[attr.name] = None
    
    def get_attribute(self, name):
        if name in self.attributes:
            return self.attributes[name]
        
        if self.class_def.parent and self.class_def.parent in self.parent_classes:
            parent_def = self.parent_classes[self.class_def.parent]
            for attr in parent_def.attributes:
                if attr.name == name:
                    return self.attributes.get(name)
        
        return None
    
    def set_attribute(self, name, value):
        self.attributes[name] = value
    
    def get_method(self, name):
        for method in self.class_def.methods:
            if method.name == name:
                return method
        
        if self.class_def.parent and self.class_def.parent in self.parent_classes:
            parent_def = self.parent_classes[self.class_def.parent]
            for method in parent_def.methods:
                if method.name == name:
                    return method
        
        return None


class Interpreter:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.global_scope = {}
        self.local_storage = threading.local()
        self.classes = {}
        self.functions = {}
        self.thread_manager = ThreadManager()
        self.return_value = None
        self.print_lock = threading.Lock()
    
    @property
    def local_scope(self):
        if not hasattr(self.local_storage, 'scope'):
            self.local_storage.scope = {}
        return self.local_storage.scope
    
    @local_scope.setter
    def local_scope(self, value):
        self.local_storage.scope = value
    
    def interpret(self, ast):
        if isinstance(ast, ProgramNode):
            self.collect_definitions(ast)
            self.execute_program(ast)
    
    def collect_definitions(self, program):
        for node in program.children:
            if isinstance(node, ClassNode):
                self.classes[node.name] = node
                self.symbol_table.define_class(
                    node.name,
                    [attr.name for attr in node.attributes],
                    [method.name for method in node.methods],
                    node.parent
                )
            elif isinstance(node, FunctionNode):
                self.functions[node.name] = node
                self.symbol_table.define_function(
                    node.name,
                    node.return_type,
                    node.parameters
                )
            elif isinstance(node, DeclarationNode):
                self.execute_declaration(node, self.global_scope)
    
    def execute_program(self, program):
        for node in program.children:
            if isinstance(node, BlockNode):
                self.execute_block(node)
            elif isinstance(node, FunctionCallNode):
                self.execute_function_call(node)
    
    def execute_block(self, node):
        if node.block_type == "seq":
            for stmt in node.statements:
                self.execute_statement(stmt)
        elif node.block_type == "par":
            self.execute_parallel_block(node)
    
    def execute_parallel_block(self, node):
        self.thread_manager.clear()
        
        for stmt in node.statements:
            if isinstance(stmt, FunctionCallNode):
                func = self.functions.get(stmt.name)
                if func:
                    thread = self.thread_manager.create_thread(
                        target=self.execute_function_in_thread,
                        args=(func, stmt.arguments)
                    )
            elif isinstance(stmt, BlockNode):
                thread = self.thread_manager.create_thread(
                    target=self.execute_block,
                    args=(stmt,)
                )
            else:
                thread = self.thread_manager.create_thread(
                    target=self.execute_statement,
                    args=(stmt,)
                )
        
        self.thread_manager.start_all()
        self.thread_manager.join_all()
    
    def execute_function_in_thread(self, func, arguments):
        local_env = {}
        
        for i, (param_type, param_name) in enumerate(func.parameters):
            if i < len(arguments):
                local_env[param_name] = self.evaluate_expression(arguments[i])
        
        old_local = self.local_scope
        self.local_scope = local_env
        
        try:
            for stmt in func.body:
                self.execute_statement(stmt)
        except ReturnException as e:
            pass
        finally:
            self.local_scope = old_local
    
    def execute_statement(self, node):
        if node is None:
            return
        
        if isinstance(node, BlockNode):
            self.execute_block(node)
        elif isinstance(node, DeclarationNode):
            self.execute_declaration(node, self.local_scope if self.local_scope else self.global_scope)
        elif isinstance(node, AssignmentNode):
            self.execute_assignment(node)
        elif isinstance(node, ArrayAssignmentNode):
            self.execute_array_assignment(node)
        elif isinstance(node, AttributeAssignmentNode):
            self.execute_attribute_assignment(node)
        elif isinstance(node, IfNode):
            self.execute_if(node)
        elif isinstance(node, WhileNode):
            self.execute_while(node)
        elif isinstance(node, ForNode):
            self.execute_for(node)
        elif isinstance(node, PrintNode):
            self.execute_print(node)
        elif isinstance(node, InputNode):
            self.execute_input(node)
        elif isinstance(node, FunctionCallNode):
            self.execute_function_call(node)
        elif isinstance(node, MethodCallNode):
            self.execute_method_call(node)
        elif isinstance(node, SendNode):
            self.execute_send(node)
        elif isinstance(node, ReceiveNode):
            self.execute_receive(node)
        elif isinstance(node, ReturnNode):
            self.execute_return(node)
        elif isinstance(node, InstantiationNode):
            self.execute_instantiation(node)
        elif isinstance(node, AttributeAccessNode):
            self.evaluate_attribute_access(node)
        elif isinstance(node, ArrayAccessNode):
            self.evaluate_array_access(node)
    
    def execute_declaration(self, node, scope):
        value = None
        
        if node.type_name.lower() == "c_channel":
            value = Channel()
        elif node.is_array:
            if node.initial_value:
                if isinstance(node.initial_value, ArrayInitNode):
                    value = [self.evaluate_expression(elem) for elem in node.initial_value.elements]
                else:
                    value = self.evaluate_expression(node.initial_value)
            elif node.array_size:
                size = self.evaluate_expression(node.array_size)
                value = [None] * int(size)
            else:
                value = []
        elif node.initial_value:
            value = self.evaluate_expression(node.initial_value)
        
        scope[node.identifier] = value
        
        if scope is self.global_scope:
            self.symbol_table.define(
                node.identifier,
                node.type_name,
                value,
                node.is_array,
                node.array_size
            )
    
    def execute_assignment(self, node):
        value = self.evaluate_expression(node.expression)
        if node.identifier in self.local_scope:
            self.local_scope[node.identifier] = value
        else:
            self.global_scope[node.identifier] = value
            self.symbol_table.update(node.identifier, value)
    
    def execute_attribute_assignment(self, node):
        obj = self.get_variable(node.object_name)
        if isinstance(obj, ObjectInstance):
            value = self.evaluate_expression(node.expression)
            obj.set_attribute(node.attribute_name, value)
    
    def execute_array_assignment(self, node):
        array = self.get_variable(node.array_name)
        if isinstance(array, list):
            index = self.evaluate_expression(node.index)
            value = self.evaluate_expression(node.expression)
            array[int(index)] = value
    
    def execute_if(self, node):
        condition = self.evaluate_condition(node.condition)
        if condition:
            for stmt in node.then_body:
                self.execute_statement(stmt)
        elif node.else_body:
            for stmt in node.else_body:
                self.execute_statement(stmt)
    
    def execute_while(self, node):
        while self.evaluate_condition(node.condition):
            for stmt in node.body:
                self.execute_statement(stmt)
    
    def execute_for(self, node):
        scope = self.local_scope if self.local_scope else self.global_scope
        scope[node.var] = self.evaluate_expression(node.init_expr)
        
        while self.evaluate_condition(node.condition):
            for stmt in node.body:
                self.execute_statement(stmt)
            self.execute_statement(node.increment)
    
    def execute_print(self, node):
        value = self.evaluate_expression(node.expression)
        print(value)
    
    def execute_input(self, node):
        prompt = ""
        if node.prompt:
            prompt = str(self.evaluate_expression(node.prompt))
        
        value = input(prompt)
        
        try:
            if '.' in value:
                value = float(value)
            else:
                value = int(value)
        except ValueError:
            pass
        
        if node.identifier in self.local_scope:
            self.local_scope[node.identifier] = value
        else:
            self.global_scope[node.identifier] = value
    
    def execute_function_call(self, node):
        if node.name not in self.functions:
            return None
        
        func = self.functions[node.name]
        local_env = {}
        
        for i, (param_type, param_name) in enumerate(func.parameters):
            if i < len(node.arguments):
                local_env[param_name] = self.evaluate_expression(node.arguments[i])
        
        old_local = self.local_scope
        self.local_scope = local_env
        
        try:
            for stmt in func.body:
                self.execute_statement(stmt)
        except ReturnException as e:
            self.local_scope = old_local
            return e.value
        
        self.local_scope = old_local
        return None
    
    def execute_method_call(self, node):
        obj = self.get_variable(node.object_name)
        
        if isinstance(obj, ObjectInstance):
            method = obj.get_method(node.method_name)
            if method:
                local_env = {'this': obj}
                
                for i, (param_type, param_name) in enumerate(method.parameters):
                    if i < len(node.arguments):
                        local_env[param_name] = self.evaluate_expression(node.arguments[i])
                
                old_local = self.local_scope
                self.local_scope = local_env
                
                try:
                    for stmt in method.body:
                        self.execute_statement(stmt)
                except ReturnException as e:
                    self.local_scope = old_local
                    return e.value
                finally:
                    self.local_scope = old_local
                
                return None
        elif obj and hasattr(obj, node.method_name):
            method = getattr(obj, node.method_name)
            args = [self.evaluate_expression(arg) for arg in node.arguments]
            return method(*args)
        
        return None
    
    def execute_send(self, node):
        channel = self.get_variable(node.channel)
        if isinstance(channel, Channel):
            values = [self.evaluate_expression(val) for val in node.values]
            channel.send(*values)
    
    def execute_receive(self, node):
        channel = self.get_variable(node.channel)
        if isinstance(channel, Channel):
            values = channel.receive(len(node.variables))
            
            if values is not None:
                if not isinstance(values, tuple):
                    values = (values,)
                
                for i, var in enumerate(node.variables):
                    if i < len(values):
                        if isinstance(var, IdentifierNode):
                            var_name = var.name
                        else:
                            var_name = str(var)
                        
                        if var_name in self.local_scope:
                            self.local_scope[var_name] = values[i]
                        else:
                            self.global_scope[var_name] = values[i]
    
    def execute_return(self, node):
        value = self.evaluate_expression(node.expression)
        raise ReturnException(value)
    
    def execute_instantiation(self, node):
        if node.class_name in self.classes:
            class_def = self.classes[node.class_name]
            obj = ObjectInstance(node.class_name, class_def, self.classes)
            
            scope = self.local_scope if self.local_scope else self.global_scope
            scope[node.var_name] = obj
    
    def evaluate_expression(self, node):
        if isinstance(node, NumberNode):
            value = node.value
            if '.' in str(value):
                return float(value)
            return int(value)
        elif isinstance(node, StringNode):
            return str(node.value)
        elif isinstance(node, IdentifierNode):
            return self.get_variable(node.name)
        elif isinstance(node, AttributeAccessNode):
            return self.evaluate_attribute_access(node)
        elif isinstance(node, ArrayAccessNode):
            return self.evaluate_array_access(node)
        elif isinstance(node, BinaryOpNode):
            left = self.evaluate_expression(node.left)
            right = self.evaluate_expression(node.right)
            return self.apply_binary_op(left, node.operator, right)
        elif isinstance(node, UnaryOpNode):
            operand = self.evaluate_expression(node.operand)
            if node.operator == '-':
                return -operand
            return operand
        elif isinstance(node, FunctionCallNode):
            return self.execute_function_call(node)
        elif isinstance(node, MethodCallNode):
            return self.execute_method_call(node)
        return None
    
    def evaluate_attribute_access(self, node):
        obj = self.get_variable(node.object_name)
        if isinstance(obj, ObjectInstance):
            return obj.get_attribute(node.attribute_name)
        return None
    
    def evaluate_array_access(self, node):
        array = self.get_variable(node.array_name)
        if isinstance(array, list):
            index = self.evaluate_expression(node.index)
            return array[int(index)]
        return None
    
    def evaluate_condition(self, node):
        if isinstance(node, ConditionNode):
            left = self.evaluate_expression(node.left)
            right = self.evaluate_expression(node.right)
            return self.apply_comparison(left, node.operator, right)
        else:
            return self.evaluate_expression(node)
    
    def apply_binary_op(self, left, operator, right):
        if operator == '+':
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            return left + right
        elif operator == '-':
            return left - right
        elif operator == '*':
            return left * right
        elif operator == '/':
            if right == 0:
                raise ZeroDivisionError("Division by zero")
            if isinstance(left, int) and isinstance(right, int):
                return left // right
            return left / right
        return None
    
    def apply_comparison(self, left, operator, right):
        if operator == '==':
            return left == right
        elif operator == '!=':
            return left != right
        elif operator == '>':
            return left > right
        elif operator == '<':
            return left < right
        elif operator == '>=':
            return left >= right
        elif operator == '<=':
            return left <= right
        return False
    
    def get_variable(self, name):
        if name in self.local_scope:
            return self.local_scope[name]
        elif name in self.global_scope:
            return self.global_scope[name]
        return None
