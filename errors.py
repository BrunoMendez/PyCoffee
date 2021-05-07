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