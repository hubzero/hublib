from base64 import b64decode, b64encode
import zlib
from IPython.display import Image

"""
Image display code for the Rappture Compatibility Library
"""


class RapImage(Image):

    def __init__(self, val):
        compressed_header = '@@RP-ENC:zb64\n'
        hlen = len(compressed_header)
        compressed = False
        if val.startswith(compressed_header):
            compressed = True
            val = val[hlen:-1]
        data = b64decode(val)
        if compressed:
            data = zlib.decompress(data, zlib.MAX_WBITS | 32)
        Image.__init__(self, data)

def encode(data):
    if type(data) == Image:
        return b64encode(data.data)
    return b64encode(data)
