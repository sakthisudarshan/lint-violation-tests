"""Hotfile module - more than 10 violations concentrated in a single file."""
import os    # W0611
import sys   # W0611
import re    # W0611


x = 1           # C0103
y = 2           # C0103
z = x + y


def BadFunc1(A):    # C0103 x2
    """Bad function 1."""
    UnusedVar = A   # C0103, W0612
    return None


def BadFunc2(B):    # C0103 x2
    """Bad function 2."""
    TempVar = B     # C0103, W0612
    return None


def BadFunc3(C, D, E, F, G, H):  # C0103, R0913
    """Bad function 3 - too many arguments."""
    return C + D + E + F + G + H


def BadFunc4(X):    # C0103 x2
    """Bad function 4."""
    ResultVal = X * 2  # C0103, W0612
    return None


class badClass:        # C0103
    """Bad class name."""

    def BadMethod(self):   # C0103
        """Bad method name."""
        return 0
