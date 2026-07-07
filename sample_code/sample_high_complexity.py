"""Module with complexity violations - too many branches and deep nesting (R0912, R1702)."""


def too_many_branches(a, b, c, d, e, f, g):  # R0913 too-many-arguments
    """Function exceeding the max-branches=12 threshold (has 14 branches)."""
    result = 0
    if a > 0:
        result += 1
    if b > 0:
        result += 2
    if c > 0:
        result += 3
    if d > 0:
        result += 4
    if e > 0:
        result += 5
    if f > 0:
        result += 6
    if g > 0:
        result += 7
    if a > 10:
        result += 8
    if b > 10:
        result += 9
    if c > 10:
        result += 10
    if d > 10:
        result += 11
    if e > 10:
        result += 12
    if f > 10:
        result += 13
    return result


def deeply_nested_function(data):
    """Function exceeding max-nested-blocks=5 threshold (6 levels deep)."""
    result = []
    if data:                               # level 1
        for group in data:                 # level 2
            if group:                      # level 3
                for item in group:         # level 4
                    if item is not None:   # level 5
                        if item > 0:       # level 6 - R1702
                            result.append(item)
    return result


def long_function_with_many_statements(items):
    """Function exceeding max-statements=50 threshold."""
    s1 = 0
    s2 = 0
    s3 = 0
    s4 = 0
    s5 = 0
    s6 = 0
    s7 = 0
    s8 = 0
    s9 = 0
    s10 = 0
    s11 = 0
    s12 = 0
    s13 = 0
    s14 = 0
    s15 = 0
    s16 = 0
    s17 = 0
    s18 = 0
    s19 = 0
    s20 = 0
    s21 = 0
    s22 = 0
    s23 = 0
    s24 = 0
    s25 = 0
    s26 = 0
    s27 = len(items)
    s28 = s1 + s2
    s29 = s3 + s4
    s30 = s5 + s6
    s31 = s7 + s8
    s32 = s9 + s10
    s33 = s11 + s12
    s34 = s13 + s14
    s35 = s15 + s16
    s36 = s17 + s18
    s37 = s19 + s20
    s38 = s21 + s22
    s39 = s23 + s24
    s40 = s25 + s26
    s41 = s27 + s28
    s42 = s29 + s30
    s43 = s31 + s32
    s44 = s33 + s34
    s45 = s35 + s36
    s46 = s37 + s38
    s47 = s39 + s40
    s48 = s41 + s42
    s49 = s43 + s44
    s50 = s45 + s46
    s51 = s47 + s48   # 51st statement - R0915
    return s49 + s50 + s51
