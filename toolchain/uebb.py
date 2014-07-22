import ir

def interpret(instructions):
    pc = 0
    stack = []
    total = 0
    while total < 250:
        total += 1
        i = instructions[pc]
        pc += 1
        print ("Issuing %02d. %s" % (pc, i)).ljust(30),
        if isinstance(i, ir.PushInt):
            stack.append(i.value)
        elif isinstance(i, ir.PushAddr):
            stack.append(i.target)
        elif isinstance(i, ir.Call):
            stack, pc = stack[:-1] + [pc], stack[-1]
        elif isinstance(i, ir.Return):
            stack, pc = stack[:-2] + stack[-1:], stack[-2]
        elif isinstance(i, ir.ConditionalJump):
            stack, cond = stack[:-1], stack[-1]
            if cond == 0:
                pc = i.target
        elif isinstance(i, ir.Jump):
            pc = i.target
        elif isinstance(i, ir.Swap):
            stack = stack[:-2] + [stack[-1], stack[-2]]
        elif isinstance(i, ir.Push):
            stack.append(stack[-i.name-1])
        elif isinstance(i, ir.Mul):
            stack = stack[:-2] + [stack[-2] * stack[-1]]
        elif isinstance(i, ir.Add):
            stack = stack[:-2] + [sum(stack[-2:])]
        elif isinstance(i, ir.Sub):
            stack = stack[:-2] + [stack[-1] - stack[-2]]
        elif isinstance(i, ir.Div):
            stack = stack[:-2] + [stack[-1] / stack[-2]]

        elif isinstance(i, ir.Eq):
            stack = stack[:-2] + [int(stack[-1] == stack[-2])]

        elif isinstance(i, ir.Slide):
            stack = stack[:-i.offset-1] + stack[-1:]
        elif isinstance(i, ir.Stop):
            try:
                value, = stack
                return value
            except ValueError:
                raise RuntimeError("Expected stack to contain 1 element, got %d" % len(stack))
        else:
            raise RuntimeError("Unknown instruction: %s" % i)
        print "  stack:", ", ".join([str(i) for i in stack])
    raise RuntimeError("VM timed out")

