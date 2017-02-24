import os

print "TEST: tests/scanner_valid_1.src"
os.system("python compiler.py tests/scanner_valid_1.src")
print "TEST: tests/scanner_valid_2.src"
os.system("python compiler.py tests/scanner_valid_2.src")
