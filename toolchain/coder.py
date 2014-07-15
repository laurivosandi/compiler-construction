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
    """
    Environment hold compiler state: what functions are available,
    what's in the stack and what instructions have been issued so far.
    """
    def __init__(self, gctx, stack=(), instructions=()):
        self.gctx = gctx
        self.stack = stack
        self.instructions = instructions
        
    def push_constant(env, constant):
        constant = int(constant) # Coarse True/False to 1/0
        return Environment(env.gctx, env.stack + (constant,), env.instructions + (ir.PushInt(constant),))
    
    def push_var(env, name):
        if name not in env.stack: raise Exception("Variable not present in stack!")
        if env.stack[-1] != name:
            offset = tuple(reversed(env.stack)).index(name) + 1
            return Environment(env.gctx, env.stack + (name,), env.instructions + (ir.Push(offset),))
        else:
            return env
        
    def push(self, instruction):
        stack = self.stack
        if isinstance(instruction, absy.DefinitionBuiltin): # Operands will be replaced with result
            stack = self.stack[:-1] # pop stack
        return Environment(self.gctx, self.stack, self.instructions + (instruction,))
        
    def __iter__(self):
        return iter(self.instructions)
        
    def compile(env, node):
        if isinstance(node, absy.Variable):
            # is is further in stack push i-th node
            return env.push_var(node.name)
            
        elif isinstance(node, absy.Nat) or isinstance(node, absy.Boolean):
            return env.push_constant(node.value)

        elif isinstance(node, absy.Apply):
            # Push function application arguments to stack
            
            for param in reversed(node.parameters):
                env = env.compile(param)
                
            d = env.gctx[node.func_name]
            if isinstance(d, absy.DefinitionBuiltin):
                if isinstance(d, builtin.DefinitionEq):
                    return env.push(ir.Eq())
                elif isinstance(d, builtin.DefinitionLessThan):
                    return env.push(ir.Lt())
                elif isinstance(d, builtin.DefinitionAdd):
                    return env.push(ir.Add())
                elif isinstance(d, builtin.DefinitionSub):
                    return env.push(ir.Sub())
                elif isinstance(d, builtin.DefinitionMul):
                    return env.push(ir.Mul())
                else:
                    raise Exception("Don't know how to compile built-in %s" % node.func_name)

            else:
                return env.push(ir.Call(node.func_name))

                # Pop parameters?
            
        elif isinstance(node, absy.Conditional):
            label_else = ir.Label("else%d" % id(env))
            label_end = ir.Label("end%d" % id(env))
            
            # If the expr_if is eq(_, 0) then we can skip some stuff
            optimize = isinstance(node.expr_if, absy.Apply) and node.expr_if.func_name == "eq" and isinstance(node.expr_if.parameters[1], absy.Nat) and node.expr_if.parameters[1].value == 0
            
            if not optimize:
                env = env.push(ir.PushInt(0))
            
            env = env.compile(node.expr_if)
                
            if not optimize:
                env = env.push(ir.Eq()) # Compare 0 to number previously on top of stack

            # Stack persists for both branches, start from scratch for instructions
            env_then = Environment(env.gctx, env.stack, ()).push(ir.ConditionalJump(label_else)).compile(node.expr_then).push(ir.Jump(label_end))
            env_else = Environment(env.gctx, env.stack, ()).push(label_else).compile(node.expr_else).push(label_end)
            #assert len(env_then.stack) == len(env_else.stack), "This should not happen, %s in then stack and %s in else stack" % (env_then.stack, env_else.stack)
            
            # Merge instruction branches and add placeholder for conditional return value
            return Environment(env.gctx, env.stack + ("cond%d" % id(env),), env.instructions + env_then.instructions + env_else.instructions)

        else:
            raise Exception("Don't know how to compile: %s of class %s" % (node, node.__class__.__name__))

            
def compile_program(gctx):
    for i  in Environment(gctx).compile(gctx["MAIN"].body):
        yield i
    yield ir.Stop()
    for label, d in gctx.iteritems():
        if not isinstance(d, absy.DefinitionBuiltin) and label != "MAIN":
            yield ir.Label(label)
            arg_names = tuple([arg_name for arg_name, arg_type in d.args])
            for i in Environment(gctx, arg_names).compile(d.body): yield i
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

