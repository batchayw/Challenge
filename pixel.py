class Pixel:
    def __init__(self, red: int, green: int, blue: int):
        if not all(0 <= c <= 255 for c in (red, green, blue)):
            raise Exception("RGB values must be between 0 and 255")
        self._red = red
        self._green = green
        self._blue = blue

    @property
    def red(self):
        return self._red

    @property
    def green(self):
        return self._green

    @property
    def blue(self):
        return self._blue

    def __str__(self):
        return 'rgb(%d, %d, %d)' % (self._red, self.green, self._blue)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, Pixel):
            return False
        return self._red == other._red and self._green == other._green and self._blue == other._blue
