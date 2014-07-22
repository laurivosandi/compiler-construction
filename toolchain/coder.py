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

BUILTIN_MAPPING = {
    builtin.DefinitionEq:         ir.Eq,
    builtin.DefinitionLessThan:   ir.Lt,
    builtin.DefinitionAdd:        ir.Add,
    builtin.DefinitionSub:        ir.Sub,
    builtin.DefinitionMul:        ir.Mul,
    builtin.DefinitionDiv:        ir.Div
}

def elaborate(func):
    def wrapped(old_env, node):
        env = func(old_env, node)
        print "Compiled node", node, "to", env.instructions[-len(env.instructions)+len(old_env.instructions):], env.stack
        return env
    return wrapped

class Environment(object):
    """
    Environment holds compiler state: what functions are available,
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
        # Find the first instance of the variable on the stack
        offset = len(env.stack) - env.stack.index(name) - 1
        return Environment(env.gctx, env.stack + (name,), env.instructions + (ir.Push(offset),))

    def push(self, instruction):
        
        stack = self.stack
        if isinstance(instruction, ir.BinaryOperator): # Do this for builtins such as add, mul, div, sub
            stack = stack[:-2] + ("%s%s" % (instruction.mnemonic, id(self)),)
        elif isinstance(instruction, ir.PushAddr):
            stack = stack + ("CallAddr%s%dx" % (instruction.mnemonic, id(self)),)
        elif isinstance(instruction, ir.Call):
            # For the caller it looks like the call address gets popped and substituted with return value
            stack = stack[:-1] + ("CallReturnValue%d" % id(self),)
        elif isinstance(instruction, ir.Return):
            # Returning from function pops the return address from stack which is exactly before return value
            stack = stack[:-2] + stack[-1:]
        elif isinstance(instruction, ir.Slide):
            assert len(stack) > instruction.offset, "Stack is %s, attempted to slide by %d" % (stack, instruction.offset)
            stack = stack[:-instruction.offset-1] + stack[-1:]
        print "==> Pushed instruction", instruction, "stack was:", self.stack, "stack is now:", stack
        return Environment(self.gctx, stack, self.instructions + (instruction,))
        
    def __iter__(self):
        return iter(self.instructions)
        
    @elaborate
    def compile(env, node):
        if isinstance(node, absy.Variable):
            # is is further in stack push i-th node
            return env.push_var(node.name)
            
        elif isinstance(node, absy.Nat) or isinstance(node, absy.Boolean):
            return env.push_constant(node.value)

        elif isinstance(node, absy.Apply):



            # Resolve function definition
            d = env.gctx[node.func_name]
            
            assert len(node.parameters) == len(d.args), "Invalid invocation of %s" % node.func_name

            # Push function application arguments to stack            
            for param in reversed(node.parameters):
                env = env.compile(param)
                print "Pushed function call parameter:", param, "stack is now:", env.stack
            
            if isinstance(d, absy.DefinitionBuiltin):
                for dc, ic in BUILTIN_MAPPING.iteritems():
                    if  isinstance(d, dc):
                        return env.push(ic())
                raise Exception("Don't know how to compile built-in %s" % d.name)

            else:
                print "Compiling function call of", node.func_name
                return env.push(ir.PushAddr(node.func_name)).push(ir.Call()).push(ir.Slide(len(node.parameters)))
            
        elif isinstance(node, absy.Conditional):
            print "Compiling conditional if-expression"
            label_else = ir.Label("else%d" % id(env))
            label_fi = ir.Label("fi%d" % id(env))
            
            # If the expr_if is eq(_, 0) then we can skip some stuff
            optimize = isinstance(node.expr_if, absy.Apply) and node.expr_if.func_name == "eq" and isinstance(node.expr_if.parameters[1], absy.Nat) and node.expr_if.parameters[1].value == 0
            
            if not optimize:
                env = env.push(ir.PushInt(0))
            
            env = env.compile(node.expr_if)
                
            if not optimize:
                env = env.push(ir.Eq()) # Compare 0 to number previously on top of stack

            # Stack persists for both branches, start from scratch for instructions
            env_then = Environment(env.gctx, env.stack[:-1], ()).push(ir.ConditionalJump(label_else)).compile(node.expr_then).push(ir.Jump(label_fi))
            env_else = Environment(env.gctx, env.stack[:-1], ()).push(label_else).compile(node.expr_else).push(label_fi)
            assert len(env_then.stack) == len(env_else.stack), "This should not happen, %s in then stack and %s in else stack" % (env_then.stack, env_else.stack)
            
            # Pop if-expression value and push then-else expression value placeholder
            stack = env.stack[:-1] + ("cond%d" % id(env),)
            
            # Merge instruction branches and add placeholder for conditional return value
            instructions = env.instructions + env_then.instructions + env_else.instructions
            print "Merging conditional branches"
#            return Environment(env.gctx, stack, )
            return Environment(env.gctx, env.stack, env.instructions + env_then.instructions + env_else.instructions)

        else:
            raise Exception("Don't know how to compile: %s of class %s" % (node, node.__class__.__name__))

            
def compile_program(gctx):
    def compile_with_labels():
        print "Compiling function MAIN"
        for i  in Environment(gctx).compile(gctx["MAIN"].body):
            print "Produced instruction", i
            yield i
        yield ir.Stop()
        print
        for label, d in gctx.iteritems():
            if not isinstance(d, absy.DefinitionBuiltin) and label != "MAIN":
                print "Compiling function", label
                yield ir.Label(label)
                arg_names = tuple([arg_name for arg_name, arg_type in d.args])
                for i in Environment(gctx, arg_names + ("ReturnAddress",)).compile(d.body).push(ir.Return()):
                    print "Produced instruction", i
                    yield i
                print

    def scrub():
        offsets = {}
        instructions = ()
        j = 0
        for i in compile_with_labels():
            if isinstance(i, ir.Label):
                offsets[i.name] = j
            else:
                instructions = instructions + (i,)
                j += 1
        for i in instructions:
            if isinstance(i, ir.PushAddr) or isinstance(i, ir.Jump):
                i.target = offsets[i.target]
        return instructions
            
    return scrub()

if __name__ == "__main__":
    filename, = sys.argv[1:]
    tokens = tuple(lexer.tokenize(filename))
    defs, state = Parser(*tokens).parse()
    gctx, errors = context_check(defs)

    if errors:
        for node, msg in errors:
            print msg, "on line", node.line, "column", node.column
                
    else:
        fh = open(filename[:-3] + ".ma", "w")
        for i in compile_program(gctx):
            fh.write(repr(i) + "\n")
        fh.close()

