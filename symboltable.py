from scanner import Token



class SymbolTable:
    def __init__(self):
        self.symbols = []

    def fetch(self,identifier,scope):
        results = filter( lambda record: record['identifier']==identifier and record['scope']==scope, self.symbols)
        if len(results):
            return results[0]
        else:
            return None

    def _new_symbol(self):
        return {
            'identifier': '',
            'type': '',
            'scope':'',
            'data_type':'',
            'array_length':None
        }

    def printable_string(self):
        string = '%-20s%-20s%-20s%-20s%-20s\n'%('identifier','type','data_type','array_length','scope')
        for s in self.symbols:
            string += '%-20s%-20s%-20s%-20s%-20s\n'%(str(s['identifier']),str(s['type']),str(s['data_type']),str(s['array_length']),str(s['scope']))
        return string

    def create_symbol_from_declaration(self, declaration, current_scope):
        if not len(declaration.children):
            raise Exception("<declaration> node with no child node encoutered.")
        else:
            child = declaration.children[0]
            if child.name_matches('procedure_declaration'):
                symbol = self.create_symbol_from_procedure_declaration(child, current_scope)
            elif child.name_matches('variable_declaration'):
                symbol = self.create_symbol_from_variable_declaration(child, current_scope)
            else:
                raise Exception('%s is not a valid child node for type <declaration>'%(child.name))
            if declaration.token and declaration.token.value_matches('global'):
                symbol['global'] = True
            else:
                symbol['global'] = False

        self.symbols.append(symbol)

    def create_symbol_from_variable_declaration(self, variable_declaration, current_scope):
        symbol = self._new_symbol()
        symbol['data_type'] = variable_declaration.children[0].token.value
        symbol['identifier'] = variable_declaration.children[1].token.value
        if len(variable_declaration.children) >= 3:
            symbol['type'] = 'array'
            symbol['array_length'] = variable_declaration.children[2].token.value
        else:
            symbol['type'] = 'variable'
            symbol['array_length'] = None
        return symbol

    def create_symbol_from_procedure_declaration(self, procedure_declaration, current_scope):
        symbol = self._new_symbol()
        symbol['type'] = 'procedure'
        procedure_header = procedure_declaration.children[0]
        symbol['identifier'] = procedure_header.children[0].token.value
        if len(procedure_header.children) >= 2:
            parameter_list = procedure_header.children[1]
            while True:
                parameter = parameter_list.children[0]
                variable_declaration = parameter.children[0]
                arg_symbol = self.create_symbol_from_variable_declaration(variable_declaration,current_scope)
                self.symbols.append(arg_symbol)
                if len(parameter_list.children) > 1:
                    parameter_list = parameter_list.children[1]
                else:
                    break
        return symbol
