# coding: utf-8
"""
Interpreter sets up global context and runs the context on the abstract
syntax tree.
"""

import sys
import lexer
from parser import Parser
from ctxcheck import context_check

def interpret(filename):
    tokens = tuple(lexer.tokenize(filename))
    defs, state = Parser(*tokens).parse()
    gctx, errors = context_check(defs)

    if errors:
        for node, msg in errors:
            print msg, "on line", node.line, "column", node.column

    else:
        return gctx["MAIN"].evaluate({}, gctx)

if __name__ == "__main__":
    filename, = sys.argv[1:]
    print "The MAIN function returned:",  interpret(filename)
