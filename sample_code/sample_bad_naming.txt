"""Module with naming convention violations (C0103 invalid-name)."""


def CalculateTotal(ValueA, ValueB):   # C0103 - PascalCase function + args
    """Add two values."""
    ResultValue = ValueA + ValueB     # C0103 - PascalCase local variable
    return ResultValue


def ProcessData(InputList):           # C0103 - PascalCase function + arg
    """Process a list."""
    FilteredItems = [i for i in InputList if i]  # C0103
    return FilteredItems


class dataManager:                    # C0103 - not CapWords class name
    """Manages data."""

    def LoadFromFile(self, FilePath): # C0103 - PascalCase method + arg
        """Load from file."""
        RawContent = open(FilePath).read()  # C0103, W1514 open-without-context
        return RawContent

    def SaveToFile(self, FilePath, Content):  # C0103
        """Save to file."""
        with open(FilePath, "w") as FileHandle:  # C0103
            FileHandle.write(Content)


def validateInput(UserInput):         # C0103 - camelCase function
    """Validate user input."""
    IsValid = bool(UserInput)         # C0103
    return IsValid


NumberOfItems = 10       # C0103 - looks like a constant but not UPPER_CASE format
currentUserName = ""     # C0103 - camelCase module-level variable
