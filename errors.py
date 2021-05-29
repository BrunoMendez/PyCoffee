class TypeMismatchError(Exception):
    def __init__(self, message="Type Mismatch"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class VarAlreadyInTable(Exception):
    def __init__(self, message="Variable already in table"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class VarNotDefined(Exception):
    def __init__(self, message="Variable not defined"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class FunctionNotDeclared(Exception):
    def __init__(self, message="Function not declared"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class InvalidParamNum(Exception):
    def __init__(self, message="Invalid parameters number"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class NonVoidFuncReturnMissing(Exception):
    def __init__(self,
                 message="Non-void functions must have a return statement"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class InvalidType(Exception):
    def __init__(self, message="Invalid type"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class CustomSyntaxError(Exception):
    def __init__(self, message="Syntax error"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class OutOfBounds(Exception):
    def __init__(self, message="Index out of bounds"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message

class StackOverflow(Exception):
    def __init__(self, message="StackOverflow!"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message
