from scanner import Token
from runtimeprocedures import SYMBOL_TABLE_ENTRIES

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

    def push_node(self,node):
        if node.name_matches('procedure_declaration'):
            header = node.children[0]
            identifier = header.children[0]
            self.push(identifier.token.value)

    def pop_node(self,node):
        if node.name_matches('procedure_declaration'):
            self.pop()

class SymbolTable:
    def __init__(self):
        self._symbols = []
        self._scope_stack = ScopeStack()
        self._errors = False

        self._scope_stack.push('main')
        self._symbols += SYMBOL_TABLE_ENTRIES


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
        results = filter( lambda record: record['identifier']==identifier and (record['scope']==scope or record["global"]), self._symbols)
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
                self.populate(child.children[1]) # check procedure body
            if node.token and node.token.value_matches('global'):
                symbol['global'] = True;
            if not self._validate_and_save(symbol):
                self._report_attempted_redefinition(symbol['identifier'], symbol['definition_line'])
        else:
            for child in node.children:
                self.populate(child)

        if node.name_matches('procedure_body'):
            self._scope_stack.pop()

    def printable_string(self):
        string = '%-20s%-20s%-20s%-20s%-20s%-20s%-20s%-20s%-20s\n'%('identifier','type','data_type','array_length','scope','is_argument','direction','initialized','global')
        for s in self._symbols:
            string += '%-20s%-20s%-20s%-20s%-20s%-20s%-20s%-20s%-20s\n'%(str(s['identifier']),
                                                                    str(s['type']),
                                                                    str(s['data_type']),
                                                                    str(s['array_length']),
                                                                    str(s['scope']),
                                                                    str(s['is_argument']),
                                                                    str(s['direction']),
                                                                    str(s['initialized']),
                                                                    str(s['global']))
        return string

    def get_expected_arguments(self,identifier):
        return filter( lambda record: record['scope']=='main/'+identifier and \
                                      record['is_argument']==True, self._symbols)

    def _new_symbol(self):
        return {
            'identifier':'',
            'type': '',
            'scope':'',
            'data_type':'',
            'array_length':None,
            'direction':None,
            'is_argument':False,
            'definition_line':-1,
            'initialized': False,
            'global': False
        }

    def _is_valid(self,symbol):
        return self.fetch(symbol['identifier'],symbol['scope']) == None

    def _validate_and_save(self,symbol):
        if self._is_valid(symbol):
            self._symbols.append(symbol)
            return True
        else:
            self._errors = True
            return False

    def _create_symbol_from_variable_declaration(self, variable_declaration):
        symbol = self._new_symbol()
        symbol['scope'] = self._scope_stack.as_string()
        symbol['data_type'] = variable_declaration.children[0].token.value
        symbol['identifier'] = variable_declaration.children[1].token.value
        symbol['definition_line'] = variable_declaration.children[1].token.line
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
        symbol['definition_line'] = procedure_header.children[0].token.line
        self._scope_stack.push(symbol['identifier'])
        if len(procedure_header.children) >= 2:
            parameter_list = procedure_header.children[1]
            while True:
                parameter = parameter_list.children[0]
                variable_declaration = parameter.children[0]
                arg_symbol = self._create_symbol_from_variable_declaration(variable_declaration)
                arg_symbol['is_argument'] = True
                arg_symbol['direction'] = parameter.token.value
                self._validate_and_save(arg_symbol)
                if len(parameter_list.children) > 1:
                    parameter_list = parameter_list.children[1]
                else:
                    break
        return symbol


    def _report_error(self,message,line):
        print "SEMANTIC ERROR (line %s): %s"%(str(line), message)

    def _report_attempted_redefinition(self,name,line_no):
        message = "Attempted redefinition of symbol \'%s\' in present scope."%(name)
        self._report_error(message,line_no)
