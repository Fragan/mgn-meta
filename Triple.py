class Triple():

    def __init__(self):
        self.left = object()
        self.midle = object()
        self.right = object()

    def set_left(self, left):
        self.left = left
        return self

    def get_left(self):
        return self.left

    def set_midle(self, midle):
        self.midle = midle
        return self

    def get_midle(self):
        return self.midle

    def set_right(self, right):
        self.right = right
        return self

    def get_right(self):
        return self.right

    def to_s(self):
        return "[{0}, {1}, {2}]".format(self.left.__str__(), self.midle.__str__(), self.right.__str__())
