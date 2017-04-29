import os

print "TEST: tests/valid_functional.src"
os.system("python compiler.py tests/valid_functional.src")
os.system("lli ir.ll")
