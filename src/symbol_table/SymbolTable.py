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
    
    def enter_scope(self):
        self.scope_level += 1
        new_scope = Scope(self.scope_level, self.current_scope)
        self.current_scope = new_scope
        return new_scope
    
    def exit_scope(self):
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent
            self.scope_level -= 1
    
    def define(self, name, symbol_type, value=None, is_array=False, array_size=None):
        with self.lock:
            if self.current_scope.exists(name):
                return self.current_scope.lookup(name)
            symbol = Symbol(name, symbol_type, value, self.scope_level, is_array, array_size)
            self.current_scope.define(name, symbol)
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
