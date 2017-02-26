from scanner import Token

#reserved_key_words = ['program','is','begin','procedure','end','global','in','out','inout','integer','bool','char','string','float','if','then','else','loop','return','not','false','true']


class ParseTreeNode:
    def __init__(self,name):
        self.name = name
        self.token = None
        self.children = []

    def set_token(self,token):
        self.token = token

    def add_child(self,child):
        self.children.append(child)

    def _as_string(self,depth):
        s = 2*depth*' ' + "<%s>"%(self.name)
        if self.token is not None:
            s += " %s"%(self.token.value)
        return s

    def printable_string(self,depth=0):
        s = self._as_string(depth)
        for child in self.children:
            s += '\n' + child.printable_string(depth + 1)
        return s



class Parser:

    DATA_TYPES = ['integer','float','string','char','bool']
    DECLARATION_INITS = ['global','procedure'] + DATA_TYPES
    PARAM_DIRECTIONS = ['in','out','inout']

    def __init__(self):
        self._tokens = []
        self._current_token_index = 0
        self._errors = False

    def _error(self):
        self._errors = True

    def _next(self):
        token = self._peek()
        self._current_token_index += 1
        return token;

    def _peek(self):
        if self._current_token_index >= len(self._tokens):
            report_unexpected_eof()
            exit()
        else:
            token = self._tokens[self._current_token_index]
            return token

    def _step(self):
        self._current_token_index += 1

    def parse(self,tokens):
        self._tokens = tokens
        self._current_token_index = 0
        return self._parse_program()

    def _parse_program(self):
        program = ParseTreeNode('program')
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
                self._get_token_by_value(';')
            else:
                break
        self._get_token_by_value('begin')
        while True:
            if self._next_token_value_matches('end'):
                break
            else:
                program_body.add_child(self._parse_statement())
                self._get_token_by_value(';')
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
        else:
            report_expected_vs_encountered(str(Parser.DATA_TYPES)+" or 'procedure'",self._next())
        return declaration

    def _parse_procedure_declaration(self):
        procedure_declaration = ParseTreeNode('procedure_declaration')
        procedure_declaration.add_child(self._parse_procedure_header())
        procedure_declaration.add_child(self._parse_procedure_body())
        return procedure_declaration

    def _parse_procedure_header(self):
        procedure_header = ParseTreeNode('procedure_header')
        self._get_token_by_value('procedure')
        procedure_header.add_child(self._parse_identifier())
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
        return parameter

    def _parse_procedure_body(self):
        procedure_body = ParseTreeNode('procedure_body')
        while True:
            if self._next_token_value_matches(Parser.DECLARATION_INITS):
                procedure_body.add_child(self._parse_declaration())
                self._get_token_by_value(';')
            else:
                break
        self._get_token_by_value('begin')
        while True:
            if self._next_token_value_matches('end'):
                break
            else:
                procedure_body.add_child(self._parse_statement())
                self._get_token_by_value(';')
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
            type_mark.set_token(Token(value='[filler]',type='WORD',line=token.line))
        return type_mark

    def _parse_statement(self):
        self._step()
        return ParseTreeNode('statements')

    def _parse_identifier(self):
        identifier = ParseTreeNode('identifier')
        if self._next_token_type_matches('WORD'):
            identifier.set_token(self._next())
        else:
            token = self._next()
            report_expected_vs_encountered('[identifier]', token.value, token.line)
            #filler = self._create_filler_token(value='[identifier]',type='WORD')
            #identifier.set_token(filler)
        return identifier

    def _next_token_value_matches(self,value):
        return self._peek().value_matches(value)

    def _next_token_type_matches(self,type):
        return self._peek().type_matches(type)

    def _get_token_by_value(self,value):
        token = self._next()
        if not token.value_matches(value):
            report_expected_vs_encountered(str(value),token.value,token.line)
        return token

    def _get_token_by_type(self,type):
        token = self._next()
        if not token.type_matches(type):
            report_expected_vs_encountered(str(type),token.value,token.line)
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
