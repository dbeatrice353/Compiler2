from scanner import Token
from symboltable import SymbolTable
import constants

class ParseTreeNode:
    def __init__(self,name):
        self.name = name
        self.token = None
        self.children = []
        self.ir_string_reference = None

    def name_matches(self, string):
        return self.name == string

    def set_token(self,token):
        self.token = token

    def add_child(self,child):
        self.children.append(child)

    def _as_string(self,depth):
        s = 2*depth*' |' + "<%s>"%(self.name)
        if self.token is not None:
            s += " %s"%(self.token.value)
        return s

    def printable_string(self,depth=0):
        s = self._as_string(depth)
        for child in self.children:
            s += '\n' + child.printable_string(depth + 1)
        return s

    def is_binary_operation(self):
        if self.token is not None:
            return (self.token.value in constants.BINARY_OPS) and len(self.children)==2
        else:
            return False

    def is_literal(self):
        return self.token is not None and self.token.is_literal()



class ScopeStack:
    def __init__(self, stack=[]):
        self.stack = stack

    def push(self,scope):
        self.stack.append(scope)

    def pop(self):
        if len(self.stack):
            self.stack.pop()

    def as_string(self):
        return '/'.join(self.stack)

    def as_list(self):
        return self.stack


class Parser:

    DATA_TYPES = constants.DATA_TYPES
    DECLARATION_INITS = constants.DECLARATION_INITS
    PARAM_DIRECTIONS = constants.PARAM_DIRECTIONS
    EXPRESSION_OPS = constants.EXPRESSION_OPS
    ARITH_OPS = constants.ARITH_OPS
    RELATION_OPS = constants.RELATION_OPS
    TERM_OPS = constants.TERM_OPS

    def __init__(self):
        self._tokens = []
        self._current_token_index = 0
        self._errors = False
        self.symbol_table = None
        self.root = None

    def _register_error(self):
        self._errors = True

    def _print_tree_to_terminal(self):
        if self.root is not None:
            print self.root.printable_string()

    def _next(self):
        token = self._peek()
        self._current_token_index += 1
        return token

    def _peek(self):
        if self._current_token_index >= len(self._tokens):
            report_unexpected_eof()
            self._register_error()
            exit()
        else:
            token = self._tokens[self._current_token_index]
            return token

    def _step(self):
        self._current_token_index += 1

    def errors(self):
        return self._errors

    def parse(self,tokens):
        self.symbol_table = SymbolTable()
        self._tokens = tokens
        self._current_token_index = 0
        return self._parse_program()

    def _parse_program(self):
        program = ParseTreeNode('program')
        self.root = program
        program.add_child(self._parse_program_header())
        program.add_child(self._parse_program_body())
        self._get_token_by_value('.')
        return program

    def _parse_program_header(self):
        program_header = ParseTreeNode('program_header')
        self._get_token_by_value('program')
        program_header.add_child(self._parse_identifier())
        self._get_token_by_value('is')
        return program_header

    def _parse_program_body(self):
        program_body = ParseTreeNode('program_body')
        while True:
            if self._next_token_value_matches(Parser.DECLARATION_INITS):
                program_body.add_child(self._parse_declaration())
            else:
                break
        self._get_token_by_value('begin')
        while True:
            if self._next_token_value_matches('end'):
                break
            else:
                program_body.add_child(self._parse_statement())
        self._get_token_by_value('end')
        self._get_token_by_value('program')
        return program_body

    def _parse_declaration(self):
        declaration = ParseTreeNode('declaration')
        if self._next_token_value_matches('global'):
            declaration.set_token(self._next())

        if self._next_token_value_matches('procedure'):
            declaration.add_child(self._parse_procedure_declaration())
        elif self._next_token_value_matches(Parser.DATA_TYPES):
            declaration.add_child(self._parse_variable_declaration())
            self._get_token_by_value(';')
        else:
            report_expected_vs_encountered(str(Parser.DATA_TYPES)+" or 'procedure'",self._next())
            self._register_error()
        return declaration

    def _parse_procedure_declaration(self):
        procedure_declaration = ParseTreeNode('procedure_declaration')
        procedure_declaration.add_child(self._parse_procedure_header())
        procedure_declaration.add_child(self._parse_procedure_body())
        return procedure_declaration

    def _parse_procedure_header(self):
        procedure_header = ParseTreeNode('procedure_header')
        self._get_token_by_value('procedure')
        identifier = self._parse_identifier()
        procedure_header.add_child(identifier)
        self._get_token_by_value('(')
        if not self._next_token_value_matches(')'):
            procedure_header.add_child(self._parse_parameter_list())
        self._get_token_by_value(')')
        return procedure_header

    def _parse_parameter_list(self):
        parameter_list = ParseTreeNode('parameter_list')
        parameter_list.add_child(self._parse_parameter())
        if not self._next_token_value_matches(')'):
            self._get_token_by_value(',')
            parameter_list.add_child(self._parse_parameter_list())
        return parameter_list

    def _parse_parameter(self):
        parameter = ParseTreeNode('parameter')
        parameter.add_child(self._parse_variable_declaration())
        direction = self._get_token_by_value(Parser.PARAM_DIRECTIONS)
        parameter.set_token(direction)
        return parameter

    def _parse_procedure_body(self):
        procedure_body = ParseTreeNode('procedure_body')
        while True:
            if self._next_token_value_matches(Parser.DECLARATION_INITS):
                procedure_body.add_child(self._parse_declaration())
            else:
                break
        self._get_token_by_value('begin')
        while True:
            if self._next_token_value_matches('end'):
                break
            else:
                procedure_body.add_child(self._parse_statement())
        self._get_token_by_value('end')
        self._get_token_by_value('procedure')
        return procedure_body

    def _parse_variable_declaration(self):
        variable_declaration = ParseTreeNode('variable_declaration')
        variable_declaration.add_child(self._parse_type_mark())
        variable_declaration.add_child(self._parse_identifier())
        if self._next_token_value_matches('['):
            self._get_token_by_value('[')
            variable_declaration.add_child(self._parse_array_size())
            self._get_token_by_value(']')
        return variable_declaration

    def _parse_array_size(self):
        array_size = ParseTreeNode('array_size')
        array_size.set_token(self._get_token_by_type('NUMBER'))
        return array_size

    def _parse_type_mark(self):
        type_mark = ParseTreeNode('type_mark')
        if self._next_token_value_matches(Parser.DATA_TYPES):
            type_mark.set_token(self._next())
        else:
            token = self._next()
            report_expected_vs_encountered(str(Parser.DATA_TYPES), token.value, token.line)
            self._register_error()
            type_mark.set_token(Token(value='[filler]',type='WORD',line=token.line))
        return type_mark

    def _parse_statement(self):
        statement = ParseTreeNode('statement')
        token = self._peek()
        if token.value_matches('if'):
            statement.add_child(self._parse_if())
        elif token.value_matches('for'):
            statement.add_child(self._parse_loop())
        elif token.value_matches('return'):
            statement.add_child(self._parse_return())
            self._get_token_by_value(';')
        else:
            statement.add_child(self._parse_assignment_statement_or_procedure_call())
            self._get_token_by_value(';')
        return statement

    def _parse_if(self):
        if_statement = ParseTreeNode('if_statement')
        self._get_token_by_value('if')
        self._get_token_by_value('(')
        if_statement.add_child(self._parse_expression())
        self._get_token_by_value(')')
        then = ParseTreeNode('then')
        then.set_token(self._get_token_by_value('then'))
        if_statement.add_child(then)
        while True:
            if self._next_token_value_matches(['else', 'end']):
                break
            else:
                then.add_child(self._parse_statement())
        if self._next_token_value_matches('else'):
            else_ = ParseTreeNode('else')
            else_.set_token(self._next())
            if_statement.add_child(else_)
            while True:
                if self._next_token_value_matches('end'):
                    break
                else:
                    else_.add_child(self._parse_statement())
        self._get_token_by_value('end')
        self._get_token_by_value('if')
        return if_statement

    def _parse_loop(self):
        loop_statement = ParseTreeNode('loop_statement')
        self._get_token_by_value('for')
        self._get_token_by_value('(')
        loop_statement.add_child(self._parse_assignment_statement())
        self._get_token_by_value(';')
        loop_statement.add_child(self._parse_expression())
        self._get_token_by_value(')')
        while True:
            if self._next_token_value_matches('end'):
                break
            else:
                loop_statement.add_child(self._parse_statement())
        self._get_token_by_value('end')
        self._get_token_by_value('for')
        return loop_statement

    def _parse_return(self):
        return_statement = ParseTreeNode('return_statement')
        self._get_token_by_value('return')
        return return_statement

    def _parse_destination(self):
        destination = ParseTreeNode('destination')
        destination.add_child(self._parse_identifier())
        if self._next_token_value_matches('['):
            self._next()
            destination.add_child(self._parse_expression())
            self._get_token_by_value(']')
        return destination

    def _parse_assignment_statement(self):
        assignment_statement = ParseTreeNode('assignment_statement')
        assignment_statement.add_child(self._parse_destination())
        assignment_statement.set_token(self._get_token_by_value(':='))
        assignment_statement.add_child(self._parse_expression())
        return assignment_statement

    def _parse_assignment_statement_or_procedure_call(self):
        identifier = ParseTreeNode('identifier')
        identifier.set_token(self._next())
        next_token = self._peek()
        if next_token.value_matches('('):
            self._next()
            procedure_call = ParseTreeNode('procedure_call')
            procedure_call.add_child(identifier)
            if not self._next_token_value_matches(')'):
                procedure_call.add_child(self._parse_argument_list())
            self._get_token_by_value(')')
            return procedure_call
        else:
            assignment_statement = ParseTreeNode('assignment_statement')
            destination = ParseTreeNode('destination')
            destination.add_child(identifier)
            if self._next_token_value_matches('['):
                self._next()
                destination.add_child(self._parse_expression())
                self._get_token_by_value(']')
            assignment_statement.add_child(destination)
            assignment_statement.set_token(self._get_token_by_value(':='))
            assignment_statement.add_child(self._parse_expression())
            return assignment_statement

    def _parse_argument_list(self):
        argument_list = ParseTreeNode('argument_list')
        argument_list.add_child(self._parse_expression())
        if not self._next_token_value_matches(')'):
            self._get_token_by_value(',')
            argument_list.add_child(self._parse_argument_list())
        return argument_list

    def _parse_expression(self):
        expression = ParseTreeNode('expression')
        if self._next_token_value_matches('not'):
            expression.set_token(self._next())
        expression.add_child(self._parse_arithop())
        if self._next_token_value_matches(Parser.EXPRESSION_OPS):
            expression.set_token(self._next())
            expression.add_child(self._parse_expression())
        return expression

    def _parse_arithop(self):
        arithop = ParseTreeNode('arithop')
        arithop.add_child(self._parse_relation())
        if self._next_token_value_matches(Parser.ARITH_OPS):
            arithop.set_token(self._next())
            arithop.add_child(self._parse_arithop())
        return arithop

    def _parse_relation(self):
        relation = ParseTreeNode('relation')
        relation.add_child(self._parse_term())
        if self._next_token_value_matches(Parser.RELATION_OPS):
            relation.set_token(self._next())
            relation.add_child(self._parse_relation())
        return relation

    def _parse_term(self):
        term = ParseTreeNode('term')
        term.add_child(self._parse_factor())
        if self._next_token_value_matches(Parser.TERM_OPS):
            term.set_token(self._next())
            term.add_child(self._parse_term())
        return term

    def _parse_factor(self):
        factor = ParseTreeNode('factor')
        if self._next_token_value_matches('('):
            self._next()
            factor.add_child(self._parse_expression())
            self._get_token_by_value(')')
        else:
            if self._next_token_value_matches('-'):
                factor.set_token(self._next())
            if self._next_token_type_matches('NUMBER'):
                factor.add_child(self._parse_number())
            elif self._next_token_type_matches('STRING'):
                factor.add_child(self._parse_string())
            elif self._next_token_type_matches('CHARACTER'):
                factor.add_child(self._parse_character())
            elif self._next_token_value_matches(['true','false']):
                factor.set_token(self._next()) # this would overwrite a '-' i.e. in the case of '-true'
            else:
                factor.add_child(self._parse_name())
        return factor

    def _parse_number(self):
        number = ParseTreeNode('number')
        number.set_token(self._get_token_by_type('NUMBER'))
        return number

    def _parse_string(self):
        string = ParseTreeNode('string')
        string.set_token(self._get_token_by_type('STRING'))
        return string

    def _parse_character(self):
        character = ParseTreeNode('character')
        character.set_token(self._get_token_by_type('CHARACTER'))
        return character

    def _parse_name(self):
        name = ParseTreeNode('name')
        name.add_child(self._parse_identifier())
        if self._next_token_value_matches('['):
            self._next()
            name.add_child(self._parse_expression())
            self._get_token_by_value(']')
        return name

    def _parse_identifier(self):
        identifier = ParseTreeNode('identifier')
        if self._next_token_type_matches('WORD'):
            identifier.set_token(self._next())
        else:
            token = self._next()
            report_expected_vs_encountered('[identifier]', token.value, token.line)
            self._register_error()
        return identifier

    def _next_token_value_matches(self,value):
        return self._peek().value_matches(value)

    def _next_token_type_matches(self,type):
        return self._peek().type_matches(type)

    def _get_token_by_value(self,value):
        token = self._next()
        if not token.value_matches(value):
            report_expected_vs_encountered(str(value),token.value,token.line)
            self._register_error()
            while not token.value_matches(value):
                token = self._next()
        return token

    def _get_token_by_type(self,type):
        token = self._next()
        if not token.type_matches(type):
            report_expected_vs_encountered(str(type),token.value,token.line)
            self._register_error()
            while not token.value_matches(type):
                token = self._next()
        return token

    def _create_filler_token(value='[filler value]',type='[filler type]',line=-1):
        return Token(value=value,type=type,line=line)


def report(message):
    print message

def parser_error(line):
    return "SYNTACTIC ERROR (line %i): "%(line)

def report_expected_vs_encountered(expected,encountered,line):
    message = parser_error(line)
    message += "token expected: \"%s\", token encountered: \"%s\""%(expected, encountered)
    report(message)

def report_unexpected_eof():
    report("SYNTACTIC ERROR: unexpected EOF")
