import sys
import re
import lexer
import absy

# http://stackoverflow.com/questions/1788923/parameter-vs-argument
# arguments are passed in application of function
# parameters are defined in abstraction of function

# Note that same funcitonality in Scala was 382 lines

"""
Prog    ::= Def DefOpt eof
DefOpt  ::= Def DefOpt
          | eps  //Follow(DefOpt) = {'eof'}
Def     ::= 'DEF' Lhs '==' Expr 1
Lhs     ::= 'MAIN' ':' Type
          | id '(' Lhs1
Lhs1    ::= ')' ':' Type
          | Arg ArgOpt ')' ':' Type  //First(Arg) = {id}
ArgOpt  ::= ',' Arg ArgOpt
          | eps  //Follow(ArgOpt) = {')'}
Arg     ::= id ':' Type 2
Type    ::= nat 3
          | bool 4
Expr    ::= number 5
          | ture 6
          | false 7
          | id Expr1
          | 'IF' Expr 'THEN' Expr Expr3
Expr1   ::= '(' Expr2
          | eps 8  //Follow(Expr1) = Follow(Expr) = {',', 'eof', 'THEN', 'FI', 'ELSE', ',', '),}
ExprOpt ::= ',' Expr ExprOpt
          | eps  //Follow(ExprOpt) = {')'}
Expr2   ::= ')' 9
          | Expr ExprOpt ')' 9  //First(Expr) = {number, ture, false, id, 'IF'}
Expr3   ::=  'FI' 10
          |  'ELSE' Expr 'FI' 10
"""

class ParseError(StandardError):
    def __init__(self, message, token):
        self.message = message
        self.token = token

    def __str__(self):
        if self.token:
            return "%s on line %d column %d" % (self.message, 1,2)#self.token.line, self.token.column)
        return self.message

class Parser(object):
    """
    Parser object represents the tokens that haven't been parsed yet
    """
    def __init__(self, head, *tail):
        self.head = head
        self.tail = tail
        
    def parse_definition(state): # semantic action 1
        """
        Parse function definition
        """
        def_token, state = state.pop(lexer.TokenDef)
        function_name_identifier, state = state.pop(lexer.TokenIdentifier)
        arguments = ()
        
        if function_name_identifier.lexeme != "MAIN":
            state = state.skip(lexer.TokenOpen)
            if state.peek(lexer.TokenIdentifier):
                while True:
                    argument_token, state = state.pop(lexer.TokenIdentifier)
                    type_token, state = state.skip(lexer.TokenColon).pop(lexer.TokenType)
                    arguments = arguments + ((argument_token.lexeme, type_token.lexeme),)
                    token, state = state.pop(lexer.TokenClose, lexer.TokenComma)
                    if isinstance(token, lexer.TokenClose):
                        break
            else:
                state = state.skip(lexer.TokenClose)
        
        return_type, state = state.skip(lexer.TokenColon).pop(lexer.TokenType)
        body_expression, state = state.skip(lexer.TokenDefAs).parse_expression()
        return absy.Definition(function_name_identifier.lexeme, arguments, return_type.lexeme, body_expression, def_token), state
    

    def parse_nat(state): # semantic action 5
        return absy.Nat(state.head.lexeme), state.skip(lexer.TokenNat)

    def parse_true(state): # semantic action 6
        return absy.Boolean(True), state.skip(lexer.TokenTrue)
        
    def parse_false(state): # semantic action 7
        return absy.Boolean(False), state.skip(lexer.TokenFalse)

    def parse_conditional(state): # semantic action 8
        """
        Parse conditional expression
        """
        expr_if, state = state.skip(lexer.TokenIf).parse_expression()
        expr_then, state = state.skip(lexer.TokenThen).parse_expression()
        if state.peek(lexer.TokenElse):
            expr_else, state = state.skip(lexer.TokenElse).parse_expression()
            expr = absy.Conditional(expr_if, expr_then, expr_else)
        else:
            expr = absy.Conditional(expr_if, expr_then)
        return expr, state.skip(lexer.TokenFi)
                
    def parse_expression(state):
        """
        Expr ::= number 5
               | ture 6
               | false 7
               | id Expr1
               | 'IF' Expr 'THEN' Expr Expr3
        """
        if isinstance(state.head, lexer.TokenTrue):
            expr, state = state.parse_true()
        elif isinstance(state.head, lexer.TokenFalse):
            expr, state = state.parse_false()
        elif isinstance(state.head, lexer.TokenIdentifier):
            expr, state = state.parse_identifier()
        elif isinstance(state.head, lexer.TokenNat):
            expr, state = state.parse_nat()
        elif isinstance(state.head, lexer.TokenIf):
            expr, state = state.parse_conditional()
        else:
            raise ParseError("This should not happen")
        return expr, state

    def parse_identifier(state):
        """
        Expr1 ::= '(' Expr2
                | eps 8  //Follow(Expr1) = Follow(Expr) = {',', 'eof', 'THEN', 'FI', 'ELSE', ',', '),}
        """
        token, state = state.pop(lexer.TokenIdentifier)
        if state.peek(lexer.TokenOpen):
            # This is function application
            state = state.skip(lexer.TokenOpen)
            parameters = ()
            while True:
                parameter, state = state.parse_expression()
                parameters = parameters + (parameter,)
                if state.peek(lexer.TokenComma):
                    state = state.skip(lexer.TokenComma)
                    continue
                if state.peek(lexer.TokenClose):
                    break
            return absy.Apply(token.lexeme, parameters, token), state.skip(lexer.TokenClose)
        else:
            # This is a variable
            return absy.Variable(token.lexeme, token), state
        

    def parse(state):
        """
        Parse all tokens and generate list of function definition nodes
        """
        d, state = state.parse_definition()
        defs = [d]
        while not state.peek(lexer.TokenEndOfFile):
            d, state = state.parse_definition()
            defs.append(d)
        return defs, state # state.skip(lexer.TokenEndOfFile)
        
    def pop(state, *token_classes):
        """
        Check whether the head of tokens is instance of any of the required classes, return it if it is otherwise throw exception
        """
        for token_class in token_classes:
            if isinstance(state.head, token_class):
                return state.head, Parser(*state.tail)

        # No token class was matched, raise exception.
        # Note that as parsing is very strict it does not make much sense to
        # gather all error messages because the subsequent ones don't make much sense.
        raise ParseError("Got " + repr(state.head) + " of class " + state.head.__class__.__name__ + ", was expecting " + " or ".join([tc.__name__ for tc in token_classes]), state.head)

        
    def peek(state, token_class):
        return isinstance(state.head, token_class)
        
    def skip(state, *token_classes):
        token, state = state.pop(*token_classes)
        return state

if __name__ == "__main__":
    filename, = sys.argv[1:]
    tokens = tuple(lexer.tokenize(filename))
    defs, state = Parser(*tokens).parse()
    print "Parsed defs:"
    for d in defs:
        print d

