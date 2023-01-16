
class Pid:
    def __init__(self, name, key, formula):
        self.name = name
        self.key = key
        self.formula = formula

    def encode(self, value):
        A = value
        return eval(self.formula)
