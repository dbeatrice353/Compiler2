

class Scanner:
    def __init__(self):
        self.code = []
        self.current_char_index = 0
        self.current_lexeme = ""
        self.tokens = []

    def _next_character(self):
        if self.current_char_index + 1 < len(self.code):
            return self.code[self.current_char_index + 1]['char']
        else:
            return None

    def _current_character(self):
        return self.code[self.current_char_index]['char']

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
                char_records.append({'char': char, 'line_no':line})
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

            if char == '"':
                self._scan_string()

            elif char == '\'':
                self._scan_character()

            elif self._is_letter(char):
                self._scan_word()

            elif self._is_digit(char):
                self._scan_number()

            elif char == '.':
                self._step()
            elif char == ',':
                self._step()
            elif char == ';':
                self._step()
            elif char == '=':
                self._step()
            elif char == '!':
                self._step()
            elif char == '>':
                self._step()
            elif char == '<':
                self._step()
            elif char == '&':
                self._step()
            elif char == '|':
                self._step()
            elif char == '+':
                self._step()
            elif char == '-':
                self._step()
            elif char == '(':
                self._step()
            elif char == ')':
                self._step()
            elif char == '[':
                self._step()
            elif char == ']':
                self._step()
            elif char == '*':
                self._step()
            elif char == '/':
                self._step()
            elif char == ':':
                self._step()
            elif char == '_':
                self._step()
            else:
                white_space.append(char)
                self._step()

    def _scan_string(self):
        self._step()

    def _scan_character(self):
        self._step()

    def _scan_word(self):
        self._step()

    def _scan_number(self):
        self._step()

    def _is_letter(self,char):
        ascii_value = ord(char)
        return (ascii_value > 96 and ascii_value < 123) or (ascii_value > 64 and ascii_value < 91)

    def _is_digit(self,char):
        ascii_value = ord(char)
        return ascii_value > 47 and ascii_value < 58
