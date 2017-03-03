from base64 import b64decode, b64encode
import zlib
from IPython.display import display, Image
from .node import Node

"""
Image display code for the Rappture Compatibility Library
"""


class RapImage(Node):

    def __init__(self, tree, path, elem=None):
        self.tree = tree
        self.path = path
        self.elem = elem
        self.image = None

        if elem is None:
            return

        val = elem.text

        compressed_header = '@@RP-ENC:zb64\n'
        hlen = len(compressed_header)
        compressed = False
        if val.startswith(compressed_header):
            compressed = True
            val = val[hlen:-1]
        data = b64decode(val)
        if compressed:
            data = zlib.decompress(data, zlib.MAX_WBITS | 32)

        self.image = Image.__init__(self, data)

    def _value(self):
        print("image _value()")
        return self.image

    def encode(data):
        if type(data) == Image:
            return b64encode(data.data)
        return b64encode(data)
