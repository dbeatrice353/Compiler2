from symboltable import ScopeStack
from parser import Parser, ParseTreeNode
from scanner import Scanner, Token
# convert vector expressions to loops over expressions in the parse tree.

class Unvectorizer:
    def __init__(self):
        self._symbol_table = None
        self._scope_stack = ScopeStack()
        self._unvectorization_template_file = "unvectorization_template"
        self._index_identifier = "i_697476643"
        self._scope_stack.push("main")

    def unvectorize(self,parse_tree,symbol_table):
        self._symbol_table = symbol_table
        self._unvectorize(parse_tree)
        return parse_tree

    def _unvectorize(self,node):
        self._scope_stack.push_node(node)
        if len(node.children):
            new_list = []
            for child in node.children:
                if child.name_matches("statement"):
                    statement = child.children[0]
                    if statement.name_matches("assignment_statement"):
                        dimension = self._get_dimension(statement)
                        if dimension is not None:
                            [set_max, set_counter, loop] = self._get_template(dimension)
                            self._index_vectors(statement)
                            loop.add_child(statement)
                            new_list.append(set_max)
                            new_list.append(set_counter)
                            new_list.append(loop)
                        else:
                            self._unvectorize(child)
                            new_list.append(child)
                    else:
                        self._unvectorize(child)
                        new_list.append(child)
                else:
                    self._unvectorize(child)
                    new_list.append(child)
            node.children = new_list
        self._scope_stack.pop_node(node)


    def _get_dimension(self,node):
        if node.name_matches("name") or node.name_matches("destination"):
            identifier = node.children[0].token.value
            scope = self._scope_stack.as_string()
            symbol = self._symbol_table.fetch(identifier,scope)
            if symbol["type"] == "array" and len(node.children) == 1:
                return symbol["array_length"]
            else:
                return None
        for child in node.children:
            value = self._get_dimension(child)
            if value is not None:
                return value

    def _set_dimension(self, statement, dimension):
        assignment = statement.children[0]
        expression = assignment.children[1]
        arithop = expression.children[0]
        relation = arithop.children[0]
        term = relation.children[0]
        factor = term.children[0]
        number = factor.children[0]
        token = Token(dimension,"NUMBER")
        number.set_token(token)
        return statement

    def _get_template(self,dimension):
        scanner = Scanner()
        parser = Parser()
        with open(self._unvectorization_template_file,'r') as f:
            code = f.read()
        tokens = scanner.scan(code)
        [set_max, set_counter, loop] = parser.parse_unvectorization_template(tokens)
        set_max = self._set_dimension(set_max,dimension)
        return [set_max, set_counter, loop]

    def _index_vectors(self,node):
        for child in node.children:
            if child.name_matches("name") or child.name_matches("destination"):
                identifier = child.children[0].token.value
                scope = self._scope_stack.as_string()
                symbol = self._symbol_table.fetch(identifier,scope)
                if symbol["type"] == "array" and len(child.children) != 2: # if its an array, but there's no index node on the tree
                    child.children.append(self._index())
            else:
                self._index_vectors(child)

    def _index(self):
        identifier = ParseTreeNode("identifier")
        token = Token(value=self._index_identifier,type="WORD")
        identifier.set_token(token)
        name = ParseTreeNode("name")
        name.add_child(identifier)
        factor = ParseTreeNode("factor")
        factor.add_child(name)
        term = ParseTreeNode("term")
        term.add_child(factor)
        relation = ParseTreeNode("relation")
        relation.add_child(term)
        arithop = ParseTreeNode("arithop")
        arithop.add_child(relation)
        expression = ParseTreeNode("expression")
        expression.add_child(arithop)
        return expression

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
