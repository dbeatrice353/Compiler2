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
            return None
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
        self._consume_token_by_value('.')
        return program

    def _parse_program_header(self):
        program_header = ParseTreeNode('program_header')
        self._consume_token_by_value('program')
        program_header.add_child(self._parse_identifier())
        self._consume_token_by_value('is')
        return program_header

    def _parse_program_body(self):
        program_body = ParseTreeNode('program_body')
        while True:
            if self._check_for_token_by_values(Parser.DECLARATION_INITS):
                program_body.add_child(self._parse_declaration())
                self._consume_token_by_value(';')
            else:
                break
        self._consume_token_by_value('begin')
        """
        while True:
            if self._check_for_token_by_value('end'):
                break
            else:
                program_body.add_child(self._parse_statement())
                self._consume_token_by_value(';')
        """
        self._consume_token_by_value('end')
        self._consume_token_by_value('program')
        return program_body

    def _parse_declaration(self):
        declaration = ParseTreeNode('declaration')
        if self._check_for_token_by_value('global'):
            declaration.set_token(self._consume_token_by_value('global'))

        if self._check_for_token_by_value('procedure'):
            declaration.add_child(self._parse_procedure_declaration())
        elif self._check_for_token_by_values(Parser.DATA_TYPES):
            declaration.add_child(self._parse_variable_declaration())
        else:
            report_expected_vs_encountered(str(Parser.DATA_TYPES)+" or 'procedure'",self._next())
        return declaration

    def _parse_procedure_declaration(self):
        self._step()
        return ParseTreeNode('procedure_declaration')

    def _parse_variable_declaration(self):
        variable_declaration = ParseTreeNode('variable_declaration')
        variable_declaration.add_child(self._parse_type_mark())
        variable_declaration.add_child(self._parse_identifier())
        if self._check_for_token_by_value('['):
            self._consume_token_by_value('[')
            variable_declaration.add_child(self._parse_array_size())
            self._consume_token_by_value(']')
        return variable_declaration

    def _parse_array_size(self):
        array_size = ParseTreeNode('array_size')
        return array_size

    def _parse_type_mark(self):
        type_mark = ParseTreeNode('type_mark')
        if self._check_for_token_by_values(Parser.DATA_TYPES):
            type_mark.set_token(self._consume_token_by_type('WORD'))
        else:
            token = self._next()

            report_expected_vs_encountered(str(Parser.DATA_TYPES), token)
            type_mark.set_token(Token(value='[filler]',type='WORD',line=token.line))
        return type_mark

    def _parse_statement(self):
        self._step()
        return ParseTreeNode('statements')

    def _parse_identifier(self):
        identifier = ParseTreeNode('identifier')
        identifier.set_token(self._consume_token_by_type('WORD'))
        return identifier

    def _check_for_token_by_value(self,value):
        token = self._peek()
        return token.value_matches(value)

    def _check_for_token_by_values(self,value_list):
        token = self._peek()
        return token.value_matches_any(value_list)

    def _check_for_token_by_type(self,type):
        token = self._peek()
        return token.type_matches(type)

    def _consume_token_by_value(self,value):
        token = self._peek()
        if token is None:
            return None
        elif token.value_matches(value):
            self._step()
            return token
        else:
            report_expected_vs_encountered(value,token.value,token.line)
            return Token(value=value,type='[filler]',line=token.line)

    def _consume_token_by_type(self,type):
        token = self._peek()
        if token is None:
            return None
        elif token.type_matches(type):
            self._step()
            return token
        else:
            report_expected_vs_encountered('[name/word]',token.value,token.line)
            return Token(value='[filler]',type=type,line=token.line)



def report(message):
    print message

def parser_error(line):
    return "SYNTACTIC ERROR (line %i): "%(line)

def report_expected_vs_encountered(expected,encountered,line):
    message = parser_error(line)
    message += "token expected --> %s, token encountered --> %s"%(expected, encountered)
    report(message)
