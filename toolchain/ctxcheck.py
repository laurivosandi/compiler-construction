
import builtin

def context_check(defs):
    gctx = {
        "eq":  builtin.DefinitionEq(),
        "sub": builtin.DefinitionSub(),
        "add": builtin.DefinitionAdd(),
        "mul": builtin.DefinitionMul(),
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
            
        # Check that definition body expression evaluates to something of definition return type
        if "MAIN" not in gctx:
            yield d.token, "No MAIN defined"
    return gctx, tuple(aggregate())
