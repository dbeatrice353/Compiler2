from scanner import Scanner
import sys

file_name = sys.argv[1]

with open(file_name,'r') as f:
    code = f.read()

scanner = Scanner()
tokens = scanner.scan(code)
