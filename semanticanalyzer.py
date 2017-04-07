from symboltable import SymbolTable, ScopeStack
import constants


class SemanticAnalyzer:

    RESERVED_KEY_WORDS = constants.RESERVED_KEY_WORDS
    EXPRESSION_OPS = constants.EXPRESSION_OPS
    ARITH_OPS = constants.ARITH_OPS
    RELATION_OPS = constants.RELATION_OPS
    TERM_OPS = constants.TERM_OPS
    BINARY_OPS = constants.BINARY_OPS

    def __init__(self):
        self._parse_tree = None
        self._symbol_table = None
        self._errors = False
        self._scope_stack = ScopeStack()

        self._scope_stack.push('main')

    def errors(self):
        return self._errors

    def analyze(self,parse_tree,symbol_table):
        program_body = parse_tree.children[1]
        self._symbol_table = symbol_table
        self._check_for_valid_identifiers(parse_tree)
        self._check_for_scope_errors(program_body)
        self._check_data_types(program_body)
        self._check_arguments(program_body)


    def _scope_stack_push(self,node):
        if node.name_matches('procedure_declaration'):
            header = node.children[0]
            identifier = header.children[0]
            self._scope_stack.push(identifier.token.value)

    def _scope_stack_pop(self,node):
        if node.name_matches('procedure_declaration'):
            self._scope_stack.pop()

    def _check_arguments(self,node):
        self._scope_stack_push(node)
        if node.name_matches('procedure_call'):
            identifier = node.children[0].token.value
            line = node.children[0].token.line
            given_args = self._get_given_args(node)
            expected_args = self._symbol_table.get_expected_arguments(identifier)
            self._compare_expected_and_given_args(expected_args,given_args,line)
        else:
            for child in node.children:
                self._check_arguments(child)
        self._scope_stack_pop(node)

    def _compare_expected_and_given_args(self,expected,given,line):
        given_len = len(given)
        expected_len = len(expected)

        for i in range(min(given_len,expected_len)):
            if given[i]['type'] != expected[i]['data_type']:
                print "type missmatch"
            if given[i]['dimension'] != expected[i]['array_length']:
                print "dim missmatch"
            if given[i]['literal'] and expected[i]['direction'] != 'in':
                print "byVal error"

        if given_len < expected_len:
            report_error("Too few arguments in procedure call.",line)
        elif given_len > expected_len:
            report_error("Too many arguments in procedure call.",line)
            print given
            print expected
        else:
            pass

    def _get_dimension(self,node):
        dimensions = []
        if len(node.children):
            for child in node.children:
                dim = self._get_dimension(child)
                if dim != 1:
                    dimensions.append(dim)
            if len(set(dimensions)) != 1:
                return 'undefined'
            else:
                return dimensions[0]
        else:
            symbol = self._symbol_table.fetch(node.token.value,self._scope_stack.as_string())

    def _check_for_literal(self,node):
        if len(node.children):
            return self._check_for_literal(node.children[0])
        else:
            return node.token.is_literal()

    def _get_given_args(self, procedure_call):
        given_args = []
        if len(procedure_call.children) == 2:
            arg_list = procedure_call.children[1]
            while True:
                arg_node = arg_list.children[0]
                arg = {
                    'type': self._check_data_types(arg_node),
                    'dimension': self._get_dimension(arg_node),
                    'literal': self._check_for_literal(arg_node)
                }
                given_args.append(arg)
                if len(arg_list.children) == 2:
                    arg_list = arg_list.children[1]
                else:
                    break
        return given_args

    def _check_for_valid_identifiers(self, node):
        if node.name_matches('identifier'):
            if node.token.value in SemanticAnalyzer.RESERVED_KEY_WORDS:
                report_error("Attempt to use a reserved key word as an identifier", node.token.line)
        else:
            for child in node.children:
                self._check_for_valid_identifiers(child)

    def _check_for_scope_errors(self,node):
        self._scope_stack_push(node)
        if node.name_matches('procedure_declaration'):
            header = node.children[0]
            identifier = header.children[0]
        elif node.name_matches('identifier'):
            value = node.token.value
            line = node.token.line
            scope = self._scope_stack.as_string()
            if not self._symbol_table.fetch(value,scope):
                report_error("Identifer, \'%s\' not found in current scope"%(value),line)
        for child in node.children:
            self._check_for_scope_errors(child)
        self._scope_stack_pop(node)

    def _handle_binary_operation(self, node):
        operator = node.token.value
        datatype1 = self._check_data_types(node.children[0])
        datatype2 = self._check_data_types(node.children[1])
        datatype3 = self._get_return_type(datatype1,datatype2,operator)
        if datatype3 is not None:
            return datatype3
        else:
            line = node.token.line
            report_type_error(datatype1,datatype2,operator,line)
            return "[undefined due to previous error]"

    def _handle_assignment_statement(self,node):
        datatype1 = self._check_data_types(node.children[0])
        datatype2 = self._check_data_types(node.children[1])
        if not self._valid_assignment_types(datatype1,datatype2):
            line = node.token.line
            report_type_error(datatype1,datatype2,':=',line)

    def _handle_identifier(self, node):
        scope = self._scope_stack.as_string()
        name = node.token.value
        symbol = self._symbol_table.fetch(name,scope)
        if symbol is not None:
            if len(node.children) == 1:
                self._check_data_types(node.children[0])
            return symbol['data_type']
        else:
            return 'undefined'

    def _handle_number(self, node):
        if '.' in node.token.value:
            return 'float'
        else:
            return 'integer'

    def _check_data_types(self, node):
        #if node.token is not None:
        #    print "DEBUG: " + node.token.value + " " + str(node.token.line)
        return_value = None
        if node.name_matches('procedure_declaration'):
            header = node.children[0]
            identifier = header.children[0]
            self._scope_stack.push(identifier.token.value)
        else:
            if node.is_binary_operation():
                return_value = self._handle_binary_operation(node)
            elif node.name_matches("assignment_statement"):
                self._handle_assignment_statement(node)
            elif node.name_matches('identifier'):
                return_value = self._handle_identifier(node)
            elif node.name_matches('number'):
                return_value = self._handle_number(node)
            elif node.name_matches('string'):
                return_value = 'string'
            elif node.name_matches('character'):
                return_value = 'char'
            elif node.token and node.token.value_matches(['true','false']):
                return_value = 'bool'
            else:
                type_aquired = False
                for child in node.children:
                    result = self._check_data_types(child)
                    if result is not None and not type_aquired:
                        return_value = result
                        type_aquired = True
        if node.name_matches('procedure_declaration'):
            self._scope_stack.pop()
        return return_value


    def _get_return_type(self,datatype1,datatype2,operator):
        if operator in SemanticAnalyzer.EXPRESSION_OPS:
            valid_types = ['bool','integer']
            if datatype1 in valid_types and datatype2 in valid_types:
                return 'bool'
            else:
                return None
        elif operator in SemanticAnalyzer.ARITH_OPS:
            valid_types = ['float','integer']
            if datatype1 in valid_types and datatype2 in valid_types:
                if datatype1 == 'float' or datatype2 == 'float':
                    return 'float'
                else:
                    return 'integer'
            else:
                return None
        elif operator in SemanticAnalyzer.RELATION_OPS:
            if datatype1 == 'bool' and datatype2 == 'bool':
                return 'bool'
            elif datatype1 == 'integer' and datatype2 == 'integer':
                return 'bool'
            else:
                return None
        elif operator in SemanticAnalyzer.TERM_OPS:
            valid_types = ['float','integer']
            if datatype1 == datatype2 == 'integer':
                return 'integer'
            elif datatype1 in valid_types and datatype2 in valid_types:
                return 'float'
            else:
                return None
        else:
            raise Exception('Not a valid binary operator: %s'%(operator))

    def _valid_assignment_types(self,datatype1,datatype2):
        if datatype1 == datatype2:
            return True
        elif datatype1 == 'integer' and datatype2 == 'float':
            return True
        elif datatype1 == 'float' and datatype2 == 'integer':
            return True
        elif datatype1 == 'bool' and datatype2 == 'integer':
            return True
        elif datatype1 == 'integer' and datatype2 == 'bool':
            return True
        else:
            return False

    def _get_likely_return_type(self,operator):
        if operator in SemanticAnalyzer.EXPRESSION_OPS:
            return 'bool'
        elif operator in SemanticAnalyzer.ARITH_OPS:
            return 'integer'
        elif operator in SemanticAnalyzer.RELATION_OPS:
            return 'bool'
        elif operator in SemanticAnalyzer.TERM_OPS:
            return 'integer'
        elif operator == ':=':
            return "[doesn't matter]"
        else:
            raise Exception('Not a valid binary operator: %s'%(operator))

def report_error(message,line):
    print "SEMANTIC ERROR (line %s): %s"%(str(line), message)

def report_type_error(type_1, type_2, operator, line):
    message = "datatype error: %s %s %s."%(type_1,operator,type_2)
    report_error(message,line)
