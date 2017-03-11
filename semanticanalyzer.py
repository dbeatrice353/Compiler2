from symboltable import SymbolTable

class SemanticAnalyzer:
    def __init__(self):
        self._parse_tree = None
        self._symbol_table = None
        self._errors = False

    def errors(self):
        return self._errors

    def analyze(self,parse_tree,symbol_table):
        
