import sys
import re
import lexer
import absy

# http://stackoverflow.com/questions/1788923/parameter-vs-argument
# arguments are passed in application of function
# parameters are defined in abstraction of function

# Note that same funcitonality in Scala was 382 lines

class ParseError(StandardError):
    def __init__(self, message, token):
        self.message = message
        self.token = token

    def __str__(self):
        if self.token:
            return "%s on line %d column %d" % (self.message, self.token.line, self.token.column)
        return self.message

class Parser(object):
    """
    Parser object represents the tokens that haven't been parsed yet
    """
    def __init__(self, tokens):
        self.tokens = tokens

    def parse_conditional(state):
        """
        Parse conditional expression
        """
        expr_if, state = state.parse_expression()
        expr_then, state = state.skip(lexer.TokenThen).parse_expression()
        if state.peek(lexer.TokenElse):
            expr_else, state = state.skip(lexer.TokenElse).parse_expression()
            expr = absy.Conditional(expr_if, expr_then, expr_else)
        else:
            expr = absy.Conditional(expr_if, expr_then)
        return expr, state.skip(lexer.TokenFi)
        
    def parse_expression(state):
        """
        Recursively parse expression
        """
        token, state = state.pop(lexer.TokenBoolean, lexer.TokenIdentifier, lexer.TokenIf, lexer.TokenNat)
        if isinstance(token, lexer.TokenBoolean):
            # This is boolean constant
            expr = absy.Boolean(token.lexeme)
        elif isinstance(token, lexer.TokenIdentifier):
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

                expr = absy.Apply(token.lexeme, parameters)
                state = state.skip(lexer.TokenClose)
            else:
                # This is a variable
                expr = absy.Variable(token.lexeme)

        elif isinstance(token, lexer.TokenIf):
            # This is conditional expression
            expr, state = state.parse_conditional()
        elif isinstance(token, lexer.TokenNat):
            # This is natural number constant
            expr = absy.Nat(token.lexeme)
        else:
            print "This should not happen"
            return None, state
        return expr, state
        
    def parse_definition(state):
        """
        Parse function definition
        """
        function_name_identifier, state = state.skip(lexer.TokenDef).pop(lexer.TokenIdentifier)
        state = state.skip(lexer.TokenOpen)
        arguments = ()
        while state.peek(lexer.TokenIdentifier):
            argument_token, state = state.pop(lexer.TokenIdentifier)
            type_token, state = state.skip(lexer.TokenColon).pop(lexer.TokenType)
            arguments = arguments + (absy.Argument(argument_token, type_token),)
            if state.peek(lexer.TokenComma):
                state.pop(lexer.TokenComma)
                continue
            elif state.peek(lexer.TokenClose):
                break
        
        return_type, state = state.skip(lexer.TokenClose).skip(lexer.TokenColon).pop(lexer.TokenType)
        body_expression, state = state.skip(lexer.TokenDefAs).parse_expression()
        return absy.Definition(function_name_identifier.lexeme, arguments, return_type.lexeme, body_expression), state
    
    def parse(state):
        """
        Parse all tokens and generate list of function definition nodes
        """
        d, state = state.parse_definition()
        defs = [d]
        while not state.peek(lexer.TokenEndOfFile):
            d, state = state.parse_definition()
            defs.append(d)
        return defs, state.skip(lexer.TokenEndOfFile)
        
    def pop(state, *token_classes):
        """
        Check whether the head of tokens is instance of any of the required classes, return it if it is otherwise throw exception
        """
        for token_class in token_classes:
            if isinstance(state.tokens[0], token_class):
                break
        else:
            # No token class was matched, raise exception.
            # Note that as parsing is very strict it does not make much sense to
            # gather all error messages because the subsequent ones don't make much sense.
            raise ParseError("Got " + state.tokens[0].__class__.__name__ + ", was expecting " + " or ".join([token_class.__name__ for token_class in token_classes]), state.tokens[0])
        return state.tokens[0], Parser(state.tokens[1:])
        
    def peek(state, token_class):
        return isinstance(state.tokens[0], token_class)
        
    def skip(state, *token_classes):
        return state.pop(*token_classes)[1]

if __name__ == "__main__":
    filename, = sys.argv[1:]
    tokens = tuple(lexer.tokenize(filename))
    defs, state = Parser(tokens).parse()
    print "Parsed defs:"
    for d in defs:
        print d

