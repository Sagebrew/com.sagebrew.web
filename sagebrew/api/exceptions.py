class DoesNotExistWrapper(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class RaiseWrapperException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)