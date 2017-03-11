from symboltable import SymbolTable, ScopeStack

class SemanticAnalyzer:

    RESERVED_KEY_WORDS = ['program','is','begin','procedure','end','global','in','out','inout','integer','bool','char','string','float','if','then','else','loop','return','not','false','true']

    def __init__(self):
        self._parse_tree = None
        self._symbol_table = None
        self._errors = False
        self._scope_stack = ScopeStack()

        self._scope_stack.push('main')

    def errors(self):
        return self._errors

    def analyze(self,parse_tree,symbol_table):
        self._symbol_table = symbol_table
        self._check_for_valid_identifiers(parse_tree)
        self._check_for_scope_errors(parse_tree.children[1]) # skip the program name

    def _check_for_valid_identifiers(self, node):
        if node.name_matches('identifier'):
            if node.token.value in SemanticAnalyzer.RESERVED_KEY_WORDS:
                report_error("Attempt to use a reserved key word as an identifier", node.token.line)
        else:
            for child in node.children:
                self._check_for_valid_identifiers(child)

    def _check_for_scope_errors(self,node):
        if node.name_matches('procedure_declaration'):
            header = node.children[0]
            identifier = header.children[0]
            self._scope_stack.push(identifier.token.value)
        elif node.name_matches('identifier'):
            value = node.token.value
            line = node.token.line
            scope = self._scope_stack.as_string()
            if not self._symbol_table.fetch(value,scope):
                report_error("Identifer, \'%s\' not found in current scope"%(value),line)
        for child in node.children:
            self._check_for_scope_errors(child)
        if node.name_matches('procedure_declaration'):
            self._scope_stack.pop()

def report_error(message,line):
    print "SEMANTIC ERROR (line %s): %s"%(str(line), message)
