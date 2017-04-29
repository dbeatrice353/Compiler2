# Compiler2

python 2.7
LLVM 3.4

A study in compiler theory.

To run:

$ python compiler.py hello_world.src  # compile a source file to the llvm ir (.ll)

$ lli ir.ll                           # run the .ll file using lli
