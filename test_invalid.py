import os

print "TEST: tests/invalid_1.src"
os.system("python compiler.py tests/invalid_1.src")
print "TEST: tests/invalid_2.src"
os.system("python compiler.py tests/invalid_2.src")
print "TEST: tests/invalid_3.src"
os.system("python compiler.py tests/invalid_3.src")
