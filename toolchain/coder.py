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
import builtin

class Environment(object):
    def __init__(self, *variables):
        
        self.stack = variables
            
        print "# Created environment:", self.stack
        
    def push_constant(self, constant):
        self.stack.append(constant)
    
    def push_var(self, name):
        if self.stack[-1] != name:
            self.stack.append(name)
        if name not in self.stack: raise Exception("Variable not present in stack!")
        yield Slide(reversed(self.stack).index(name))
        
    def compile(self, node, gctx):
        if isinstance(node, absy.Variable):
            # is is further in stack push i-th node
            yield ir.Push(node.name)
            
        elif isinstance(node, absy.Nat):
            yield ir.PushInt(node.value)

        elif isinstance(node, absy.Apply):
            # Push function application arguments to stack
            for param in reversed(node.parameters):
                for i in self.compile(param, gctx): yield i
                
            d = gctx[node.func_name]
            if isinstance(d, absy.DefinitionBuiltin):
                if isinstance(d, builtin.DefinitionEq):
                    yield ir.Eq()
                elif isinstance(d, builtin.DefinitionLessThan):
                    yield ir.Lt()
                elif isinstance(d, builtin.DefinitionAdd):
                    yield ir.Add()
                elif isinstance(d, builtin.DefinitionSub):
                    yield ir.Sub()
                elif isinstance(d, builtin.DefinitionMul):
                    yield ir.Mul()
                else:
                    raise Exception("Don't know how to compile built-in %s" % node.func_name)

            else:
                yield ir.Call(node.func_name)

                # Pop parameters?
            
        elif isinstance(node, absy.Conditional):
            label_else = ir.Label("else%d" % id(self))
            label_end = ir.Label("end%d" % id(self))
            
            # If the expr_if is eq(_, 0) then we can skip some stuff
            optimize = isinstance(node.expr_if, absy.Apply) and node.expr_if.func_name == "eq" and isinstance(node.expr_if.parameters[1], absy.Nat) and node.expr_if.parameters[1].value == 0
            
            if not optimize:
                yield ir.PushInt(0)
            
            for i in self.compile(node.expr_if, gctx):
                yield i
                
            if not optimize:
                yield ir.Eq() # Compare 0 to number previously on top of stack
                
            yield ir.ConditionalJump(label_else)
            for i in self.compile(node.expr_then, gctx):
                yield i
            yield ir.Jump(label_end)
            yield label_else
            for i in self.compile(node.expr_else, gctx): yield i
            yield label_end

    #    elif isinstance(node, absy.Boolean):
    #        return ir.PushInt(1 if self.value else 0)

        else:
            raise Exception("Don't know how to compile: %s of class %s" % (node, node.__class__.__name__))

            
def compile_program(gctx):
    for i  in Environment().compile(gctx["MAIN"].body, gctx):
        yield i
    yield ir.Stop()
    for label, d in gctx.iteritems():
        if not isinstance(d, absy.DefinitionBuiltin) and label != "MAIN":
            yield ir.Label(label)
            arg_names = [arg_name for arg_name, arg_type in d.args]
            for i in Environment(*arg_names).compile(d.body, gctx): yield i
            yield ir.Return()


if __name__ == "__main__":
    filename, = sys.argv[1:]
    tokens = tuple(lexer.tokenize(filename))
    defs, state = Parser(tokens).parse()
    gctx, errors = context_check(defs)

    if errors:
        for node, msg in errors:
            print msg, "on line", node.line, "column", node.column
                
    else:
        for i in compile_program(gctx):
            print i

