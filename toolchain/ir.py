# coding: utf-8

"""
Built-in functions
"""

class Instruction(object):
    @property
    def mnemonic(self):
        return self.__class__.__name__
        
    def __repr__(self):
        return self.mnemonic	

class Label(Instruction):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.mnemonic + "(" + self.name + ")"


class PushInt(Instruction):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "%s(%d)" % (self.mnemonic, self.value)
        
class Slide(Instruction):
    def __init__(self, offset):
        self.offset = offset

    def __repr__(self):
        return "%s(%d)" % (self.mnemonic, self.offset)

        
class Push(Instruction):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "%s(%s)" % (self.mnemonic, self.name)
       
class PushAddr(Instruction):
    def __init__(self, target):
        if isinstance(target, Label):
            self.target = target.name
        else:
            self.target = target
        
    def __repr__(self):
        return "%s(%s)" % (self.mnemonic, self.target)


        
class Call(Instruction):
    pass
    
class Return(Instruction):
    mnemonic = "Ret"
    
    

    
    
class Stop(Instruction):
    pass
    
class Jump(Instruction):
    def __init__(self, target):
        if isinstance(target, Label):
            self.target = target.name
        else:
            self.target = target
        
    def __repr__(self):
        return "%s(%s)" % (self.mnemonic, self.target)

    mnemonic = "Jmp"
    
class ConditionalJump(Jump):
    mnemonic = "Jz"

"""
Binary operators consumne two items from the top of the stack
"""
 
class BinaryOperator(Instruction): # Assume subclasses of this pop 2 arguments
    pass
    
class Eq(BinaryOperator):
    pass

class Add(BinaryOperator):
    pass
    
class Mul(BinaryOperator):
    pass
    
class Eq(BinaryOperator):
    pass
    
class Sub(BinaryOperator):
    pass
    
class Lt(BinaryOperator):
    pass

class Div(BinaryOperator):
    pass


