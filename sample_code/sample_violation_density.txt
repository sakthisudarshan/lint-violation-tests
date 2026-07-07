"""Module with intentionally high violation density across multiple severity levels."""
import os   # W0611 unused-import
import sys  # W0611 unused-import
import re   # W0611 unused-import


x = 1          # C0103 invalid-name (too short)
y = 2          # C0103 invalid-name
AB = 3         # C0103 invalid-name (non-constant uppercase)
longVariableName = "value"   # C0103 - camelCase variable

def BadFunctionName(a, b):   # C0103 - PascalCase function
    """Badly named function."""
    unused_here = a + b      # W0612 unused-variable
    return None


def another_bad_one(p, q, r, s, t, u):  # R0913 too-many-arguments (>5)
    """Function with too many arguments."""
    i = p + q      # C0103 short name i allowed, but this stacks violations
    j = r + s      # W0612 unused-variable
    return t + u


class lowercaseClass:           # C0103 invalid-name (not CapWords)
    """Class with bad naming."""

    def BadMethod(self, val):   # C0103 invalid-name
        """Method with bad name."""
        TempVar = val * 2       # C0103 invalid-name
        return TempVar


a = 1     # C0103
b = 2     # C0103
c = a + b
d = c * 2
