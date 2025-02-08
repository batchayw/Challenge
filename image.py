from pixel import Pixel

class Image:
    def __init__(self, width: int, height: int, pixels: list[Pixel]):
        if width <= 0 or height <= 0:
            raise Exception("Les dimensions de l'image doivent être des entiers positifs")
        if len(pixels) != width * height:
            raise Exception("La liste de pixels ne correspond pas aux dimensions de l'image")
        if not all(isinstance(pixel, Pixel) for pixel in pixels):
            raise Exception("La liste de pixels doit contenir uniquement des instances de la classe Pixel")
        self._width = width
        self._height = height
        self._pixels = pixels

    @property
    def pixels(self):
        return self._pixels

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def __getitem__(self, pos: tuple[int, int]) -> Pixel:
        x, y = pos
        if not (0 <= x < self._width and 0 <= y < self._height):
            raise IndexError("Position out of bounds")
        return self._pixels[y * self._width + x]

    def __setitem__(self, pos: tuple[int, int], pix: Pixel) -> None:
        x, y = pos
        if not (0 <= x < self._width and 0 <= y < self._height):
            raise IndexError("Position out of bounds")
        self._pixels[y * self._width + x] = pix

    def __eq__(self, other: 'Image') -> bool:
        if not isinstance(other, Image):
            return False
        return (self._width, self._height, self._pixels) == (other._width, other._height, other._pixels)
