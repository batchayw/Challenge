import tempfile
from os import listdir
from encoding import Decoder, Encoder


def test_decode_all_file():
    has_error = False
    for file in listdir('imgs'):
        file = f'imgs/{file}'
        print(f'Decoding {file}', end=' ')
        try:
            Decoder.load_from(file)
            print('SUCCESS')
        except:
            has_error = True
            print('FAILED')
    assert has_error == False


def test_encode_all_file_to_v4():
    has_error = False
    for file in listdir('imgs'):
        file = f'imgs/{file}'
        print(f'Encoding {file}', end=' ')
        try:
            Encoder(Decoder.load_from(file), 4).save_to(tempfile.mktemp())
            print('SUCCESS')
        except:
            has_error = True
            print('FAILED')
    assert has_error == False


