# coding: utf-8

"""
Built-in functions
"""

from absy import Definition


class DefinitionBuiltin(Definition):
    body = "[built-in]"
    
    def __init__(self):
        pass

class DefinitionEq(DefinitionBuiltin):
    name = "eq"
    return_type = "nat"
    args = ("a", "nat"), ("b", "nat")
    
    def evaluate(self, parameters, gctx):
        a, b = parameters
        return a == b

class DefinitionMul(DefinitionBuiltin):
    name = "mul"
    return_type = "nat"
    args = ("a", "nat"), ("b", "nat")
    
    def evaluate(self, parameters, gctx):
        a, b = parameters
        return a * b


class DefinitionSub(DefinitionBuiltin):
    name = "sub"
    return_type = "nat"
    args = ("a", "nat"), ("b", "nat")
    
    def evaluate(self, parameters, gctx):
        a, b = parameters
        return a - b

class DefinitionAdd(DefinitionBuiltin):
    name = "add"
    return_type = "nat"
    args = ("a", "nat"), ("b", "nat")
    
    def evaluate(self, parameters, gctx):
        a, b = parameters
        return a + b

class DefinitionLessThan(DefinitionBuiltin):
    name = "lt"
    return_type = "nat"
    args = ("a", "nat"), ("b", "nat")
    
    def evaluate(self, parameters, gctx):
        a, b = parameters
        return a < b
