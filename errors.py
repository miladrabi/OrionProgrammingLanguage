from strings_with_arrows import *
class Error:
    def __init__(self, pos_start, pos_end, err_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.name = err_name
        self.details = details

    def as_string(self): 
        result  = f'{self.name}: {self.details} in '
        result += f'File "{self.pos_start.fileName}", line {self.pos_start.line}'
        result += '\n\n' + string_with_arrows(self.pos_start.fileText, self.pos_start, self.pos_end)
        return result




class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "Illegal Character", details)


class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "Invalid Syntax", details)


class RTError(Error):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, "Runtime Error", details)
        self.context = context

    def as_string(self):
        result  = self.generateTraceback()
        result += f'{self.name}: {self.details}'
        result += '\n\n' + string_with_arrows(self.pos_start.fileText, self.pos_start, self.pos_end)
        return result


    def generateTraceback(self):
        result = ''
        pos = self.pos_start
        ctx = self.context

        while ctx:
            result = f' File {pos.fileName}, line {str(pos.line)}, in {ctx.display_name}\n' + result
            pos = ctx.parent_entry_position
            ctx = ctx.parent

        return 'Traceback (Most Recent Call Last):\n' + result
        
