from scanner import Scanner
from parser import Parser
from symboltable import SymbolTable
from semanticanalyzer import SemanticAnalyzer
from codegen import CodeGenerator
import sys


def print_out(path,data):
    with open(path,'w') as f:
        f.write(data)

# get the source file path
file_name = sys.argv[1]

# read the source file
with open(file_name,'r') as f:
    code = f.read()

# keep track of whether errors occur at any stages
errors = False

# instantiate everything
scanner = Scanner()
parser = Parser()
symbol_table = SymbolTable()
semantic_analyzer = SemanticAnalyzer()
code_generator = CodeGenerator()

# scan
tokens = scanner.scan(code)
print_out(file_name+'.scan.temp','\n'.join([t.as_string() for t in tokens]))

# parse
parse_tree = parser.parse(tokens)
errors = errors or parser.errors()
print_out(file_name+'.parse.temp',parse_tree.printable_string())

# create a symbol table
if not errors:
    symbol_table.populate(parse_tree)
    errors = errors or symbol_table.errors()
    print_out(file_name+'.symbols.temp',symbol_table.printable_string())

# perform semantic analysis
if not errors:
    semantic_analyzer.analyze(parse_tree,symbol_table)
    errors = errors or semantic_analyzer.errors()
    print_out(file_name+'.operations.temp',semantic_analyzer.printable_string())

# generate the LLVM IR
if not errors:
    code_generator.generate(parse_tree)
