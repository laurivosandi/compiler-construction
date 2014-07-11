# coding: utf-8
"""
Abstract syntax tree classes
"""

class Value(object):
    pass
    
class Expr(object):
    pass
    
class Type(object):
    pass
    
class Variable(object):
    def __init__(self, name):
        self.name = name
        
    def __repr__(self):
        return self.name
        
class Argument(object):
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

class Definition():
    def __init__(self, name, args, return_type, body):
        self.name = name
        self.args = args
        self.return_type = return_type
        self.body = body

    def __repr__(self):
        return "DEF " + self.name + "(" + ", ".join([repr(j) for j in self.args]) + "):" + self.return_type + " == " + repr(self.body)

class Conditional(Expr):
    def __init__(self, expr_if, expr_then, expr_else=None):
        self.expr_if = expr_if
        self.expr_then = expr_then
        self.expr_else = expr_else
        
    def __repr__(self):
        return "IF " + repr(self.expr_if) + " THEN " + repr(self.expr_then) + ((" ELSE " + repr(self.expr_else)) if self.expr_else else "") + " FI"

class Apply():
    def __init__(self, func_name, parameters):
        self.func_name = func_name
        self.parameters = parameters
        
    def __repr__(self):
        return self.func_name + "(" + ", ".join([repr(j) for j in self.parameters]) + ")"

class TypeBool(Type):
    pass
    
class TypeNat(Type):
    pass
    
class TypeUnknown(Type):
    pass
    
class TypeFunction(Type):
    pass
