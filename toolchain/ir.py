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

class Jump(PushAddr):
    mnemonic = "Jmp"
        
class ConditionalJump(PushAddr):
    mnemonic = "Jz"

class Call(Instruction):
    pass
    
class Return(Instruction):
    mnemonic = "Ret"
    
class Eq(Instruction):
    pass

class Add(Instruction):
    pass
    
class Mul(Instruction):
    pass
    
class Eq(Instruction):
    pass
    
class Sub(Instruction):
    pass
    
class Lt(Instruction):
    pass

    
class Stop(Instruction):
    pass
    
    

