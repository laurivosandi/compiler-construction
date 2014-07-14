# coding: utf-8
"""
µ-Opal to UEBB machine instruction set compiler
"""

import sys
import lexer
from parser import Parser
from ctxcheck import context_check
import absy
import ir

def compile(gctx):
    for i  in gctx["MAIN"].compile(gctx):
        yield i
    yield ir.Stop()
    for label, d in gctx.iteritems():
        if not isinstance(d, absy.DefinitionBuiltin) and label != "MAIN":
            yield ir.Label(label)
            for i in d.compile(gctx): yield i

if __name__ == "__main__":
    filename, = sys.argv[1:]
    tokens = tuple(lexer.tokenize(filename))
    defs, state = Parser(tokens).parse()
    gctx, errors = context_check(defs)

    if errors:
        for node, msg in errors:
            print msg, "on line", node.line, "column", node.column
                
    else:
        for i in compile(gctx):
            print i

