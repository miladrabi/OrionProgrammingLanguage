import constant as cons


# TODO: remember to add position for better debugging
class Token:
    def __init__(self, Type, value, pos_start = None, pos_end = None):
        self.type = Type
        self.value = value
        self.pos_start = None
        self.pos_end = None

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end

    def __repr__(self):
        return f'Token({self.type}, {self.value})'

