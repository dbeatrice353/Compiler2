import os

print "TEST: tests/scanner_invalid_1.src"
os.system("python compiler.py tests/scanner_invalid_1.src")
print "TEST: tests/scanner_invalid_2.src"
os.system("python compiler.py tests/scanner_invalid_2.src")
print "TEST: tests/scanner_invalid_3.src"
os.system("python compiler.py tests/scanner_invalid_3.src")
