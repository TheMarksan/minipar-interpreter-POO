# ============================================================================
# Parser.py - Analisador Sintático (Parser) 
# ============================================================================
# Implementa um parser descendente recursivo (Recursive Descent Parser) para
# a linguagem MiniPar. Utiliza lookahead (LL(k)) para analisar tokens e
# construir a Árvore de Sintaxe Abstrata (AST).
#
# Características:
# - Lookahead de 1-2 tokens para decisões de parsing
# - Precedência de operadores (multiplicação > adição > relacional > lógico)
# - Suporte a estruturas OO, concorrência (SEQ/PAR), arrays 1D/2D
# ============================================================================

from lexer.token_type import TokenType
from parser.AST import *


class Parser:
    """Parser descendente recursivo para MiniPar."""
    
    def __init__(self, tokens):
        """Inicializa o parser com lista de tokens do lexer."""
        self.tokens = tokens  # Lista de tokens gerados pelo lexer
        self.pos = 0          # Posição atual na lista de tokens

    def current_token(self):
        """Retorna o token atual sem avançar."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]  # Retorna EOF se passou do fim

    def peek(self, offset=1):
        """Olha adiante (lookahead) sem consumir tokens."""
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]

    def advance(self):
        """Consome e retorna o token atual, avançando para o próximo."""
        token = self.current_token()
        if token.type != TokenType.EOF:
            self.pos += 1
        return token

    def expect(self, token_type):
        """Consome token se for do tipo esperado, senão lança erro de sintaxe."""
        token = self.current_token()
        if token.type != token_type:
            raise SyntaxError(f"Expected {token_type}, got {token.type} at line {token.line}, column {token.column}")
        return self.advance()

    def match(self, *token_types):
        """Verifica se o token atual é um dos tipos especificados."""
        return self.current_token().type in token_types

    def skip_comments(self):
        """Pula todos os comentários consecutivos."""
        while self.match(TokenType.COMMENT):
            self.advance()

    def parse(self):
        """Inicia o processo de parsing e retorna a AST."""
        return self.programa_minipar()

    def programa_minipar(self):
        """
        Parse do programa completo.
        Processa classes, funções globais, declarações e blocos SEQ/PAR.
        """
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
                elif self.peek().type == TokenType.LPAREN:
                    program.children.append(self.parse_statement())
                elif self.peek().type == TokenType.ASSIGN:
                    program.children.append(self.parse_statement())
                elif self.peek().type == TokenType.DOT:
                    program.children.append(self.parse_statement())
                elif self.peek().type == TokenType.LBRACKET:
                    program.children.append(self.parse_statement())
                else:
                    break
            elif self.match(TokenType.C_CHANNEL):
                program.children.append(self.parse_declaration())
            elif self.match(TokenType.SEQ, TokenType.PAR):
                program.children.append(self.parse_block())
            elif self.match(TokenType.PRINT):
                program.children.append(self.parse_statement())
            elif self.match(TokenType.COMMENT):
                self.advance()
            else:
                break
            
            self.skip_comments()
        
        return program

    def parse_class(self):
        """
        Parse de definição de classe com herança opcional.
        Sintaxe: class Nome [extends Pai] { atributos e métodos }
        """
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
                            
                            # Verificar se o parâmetro é array
                            if self.match(TokenType.LBRACKET):
                                self.advance()
                                if not self.match(TokenType.RBRACKET):
                                    # Tem tamanho especificado (como [16])
                                    array_size_expr = self.parse_expression()
                                self.expect(TokenType.RBRACKET)
                                # Para parâmetros de array, adicionar [] ao tipo
                                param_type = param_type + "[]"
                            
                            parameters.append((param_type, param_name))
                            if not self.match(TokenType.COMMA):
                                break
                            self.advance()
                    self.expect(TokenType.RPAREN)
                    self.expect(TokenType.LBRACE)
                    body = self.parse_statements_list()
                    self.expect(TokenType.RBRACE)
                    methods.append(MethodNode(return_type, name_token.lexeme, parameters, body))
                elif self.match(TokenType.LBRACKET):
                    self.advance()
                    array_size = None
                    if not self.match(TokenType.RBRACKET):
                        array_size = self.parse_expression()
                    self.expect(TokenType.RBRACKET)
                    
                    # Check for second dimension (2D array)
                    is_2d = False
                    array_size2 = None
                    if self.match(TokenType.LBRACKET):
                        is_2d = True
                        self.advance()
                        if not self.match(TokenType.RBRACKET):
                            array_size2 = self.parse_expression()
                        self.expect(TokenType.RBRACKET)
                    
                    if is_2d:
                        attributes.append(AttributeNode(return_type, name_token.lexeme, is_array=False, array_size=None, is_2d_array=True, array_dimensions=[array_size, array_size2]))
                    else:
                        attributes.append(AttributeNode(return_type, name_token.lexeme, is_array=True, array_size=array_size))
                    if self.match(TokenType.SEMICOLON):
                        self.advance()
                else:
                    attributes.append(AttributeNode(return_type, name_token.lexeme))
                    if self.match(TokenType.SEMICOLON):
                        self.advance()
            self.skip_comments()
        
        self.expect(TokenType.RBRACE)
        return ClassNode(name, parent, attributes, methods)

    def parse_function(self):
        """
        Parse de função global.
        Sintaxe: tipo nome(parametros) { corpo }
        Suporta parâmetros array com [] no tipo.
        """
        return_type = self.advance().lexeme
        name = self.expect(TokenType.IDENT).lexeme
        self.expect(TokenType.LPAREN)
        
        parameters = []
        if not self.match(TokenType.RPAREN):
            while True:
                param_type = self.advance().lexeme
                param_name = self.expect(TokenType.IDENT).lexeme
                
                # Verificar se o parâmetro é array
                if self.match(TokenType.LBRACKET):
                    self.advance()
                    if not self.match(TokenType.RBRACKET):
                        # Tem tamanho especificado (como [16])
                        array_size_expr = self.parse_expression()
                    self.expect(TokenType.RBRACKET)
                    # Para parâmetros de array, adicionar [] ao tipo
                    param_type = param_type + "[]"
                
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

        # Special handling for channel declaration syntax:
        # c_channel chan [id1 id2 ...];  -> store extra identifiers in channel_info
        channel_info = None
        if type_name.lower() == 'c_channel':
            channel_info = []
            # Collect following identifiers until semicolon or other token
            while self.match(TokenType.IDENT):
                channel_info.append(self.advance().lexeme)
        
        is_array = False
        is_2d_array = False
        array_size = None
        array_dimensions = None
        initial_value = None
        
        # Verificar se é array [tamanho] ou [dim1][dim2]
        if self.match(TokenType.LBRACKET):
            self.advance()
            is_array = True
            
            if not self.match(TokenType.RBRACKET):
                first_size = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                
                # Verificar se há uma segunda dimensão
                if self.match(TokenType.LBRACKET):
                    self.advance()
                    is_2d_array = True
                    second_size = None
                    if not self.match(TokenType.RBRACKET):
                        second_size = self.parse_expression()
                    self.expect(TokenType.RBRACKET)
                    array_dimensions = [first_size, second_size]
                else:
                    array_size = first_size
            else:
                self.expect(TokenType.RBRACKET)
        
        # Verificar inicialização
        if self.match(TokenType.ASSIGN):
            self.advance()
            if self.match(TokenType.LBRACE):
                initial_value = self.parse_brace_init()
            elif self.match(TokenType.LBRACKET):
                initial_value = self.parse_array_init()
            else:
                initial_value = self.parse_expression()
        
        if self.match(TokenType.SEMICOLON):
            self.advance()

        # Return DeclarationNode with optional channel_info
        try:
            return DeclarationNode(type_name, identifier, initial_value, is_array, array_size, is_2d_array, array_dimensions, channel_info)
        except TypeError:
            # Fallback in case AST.DeclarationNode not updated
            node = DeclarationNode(type_name, identifier, initial_value, is_array, array_size, is_2d_array, array_dimensions)
            setattr(node, 'channel_info', channel_info)
            return node
    
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
    
    def parse_brace_init(self):
        self.expect(TokenType.LBRACE)
        values = []
        
        if not self.match(TokenType.RBRACE):
            while True:
                values.append(self.parse_expression())
                if not self.match(TokenType.COMMA):
                    break
                self.advance()
        
        self.expect(TokenType.RBRACE)
        return BraceInitNode(values)

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
            
            # Guardar posição atual para detectar loop infinito
            old_pos = self.pos
            
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            
            # Se não avançou, há um problema - avançar manualmente para evitar loop infinito
            if self.pos == old_pos and not self.match(TokenType.RBRACE, TokenType.EOF):
                token = self.current_token()
                print(f"AVISO: Token não processado na linha {token.line}: {token.type.name if hasattr(token.type, 'name') else token.type} = '{token.lexeme}'")
                self.advance()  # Força avanço
            
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
                
                # Criar AttributeAccessNode inicial
                attr_access = AttributeAccessNode(obj_name, attr_name)
                
                # Suporte a acesso encadeado: this.obj.attr ou this.obj.arr[i]
                while self.match(TokenType.DOT):
                    self.advance()
                    next_attr = self.expect(TokenType.IDENT).lexeme
                    attr_access = AttributeAccessNode(attr_access, next_attr)
                
                # Verificar se é acesso a array (this.attr[index] ou this.obj.arr[index])
                if self.match(TokenType.LBRACKET):
                    self.advance()
                    index = self.parse_expression()
                    self.expect(TokenType.RBRACKET)
                    
                    # Verificar se há segunda dimensão
                    index2 = None
                    if self.match(TokenType.LBRACKET):
                        self.advance()
                        index2 = self.parse_expression()
                        self.expect(TokenType.RBRACKET)
                    
                    # Verificar se é acesso a método/atributo de objeto no array
                    if self.match(TokenType.DOT):
                        self.expect(TokenType.DOT)
                        member_name = self.expect(TokenType.IDENT).lexeme
                        
                        if self.match(TokenType.LPAREN):
                            # Chamada de método: this.produtos[i].metodo() ou this.obj.arr[i].metodo()
                            self.advance()
                            args = self.parse_arguments()
                            self.expect(TokenType.RPAREN)
                            if self.match(TokenType.SEMICOLON):
                                self.advance()
                            # Usar attr_access já construído
                            array_access = ArrayAccessWithObjectNode(attr_access, index, index2)
                            return ArrayElementMethodCallNode(array_access, member_name, args)
                        elif self.match(TokenType.ASSIGN):
                            # Atribuição: this.produtos[i].nome = valor ou this.obj.arr[i].nome = valor
                            self.advance()
                            expression = self.parse_expression()
                            if self.match(TokenType.SEMICOLON):
                                self.advance()
                            array_access = ArrayAccessWithObjectNode(attr_access, index, index2)
                            return ArrayElementAttributeAssignmentNode(array_access, member_name, expression)
                    elif self.match(TokenType.ASSIGN):
                        # Atribuição simples a elemento do array: this.produtos[i] = valor ou this.obj.arr[i] = valor
                        self.advance()
                        expression = self.parse_expression()
                        if self.match(TokenType.SEMICOLON):
                            self.advance()
                        # Para compatibilidade com ObjectAttributeArrayAssignmentNode, 
                        # extrair object_name e attr_name do attr_access final
                        if isinstance(attr_access, AttributeAccessNode):
                            # Se attr_access é encadeado, precisamos usar o nó completo
                            # mas ObjectAttributeArrayAssignmentNode espera strings
                            # Vamos mudar para usar ArrayAccessWithObjectNode + AttributeAssignmentNode
                            array_access = ArrayAccessWithObjectNode(attr_access, index, index2)
                            # Retornar uma atribuição ao elemento do array
                            return ObjectAttributeArrayAssignmentNode(obj_name, attr_name, index, expression, index2)
                elif self.match(TokenType.ASSIGN):
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
                
                # Verificar se há segunda dimensão
                index2 = None
                if self.match(TokenType.LBRACKET):
                    self.advance()
                    index2 = self.parse_expression()
                    self.expect(TokenType.RBRACKET)
                
                # Verificar se é acesso a método/atributo de objeto no array
                if self.match(TokenType.DOT):
                    self.expect(TokenType.DOT)
                    member_name = self.expect(TokenType.IDENT).lexeme
                    
                    if self.match(TokenType.LPAREN):
                        # Chamada de método em elemento do array
                        self.advance()
                        args = self.parse_arguments()
                        self.expect(TokenType.RPAREN)
                        if self.match(TokenType.SEMICOLON):
                            self.advance()
                        # Criar node especial para método em array
                        array_access = ArrayAccessNode(array_name, index, index2)
                        return ArrayElementMethodCallNode(array_access, member_name, args)
                    elif self.match(TokenType.ASSIGN):
                        # Atribuição a atributo de elemento do array
                        self.advance()
                        expression = self.parse_expression()
                        if self.match(TokenType.SEMICOLON):
                            self.advance()
                        array_access = ArrayAccessNode(array_name, index, index2)
                        return ArrayElementAttributeAssignmentNode(array_access, member_name, expression)
                    else:
                        # Acesso a atributo de elemento do array
                        array_access = ArrayAccessNode(array_name, index, index2)
                        return ArrayElementAttributeAccessNode(array_access, member_name)
                elif self.match(TokenType.ASSIGN):
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
                        assign_node = ArrayAssignmentNode(array_name, index, IdentifierNode(temp_var), index2)
                        return BlockNode("seq", [input_node, assign_node])
                    else:
                        expression = self.parse_expression()
                        if self.match(TokenType.SEMICOLON):
                            self.advance()
                        return ArrayAssignmentNode(array_name, index, expression, index2)
                else:
                    if self.match(TokenType.SEMICOLON):
                        self.advance()
                    return ArrayAccessNode(array_name, index, index2)
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
        left = self.parse_logical_and()
        return left
    
    def parse_logical_and(self):
        left = self.parse_logical_or()
        
        while self.match(TokenType.AND):
            operator = self.advance().lexeme
            right = self.parse_logical_or()
            left = BinaryOpNode(left, operator, right)
        
        return left
    
    def parse_logical_or(self):
        left = self.parse_relational()
        
        while self.match(TokenType.OR):
            operator = self.advance().lexeme
            right = self.parse_relational()
            left = BinaryOpNode(left, operator, right)
        
        return left
    
    def parse_relational(self):
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
        
        while self.match(TokenType.MUL, TokenType.DIV, TokenType.MOD):
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
        elif self.match(TokenType.NEW):
            self.advance()
            class_name = self.expect(TokenType.IDENT).lexeme
            self.expect(TokenType.LPAREN)
            self.expect(TokenType.RPAREN)
            return NewExpressionNode(class_name)
        elif self.match(TokenType.THIS):
            name = self.advance().lexeme
            if self.match(TokenType.DOT):
                self.advance()
                attr_or_method = self.expect(TokenType.IDENT).lexeme
                
                # Criar AttributeAccessNode inicial
                result = AttributeAccessNode(name, attr_or_method)
                
                # Suporte a acesso encadeado: this.obj.attr ou this.obj.method()
                while self.match(TokenType.DOT):
                    self.advance()
                    next_attr = self.expect(TokenType.IDENT).lexeme
                    # Encadear: result se torna o objeto base para o próximo acesso
                    result = AttributeAccessNode(result, next_attr)
                
                # Verificar se é chamada de método no final da cadeia
                if self.match(TokenType.LPAREN):
                    self.advance()
                    args = self.parse_arguments()
                    self.expect(TokenType.RPAREN)
                    # Converter último AttributeAccessNode para MethodCallNode
                    if isinstance(result, AttributeAccessNode):
                        return MethodCallNode(result.object_name, result.attribute_name, args)
                elif self.match(TokenType.LBRACKET):
                    # this.attribute[index] - atributo é array
                    self.advance()
                    index = self.parse_expression()
                    self.expect(TokenType.RBRACKET)
                    
                    # Verificar se há segunda dimensão
                    index2 = None
                    if self.match(TokenType.LBRACKET):
                        self.advance()
                        index2 = self.parse_expression()
                        self.expect(TokenType.RBRACKET)
                    
                    # Verificar se é acesso a atributo/método de objeto no array
                    if self.match(TokenType.DOT):
                        self.advance()
                        member_name = self.expect(TokenType.IDENT).lexeme
                        if self.match(TokenType.LPAREN):
                            # this.array[i].metodo() ou this.obj.array[i].metodo()
                            self.advance()
                            args = self.parse_arguments()
                            self.expect(TokenType.RPAREN)
                            # Usar result (cadeia completa) ao invés de reconstruir
                            array_access = ArrayAccessWithObjectNode(result, index, index2)
                            return ArrayElementMethodCallNode(array_access, member_name, args)
                        else:
                            # this.array[i].attribute ou this.obj.array[i].attribute
                            # Usar result (cadeia completa) ao invés de reconstruir
                            array_access = ArrayAccessWithObjectNode(result, index, index2)
                            return ArrayElementAttributeAccessNode(array_access, member_name)
                    else:
                        # this.array[i] ou this.obj.arr[i]
                        # Usar result (cadeia completa)
                        return ArrayAccessWithObjectNode(result, index, index2)
                else:
                    # Retornar o resultado (pode ser encadeado)
                    return result
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
                
                # Verificar se há segunda dimensão
                index2 = None
                if self.match(TokenType.LBRACKET):
                    self.advance()
                    index2 = self.parse_expression()
                    self.expect(TokenType.RBRACKET)
                
                # Verificar se é acesso a atributo/método de objeto no array
                if self.match(TokenType.DOT):
                    self.advance()
                    attr_or_method = self.expect(TokenType.IDENT).lexeme
                    if self.match(TokenType.LPAREN):
                        # Chamada de método em elemento do array
                        self.advance()
                        args = self.parse_arguments()
                        self.expect(TokenType.RPAREN)
                        array_access = ArrayAccessNode(name, index, index2)
                        return ArrayElementMethodCallNode(array_access, attr_or_method, args)
                    else:
                        # Acesso a atributo de elemento do array
                        array_access = ArrayAccessNode(name, index, index2)
                        return ArrayElementAttributeAccessNode(array_access, attr_or_method)
                
                return ArrayAccessNode(name, index, index2)
            elif self.match(TokenType.DOT):
                self.advance()
                attr_or_method = self.expect(TokenType.IDENT).lexeme
                
                # Criar AttributeAccessNode inicial
                result = AttributeAccessNode(name, attr_or_method)
                
                # Suporte a acesso encadeado: obj.obj2.attr
                while self.match(TokenType.DOT):
                    self.advance()
                    next_attr = self.expect(TokenType.IDENT).lexeme
                    result = AttributeAccessNode(result, next_attr)
                
                # Verificar se é chamada de método no final da cadeia
                if self.match(TokenType.LPAREN):
                    self.advance()
                    args = self.parse_arguments()
                    self.expect(TokenType.RPAREN)
                    if isinstance(result, AttributeAccessNode):
                        return MethodCallNode(result.object_name, result.attribute_name, args)
                elif self.match(TokenType.LBRACKET):
                    # object.attribute[index] - atributo é array
                    self.advance()
                    index = self.parse_expression()
                    self.expect(TokenType.RBRACKET)
                    
                    # Verificar se há segunda dimensão
                    index2 = None
                    if self.match(TokenType.LBRACKET):
                        self.advance()
                        index2 = self.parse_expression()
                        self.expect(TokenType.RBRACKET)
                    
                    # Verificar se é acesso a atributo/método de objeto no array
                    if self.match(TokenType.DOT):
                        self.advance()
                        member_name = self.expect(TokenType.IDENT).lexeme
                        if self.match(TokenType.LPAREN):
                            # object.array[i].metodo()
                            self.advance()
                            args = self.parse_arguments()
                            self.expect(TokenType.RPAREN)
                            attr_access = AttributeAccessNode(name, attr_or_method)
                            array_access = ArrayAccessWithObjectNode(attr_access, index, index2)
                            return ArrayElementMethodCallNode(array_access, member_name, args)
                        else:
                            # object.array[i].attribute
                            attr_access = AttributeAccessNode(name, attr_or_method)
                            array_access = ArrayAccessWithObjectNode(attr_access, index, index2)
                            return ArrayElementAttributeAccessNode(array_access, member_name)
                    else:
                        # object.array[i]
                        attr_access = AttributeAccessNode(name, attr_or_method)
                        return ArrayAccessWithObjectNode(attr_access, index, index2)
                else:
                    # Retornar o resultado (pode ser encadeado)
                    return result
            return IdentifierNode(name)
        elif self.match(TokenType.LPAREN):
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        elif self.match(TokenType.STRLEN, TokenType.SUBSTR, TokenType.CHARAT, TokenType.INDEXOF, TokenType.PARSEINT):
            name = self.advance().lexeme
            self.expect(TokenType.LPAREN)
            args = self.parse_arguments()
            self.expect(TokenType.RPAREN)
            return FunctionCallNode(name, args)
        elif self.match(TokenType.MINUS):
            operator = self.advance().lexeme
            operand = self.parse_unary()
            return UnaryOpNode(operator, operand)
        else:
            raise SyntaxError(f"Unexpected token: {self.current_token()}")  # nó raiz da AST
