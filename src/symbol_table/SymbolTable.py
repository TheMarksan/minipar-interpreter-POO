import threading


class Symbol:
    def __init__(self, name, symbol_type, value=None, scope_level=0, is_array=False, array_size=None):
        self.name = name
        self.symbol_type = symbol_type
        self.value = value
        self.scope_level = scope_level
        self.is_array = is_array
        self.array_size = array_size
        self.is_function = False
        self.is_class = False
        self.parameters = []
        self.return_type = None
    
    def __repr__(self):
        return f"Symbol({self.name}, {self.symbol_type}, scope={self.scope_level})"


class Scope:
    def __init__(self, scope_level, parent=None):
        self.scope_level = scope_level
        self.parent = parent
        self.symbols = {}
    
    def define(self, name, symbol):
        if name in self.symbols:
            raise Exception(f"Symbol '{name}' already defined in current scope")
        self.symbols[name] = symbol
    
    def lookup(self, name):
        if name in self.symbols:
            return self.symbols[name]
        return None
    
    def lookup_recursive(self, name):
        symbol = self.lookup(name)
        if symbol:
            return symbol
        if self.parent:
            return self.parent.lookup_recursive(name)
        return None
    
    def update(self, name, value):
        if name in self.symbols:
            self.symbols[name].value = value
            return True
        if self.parent:
            return self.parent.update(name, value)
        return False
    
    def exists(self, name):
        return name in self.symbols
    
    def exists_recursive(self, name):
        if self.exists(name):
            return True
        if self.parent:
            return self.parent.exists_recursive(name)
        return False


class SymbolTable:
    def __init__(self):
        self.global_scope = Scope(0)
        self.lock = threading.Lock()
        self.current_scope = self.global_scope
        self.scope_level = 0
        self.all_symbols = []  # Lista para rastrear todos os símbolos declarados
    
    def enter_scope(self):
        self.scope_level += 1
        new_scope = Scope(self.scope_level, self.current_scope)
        self.current_scope = new_scope
        return new_scope
    
    def exit_scope(self):
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent
            self.scope_level -= 1
    
    def to_dict(self):
        """Serializa a tabela de símbolos para um dicionário JSON-serializável"""
        def symbol_to_dict(symbol):
            return {
                'name': symbol.name,
                'type': symbol.symbol_type,
                'value': str(symbol.value) if symbol.value is not None else None,
                'scope_level': symbol.scope_level,
                'is_array': symbol.is_array,
                'array_size': symbol.array_size,
                'is_function': symbol.is_function,
                'is_class': symbol.is_class,
                'return_type': symbol.return_type,
                'parameters': [{'name': p[1], 'type': p[0]} for p in symbol.parameters] if symbol.parameters else []
            }
        
        # Separar símbolos por categoria
        variables = []
        functions = []
        classes = []
        types = []
        
        # Coletar símbolos do escopo global
        for name, symbol in self.global_scope.symbols.items():
            sym_dict = symbol_to_dict(symbol)
            if symbol.symbol_type == 'type':
                # Pular tipos built-in do sistema
                if name.lower() not in ['int', 'float', 'string', 'bool', 'char', 'void', 'c_channel']:
                    types.append(sym_dict)
            elif symbol.is_function:
                # Pular funções built-in
                if name not in ['strlen', 'substr', 'charat', 'indexof', 'parseint', 'print', 'input']:
                    functions.append(sym_dict)
            elif symbol.is_class:
                classes.append(sym_dict)
            else:
                variables.append(sym_dict)
        
        # Adicionar símbolos rastreados durante a análise
        for symbol in self.all_symbols:
            sym_dict = symbol_to_dict(symbol)
            if symbol.is_function and symbol.name not in [f['name'] for f in functions]:
                functions.append(sym_dict)
            elif symbol.is_class and symbol.name not in [c['name'] for c in classes]:
                classes.append(sym_dict)
            elif not symbol.is_function and not symbol.is_class and symbol.symbol_type != 'type':
                if symbol.name not in [v['name'] for v in variables]:
                    variables.append(sym_dict)
        
        return {
            'variables': variables,
            'functions': functions,
            'classes': classes,
            'user_types': types,
            'total_symbols': len(variables) + len(functions) + len(classes) + len(types)
        }
    
    def define(self, name, symbol_type, value=None, is_array=False, array_size=None):
        with self.lock:
            if self.current_scope.exists(name):
                return self.current_scope.lookup(name)
            symbol = Symbol(name, symbol_type, value, self.scope_level, is_array, array_size)
            self.current_scope.define(name, symbol)
            # Rastrear símbolo se não for built-in
            if symbol_type != 'type' and name not in ['strlen', 'substr', 'charat', 'indexof', 'parseint', 'print', 'input']:
                self.all_symbols.append(symbol)
            return symbol
    
    def define_function(self, name, return_type, parameters):
        with self.lock:
            if self.current_scope.exists(name):
                return self.current_scope.lookup(name)
            symbol = Symbol(name, return_type, None, self.scope_level)
            symbol.is_function = True
            symbol.return_type = return_type
            symbol.parameters = parameters
            self.current_scope.define(name, symbol)
            # Rastrear função se não for built-in
            if name not in ['strlen', 'substr', 'charat', 'indexof', 'parseint', 'print', 'input']:
                self.all_symbols.append(symbol)
            return symbol
    
    def define_class(self, name, attributes, methods, parent=None):
        with self.lock:
            if self.current_scope.exists(name):
                return self.current_scope.lookup(name)
            symbol = Symbol(name, "class", None, self.scope_level)
            symbol.is_class = True
            symbol.value = {
                'attributes': attributes,
                'methods': methods,
                'parent': parent
            }
            self.current_scope.define(name, symbol)
            self.all_symbols.append(symbol)
            return symbol
    
    def lookup(self, name):
        return self.current_scope.lookup_recursive(name)
    
    def update(self, name, value):
        symbol = self.lookup(name)
        if symbol:
            symbol.value = value
            return True
        return False
    
    def exists(self, name):
        return self.current_scope.exists_recursive(name)
    
    def get_value(self, name):
        symbol = self.lookup(name)
        if symbol:
            return symbol.value
        return None
    
    def get_all_symbols(self, scope=None):
        if scope is None:
            scope = self.current_scope
        
        symbols = []
        current = scope
        while current:
            for name, symbol in current.symbols.items():
                symbols.append(symbol)
            current = current.parent
        
        return symbols
    
    def print_table(self):
        print("=== Symbol Table ===")
        symbols = self.get_all_symbols()
        for symbol in symbols:
            print(f"  {symbol.name:20} | Type: {symbol.symbol_type:10} | Scope: {symbol.scope_level} | Value: {symbol.value}")
        print("=" * 80)
