import os

os.system("python compiler.py tests/scanner_valid_1.src")
os.system("python compiler.py tests/scanner_valid_2.src")
os.system("python compiler.py tests/scanner_invalid_1.src")
os.system("python compiler.py tests/scanner_invalid_2.src")
