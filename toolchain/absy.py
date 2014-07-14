# coding: utf-8
"""
Abstract syntax tree classes
"""

class Node(object):
    def free_variables(self):
        """
        By default AST node has no free variabls associated with it
        """
        return set()
        
    def check(self, gctx, lctx=None):
        return ()

class Value(Node):
    def evaluate(self, *args):
        return self.value
    
class Expr(Node):
    pass
    
class Definition(Node):
    inline = False # Don't attempt to inline this function during compilation

    def __init__(self, name, args, return_type, body, token):
        self.name = name
        self.args = args
        self.return_type = return_type
        self.body = body
        self.token = token
        
    def check(self, gctx):
        arg_names = []
        for arg_name, arg_type in self.args:
            if arg_name in arg_names:
                yield self.token, "Multiple arguments with same name: %s" % arg_name
            else:
                arg_names.append(arg_name)
        lctx = dict(self.args)
        for e, err in self.body.check(gctx, lctx):
            yield e, err
        
    def check_application(self, expr_types):
        """
        Check function application with particular parameter types
        """
        if len(expr_types) != len(self.args):
            yield self.token, "Was expecting %s arguments, got %d" % (len(self.args), len(expr_types))
        else:
            for index, (arg_nam, arg_type) in enumerate(self.args):
                if expr_types[index] != arg_type:
                    yield self.token, "Was expecting %s, got %s" % (arg_type, expr_types[index])
        
    def evaluate(self, parameters, gctx={}):
        """
        Evaluate function body with given parameters and functions defined in global context
        """
        lctx = dict(zip([arg_name for arg_name, arg_type in self.args], parameters))
        return self.body.evaluate(lctx, gctx)
        
    def compile(self):
        for instruction in self.body.compile():
            yield instruction
            
    def __repr__(self):
        return "DEF " + self.name + "(" + ", ".join([arg_name + ":"+ arg_type for arg_name, arg_type in self.args]) + "):" + self.return_type + " == " + repr(self.body)

class Apply(Node):
    def __init__(self, func_name, parameters, token):
        self.func_name = func_name
        self.parameters = parameters
        self.token = token
        
    def free_variables(self):
        r = set()
        for param in self.parameters:
            r.update(param.free_variables())
        return s
        
    def check(self, gctx, lctx):
        """
        Attempt to check function call with lctx types and gctx function (signatures)
        """
        if self.func_name not in gctx:
            yield self.token, "Could not resolve function named %s" % self.func_name
        return
        # TODO: unification?
#        for d, err in gctx[self.func_name].check_application([lctx[j] for j in self.parameters]):
#            yield d, err

        
    def infer_type(self):
        return gctx[self.func_name].return_type
        
    def evaluate(self, lctx={}, gctx={}):
        """
        Attempt to evaluate function call with lctx values and gctx functions
        """
        return gctx[self.func_name].evaluate([p.evaluate(lctx, gctx) for p in self.parameters], gctx)
        
    def compile(self):
        if gctx[self.func_name].inline:
            yield "pusha"
            yield "pushb"
            for instruction in gctx[self.func_name].compile():
                yield instruction
        else:
            NotImplemented
                
        
    def __repr__(self):
        return self.func_name + "(" + ", ".join([repr(j) for j in self.parameters]) + ")"
    
class Variable(Node):
    def __init__(self, name, token):
        self.name = name
        self.token = token
        
    def free_variables(self):
        return set(self.name)
        
    def infer_type(self):
        return lctx[self.name].infer_type()
        
    def evaluate(self, lctx={}, gctx={}):
        return lctx[self.name]
        
    def __repr__(self):
        return self.name
        
    def check(self, gctx, lctx):
        if self.name not in lctx:
            yield self.token, "Variable not defined in local context"
        

class Boolean(Value):
    def __init__(self, value):
        if value in ("True", "true", "1", 1, True):
            self.value = True
        elif value in ("False", "false", "0", 0, False):
            self.value = False
        else:
            raise ValueError("Unable to convert %s to boolean" % value)
            
    def __repr__(self):
        return "True" if self.value else "False"
    
class Nat(Value):
    def __init__(self, value):
        value = int(value)
        if (value < 0):
            raise ValueError("%d is not natural number" % value)
        self.value = value

    def __repr__(self):
        return str(self.value)
        
    def evaluate(self, lctx={}, gctx={}):
        return self.value

class Conditional(Expr):
    def __init__(self, expr_if, expr_then, expr_else=None):
        self.expr_if = expr_if
        self.expr_then = expr_then
        self.expr_else = expr_else

    def free_variables(self):
        return self.expr_if.free_variables().union(self.expr_then.free_variables().union(self.expr_else.free_variables()))
        
    def __repr__(self):
        return "IF " + repr(self.expr_if) + " THEN " + repr(self.expr_then) + ((" ELSE " + repr(self.expr_else)) if self.expr_else else "") + " FI"
        
    def evaluate(self, lctx={}, gctx={}):
        if self.expr_if.evaluate(lctx, gctx):
            return self.expr_then.evaluate(lctx, gctx)
        else:
            return self.expr_else.evaluate(lctx, gctx)

    def check(self, gctx, lctx):
        for d, err in self.expr_if.check(gctx, lctx):
            yield d, err
        for d, err in self.expr_then.check(gctx, lctx):
            yield d, err
        for d, err in self.expr_else.check(gctx, lctx):
            yield d, err        

