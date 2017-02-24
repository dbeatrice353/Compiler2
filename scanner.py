
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



class Scanner:
    def __init__(self):
        self.code = []
        self.current_char_index = 0
        self.current_lexeme = ""
        self.tokens = []
        self.current_token = ""

    def _next_character(self):
        if self.current_char_index + 1 < len(self.code):
            return self.code[self.current_char_index + 1]
        else:
            return None

    def _current_character(self):
        return self.code[self.current_char_index]

    def _current_line_number(self):
        self.code[self.current_char_index]['line_no']

    def _step(self):
        self.current_char_index += 1

    def _preprocess_code(self,code):
        chars = list(code)
        line = 1
        char_records = []
        for char in chars:
            if char == '\n':
                line += 1
            else:
                char_records.append(Character(char,line))
        return char_records

    def _reset_character_index(self):
        self.current_char_index = 0

    def scan(self, code):
        self.code = self._preprocess_code(code)
        self._reset_character_index()
        white_space = []
        while True:
            char = self._next_character()
            if not char:
                print(set(white_space))
                return []

            if char.matches('"'):
                self._scan_string()
            elif char.matches('\''):
                self._scan_character()
            elif char.is_letter():
                self._scan_word()
            elif char.is_digit():
                self._scan_number()
            elif char.matches('.'):
                self._step()
            elif char.matches(','):
                self._step()
            elif char.matches(';'):
                self._step()
            elif char.matches('='):
                self._step()
            elif char.matches('!'):
                self._step()
            elif char.matches('>'):
                self._step()
            elif char.matches('<'):
                self._step()
            elif char.matches('&'):
                self._step()
            elif char.matches('|'):
                self._step()
            elif char.matches('+'):
                self._step()
            elif char.matches('-'):
                self._step()
            elif char.matches('('):
                self._step()
            elif char.matches(')'):
                self._step()
            elif char.matches('['):
                self._step()
            elif char.matches(']'):
                self._step()
            elif char.matches('*'):
                self._step()
            elif char.matches('/'):
                self._step()
            elif char.matches(':'):
                self._step()
            elif char.matches('_'):
                self._step()
            else:
                white_space.append(char.value)
                self._step()

    def _scan_string(self):
        self._step()

    def _scan_character(self):
        self._step()

    def _scan_word(self):
        self._step()

    def _scan_number(self):
        self._step()
