from scanner import Token


class ScopeStack:
    def __init__(self):
        self.stack = []

    def push(self,scope):
        self.stack.append(scope)

    def pop(self):
        if len(self.stack):
            self.stack.pop()

    def as_string(self):
        return '/'.join(self.stack)

    def as_list(self):
        return self.stack



class SymbolTable:
    def __init__(self):
        self._symbols = []
        self._scope_stack = ScopeStack()
        self._errors = False

        self._scope_stack.push('main')


    def fetch(self,identifier,scope):
        symbol = self._fetch(identifier,scope)
        if symbol is not None:
            return symbol
        else:
            # a procedure name found in the parent scope counts too.
            parent_scope = '/'.join(scope.split('/')[:-1])
            symbol = self._fetch(identifier,parent_scope)
            if symbol is not None and symbol['type'] == 'procedure':
                return symbol
            else:
                return None

    def _fetch(self,identifier,scope):
        results = filter( lambda record: record['identifier']==identifier and record['scope']==scope, self._symbols)
        if len(results):
            return results[0]
        else:
            return None

    def errors(self):
        return self._errors

    def populate(self,node):
        if node.name_matches('declaration'):
            child = node.children[0]
            if child.name_matches('variable_declaration'):
                symbol = self._create_symbol_from_variable_declaration(child)
            else: # procedure_declaration
                symbol = self._create_symbol_from_procedure_declaration(child)
            if node.token and node.token.value_matches('global'):
                symbol['global'] = True;
            self._validate_and_save(symbol)
        else:
            for child in node.children:
                self.populate(child)

    def printable_string(self):
        string = '%-20s%-20s%-20s%-20s%-20s\n'%('identifier','type','data_type','array_length','scope')
        for s in self._symbols:
            string += '%-20s%-20s%-20s%-20s%-20s\n'%(str(s['identifier']),str(s['type']),str(s['data_type']),str(s['array_length']),str(s['scope']))
        return string

    def _new_symbol(self):
        return {
            'identifier':'',
            'type': '',
            'scope':'',
            'data_type':'',
            'array_length':None
        }

    def _report_error(self, message):
        print "SYMBOL ERROR: " + message

    def _is_valid(self,symbol):
        return self.fetch(symbol['identifier'],symbol['scope']) == None

    def _validate_and_save(self,symbol):
        if self._is_valid(symbol):
            self._symbols.append(symbol)
        else:
            self._report_error("")
            self._errors = True

    def _create_symbol_from_variable_declaration(self, variable_declaration):
        symbol = self._new_symbol()
        symbol['scope'] = self._scope_stack.as_string()
        symbol['data_type'] = variable_declaration.children[0].token.value
        symbol['identifier'] = variable_declaration.children[1].token.value
        if len(variable_declaration.children) >= 3:
            symbol['type'] = 'array'
            symbol['array_length'] = variable_declaration.children[2].token.value
        else:
            symbol['type'] = 'variable'
            symbol['array_length'] = None
        return symbol

    def _create_symbol_from_procedure_declaration(self, procedure_declaration):
        procedure_header = procedure_declaration.children[0]
        procedure_body = procedure_declaration.children[1]
        symbol = self._new_symbol()
        symbol['type'] = 'procedure'
        symbol['scope'] = self._scope_stack.as_string()
        symbol['identifier'] = procedure_header.children[0].token.value
        self._scope_stack.push(symbol['identifier'])
        if len(procedure_header.children) >= 2:
            parameter_list = procedure_header.children[1]
            while True:
                parameter = parameter_list.children[0]
                variable_declaration = parameter.children[0]
                arg_symbol = self._create_symbol_from_variable_declaration(variable_declaration)
                self._validate_and_save(arg_symbol)
                if len(parameter_list.children) > 1:
                    parameter_list = parameter_list.children[1]
                else:
                    break
        self.populate(procedure_body)
        self._scope_stack.pop()
        return symbol
