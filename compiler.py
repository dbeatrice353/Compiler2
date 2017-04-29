from scanner import Scanner
from parser import Parser
from symboltable import SymbolTable
from semanticanalyzer import SemanticAnalyzer
from unvectorizer import Unvectorizer
from codegen import CodeGenerator
import sys

output_file = "ir.ll"

def print_out(path,data):
    with open(path,'w') as f:
        f.write(data)

file_name = sys.argv[1]
with open(file_name,'r') as f:
    code = f.read()

errors = False

scanner = Scanner()
parser = Parser()
symbol_table = SymbolTable()
semantic_analyzer = SemanticAnalyzer()
unvectorizer = Unvectorizer()
code_generator = CodeGenerator()

tokens = scanner.scan(code)
#print_out(file_name+'.scan.temp','\n'.join([t.as_string() for t in tokens]))
parse_tree = parser.parse(tokens)
errors = errors or parser.errors()
#print_out(file_name+'.parse.temp',parse_tree.printable_string())
if not errors:
    symbol_table.populate(parse_tree)
    errors = errors or symbol_table.errors()
    #print_out(file_name+'.symbols.temp',symbol_table.printable_string())
if not errors:
    semantic_analyzer.analyze(parse_tree,symbol_table)
    errors = errors or semantic_analyzer.errors()
    #print_out(file_name+'.operations.temp',semantic_analyzer.printable_string())
if not errors:
    unvectorizer.unvectorize(parse_tree, symbol_table)
    #print_out(file_name+'.parse.temp',parse_tree.printable_string())
    output_code = code_generator.generate(parse_tree, symbol_table)
    with open(output_file,'w') as f:
        f.write(output_code)
