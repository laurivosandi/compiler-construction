
import builtin
import absy
import parser

class ContextCheckError(parser.ParseError):
    pass

def infer_type(expr, gctx, lctx):
    if isinstance(expr, absy.Boolean):
        return "bool"
    elif isinstance(expr, absy.Nat):
        return "nat"
    elif isinstance(expr, absy.Conditional):
        type_then = infer_type(expr.expr_then, gctx, lctx)
        type_else = infer_type(expr.expr_else, gctx, lctx)
        if type_then == type_else:
            return type_then
        else:
            raise ContextCheckError("Then returns %s, but else returns %s" % (type_then, type_else), expr.token)
    elif isinstance(expr, absy.Apply):
        d = gctx[expr.token.lexeme]
        assert len(expr.parameters) == len(d.args), "Function requires %d functions, got %d" % (len(d.args), len(expr.parameters))
        for i, (arg_name, arg_type) in enumerate(d.args):
            inferred_type = infer_type(expr.parameters[i], gctx, lctx)
            if inferred_type == arg_type:
                return d.return_type
            else:
                raise ContextCheckError("Function %s expected %s for argument %d, got %s" % (d.name, arg_type, i+1, inferred_type), expr.token)

    elif isinstance(expr, absy.Variable):
        return lctx[expr.name]
    raise ContextCheckError("Don't know how to infer type for %s" % expr, expr.token)
    

def context_check(defs):
    gctx = {
        "eq":  builtin.DefinitionEq(),
        "sub": builtin.DefinitionSub(),
        "add": builtin.DefinitionAdd(),
        "mul": builtin.DefinitionMul(),
        "div": builtin.DefinitionDiv(),
        "lt":  builtin.DefinitionLessThan()
    }

    def aggregate():
        errors = []
        for d in defs:
            if d.name in gctx:
                yield d.token, "Function " + d.name + " already defined"
            else:
                gctx[d.name] = d
                
        for d in defs:
            for t, msg in d.check(gctx):
                yield t, msg
        inferred_type = infer_type(d.body, gctx, dict(d.args))
        if inferred_type != d.return_type:
            raise ContextCheckError("Expression evaluated to %s, function return type was defined as %s" % (inferred_type, d.return_type), d.token)
            
        # Check that definition body expression evaluates to something of definition return type
        if "MAIN" not in gctx:
            yield d.token, "No MAIN defined"
    return gctx, tuple(aggregate())
