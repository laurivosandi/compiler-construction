
import lexer
import os
import interpreter
from parser import Parser
from ctxcheck import context_check
import uebb
import coder

EXAMPLES = os.path.join(os.path.dirname(os.path.dirname(__file__)), "examples")

def test(filename, expected_output):

    print "### Interpreting", filename
    interpreted_ast_output = interpreter.interpret(os.path.join(EXAMPLES, filename))
    
    tokens = tuple(lexer.tokenize(os.path.join(EXAMPLES, filename)))
    defs, state = Parser(*tokens).parse()
    gctx, errors = context_check(defs)
    
    print "### Testing compiled instructions:"
    interpreted_instructions_output = uebb.interpret(coder.compile_program(gctx))
    
    if interpreted_ast_output != expected_output:
        raise RuntimeError("Interpreted output %d was incorrect, was expecting %d" % (interpreted_ast_output, expected_output))
    if interpreted_instructions_output != expected_output:
        raise RuntimeError("Compiled output %d was incorrect, was expecting %d" % (interpreted_instructions_output, expected_output))
    print
    print
    
test("mul.mo", 30)
test("fac.mo", 3628800)
test("sum.mo", 55)
test("div.mo", 9)
test("div2.mo", 9)
test("sqrt.mo", 42)


