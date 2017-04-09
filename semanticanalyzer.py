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
        self._operation_records = []
        self._operation_record_counter = 0;

        self._scope_stack.push('main')

    def errors(self):
        return self._errors

    def printable_string(self):
        if len(self._operation_records):
            headers = self._operation_records[0].keys()
            string = ''.join(map(lambda x: '%-15s'%x, headers)) + '\n'
            for record in self._operation_records:
                values = map(lambda x: str(record[x]),headers)
                string += ''.join(map(lambda x: '%-15s'%x, values)) + '\n'
            return string
        else:
            return 'no records'

    def print_argument_list_records(self):
        for record in self._argument_list_records:
            print record

    def analyze(self,parse_tree,symbol_table):
        self._operation_index_counter = 0
        program_body = parse_tree.children[1]
        self._symbol_table = symbol_table
        self._check_for_valid_identifiers(parse_tree)
        self._check_for_scope_errors(program_body)
        self._gather_operation_records(program_body)
        self._check_for_type_errors()
        self._check_for_dimensional_errors()
        self._check_array_index_types()

    def _next_operation_record_id(self):
        temp = self._operation_record_counter
        self._operation_record_counter += 1
        return temp

    def _scope_stack_push(self,node):
        if node.name_matches('procedure_declaration'):
            header = node.children[0]
            identifier = header.children[0]
            self._scope_stack.push(identifier.token.value)

    def _scope_stack_pop(self,node):
        if node.name_matches('procedure_declaration'):
            self._scope_stack.pop()

    def _check_for_type_errors(self):
        type_errors = filter(lambda r: r['dtype']==None and r['op1_dtype']!=None and r['op2_dtype']!=None, self._operation_records)
        for each in type_errors:
            report_type_error(each['op1_dtype'], each['op2_dtype'], each['operator'], each['line'])

    def _check_for_dimensional_errors(self):
        expression_errors = filter(lambda r: r['op1_dim'] != None and r['op2_dim'] != None and r['op1_dim'] != r['op2_dim'], self._operation_records)
        assignment_errors = filter(lambda r: r['op1_dim'] == None and r['op2_dim'] != None, self._operation_records)
        for each in expression_errors + assignment_errors:
            report_dimensional_error(each['op1_dim'], each['op2_dim'], each['line'])

    def _check_array_index_types(self):
        index_type_errors = filter(lambda r: r['is_index'] and r['is_root'] and r['dtype'] != 'integer',self._operation_records)
        for each in index_type_errors:
            report_error("array index must be of integer type",each['line'])

    def _gather_operation_records(self, node):
        self._scope_stack_push(node)
        if node.name_matches('assignment_statement') or node.name_matches('expression'):
            context = {'indexed':False, 'is_index':False, 'is_root':True}
            self._create_operation_records(node,context)
        else:
            for child in node.children:
                self._gather_operation_records(child)
        self._scope_stack_pop(node)

    def _create_operation_records(self,node,context):
        if node.is_binary_operation() or node.name_matches('assignment_statement'):
            record = self._create_record_from_binary_operation(node,context)
            self._operation_records.append(record)
            return record
        elif node.is_literal():
            record = self._create_record_from_operand(node,context)
            self._operation_records.append(record)
            return record
        elif node.name_matches('name') or node.name_matches('destination'):
            identifier = node.children[0]
            if len(node.children) == 2: # its an indexed array
                array_index_expression = node.children[1]
                context['is_index'] = True
                context['is_root'] = True
                self._create_operation_records(array_index_expression,context)
                context['is_index'] = False
                context['indexed'] = True
            record = self._create_record_from_operand(identifier,context)
            self._operation_records.append(record)
            return record
        else:
            if len(node.children) == 1:
                return self._create_operation_records(node.children[0],context)
            else:
                print node.name
                raise Exception("PROBLEM")

    def _create_record_from_binary_operation(self,node,context):
        is_root = context['is_root']
        context['is_root'] = False
        op1_record = self._create_operation_records(node.children[0],context)
        op2_record = self._create_operation_records(node.children[1],context)
        operator = node.token.value
        return {
                'id': self._next_operation_record_id(),
                'line': node.token.line,
                'operator': operator,
                'op1_dtype': op1_record['dtype'],
                'op2_dtype': op2_record['dtype'],
                'op1_dim': op1_record['dimension'],
                'op2_dim': op2_record['dimension'],
                'dtype': self._get_resulting_datatype(op1_record,op2_record,operator),
                'dimension': self._get_resulting_dimension(op1_record,op2_record,operator),
                'scope': self._scope_stack.as_string(),
                'is_index': context['is_index'],
                'is_root': is_root
                }

    def _create_record_from_operand(self,node,context):
        scope = self._scope_stack.as_string()
        is_root = context['is_root']
        context['is_root'] = False
        if node.name_matches('identifier'):
            symbol = self._symbol_table.fetch(node.token.value,scope)
            datatype = symbol['data_type']
            dimension = None if context['indexed'] else symbol['array_length']
        else:
            datatype = self._get_datatype_from_literal(node)
            dimension = None
        return {
                'id': self._next_operation_record_id(),
                'line': node.token.line,
                'operator': None,
                'op1_dtype': None,
                'op2_dtype': None,
                'op1_dim': None,
                'op2_dim': None,
                'dtype': datatype,
                'dimension': dimension,
                'scope': scope,
                'is_index': context['is_index'],
                'is_root': is_root
                }

    def _get_datatype_from_literal(self,node):
        if node.name_matches('string'):
            return 'string'
        elif node.name_matches('character'):
            return 'char'
        elif node.name_matches('number'):
            value = node.token.value
            if '.' in value:
                return 'float'
            else:
                return 'integer'
        else:
            return 'bool'

    def _get_resulting_datatype(self, op1, op2, operator):
        type1 = op1['dtype']
        type2 = op2['dtype']
        if operator in SemanticAnalyzer.EXPRESSION_OPS:
            valid_types = ['bool','integer']
            if type1 in valid_types and type2 in valid_types:
                return 'bool'
            else:
                return None
        elif operator in SemanticAnalyzer.ARITH_OPS:
            valid_types = ['float','integer']
            if type1 in valid_types and type2 in valid_types:
                if type1 == 'float' or type2 == 'float':
                    return 'float'
                else:
                    return 'integer'
            else:
                return None
        elif operator in SemanticAnalyzer.RELATION_OPS:
            if type1 == 'bool' and type2 == 'bool':
                return 'bool'
            elif type1 == 'integer' and type2 == 'integer':
                return 'bool'
            else:
                return None
        elif operator in SemanticAnalyzer.TERM_OPS:
            valid_types = ['float','integer']
            if type1 == type2 == 'integer':
                return 'integer'
            elif type1 in valid_types and type2 in valid_types:
                return 'float'
            else:
                return None
        elif operator == ':=':
            if type1 == type2:
                return type1
            elif type1 == 'float' and type2 == 'integer':
                return 'float'
            elif type1 == 'integer' and type2 == 'float':
                return 'integer'
            elif type1 == 'bool' and type2 == 'integer':
                return 'bool'
            elif type1 == 'integer' and type2 == 'bool':
                return 'integer'
            else:
                return None
        else:
            raise Exception('Not a valid binary operator: %s'%(operator))

    def _get_resulting_dimension(self, op1, op2, operator):
        dim1 = op1['dimension']
        dim2 = op1['dimension']
        if dim1 == dim2:                   # either both variable/const or equal-sized vectors
            return dim1
        elif dim1 == None or dim1 == None: # one is a variable/const the other is a vector
            return max(dim1,dim2)
        else:                              # vectors of different sizes
            report_error('dim missmatch')
            return max(dim1,dim2)

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

def report_error(message,line):
    print "SEMANTIC ERROR (line %s): %s"%(str(line), message)

def report_type_error(type_1, type_2, operator, line):
    message = "datatype error: %s %s %s."%(type_1,operator,type_2)
    report_error(message,line)

def report_dimensional_error(dim_1, dim_2, line):
    if dim_1 is not None:
        dim1 = "ARRAY[%sx1]"%dim_1
    else:
        dim1 = 'VARIABLE'
    if dim_2 is not None:
        dim2 = "ARRAY[%sx1]"%dim_2
    else:
        dim2 = 'VARIABLE'
    message = "dimensional missmatch in vector operation: %s and %s"%(dim1, dim2)
    report_error(message,line)
