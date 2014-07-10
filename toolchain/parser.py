import sys
import re
import lexer

class Parser(object):
    """
    Parser object represents the tokens that haven't been parsed yet, defs
    that have been extracted so far and errors that have occurred until now.
    """
    def __init__(self, tokens, defs=(), errors=()):
        self.tokens = tokens
        self.defs = defs
        self.errors = errors
        
    def parse_left_hand_side(self):
        function_name_identifier, state = self.pop(lexer.TokenIdentifier)
        return_type, state = state.skip(lexer.TokenOpen).skip(lexer.TokenClose).skip(lexer.TokenColon).pop(lexer.TokenType)
        return state
        
    def parse(self):
        return self.parse_definition()
        
    def parse_expression(self):
        token, state = self.pop(lexer.TokenTrue, lexer.TokenFalse, lexer.TokenIdentifier, lexer.TokenIf, lexer.TokenNat)
        return state
    
    def error(self, diag):
        return Parser(self.tokens, self.defs, self.errors + (diag,))
        
    def skip(self, *token_classes):
        return self.pop(*token_classes)[1]
    
    def pop(self, *token_classes):
        errors = self.errors
        for token_class in token_classes:
            if isinstance(self.tokens[0], token_class):
                break
        else:
            thingies = " or ".join([token_class.__name__ for token_class in token_classes])
            errors = errors + (("Was expecting " + thingies + " got " + self.tokens[0].__class__.__name__ + " instead", self.tokens[0]),)
        return self.tokens[0], Parser(self.tokens[1:], self.defs, errors)

    def parse_definition(self):
        return self.skip(lexer.TokenDef).parse_left_hand_side().skip(lexer.TokenDefAs).parse_expression()

    
def parse(tokens):
    """
    Return parsed defs from tokens
    """
    state = Parser(tuple(tokens)).parse().skip(lexer.TokenEndOfFile)
    print "Tokens left:", state.tokens
    return state.defs, state.errors


if __name__ == "__main__":
    filename, = sys.argv[1:]
    defs, errors = parse(lexer.tokenize(filename))
    print "Parsed defs:", defs
    print "Errors:"
    for error, token in errors:
        print error, token, "on line", token.line, "column", token.column

    for d in defs:
        print token.__class__.__name__, repr(token.lexeme), token.line, token.column
    print

