
import os
from interpreter import interpret

EXAMPLES = os.path.join(os.path.dirname(os.path.dirname(__file__)), "examples")

assert interpret(os.path.join(EXAMPLES, "mul.mo")) == 30
assert interpret(os.path.join(EXAMPLES, "fac.mo")) == 3628800
assert interpret(os.path.join(EXAMPLES, "sum.mo")) == 55
assert interpret(os.path.join(EXAMPLES, "sqrt.mo")) == 42



