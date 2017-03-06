from base64 import b64decode, b64encode
import zlib
from IPython.display import display, Image
from .node import Node

"""
Image display code for the Rappture Compatibility Library
"""


class RapImage(Node):

    @property
    def value(self):
        val = self.get_text()
        compressed_header = '@@RP-ENC:zb64\n'
        hlen = len(compressed_header)
        compressed = False
        if val.startswith(compressed_header):
            compressed = True
            val = val[hlen:-1]
        data = b64decode(val)
        if compressed:
            data = zlib.decompress(data, zlib.MAX_WBITS | 32)
        return Image(data=data)

    @value.setter
    def value(self, val):
        if type(val) == Image:
            res = b64encode(val.data)
        else:
            res = b64encode(val)
        self.set_text(res)
