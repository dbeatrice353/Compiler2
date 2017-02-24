
class Character:
    def __init__(self,value,line_no):
        self.value = value
        self.line_no = line_no
        self._is_letter = False
        self._is_digit = False
        self._valid_string_componant = False
        self._valid_character = False
        self._identify(value)

    def _identify(self, value):
        if value is not None:
            ascii_value = ord(value)
            self._is_letter = (ascii_value > 96 and ascii_value < 123) or (ascii_value > 64 and ascii_value < 91)
            self._is_digit = ascii_value > 47 and ascii_value < 58
            self._valid_string_componant = self._is_letter or self._is_digit or value in ['_',',',';',':','.','\'']
            self._valid_character = self._is_letter or self._is_digit or value in ['_',',',';',':','.','"']

    def matches(self,c):
        return self.value == c

    def is_letter(self):
        return self._is_letter

    def is_digit(self):
        return self._is_digit

    def valid_string_componant(self):
        return self._valid_string_componant

    def valid_charater(self):
        return self._valid_character


class Token:
    def __init__(self,value="",type="",line=-1):
        self.value = value
        self.type = type
        self.line = line

    def push(self,c):
        self.value += c.value

    def set_type(self,type):
        self.type = type

    def set_line(self,line):
        self.line = line

    def __repr__(self):
        return "<%s, \'%s\', %i>"%(self.type,self.value,self.line)


class Scanner:
    def __init__(self):
        self.code = []
        self.current_char_index = 0
        self.current_lexeme = ""
        self.tokens = []
        self.current_token = Token()

    def _next(self):
        if self.current_char_index < len(self.code):
            c = self.code[self.current_char_index]
            self.current_char_index += 1
            return c
        else:
            return Character(None,-1)

    def _peek(self):
        if self.current_char_index < len(self.code):
            return self.code[self.current_char_index]
        else:
            return Character(None,-1)

    def _step(self):
        self.current_char_index += 1

    def _preprocess_code(self,code):
        character_list = list(code)
        character_records = self._create_character_records(character_list)
        character_records = self._discard_comments(character_records)
        return character_records

    def _discard_comments(self,character_list): # *w/o regular expression...

        # discard multi-line comments
        comment_depth = 0
        temp = []
        for i in range(0,len(character_list)-1):
            c1 = character_list[i]
            c2 = character_list[i+1]
            if c1.matches('/') and c2.matches('*'):
                comment_depth += 1
            if c1.matches('*') and c2.matches('/'):
                comment_depth -= 1
            if comment_depth == 0:
                temp.append(c1)
                if i == len(character_list):
                    temp.append(c2)
        # discard single-line comments
        final = []
        comment = False
        for i,char in enumerate(temp):
            if not comment:
                if char.matches('/'):
                    if i+1 < len(temp):
                        if temp[i+1].matches('/'):
                            comment = True
                        else:
                            final.append(char)
                    else:
                        final.append(char)
                else:
                    final.append(char)
            else: # comment == True
                if char.matches('\n'):
                    comment  = False

        return final

    def _create_character_records(self, character_list):
        line = 1
        char_records = []
        for char in character_list:
            if char == '\n':
                line += 1
            else:
                char_records.append(Character(char,line))
        return char_records

    def _reset_character_index(self):
        self.current_char_index = 0

    def _save_current_token(self):
        self.tokens.append(self.current_token)
        self.current_token = Token()

    def _discard_current_token(self):
        self.current_token = Token()

    def scan(self, code):
        self.code = self._preprocess_code(code)
        self._reset_character_index()
        invalid = []
        while True:
            c = self._peek()
            if c.matches(None):
                print(set(invalid))
                return self.tokens

            if c.matches('"'):
                self._scan_string()
            elif c.matches('\''):
                self._scan_character()
            elif c.is_letter():
                self._scan_word()
            elif c.is_digit():
                self._scan_number()
            elif c.matches('.'):
                self._scan_token('PERIOD')
            elif c.matches(','):
                self._scan_token('COMMA')
            elif c.matches(';'):
                self._scan_token('SEMICOLON')
            elif c.matches('='):
                self._step()
            elif c.matches('!'):
                self._step()
            elif c.matches('>'):
                self._step()
            elif c.matches('<'):
                self._step()
            elif c.matches('&'):
                self._scan_token('AND')
            elif c.matches('|'):
                self._scan_token('OR')
            elif c.matches('+'):
                self._scan_token('PLUS')
            elif c.matches('-'):
                self._scan_token('MINUS')
            elif c.matches('('):
                self._scan_token('OPENPAREN')
            elif c.matches(')'):
                self._scan_token('CLOSEPAREN')
            elif c.matches('['):
                self._scan_token('OPENBRACKET')
            elif c.matches(']'):
                self._scan_token('CLOSEBRACKET')
            elif c.matches('*'):
                self._scan_token('MULTIPLY')
            elif c.matches('/'):
                self._scan_token('DIVIDE')
            elif c.matches(':'):
                self._step()
            else:
                invalid.append(c.value)
                self._step()

    def _scan_string(self):
        c = self._next()
        self.current_token.set_type("STRING")
        self.current_token.set_line(c.line_no)
        if c.matches(None):
            return
        elif not c.matches('"'):
            report_malformed_string(c)
            self._discard_current_token()
            return

        while True:
            c = self._next()
            if c.matches(None):
                return
            elif c.matches('"'):
                self._save_current_token()
                return
            elif not c.valid_string_componant():
                report_invalid_string_componant(c)
                self._discard_current_token()
                return
            else:
                self.current_token.push(c)


    def _scan_character(self):
        c = self._next()
        self.current_token.set_type("CHARACTER")
        self.current_token.set_line(c.line_no)
        if c.matches(None):
            return
        elif not c.matches('\''):
            report_malformed_character(c)
            return

        c = self._next()
        if c.matches(None):
            return
        elif c.matches('\''):
            self._save_current_token()
            return
        elif not c.valid_charater():
            report_invalid_character_value(c)
            self._discard_current_token()
            return
        else:
            self.current_token.push(c)

        c = self._next()
        if c.matches(None):
            return
        elif not c.matches('\''):
            report_malformed_character(c)
            self._discard_current_token()
            return
        else:
            self._save_current_token()

    def _scan_word(self):
        c = self._next()
        self.current_token.set_type("WORD")
        self.current_token.set_line(c.line_no)
        if c.matches(None):
            return
        elif not c.is_letter():
            report_malformed_word(c)
            return
        else:
            self.current_token.push(c)

        while True:
            c = self._peek()
            if c.matches(None):
                self._save_current_token()
                return
            elif c.is_letter() or c.matches('_'):
                self.current_token.push(c)
                self._step()
            else:
                self._save_current_token()
                return

    def _scan_number(self):
        c = self._next()
        self.current_token.set_type("NUMBER")
        self.current_token.set_line(c.line_no)

        if c.matches(None):
            return
        elif c.is_digit():
            self.current_token.push(c)
        else:
            report_malformed_number(c)
            return

        while True:
            c = self._peek()
            if c.matches(None):
                self._save_current_token()
                return
            elif c.is_digit():
                self.current_token.push(c)
                self._step()
            elif c.matches('.'):
                self.current_token.push(c)
                self._step()
                break
            else:
                self._save_current_token()
                return

        while True:
            c = self._peek()
            if c.matches(None):
                self._save_current_token()
                return
            elif c.is_digit():
                self.current_token.push(c)
                self._step()
            else:
                self._save_current_token()
                return

    def _scan_token(self,type):
        c = self._next()
        self.current_token.push(c)
        self.current_token.set_type(type)
        self.current_token.set_line(c.line_no)
        self._save_current_token()

# ----- error reporting -------------------------------

def report(message):
    print message

def scanner_error(c):
    return "SCANNER ERROR (line %i): "%(c.line_no)

def report_invalid_string_componant(c):
    message = scanner_error(c)
    message += "'%s' is not a valid string component."%(c.value)
    report(message)

def report_malformed_string(c):
    message = scanner_error(c)
    message += "malformed string using '%s'."%(c.value)
    report(message)

def report_invalid_character_value(c):
    message = scanner_error(c)
    message += "'%s' is not a valid character value."%(c.value)
    report(message)

def report_malformed_character(c):
    message = scanner_error(c)
    message += "malformed character using '%s'."%(c.value)
    report(message)

def report_malformed_word(c):
    message = scanner_error(c)
    message += "malformed word using '%s'."%(c.value)
    report(message)

def report_malformed_number(c):
    message = scanner_error(c)
    message += "malformed number using '%s'."%(c.value)
    report(message)
