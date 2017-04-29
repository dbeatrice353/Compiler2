from symboltable import ScopeStack
from parser import Parser
from scanner import Scanner
# convert vector expressions to loops over expressions in the parse tree.

class Unvectorizer:
    def __init__(self):
        self._symbol_table = None
        self._scope_stack = ScopeStack()
        self._unvectorization_template_file = "unvectorization_template"
        self._scope_stack.push("main")

    def unvectorize(self):
        #self._symbol_table = symbol_table
        return self._unvectorize()

    def _unvectorize(self):
        return self._get_template()

    def _get_template(self):
        scanner = Scanner()
        parser = Parser()
        with open(self._unvectorization_template_file,'r') as f:
            code = f.read()
        tokens = scanner.scan(code)
        return parser.parse_unvectorization_template(tokens)


if __name__ == "__main__":
    u = Unvectorizer()
    t = u.unvectorize()
"""
 | | | |<statement>
 | | | | | |<loop_statement>
 | | | | | | | |<assignment_statement> :=
 | | | | | | | | | |<destination>
 | | | | | | | | | | | |<identifier> i
 | | | | | | | | | |<expression>
 | | | | | | | | | | | |<arithop> +
 | | | | | | | | | | | | | |<relation>
 | | | | | | | | | | | | | | | |<term>
 | | | | | | | | | | | | | | | | | |<factor>
 | | | | | | | | | | | | | | | | | | | |<name>
 | | | | | | | | | | | | | | | | | | | | | |<identifier> i
 | | | | | | | | | | | | | |<arithop>
 | | | | | | | | | | | | | | | |<relation>
 | | | | | | | | | | | | | | | | | |<term>
 | | | | | | | | | | | | | | | | | | | |<factor>
 | | | | | | | | | | | | | | | | | | | | | |<number> 1
 | | | | | | | |<expression>
 | | | | | | | | | |<arithop>
 | | | | | | | | | | | |<relation> <
 | | | | | | | | | | | | | |<term>
 | | | | | | | | | | | | | | | |<factor>
 | | | | | | | | | | | | | | | | | |<name>
 | | | | | | | | | | | | | | | | | | | |<identifier> i
 | | | | | | | | | | | | | |<relation>
 | | | | | | | | | | | | | | | |<term>
 | | | | | | | | | | | | | | | | | |<factor>
 | | | | | | | | | | | | | | | | | | | |<number> 10
 | | | | | | | |<statement>
 | | | | | | | | | |<assignment_statement> :=
 | | | | | | | | | | | |<destination>
 | | | | | | | | | | | | | |<identifier> j
 | | | | | | | | | | | |<expression>
 | | | | | | | | | | | | | |<arithop> -
 | | | | | | | | | | | | | | | |<relation>
 | | | | | | | | | | | | | | | | | |<term>
 | | | | | | | | | | | | | | | | | | | |<factor>
 | | | | | | | | | | | | | | | | | | | | | |<name>
 | | | | | | | | | | | | | | | | | | | | | | | |<identifier> j
 | | | | | | | | | | | | | | | |<arithop>
 | | | | | | | | | | | | | | | | | |<relation>
 | | | | | | | | | | | | | | | | | | | |<term>
 | | | | | | | | | | | | | | | | | | | | | |<factor>
 | | | | | | | | | | | | | | | | | | | | | | | |<number> 1
"""
