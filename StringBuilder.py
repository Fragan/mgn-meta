
class StringBuilder():

    UTF8="utf_8"

    def __init__(self):
        self.builder = []

    def append(self, string):
        self.builder.append(string)
        return self

    def toString(self):
        return ''.join(self.builder)

    # doesn't work
    def toStringCharset(self, charset):
        tmp = ''.join(self.builder)
        return tmp.encode(encoding=charset, errors='strict')