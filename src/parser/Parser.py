import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from lexer.token_type import TokenType
from parser.AST import *


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]

    def peek(self, offset=1):
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]

    def advance(self):
        token = self.current_token()
        if token.type != TokenType.EOF:
            self.pos += 1
        return token

    def expect(self, token_type):
        token = self.current_token()
        if token.type != token_type:
            raise SyntaxError(f"Expected {token_type}, got {token.type} at line {token.line}, column {token.column}")
        return self.advance()

    def match(self, *token_types):
        return self.current_token().type in token_types

    def skip_comments(self):
        while self.match(TokenType.COMMENT):
            self.advance()

    def parse(self):
        return self.programa_minipar()

    def programa_minipar(self):
        program = ProgramNode()
        self.skip_comments()
        
        while not self.match(TokenType.EOF):
            self.skip_comments()
            
            if self.match(TokenType.CLASS):
                program.children.append(self.parse_class())
            elif self.match(TokenType.VOID, TokenType.INT, TokenType.FLOAT, TokenType.STRING, TokenType.BOOL):
                if self.peek().type == TokenType.IDENT and self.peek(2).type == TokenType.LPAREN:
                    program.children.append(self.parse_function())
                else:
                    program.children.append(self.parse_declaration())
            elif self.match(TokenType.IDENT):
                if self.peek().type == TokenType.IDENT:
                    if self.peek(2).type == TokenType.LPAREN:
                        program.children.append(self.parse_function())
                    else:
                        program.children.append(self.parse_declaration())
                else:
                    break
            elif self.match(TokenType.C_CHANNEL):
                program.children.append(self.parse_declaration())
            elif self.match(TokenType.SEQ, TokenType.PAR):
                program.children.append(self.parse_block())
            elif self.match(TokenType.COMMENT):
                self.advance()
            else:
                break
            
            self.skip_comments()
        
        return program

    def parse_class(self):
        self.expect(TokenType.CLASS)
        name = self.expect(TokenType.IDENT).lexeme
        
        parent = None
        if self.match(TokenType.EXTENDS):
            self.advance()
            parent = self.expect(TokenType.IDENT).lexeme
        
        self.expect(TokenType.LBRACE)
        
        attributes = []
        methods = []
        
        self.skip_comments()
        while not self.match(TokenType.RBRACE):
            if self.match(TokenType.VOID, TokenType.INT, TokenType.FLOAT, TokenType.STRING, TokenType.BOOL, TokenType.IDENT, TokenType.C_CHANNEL):
                return_type_token = self.current_token()
                return_type = self.advance().lexeme
                name_token = self.expect(TokenType.IDENT)
                
                if self.match(TokenType.LPAREN):
                    self.advance()
                    parameters = []
                    if not self.match(TokenType.RPAREN):
                        while True:
                            param_type = self.advance().lexeme
                            param_name = self.expect(TokenType.IDENT).lexeme
                            parameters.append((param_type, param_name))
                            if not self.match(TokenType.COMMA):
                                break
                            self.advance()
                    self.expect(TokenType.RPAREN)
                    self.expect(TokenType.LBRACE)
                    body = self.parse_statements_list()
                    self.expect(TokenType.RBRACE)
                    methods.append(MethodNode(return_type, name_token.lexeme, parameters, body))
                else:
                    attributes.append(AttributeNode(return_type, name_token.lexeme))
                    if self.match(TokenType.SEMICOLON):
                        self.advance()
            self.skip_comments()
        
        self.expect(TokenType.RBRACE)
        return ClassNode(name, parent, attributes, methods)

    def parse_function(self):
        return_type = self.advance().lexeme
        name = self.expect(TokenType.IDENT).lexeme
        self.expect(TokenType.LPAREN)
        
        parameters = []
        if not self.match(TokenType.RPAREN):
            while True:
                param_type = self.advance().lexeme
                param_name = self.expect(TokenType.IDENT).lexeme
                parameters.append((param_type, param_name))
                if not self.match(TokenType.COMMA):
                    break
                self.advance()
        
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.LBRACE)
        body = self.parse_statements_list()
        self.expect(TokenType.RBRACE)
        
        return FunctionNode(return_type, name, parameters, body)

    def parse_declaration(self):
        type_name = self.advance().lexeme
        identifier = self.expect(TokenType.IDENT).lexeme
        
        is_array = False
        array_size = None
        initial_value = None
        
        if self.match(TokenType.LBRACKET):
            self.advance()
            is_array = True
            if not self.match(TokenType.RBRACKET):
                array_size = self.parse_expression()
            self.expect(TokenType.RBRACKET)
        
        if self.match(TokenType.ASSIGN):
            self.advance()
            if self.match(TokenType.LBRACKET):
                initial_value = self.parse_array_init()
            else:
                initial_value = self.parse_expression()
        
        if self.match(TokenType.SEMICOLON):
            self.advance()
        
        return DeclarationNode(type_name, identifier, initial_value, is_array, array_size)
    
    def parse_array_init(self):
        self.expect(TokenType.LBRACKET)
        elements = []
        
        if not self.match(TokenType.RBRACKET):
            while True:
                elements.append(self.parse_expression())
                if not self.match(TokenType.COMMA):
                    break
                self.advance()
        
        self.expect(TokenType.RBRACKET)
        return ArrayInitNode(elements)

    def parse_block(self):
        block_type = self.advance().lexeme.lower()
        
        if self.match(TokenType.LBRACE):
            self.advance()
            statements = self.parse_statements_list()
            self.expect(TokenType.RBRACE)
        else:
            statements = []
            while not self.match(TokenType.EOF, TokenType.SEQ, TokenType.PAR):
                self.skip_comments()
                if self.match(TokenType.EOF, TokenType.SEQ, TokenType.PAR):
                    break
                stmt = self.parse_statement()
                if stmt:
                    statements.append(stmt)
                if self.match(TokenType.SEQ, TokenType.PAR):
                    break
        
        return BlockNode(block_type, statements)

    def parse_statements_list(self):
        statements = []
        self.skip_comments()
        
        while not self.match(TokenType.RBRACE, TokenType.EOF):
            self.skip_comments()
            if self.match(TokenType.RBRACE):
                break
            
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_comments()
        
        return statements

    def parse_statement(self):
        self.skip_comments()
        
        if self.match(TokenType.SEQ, TokenType.PAR):
            return self.parse_block()
        elif self.match(TokenType.IF):
            return self.parse_if()
        elif self.match(TokenType.WHILE):
            return self.parse_while()
        elif self.match(TokenType.FOR):
            return self.parse_for()
        elif self.match(TokenType.PRINT):
            return self.parse_print()
        elif self.match(TokenType.RETURN):
            return self.parse_return()
        elif self.match(TokenType.THIS):
            obj_name = self.advance().lexeme
            if self.match(TokenType.DOT):
                self.expect(TokenType.DOT)
                attr_name = self.expect(TokenType.IDENT).lexeme
                if self.match(TokenType.ASSIGN):
                    self.advance()
                    expression = self.parse_expression()
                    if self.match(TokenType.SEMICOLON):
                        self.advance()
                    return AttributeAssignmentNode(obj_name, attr_name, expression)
                elif self.match(TokenType.LPAREN):
                    self.advance()
                    args = self.parse_arguments()
                    self.expect(TokenType.RPAREN)
                    if self.match(TokenType.SEMICOLON):
                        self.advance()
                    return MethodCallNode(obj_name, attr_name, args)
        elif self.match(TokenType.INT, TokenType.FLOAT, TokenType.STRING, TokenType.BOOL, TokenType.C_CHANNEL):
            return self.parse_declaration()
        elif self.match(TokenType.IDENT):
            if self.peek().type == TokenType.IDENT:
                return self.parse_declaration()
            elif self.peek().type == TokenType.DOT:
                object_name = self.advance().lexeme
                self.expect(TokenType.DOT)
                
                method_token = self.current_token()
                if self.match(TokenType.SEND):
                    method_name = self.advance().lexeme
                elif self.match(TokenType.RECEIVE):
                    method_name = self.advance().lexeme
                elif self.match(TokenType.IDENT):
                    method_name = self.advance().lexeme
                else:
                    raise SyntaxError(f"Expected method name after dot at line {method_token.line}")
                
                if self.match(TokenType.LPAREN):
                    self.advance()
                    args = self.parse_arguments()
                    self.expect(TokenType.RPAREN)
                    if self.match(TokenType.SEMICOLON):
                        self.advance()
                    
                    if method_name.lower() == "send":
                        return SendNode(object_name, args)
                    elif method_name.lower() == "receive":
                        return ReceiveNode(object_name, args)
                    else:
                        return MethodCallNode(object_name, method_name, args)
                elif self.match(TokenType.ASSIGN):
                    self.advance()
                    expression = self.parse_expression()
                    if self.match(TokenType.SEMICOLON):
                        self.advance()
                    return AttributeAssignmentNode(object_name, method_name, expression)
                else:
                    if self.match(TokenType.SEMICOLON):
                        self.advance()
                    return AttributeAccessNode(object_name, method_name)
            elif self.peek().type == TokenType.LBRACKET:
                array_name = self.advance().lexeme
                self.expect(TokenType.LBRACKET)
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                
                if self.match(TokenType.ASSIGN):
                    self.advance()
                    
                    if self.match(TokenType.INPUT):
                        self.advance()
                        self.expect(TokenType.LPAREN)
                        prompt = None
                        if not self.match(TokenType.RPAREN):
                            prompt = self.parse_expression()
                        self.expect(TokenType.RPAREN)
                        if self.match(TokenType.SEMICOLON):
                            self.advance()
                        
                        temp_var = f"__temp_input_{array_name}"
                        input_node = InputNode(temp_var, prompt)
                        assign_node = ArrayAssignmentNode(array_name, index, IdentifierNode(temp_var))
                        return BlockNode("seq", [input_node, assign_node])
                    else:
                        expression = self.parse_expression()
                        if self.match(TokenType.SEMICOLON):
                            self.advance()
                        return ArrayAssignmentNode(array_name, index, expression)
                else:
                    if self.match(TokenType.SEMICOLON):
                        self.advance()
                    return ArrayAccessNode(array_name, index)
            elif self.peek().type == TokenType.ASSIGN:
                identifier = self.advance().lexeme
                self.expect(TokenType.ASSIGN)
                
                if self.match(TokenType.INPUT):
                    self.advance()
                    self.expect(TokenType.LPAREN)
                    prompt = None
                    if not self.match(TokenType.RPAREN):
                        prompt = self.parse_expression()
                    self.expect(TokenType.RPAREN)
                    if self.match(TokenType.SEMICOLON):
                        self.advance()
                    return InputNode(identifier, prompt)
                elif self.match(TokenType.NEW):
                    self.advance()
                    class_name = self.expect(TokenType.IDENT).lexeme
                    self.expect(TokenType.LPAREN)
                    self.expect(TokenType.RPAREN)
                    if self.match(TokenType.SEMICOLON):
                        self.advance()
                    return InstantiationNode(None, identifier, class_name)
                else:
                    expression = self.parse_expression()
                    if self.match(TokenType.SEMICOLON):
                        self.advance()
                    return AssignmentNode(identifier, expression)
            elif self.peek().type == TokenType.LPAREN:
                name = self.advance().lexeme
                self.expect(TokenType.LPAREN)
                args = self.parse_arguments()
                self.expect(TokenType.RPAREN)
                if self.match(TokenType.SEMICOLON):
                    self.advance()
                return FunctionCallNode(name, args)
            elif self.peek().type == TokenType.IDENT:
                type_name = self.advance().lexeme
                var_name = self.expect(TokenType.IDENT).lexeme
                self.expect(TokenType.ASSIGN)
                self.expect(TokenType.NEW)
                class_name = self.expect(TokenType.IDENT).lexeme
                self.expect(TokenType.LPAREN)
                self.expect(TokenType.RPAREN)
                if self.match(TokenType.SEMICOLON):
                    self.advance()
                return InstantiationNode(type_name, var_name, class_name)
        elif self.match(TokenType.COMMENT):
            self.advance()
            return None
        
        if self.match(TokenType.SEMICOLON):
            self.advance()
        
        return None

    def parse_if(self):
        self.expect(TokenType.IF)
        condition = self.parse_condition()
        self.expect(TokenType.LBRACE)
        then_body = self.parse_statements_list()
        self.expect(TokenType.RBRACE)
        
        else_body = None
        if self.match(TokenType.ELSE):
            self.advance()
            if self.match(TokenType.IF):
                else_body = [self.parse_if()]
            else:
                self.expect(TokenType.LBRACE)
                else_body = self.parse_statements_list()
                self.expect(TokenType.RBRACE)
        
        return IfNode(condition, then_body, else_body)

    def parse_while(self):
        self.expect(TokenType.WHILE)
        condition = self.parse_condition()
        self.expect(TokenType.LBRACE)
        body = self.parse_statements_list()
        self.expect(TokenType.RBRACE)
        return WhileNode(condition, body)

    def parse_for(self):
        self.expect(TokenType.FOR)
        var = self.expect(TokenType.IDENT).lexeme
        self.expect(TokenType.ASSIGN)
        init_expr = self.parse_expression()
        self.expect(TokenType.SEMICOLON)
        condition = self.parse_condition()
        self.expect(TokenType.SEMICOLON)
        
        increment_var = self.expect(TokenType.IDENT).lexeme
        self.expect(TokenType.ASSIGN)
        increment_expr = self.parse_expression()
        
        self.expect(TokenType.LBRACE)
        body = self.parse_statements_list()
        self.expect(TokenType.RBRACE)
        
        return ForNode(var, init_expr, condition, AssignmentNode(increment_var, increment_expr), body)

    def parse_print(self):
        self.expect(TokenType.PRINT)
        self.expect(TokenType.LPAREN)
        expression = self.parse_expression()
        self.expect(TokenType.RPAREN)
        if self.match(TokenType.SEMICOLON):
            self.advance()
        return PrintNode(expression)

    def parse_return(self):
        self.expect(TokenType.RETURN)
        expression = self.parse_expression()
        if self.match(TokenType.SEMICOLON):
            self.advance()
        return ReturnNode(expression)

    def parse_arguments(self):
        args = []
        if self.match(TokenType.RPAREN):
            return args
        
        while True:
            args.append(self.parse_expression())
            if not self.match(TokenType.COMMA):
                break
            self.advance()
        
        return args

    def parse_condition(self):
        left = self.parse_expression()
        
        if self.match(TokenType.EQ, TokenType.NEQ, TokenType.GT, TokenType.LT, TokenType.GTE, TokenType.LTE):
            operator = self.advance().lexeme
            right = self.parse_expression()
            return ConditionNode(left, operator, right)
        
        return left

    def parse_expression(self):
        return self.parse_additive()

    def parse_additive(self):
        left = self.parse_multiplicative()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.advance().lexeme
            right = self.parse_multiplicative()
            left = BinaryOpNode(left, operator, right)
        
        return left

    def parse_multiplicative(self):
        left = self.parse_unary()
        
        while self.match(TokenType.MUL, TokenType.DIV):
            operator = self.advance().lexeme
            right = self.parse_unary()
            left = BinaryOpNode(left, operator, right)
        
        return left

    def parse_unary(self):
        if self.match(TokenType.NUMBER):
            value = self.advance().lexeme
            return NumberNode(value)
        elif self.match(TokenType.TEXT):
            value = self.advance().lexeme
            return StringNode(value)
        elif self.match(TokenType.THIS):
            name = self.advance().lexeme
            if self.match(TokenType.DOT):
                self.advance()
                attr_or_method = self.expect(TokenType.IDENT).lexeme
                if self.match(TokenType.LPAREN):
                    self.advance()
                    args = self.parse_arguments()
                    self.expect(TokenType.RPAREN)
                    return MethodCallNode(name, attr_or_method, args)
                else:
                    return AttributeAccessNode(name, attr_or_method)
            return IdentifierNode(name)
        elif self.match(TokenType.IDENT):
            name = self.advance().lexeme
            if self.match(TokenType.LPAREN):
                self.advance()
                args = self.parse_arguments()
                self.expect(TokenType.RPAREN)
                return FunctionCallNode(name, args)
            elif self.match(TokenType.LBRACKET):
                self.advance()
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                return ArrayAccessNode(name, index)
            elif self.match(TokenType.DOT):
                self.advance()
                attr_or_method = self.expect(TokenType.IDENT).lexeme
                if self.match(TokenType.LPAREN):
                    self.advance()
                    args = self.parse_arguments()
                    self.expect(TokenType.RPAREN)
                    return MethodCallNode(name, attr_or_method, args)
                else:
                    return AttributeAccessNode(name, attr_or_method)
            return IdentifierNode(name)
        elif self.match(TokenType.LPAREN):
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        elif self.match(TokenType.MINUS):
            operator = self.advance().lexeme
            operand = self.parse_unary()
            return UnaryOpNode(operator, operand)
        else:
            raise SyntaxError(f"Unexpected token: {self.current_token()}")  # nó raiz da AST
