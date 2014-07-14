# coding: utf-8

"""
Built-in functions
"""

from absy import DefinitionBuiltin
import ir

class DefinitionEq(DefinitionBuiltin):
    name = "eq"
    return_type = "nat"
    args = ("a", "nat"), ("b", "nat")
    
    def evaluate(self, parameters, gctx):
        a, b = parameters
        return a == b
        
    def compile(self, gctx):
        yield ir.Eq()

class DefinitionMul(DefinitionBuiltin):
    name = "mul"
    return_type = "nat"
    args = ("a", "nat"), ("b", "nat")
    
    def evaluate(self, parameters, gctx):
        a, b = parameters
        return a * b

    def compile(self, gctx):
        yield ir.Mul()


class DefinitionSub(DefinitionBuiltin):
    name = "sub"
    return_type = "nat"
    args = ("a", "nat"), ("b", "nat")
    
    def evaluate(self, parameters, gctx):
        a, b = parameters
        return a - b
        
    def compile(self, gctx):
        yield ir.Sub()


class DefinitionAdd(DefinitionBuiltin):
    name = "add"
    return_type = "nat"
    args = ("a", "nat"), ("b", "nat")
    
    def evaluate(self, parameters, gctx):
        a, b = parameters
        return a + b

    def compile(self, gctx):
        yield ir.Add()


class DefinitionLessThan(DefinitionBuiltin):
    name = "lt"
    return_type = "nat"
    args = ("a", "nat"), ("b", "nat")
    
    def evaluate(self, parameters, gctx):
        a, b = parameters
        return a < b

    def compile(self, gctx):
        yield ir.Lt()
        
