import os

print "TEST: tests/valid_1.src"
os.system("python compiler.py tests/valid_1.src")
os.system("lli ir.ll")
print "TEST: tests/valid_2.src"
os.system("python compiler.py tests/valid_2.src")
os.system("lli ir.ll")
print "TEST: tests/valid_3.src"
os.system("python compiler.py tests/valid_3.src")
os.system("lli ir.ll")
print "TEST: tests/valid_4.src"
os.system("python compiler.py tests/valid_4.src")
os.system("lli ir.ll")
