import pytest

#################### PHASE 1 ####################

def test_imports():
    from pixel import Pixel
    from image import Image
    from encoding import Encoder, Decoder

def test_pixel_no_negative():
    from pixel import Pixel
    with pytest.raises(Exception):
        B = Pixel(0, 0xFF, -1)

def test_pixel_eq():
    from pixel import Pixel
    RED = Pixel(0xFF, 0, 0)
    GREEN = Pixel(0, 0xFF, 0)
    BLUE = Pixel(0, 0, 0xFF)
    RED2 = Pixel(0xFF, 0, 0)
    assert RED == RED2

def test_pixel_neq():
    from pixel import Pixel
    RED = Pixel(0xFF, 0, 0)
    GREEN = Pixel(0, 0xFF, 0)
    BLUE = Pixel(0, 0, 0xFF)
    assert RED != GREEN
    assert GREEN != BLUE
    assert RED != BLUE

def test_image_init_raises_exception():
    from pixel import Pixel
    from image import Image
    with pytest.raises(Exception):
        Image(4, 4, [Pixel(0, 0, 0)])
    with pytest.raises(Exception):
        Image(1, 1, [(0, 0, 0)])

def test_image_getitem():
    from image import Image
    from pixel import Pixel
    BLACK = Pixel(0x00, 0x00, 0x00)
    WHITE = Pixel(0xFF, 0xFF, 0xFF)
    img = Image(2, 1, [BLACK, WHITE])
    assert img[0,0] == BLACK
    assert img[1,0] == WHITE

def test_image_setitem():
    from pixel import Pixel
    from image import Image
    BLACK = Pixel(0x00, 0x00, 0x00)
    WHITE = Pixel(0xFF, 0xFF, 0xFF)
    img = Image(3, 1, [BLACK, WHITE, BLACK])
    img[0,0] = WHITE
    assert img[0,0] == img[1,0] == WHITE
    assert img[2,0] == BLACK

def test_image_setitem_raises_indexerror():
    from pixel import Pixel
    from image import Image
    img = Image(1, 1, [Pixel(0, 0, 0)])
    with pytest.raises(IndexError):
        img[1,1] = Pixel(0, 0xFF, 0)

def test_img_eq():
    from pixel import Pixel
    from image import Image
    BLACK = Pixel(0x00, 0x00, 0x00)
    WHITE = Pixel(0xFF, 0xFF, 0xFF)
    img1 = Image(3, 1, [BLACK, WHITE, BLACK])
    img2 = Image(3, 1, [BLACK, WHITE, BLACK])
    assert img1 == img2

def test_img_neq():
    from pixel import Pixel
    from image import Image
    BLACK = Pixel(0x00, 0x00, 0x00)
    WHITE = Pixel(0xFF, 0xFF, 0xFF)
    img1 = Image(3, 1, [BLACK, WHITE, BLACK])
    img2 = Image(3, 1, [BLACK, BLACK, BLACK])
    assert img1 != img2

def _get_squares_img():
    from pixel import Pixel
    from image import Image
    BLACK = Pixel(0, 0, 0)
    WHITE = Pixel(0xFF, 0xFF, 0xFF)
    return Image(2, 2, [BLACK, WHITE, BLACK, WHITE])

def _get_file_content(path: str):
    return open(path, 'rb').read()

def _set_file_content(path: str, content: bytes):
    open(path, 'wb').write(content)

def _get_tempfile():
    import tempfile
    return tempfile.mktemp()

def _image_as_bytes(image, *args, **kwargs):
    from encoding import Encoder
    path = _get_tempfile()
    Encoder(image, *args, **kwargs).save_to(path)
    return _get_file_content(path)

def _bytes_as_img(b):
    from encoding import Decoder
    path = _get_tempfile()
    _set_file_content(path, b)
    return Decoder.load_from(path)

SQUARES_ULBMP1_CONTENT = bytes.fromhex('554c424d50010c0002000200000000ffffff000000ffffff')

def test_encode_squares_ulbmp1():
    assert _image_as_bytes(_get_squares_img()) == SQUARES_ULBMP1_CONTENT

def test_decode_squares_ulbmp1():
    assert _bytes_as_img(SQUARES_ULBMP1_CONTENT) == _get_squares_img()

def test_load_from_corrupt():
    bad_content = b'ULBPM\x01\x08\x00'
    with pytest.raises(Exception):
        _bytes_as_img(bad_content)

def test_load_from_incomplete():
    incomplete_content = b'ULBMP\x01\x0c\x00\x02\x00\x02\x00\x00\x00\x00'
    with pytest.raises(Exception):
        _bytes_as_img(incomplete_content)

#################### PHASE 3 ####################

def test_encode_line_100_blacks():
    from pixel import Pixel
    from image import Image
    expected = bytes.fromhex('554c424d50020c006400010064000000')
    BLACK = Pixel(0, 0, 0)
    img = Image(100, 1, [BLACK]*100)
    assert _image_as_bytes(img, 2) == expected

def test_encode_line_300_blacks():
    from pixel import Pixel
    from image import Image
    expected = bytes.fromhex('554c424d50020c002c010100ff0000002d000000')
    BLACK = Pixel(0, 0, 0)
    img = Image(300, 1, [BLACK]*300)
    assert _image_as_bytes(img, 2) == expected

def test_encode_squares_ulbmp2():
    expected = bytes.fromhex('554c424d50020c00020002000100000001ffffff0100000001ffffff')
    assert _image_as_bytes(_get_squares_img(), 2) == expected

#################### PHASE 4 ####################

def test_load_palette():
    from pixel import Pixel
    content = bytes.fromhex('554c424d50031700030001000200ff000000ff000000ff84')
    img = _bytes_as_img(content)
    assert img[0,0] == Pixel(0, 0, 255)
    assert img[1,0] == Pixel(255, 0, 0)
    assert img[2,0] == Pixel(0, 255, 0)

def test_encode_squares_ulbmp3():
    possibilities = [
        bytes.fromhex('554c424d50031400020002000100000000ffffff50'),
        bytes.fromhex('554c424d50031400020002000100ffffff000000A0')
    ]
    assert _image_as_bytes(_get_squares_img(), 3, depth=1, rle=False) in possibilities

def test_load_ulbmp3_with_symmetric_palettes():
    squares_with_different_palettes = [
        bytes.fromhex('554c424d50031400020002000100000000ffffff50'),
        bytes.fromhex('554c424d50031400020002000100ffffff000000A0')
    ]
    assert _bytes_as_img(squares_with_different_palettes[0]) == _bytes_as_img(squares_with_different_palettes[1])

def test_rle_depth_8():
    from pixel import Pixel
    img_as_bytes = bytes.fromhex('554c424d50031700030003000801ff000000ff000000ff030103020300')
    img = _bytes_as_img(img_as_bytes)
    assert img[0,0] == img[1,0] == img[2,0] == Pixel(0, 255, 0)
    assert img[0,1] == img[1,1] == img[2,1] == Pixel(0, 0, 255)
    assert img[0,2] == img[1,2] == img[2,2] == Pixel(255, 0, 0)

#################### PHASE 5 ####################

def test_ulbmp4_blocs():
    from pixel import Pixel
    from image import Image
    pixels = [
        Pixel(128, 0, 0),
        Pixel(127, 0, 0),
        Pixel(123, 0, 0),
        Pixel(255, 124, 124),
        Pixel(128, 128, 128)
    ]
    img = _image_as_bytes(Image(5, 1, pixels), 4)
    from encoding import Encoder
    expected = b''.join([
        bytes.fromhex('554c424d50040c0005000100'),  # header
        bytes.fromhex('ff800000'),                  # NEW_PIXEL R=0x80, G=B=0
        b'\x1a',                                    # SMALL_DIFF Dr=-1, Dg=Db=0 -> 0b0 001 10 10
        b'\x60\x48',                                # INTERMEDIATE_DIFF Dg=0, Dr-Dg=Dr=-4, Db-Dg=Db=0 -> 0b01 100000 0100 1000
        b'\x9f\xca\x20',                            # BIG_DIFF_G Dg=124, Dr-Dg=132-124=8, Db-Dg=124-124=0 -> 0b1001 11111100 101000 100000
        bytes.fromhex('ff808080')                   # NEW_PIXEL R=G=B=0x80
    ])
    assert img == expected

def test_load_ulbmp4_blocs():
    from pixel import Pixel
    img_as_bytes = b''.join([
        bytes.fromhex('554c424d50040c0002000200'),  # header
        bytes.fromhex('3b'),                        # SMALL_DIFF Dr=Db=+1, Dg=0 -> 0b00 11 10 11
        bytes.fromhex('aa8826'),                    # BIG_DIFF_B Db=40, Dr-Db=0, Dg-Db=6 -> 0b1010 10101000 100000 10110
        bytes.fromhex('2a'),                        # SMALL_DIFF Dr=Db=Dg=0 -> 0b00 10 10 10
        bytes.fromhex('4c0f')                       # INTERMEDIATE_DIFF Dg=-20, Dr-Dg=-8, Db-Dg=7 -> 0b01 001100 0000 1111
    ])
    img = _bytes_as_img(img_as_bytes)
    assert img[0,0] == Pixel(1, 0, 1)
    assert img[1,0] == Pixel(41, 46, 41)
    assert img[1,0] == img[0,1]
    assert img[1,1] == Pixel(13, 26, 28)
