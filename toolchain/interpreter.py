# coding: utf-8
"""
Interpreter sets up global context and runs the context on the abstract
syntax tree.
"""

import sys
import lexer
from parser import Parser
from absy import Definition


class DefinitionBuiltin(Definition):
    body = "[built-in]"
    
    def __init__(self):
        pass

class DefinitionBuiltinEq(DefinitionBuiltin):
    name = "eq"
    return_type = "bool"
    
    def evaluate(self, parameters, gctx={}):
        a, b = parameters
        return a == b

class DefinitionBuiltinMul(DefinitionBuiltin):
    name = "mul"
    return_type = "int"
    
    def evaluate(self, parameters, gctx={}):
        a, b = parameters
        return a * b


class DefinitionBuiltinSub(DefinitionBuiltin):
    name = "sub"
    return_type = "int"
    
    def evaluate(self, parameters, gctx={}):
        a, b = parameters
        return a - b


if __name__ == "__main__":
    filename, = sys.argv[1:]
    tokens = tuple(lexer.tokenize(filename))
    defs, state = Parser(tokens).parse()
    
    gctx = {
        "eq": DefinitionBuiltinEq(),
        "sub": DefinitionBuiltinSub(),
        "mul": DefinitionBuiltinMul()}
    for d in defs:
        if d.name in gctx:
            print "Function already defined:", d.name
        else:
            gctx[d.name] = d
            
    print "Global context:", gctx.keys()
    print "The MAIN function returned:",  gctx["MAIN"].evaluate({}, gctx)
