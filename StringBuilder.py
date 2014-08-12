
class StringBuilder():

    UTF8="utf_8"

    def __init__(self):
        self.builder = []

    def append(self, string):
        self.builder.append(string)
        return self

    def to_s(self):
        return ''.join(self.builder)

    # doesn't work
    def to_s_charset(self, charset):
        tmp = ''.join(self.builder)
        return tmp.encode(encoding=charset, errors='strict')
