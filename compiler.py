from scanner import Scanner
from parser import Parser
import sys

file_name = sys.argv[1]

with open(file_name,'r') as f:
    code = f.read()

scanner = Scanner()
parser = Parser()

tokens = scanner.scan(code)
parse_tree = parser.parse(tokens)

with open(file_name + '.scan.temp','w') as f:
    f.write('\n'.join([t.as_string() for t in tokens]))

with open(file_name + '.parse.temp','w') as f:
    f.write(parse_tree.printable_string())
