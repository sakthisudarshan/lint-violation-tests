"""Module with code style violations - line length and whitespace (C0301, C0303)."""


def long_line_function():
    """Function with lines that exceed the 100-character limit configured in .pylintrc."""
    very_long_variable_name_that_makes_this_line_go_far_beyond_the_configured_limit = "some extremely long string value here that pushes past the limit"  # C0301
    another_very_long_assignment = very_long_variable_name_that_makes_this_line_go_far_beyond_the_configured_limit + " extended"  # C0301
    return another_very_long_assignment


def indentation_issues():
    """Function with inconsistent indentation."""
    value = 1
    if value:
      result = value * 2   # bad indentation (2 spaces instead of 4)
      return result
    return 0


def trailing_spaces_function():   
    """Function with trailing whitespace on lines above."""   
    data = [1, 2, 3]   
    return data   


def missing_blank_lines_between_methods(): pass
def another_packed_function(): pass
def yet_another(): pass


VERY_LONG_CONSTANT_NAME_THAT_EXCEEDS_THE_MAXIMUM_LINE_LENGTH_WHEN_COMBINED_WITH_ITS_VALUE = "this entire assignment line is too long and violates line length rules configured for this project"  # C0301
