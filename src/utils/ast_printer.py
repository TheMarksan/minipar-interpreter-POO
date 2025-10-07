import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from parser.AST import *


class ASTPrinter:
    def __init__(self):
        self.indent_level = 0
        self.indent_char = "  "
    
    def print_ast(self, node, label=""):
        if label:
            print(f"\n{label}")
            print("-" * 40)
        self._print_node(node)
    
    def _print_node(self, node, prefix=""):
        if node is None:
            return
        
        indent = self.indent_char * self.indent_level
        
        if isinstance(node, ProgramNode):
            print(f"{indent}Program:")
            self.indent_level += 1
            for child in node.children:
                self._print_node(child)
            self.indent_level -= 1
        
        elif isinstance(node, ClassNode):
            parent_info = f" extends {node.parent}" if node.parent else ""
            print(f"{indent}class {node.name}{parent_info} {{")
            self.indent_level += 1
            
            if node.attributes:
                print(f"{self.indent_char * self.indent_level}Attributes:")
                self.indent_level += 1
                for attr in node.attributes:
                    self._print_node(attr)
                self.indent_level -= 1
            
            if node.methods:
                print(f"{self.indent_char * self.indent_level}Methods:")
                self.indent_level += 1
                for method in node.methods:
                    self._print_node(method)
                self.indent_level -= 1
            
            self.indent_level -= 1
            print(f"{indent}}}")
        
        elif isinstance(node, AttributeNode):
            print(f"{indent}{node.type_name} {node.name}")
        
        elif isinstance(node, MethodNode):
            params = ", ".join([f"{t} {n}" for t, n in node.parameters])
            print(f"{indent}{node.return_type} {node.name}({params}) {{")
            self.indent_level += 1
            for stmt in node.body:
                self._print_node(stmt)
            self.indent_level -= 1
            print(f"{indent}}}")
        
        elif isinstance(node, FunctionNode):
            params = ", ".join([f"{t} {n}" for t, n in node.parameters])
            print(f"{indent}func {node.name}({params}) -> {node.return_type} {{")
            self.indent_level += 1
            for stmt in node.body:
                self._print_node(stmt)
            self.indent_level -= 1
            print(f"{indent}}}")
        
        elif isinstance(node, BlockNode):
            print(f"{indent}{node.block_type.upper()} {{")
            self.indent_level += 1
            for stmt in node.statements:
                self._print_node(stmt)
            self.indent_level -= 1
            print(f"{indent}}}")
        
        elif isinstance(node, DeclarationNode):
            array_info = f"[{node.array_size if node.array_size else ''}]" if node.is_array else ""
            init_info = ""
            if node.initial_value:
                if isinstance(node.initial_value, ArrayInitNode):
                    init_info = " = [...]"
                else:
                    init_info = f" = <expr>"
            print(f"{indent}var {node.type_name} {node.identifier}{array_info}{init_info}")
        
        elif isinstance(node, AssignmentNode):
            print(f"{indent}{node.identifier} = ", end="")
            self._print_expression(node.expression)
            print()
        
        elif isinstance(node, ArrayAssignmentNode):
            print(f"{indent}{node.array_name}[", end="")
            self._print_expression(node.index)
            print("] = ", end="")
            self._print_expression(node.expression)
            print()
        
        elif isinstance(node, AttributeAssignmentNode):
            print(f"{indent}{node.object_name}.{node.attribute_name} = ", end="")
            self._print_expression(node.expression)
            print()
        
        elif isinstance(node, IfNode):
            print(f"{indent}if (", end="")
            self._print_expression(node.condition)
            print(") {")
            self.indent_level += 1
            for stmt in node.then_body:
                self._print_node(stmt)
            self.indent_level -= 1
            if node.else_body:
                print(f"{indent}}} else {{")
                self.indent_level += 1
                for stmt in node.else_body:
                    self._print_node(stmt)
                self.indent_level -= 1
            print(f"{indent}}}")
        
        elif isinstance(node, WhileNode):
            print(f"{indent}while (", end="")
            self._print_expression(node.condition)
            print(") {")
            self.indent_level += 1
            for stmt in node.body:
                self._print_node(stmt)
            self.indent_level -= 1
            print(f"{indent}}}")
        
        elif isinstance(node, ForNode):
            print(f"{indent}for {node.var} = ", end="")
            self._print_expression(node.init_expr)
            print("; ", end="")
            self._print_expression(node.condition)
            print("; ", end="")
            self._print_expression(node.increment)
            print(" {")
            self.indent_level += 1
            for stmt in node.body:
                self._print_node(stmt)
            self.indent_level -= 1
            print(f"{indent}}}")
        
        elif isinstance(node, PrintNode):
            print(f"{indent}print(", end="")
            self._print_expression(node.expression)
            print(")")
        
        elif isinstance(node, InputNode):
            prompt = f'"{node.prompt}"' if node.prompt else ''
            print(f"{indent}{node.identifier} = input({prompt})")
        
        elif isinstance(node, ReturnNode):
            print(f"{indent}return ", end="")
            self._print_expression(node.expression)
            print()
        
        elif isinstance(node, FunctionCallNode):
            args_str = ", ".join(["..." for _ in node.arguments]) if node.arguments else ""
            print(f"{indent}{node.name}({args_str})")
        
        elif isinstance(node, MethodCallNode):
            args_str = ", ".join(["..." for _ in node.arguments]) if node.arguments else ""
            print(f"{indent}{node.object_name}.{node.method_name}({args_str})")
        
        elif isinstance(node, InstantiationNode):
            print(f"{indent}{node.var_name} = new {node.class_name}()")
        
        elif isinstance(node, SendNode):
            values_str = ", ".join(["..." for _ in node.values]) if node.values else ""
            print(f"{indent}{node.channel}.send({values_str})")
        
        elif isinstance(node, ReceiveNode):
            vars_str = ", ".join(["..." for _ in node.variables]) if node.variables else ""
            print(f"{indent}{node.channel}.receive({vars_str})")
    
    def _print_expression(self, node):
        if isinstance(node, NumberNode):
            print(node.value, end="")
        elif isinstance(node, StringNode):
            print(f'"{node.value}"', end="")
        elif isinstance(node, IdentifierNode):
            print(node.name, end="")
        elif isinstance(node, BinaryOpNode):
            print("(", end="")
            self._print_expression(node.left)
            print(f" {node.operator} ", end="")
            self._print_expression(node.right)
            print(")", end="")
        elif isinstance(node, UnaryOpNode):
            print(f"{node.operator}", end="")
            self._print_expression(node.operand)
        elif isinstance(node, FunctionCallNode):
            print(f"{node.name}(...)", end="")
        elif isinstance(node, MethodCallNode):
            print(f"{node.object_name}.{node.method_name}(...)", end="")
        elif isinstance(node, ArrayAccessNode):
            print(f"{node.array_name}[", end="")
            self._print_expression(node.index)
            print("]", end="")
        elif isinstance(node, AttributeAccessNode):
            print(f"{node.object_name}.{node.attribute_name}", end="")
        elif isinstance(node, ConditionNode):
            self._print_expression(node.left)
            print(f" {node.operator} ", end="")
            self._print_expression(node.right)
        elif isinstance(node, AssignmentNode):
            print(f"{node.identifier} = ", end="")
            self._print_expression(node.expression)
        else:
            print("<expr>", end="")


def print_ast(ast, label="Árvore de Sintaxe Abstrata (AST):"):
    printer = ASTPrinter()
    printer.print_ast(ast, label)
