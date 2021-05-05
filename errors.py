class TypeMismatchError(Exception):
    def __init__(self, message="Type Mismatch"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message
        
