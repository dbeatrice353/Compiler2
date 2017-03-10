from scanner import Scanner
from parser import Parser
#from semanticanalyzer import SemanticAnalyzer
import sys

file_name = sys.argv[1]

with open(file_name,'r') as f:
    code = f.read()

scanner = Scanner()
parser = Parser()
#semantic_analyzer = SemanticAnalyzer()

tokens = scanner.scan(code)

with open(file_name + '.scan.temp','w') as f:
    f.write('\n'.join([t.as_string() for t in tokens]))

parse_tree = parser.parse(tokens)

with open(file_name + '.parse.temp','w') as f:
    f.write(parse_tree.printable_string())
