class Triple():

    def __init__(self):
        self.left = object()
        self.midle = object()
        self.right = object()

    def setLeft(self, left):
        self.left = left
        return self

    def getLeft(self):
        return self.left

    def setMidle(self, midle):
        self.midle = midle
        return self

    def getMidle(self):
        return self.midle

    def setRight(self, right):
        self.right = right
        return self

    def getRight(self):
        return self.right

    def toString(self):
        return "[{0}, {1}, {2}]".format(self.left.__str__(), self.midle.__str__(), self.right.__str__())