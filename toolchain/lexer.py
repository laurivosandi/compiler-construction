# coding: utf-8
"""
This lexer understands µ-Opal, a functional programming language
developed at Technical University of Berlin.
"""

class Token():
    def __init__(self, lexeme, line, column):
        self.lexeme = lexeme
        self.line = line
        self.column = column
        
    def __repr__(self):
        return repr(self.lexeme)

class TokenMeaningless(Token):
    pass
    
class TokenComment(TokenMeaningless):
    REGEX = "--.*\n"

class TokenNewline(TokenMeaningless):
    REGEX = "\s*\n\s*"

class TokenWhitespace(TokenMeaningless):
    REGEX = "\s+"

class TokenOpen(Token):
    REGEX = "\("

class TokenClose(Token):
    REGEX = "\)"

class TokenComma(Token):
    REGEX = ","

class TokenColon(Token):
    REGEX = "\:"

class TokenDefAs(Token):
    REGEX = "=="

class TokenDef(Token):
    REGEX = "DEF"

class TokenIf(Token):
    REGEX = "IF"

class TokenThen(Token):
    REGEX = "THEN"

class TokenElse(Token):
    REGEX = "ELSE"

class TokenFi(Token):
    REGEX = "FI"

class TokenBoolean(Token):
    pass

class TokenTrue(TokenBoolean):
    REGEX = "true"

class TokenFalse(TokenBoolean):
    REGEX = "false"

class TokenNat(Token):
    REGEX = "\d+"

class TokenType(Token):
    pass

class TokenTypeNat(TokenType):
    REGEX = "nat"
    
class TokenTypeBool(TokenType):
    REGEX = "bool"

class TokenIdentifier(Token):
    REGEX = "\w+[\w\d]*"

class TokenEndOfFile(Token):
    REGEX = "$"

    def __repr__(self):
        return "EOF"

TOKENS = \
    TokenNewline, \
    TokenWhitespace, \
    TokenOpen, \
    TokenClose, \
    TokenComma, \
    TokenColon, \
    TokenDefAs, \
    TokenDef, \
    TokenIf, \
    TokenThen, \
    TokenElse, \
    TokenFi, \
    TokenTrue, \
    TokenFalse, \
    TokenNat, \
    TokenTypeNat, \
    TokenTypeBool, \
    TokenIdentifier, \
    TokenComment
    
import sys
import re


def tokenize(filename):
    """
    Tokenize source code
    """
    remainder = open(filename).read()
    line = 1
    column = 1
    while remainder:
        for token_class in TOKENS:
            m = re.match(token_class.REGEX, remainder)
            if not m:
                continue
            lexeme = remainder[:m.end()]
            token = token_class(lexeme, line, column)

            if not isinstance(token, TokenMeaningless):
                yield token

            if "\n" in lexeme:
                line += lexeme.count("\n")
                column = len(lexeme.rsplit("\n", 1)[1])
            else:
                column += len(lexeme)
            remainder = remainder[m.end():]
            break
        else:
            raise RuntimeError("Could not parse: %s" % remainder)
            
    # Appending EOF makes it easier to parse, as head is always present for parse(head, *tokens)
    yield TokenEndOfFile("", line, column)

if __name__ == "__main__":
    filename, = sys.argv[1:]
    for token in tokenize(filename):
        print token.__class__.__name__, repr(token.lexeme), token.line, token.column
    print

