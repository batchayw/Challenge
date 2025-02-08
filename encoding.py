from typing import BinaryIO
from image import Image
from pixel import Pixel


class Encoder:
    def __init__(self, img: Image, version: int = 1, **kwargs):
        self._image = img
        self._version = version
        self._kwargs = kwargs

    def save_to(self, path: str) -> None:
        with open(path, 'wb') as file:
            # Write ULBMP header
            file.write(b'ULBMP')  # Signature
            file.write(bytes([self._version]))  # Version
            # Write pixel data
            if self._version == 1:
                self.__write_data_v1(file)
            elif self._version == 2:
                self.__write_data_v2(file)
            elif self._version == 3:
                if self._kwargs.get('rle', None) is None or self._kwargs.get('depth', None) is None:
                    raise ValueError('rle and depth must be provided')
                self.__write_data_v3(file)
            elif self._version == 4:
                self.__write_data_v4(file)
            else:
                raise ValueError("Unsupported ULBMP version")

    def __write_header_and_image_size(self, file: BinaryIO, header_size: int):
        """ write header size and image width and height """
        file.write(header_size.to_bytes(2, 'little'))  # Header size
        file.write(self._image.width.to_bytes(2, 'little'))  # Width
        file.write(self._image.height.to_bytes(2, 'little'))  # Height

    def __write_data_v1(self, file: BinaryIO):
        """ write v1 file """
        self.__write_header_and_image_size(file, 12)
        self.__write_pixels(file)

    def __write_pixels(self, file: BinaryIO):
        """ for each pixel write her color part """
        for pixel in self._image.pixels:
            file.write(pixel.red.to_bytes(1, 'little'))
            file.write(pixel.green.to_bytes(1, 'little'))
            file.write(pixel.blue.to_bytes(1, 'little'))

    def __write_rle(self, file: BinaryIO):
        """ write pixel in rle format """
        run_length = 1
        current_pixel = self._image.pixels[0]
        for pixel in self._image.pixels[1:]:
            if pixel == current_pixel and run_length < 255:
                run_length += 1
            else:
                file.write(run_length.to_bytes(1, 'little'))
                file.write(current_pixel.red.to_bytes(1, 'little'))
                file.write(current_pixel.green.to_bytes(1, 'little'))
                file.write(current_pixel.blue.to_bytes(1, 'little'))
                run_length = 1
                current_pixel = pixel
        file.write(run_length.to_bytes(1, 'little'))
        file.write(current_pixel.red.to_bytes(1, 'little'))
        file.write(current_pixel.green.to_bytes(1, 'little'))
        file.write(current_pixel.blue.to_bytes(1, 'little'))

    def __write_data_v2(self, file: BinaryIO):
        """ write v2 file"""
        self.__write_header_and_image_size(file, 12)
        # RLE Encoding for version 2
        self.__write_rle(file)

    def __get_palettes(self):
        """ extract palette from pixels list"""
        pixels = []
        for pixel in self._image.pixels:
            if pixel not in pixels:
                pixels.append(pixel)
        return pixels

    @staticmethod
    def __encode_indexes(indexes, index_length):
        """
            indexes is array of index for pixels in palette
         convert each index into binary of index_length bits """
        # convert each index to binary then concatenate them
        binary = ''.join([bin(x)[2:].rjust(index_length, '0') for x in indexes])
        binary = binary.ljust(8, '0')  # complete to 8 bit if not already
        return int(binary, 2)  # convert to int

    def __write_data_v3(self, file: BinaryIO):
        """ write v3 file"""
        palettes = self.__get_palettes()
        rle = self._kwargs['rle']
        depth = self._kwargs['depth']
        self.__write_header_and_image_size(file, 14 + 3 * len(palettes))
        file.write(depth.to_bytes(1, 'little'))
        file.write(rle.to_bytes(1, 'little'))
        if depth != 24:
            for pixel in palettes:
                file.write(pixel.red.to_bytes(1, 'little'))
                file.write(pixel.green.to_bytes(1, 'little'))
                file.write(pixel.blue.to_bytes(1, 'little'))

        if not rle:  # not rle
            if depth == 24:  # depth = 24
                self.__write_pixels(file)
            else:
                nb_group = 8 // depth  # nb of pixel per byte
                for i in range(0, len(self._image.pixels), nb_group):
                    indexes = [palettes.index(pixel) for pixel in
                               self._image.pixels[i:nb_group]]  # get pixels indexes in palettes
                    file.write(self.__encode_indexes(indexes, depth).to_bytes(1, 'little'))
        else:  # rle
            if len(palettes) == 0:  # we are on depth 24 no p
                self.__write_rle(file)
            else:  # depth = 8
                run_length = 1
                current_pixel = self._image.pixels[0]
                for pixel in self._image.pixels[1:]:
                    if pixel == current_pixel and run_length < 255:
                        run_length += 1
                    else:
                        file.write(run_length.to_bytes(1, 'little'))
                        indexes = [palettes.index(current_pixel)] * depth
                        file.write(self.__encode_indexes(indexes, depth).to_bytes(1, 'little'))
                        run_length = 1
                        current_pixel = pixel
                file.write(run_length.to_bytes(1, 'little'))
                indexes = [palettes.index(current_pixel)] * depth
                file.write(self.__encode_indexes(indexes, depth).to_bytes(1, 'little'))

    @staticmethod
    def __bin_array2bytes(arr: list[str]):
        """
        arr is parts of a binary exemple ['00', '10', '11', '01']
        join those bit then
        convert each 8bit group to byte then join them
        """
        full_binary = ''.join(arr)
        # convert each group of 8bit
        arr = [int(full_binary[x:x + 8], 2).to_bytes(1, 'little') for x in range(0, len(full_binary), 8)]
        return b''.join(arr)  # join bytes arr

    @staticmethod
    def __bin(x: int, length: int):
        """ convert x to binary of length bits"""
        return bin(x)[2:].rjust(length, '0')

    def __write_data_v4(self, file: BinaryIO):
        """ write v4 file"""
        self.__write_header_and_image_size(file, 12)
        _p = Pixel(0, 0, 0)
        for p in self._image.pixels:
            Dr, Dg, Db = (p.red - _p.red, p.green - _p.green, p.blue - _p.blue)
            if all(-2 <= x <= 1 for x in (Dr, Dg, Db)):  # ULBMP_SMALL_DIFF
                byte = self.__bin_array2bytes(
                    ['00', self.__bin(Dr + 2, 2), self.__bin(Dg + 2, 2), self.__bin(Db + 2, 2)])
                file.write(byte)
            elif (-32 <= Dg <= 31) and all(-8 <= x <= 7 for x in (Dr - Dg, Db - Dg)):  # ULBMP_INTERMEDIATE_DIFF
                file.write(self.__bin_array2bytes(
                    ['01', self.__bin(Dg + 32, 6), self.__bin(Dr - Dg + 8, 4), self.__bin(Db - Dg + 8, 4)]))
            elif (-128 <= Dr <= 127) and all(-32 <= x <= 31 for x in (Dg - Dr, Db - Dr)):  # ULBMP_BIG_DIFF_R
                byte3 = self.__bin_array2bytes(
                    ['1000', self.__bin(Dr + 128, 8), self.__bin(Dg - Dr + 32, 6), self.__bin(Db - Dr + 32, 6)])
                file.write(byte3)
            elif (-128 <= Dg <= 127) and all(-32 <= x <= 31 for x in (Dr - Dg, Db - Dg)):  # ULBMP_BIG_DIFF_G
                byte3 = self.__bin_array2bytes(
                    ['1001', self.__bin(Dg + 128, 8), self.__bin(Dr - Dg + 32, 6), self.__bin(Db - Dg + 32, 6)])
                file.write(byte3)
            elif (-128 <= Db <= 127) and all(-32 <= x <= 31 for x in (Dr - Db, Dg - Db)):  # ULBMP_BIG_DIFF_B
                byte3 = self.__bin_array2bytes(
                    ['1010', self.__bin(Db + 128, 8), self.__bin(Dr - Db + 32, 6), self.__bin(Dg - Db + 32, 6)])
                file.write(byte3)
            else:  # ULBMP_NEW_PIXEL
                file.write(self.__bin_array2bytes(['1' * 8]))
                file.write(p.red.to_bytes(1, 'little'))
                file.write(p.green.to_bytes(1, 'little'))
                file.write(p.blue.to_bytes(1, 'little'))
            _p = p  # replace de previous pixel


class Decoder:

    @staticmethod
    def __decode_data_v1(file: BinaryIO, width: int, height: int):
        """ decode v1 file"""
        pixels = []
        expected_pixel_bytes = width * height * 3
        pixel_data = file.read(expected_pixel_bytes)
        if len(pixel_data) != expected_pixel_bytes:
            raise ValueError("Incomplete pixel data")
        for i in range(0, expected_pixel_bytes, 3):
            red = pixel_data[i]
            green = pixel_data[i + 1]
            blue = pixel_data[i + 2]
            pixels.append(Pixel(red, green, blue))
        return pixels

    @staticmethod
    def __decode_data_v2(file: BinaryIO):
        # RLE Decoding for version 2
        pixels = []
        while True:
            run_length_byte = file.read(1)
            if not run_length_byte:
                break  # End of file
            run_length = int.from_bytes(run_length_byte, 'little')
            red = int.from_bytes(file.read(1), 'little')
            green = int.from_bytes(file.read(1), 'little')
            blue = int.from_bytes(file.read(1), 'little')
            pixel = Pixel(red, green, blue)
            for _ in range(run_length):
                pixels.append(pixel)
        return pixels

    @staticmethod
    def __decode_data_v3(file: BinaryIO, header_size: int, nb_pixels):
        """ decode v3 file"""
        pixels = []
        bbp = int.from_bytes(file.read(1), 'little')
        rle = bool(int.from_bytes(file.read(1), 'little'))
        palette_size = header_size - 14  # 14 is already read header part
        palettes = Decoder.__decode_palettes(file, palette_size)  # will be empty if bbp > 8
        if not rle:
            while True:
                byte = file.read(1)
                if not byte:
                    break
                if len(palettes) == 0:
                    byte_pixels = [Pixel(
                        int.from_bytes(byte, 'little'),
                        int.from_bytes(file.read(1), 'little'),
                        int.from_bytes(file.read(1), 'little')
                    )]
                else:
                    byte_pixels = Decoder.__get_pixels_in_byte(bbp, byte, palettes)
                pixels.extend(byte_pixels)
        else:
            while True:
                run_length_byte = file.read(1)
                if not run_length_byte:
                    break  # End of file
                run_length = int.from_bytes(run_length_byte, 'little')
                byte = file.read(1)
                if len(palettes) == 0:
                    byte_pixels = [Pixel(
                        int.from_bytes(byte, 'little'),
                        int.from_bytes(file.read(1), 'little'),
                        int.from_bytes(file.read(1), 'little')
                    )]
                else:  # get binary value of the byte
                    byte_pixels = Decoder.__get_pixels_in_byte(bbp, byte, palettes)
                pixels.extend(byte_pixels * run_length)  # repeat pixels by run_length
        # then remove if exists exceeded pixels
        if len(pixels) > nb_pixels:
            pixels = pixels[:nb_pixels]
        return pixels

    @staticmethod
    def __get_pixels_in_byte(bbp, byte, palettes):
        """parse byte to retrieve indexes of pixels in palette then replace them with the corresponding pixel"""
        value = bin(int.from_bytes(byte, 'little'))[2:]
        value = value.rjust(8, '0')  # add padding if the is no 8 bit
        # split byte into bit group then convert it to get pixel index
        byte_pixels = [palettes[int(value[x:x + bbp], 2)] for x in range(0, 8, bbp)]
        return byte_pixels

    @staticmethod
    def __decode_palettes(file, palette_size):
        """ extract palette into file header"""
        palette_data = file.read(palette_size)
        palettes = []
        for i in range(0, palette_size, 3):
            red = palette_data[i]
            green = palette_data[i + 1]
            blue = palette_data[i + 2]
            palettes.append(Pixel(red, green, blue))
        return palettes

    @staticmethod
    def __byte2bin(byte):
        """transform byte to binary of 8bits"""
        return bin(int.from_bytes(byte, 'little'))[2:].rjust(8, '0')

    @staticmethod
    def __get_big_diff_data(bits):
        """ retrieve int value from bits data of ULBMP_BIG_DIFF"""
        return int(bits[:8], 2) - 128, int(bits[8:14], 2) - 32, int(bits[14:], 2) - 32

    @staticmethod
    def __decode_data_v4(file: BinaryIO, nb_pixels):
        """ decode v4 file"""
        pixels = []
        _p = Pixel(0, 0, 0)
        while len(pixels) != nb_pixels:
            bits = Decoder.__byte2bin(file.read(1))
            p = Dr = Dg = Db = None
            if bits[0:2] == '00':  # ULBMP_SMALL_DIFF
                (Dr, Dg, Db) = (int(x, 2) - 2 for x in (bits[2:4], bits[4:6], bits[6:]))

            elif bits[0:2] == '01':  # ULBMP_INTERMEDIATE_DIFF
                Dg = int(bits[2:], 2) - 32
                bits = Decoder.__byte2bin(file.read(1))
                Drg, Dbg = int(bits[0:4], 2), int(bits[4:], 2)
                Dr, Db = Drg + Dg - 8, Dbg + Dg - 8

            elif bits[0:2] == '10':  # ULBMP_BIG_DIFF
                bits012 = bits[4:] + Decoder.__byte2bin(file.read(1)) + Decoder.__byte2bin(file.read(1))

                if bits[2:4] == '00':  # ULBMP_BIG_DIFF_R
                    Dr, Dgr, Dbr = Decoder.__get_big_diff_data(bits012)
                    Dg, Db = Dgr + Dr, Dbr + Dr

                elif bits[2:4] == '01':  # ULBMP_BIG_DIFF_G
                    Dg, Drg, Dbg = Decoder.__get_big_diff_data(bits012)
                    Dr, Db = Drg + Dg, Dbg + Dg

                elif bits[2:4] == '10':  # ULBMP_BIG_DIFF_B
                    Db, Drb, Dgb = Decoder.__get_big_diff_data(bits012)
                    Dr, Dg = Drb + Db, Dgb + Db

            else:  # bits[0:2] == '11' -> ULBMP_NEW_PIXEL
                r = int.from_bytes(file.read(1), 'little')
                g = int.from_bytes(file.read(1), 'little')
                b = int.from_bytes(file.read(1), 'little')
                p = Pixel(r, g, b)
            if p is None:
                p = Pixel(_p.red + Dr, _p.green + Dg, _p.blue + Db)
            pixels.append(p)
            _p = p
        return pixels

    @staticmethod
    def load_from(path: str) -> Image:
        with open(path, 'rb') as file:
            # Read ULBMP header
            signature = file.read(5)
            if signature != b'ULBMP':
                raise ValueError("Invalid ULBMP file")
            version = file.read(1)
            header_size = int.from_bytes(file.read(2), 'little')

            if version in [b'\x01', b'\x02', b'\x04'] and header_size != 12:
                raise ValueError("Incomplete ULBMP header")

            width = int.from_bytes(file.read(2), 'little')
            height = int.from_bytes(file.read(2), 'little')
            # Read pixel data
            if version == b'\x01':
                pixels = Decoder.__decode_data_v1(file, width, height)
            elif version == b'\x02':
                pixels = Decoder.__decode_data_v2(file)
            elif version == b'\x03':
                pixels = Decoder.__decode_data_v3(file, header_size, width * height)
            elif version == b'\x04':
                pixels = Decoder.__decode_data_v4(file, width * height)
            else:
                raise ValueError("Unsupported ULBMP version")
            return Image(width, height, pixels)
