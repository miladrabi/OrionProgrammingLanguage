class Position:
    def __init__(self, index, lineno, colno, fn, ftxt):
        self.index = index
        self.line = lineno
        self.col = colno
        self.fileName = fn
        self.fileText = ftxt

    def advance(self, currentChar = None):
        self.index += 1
        self.col += 1

        if currentChar == '\n':
            self.line += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.index, self.line, self.col, self.fileName, self.fileText)