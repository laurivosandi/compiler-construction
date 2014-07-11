# coding: utf-8
"""
Abstract syntax tree classes
"""

class Node(object):
    pass

class Value(Node):
    def evaluate(self, *args):
        return self.value
    
class Expr(Node):
    pass
    
class Type(Node):
    pass
    
class Definition(Node):
    def __init__(self, name, args, return_type, body):
        self.name = name
        self.args = args
        self.return_type = return_type
        self.body = body
        
    def evaluate(self, parameters, gctx={}):
        lctx = dict(zip([a.name_token.lexeme for a in self.args], parameters))
        return self.body.evaluate(lctx, gctx)

    def __repr__(self):
        return "DEF " + self.name + "(" + ", ".join([repr(j) for j in self.args]) + "):" + self.return_type + " == " + repr(self.body)

class Apply(Node):
    def __init__(self, func_name, parameters):
        self.func_name = func_name
        self.parameters = parameters
        
    def evaluate(self, lctx={}, gctx={}):
        return gctx[self.func_name].evaluate([p.evaluate(lctx, gctx) for p in self.parameters], gctx)
        
    def __repr__(self):
        return self.func_name + "(" + ", ".join([repr(j) for j in self.parameters]) + ")"
    
class Variable(Node):
    def __init__(self, name):
        self.name = name
        
    def evaluate(self, lctx={}, gctx={}):
        return lctx[self.name]
        
    def __repr__(self):
        return self.name
        
class Argument(Node):
    def __init__(self, name_token, type_token):
        self.name_token = name_token
        self.type_token = type_token
        
    def __repr__(self):
        return self.name_token.lexeme + ":" + self.type_token.lexeme
    
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
        
    def __repr__(self):
        return "IF " + repr(self.expr_if) + " THEN " + repr(self.expr_then) + ((" ELSE " + repr(self.expr_else)) if self.expr_else else "") + " FI"
        
    def evaluate(self, lctx={}, gctx={}):
        if self.expr_if.evaluate(lctx, gctx):
            return self.expr_then.evaluate(lctx, gctx)
        else:
            return self.expr_else.evaluate(lctx, gctx)

class TypeBool(Type):
    pass
    
class TypeNat(Type):
    pass
    
class TypeUnknown(Type):
    pass
    
class TypeFunction(Type):
    pass
