# Simple TMX library
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module is used by the Simple TMX Library for some common tasks.
Users can simply ignore this module.
"""


import base64
import gzip
import xml.etree.ElementTree as ET
import zlib

from .LayerTile import LayerTile


def data_decode(data, encoding, compression=None):
    """
    Decode encoded data and return a list of integers it represents.

    This is a low-level function used internally by this library; you
    don't typically need to use it.

    Arguments:

    - ``data`` -- The data to decode.
    - ``encoding`` -- The encoding of the data.  Can be ``"base64"`` or
      ``"csv"``.
    - ``compression`` -- The compression method used.  Valid compression
      methods are ``"gzip"`` and ``"zlib"``.  Set to :const:`None` for
      no compression.
    """
    if encoding == "csv":
        return [int(i) for i in data.strip().split(",")]
    elif encoding == "base64":
        data = base64.b64decode(data.strip().encode("latin1"))

        if compression == "gzip":
            data = gzip.decompress(data)
        elif compression == "zlib":
            data = zlib.decompress(data)
        elif compression:
            e = 'Compression type "{}" not supported.'.format(compression)
            raise ValueError(e)

        ndata = [i for i in data]

        data = []
        for i in range(0, len(ndata), 4):
            n = (ndata[i]  + ndata[i + 1] * (2 ** 8) +
                 ndata[i + 2] * (2 ** 16) + ndata[i + 3] * (2 ** 24))
            data.append(n)

        return data
    else:
        e = 'Encoding type "{}" not supported.'.format(encoding)
        raise ValueError(e)


def data_encode(data, encoding, compression=True, compressionlevel=None):
    """
    Encode a list of integers and return the encoded data.

    This is a low-level function used internally by this library; you
    don't typically need to use it.

    Arguments:

    - ``data`` -- The list of integers to encode.
    - ``encoding`` -- The encoding of the data.  Can be ``"base64"`` or
      ``"csv"``.
    - ``compression`` -- Whether or not compression should be used if
      supported.
    - ``compressionlevel`` -- The compression level to use, or
      :const:`None` to use the default.
    """
    if encoding == "csv":
        return ','.join([str(i) for i in data])
    elif encoding == "base64":
        ndata = []
        for i in data:
            n = [i % (2 ** 8), i // (2 ** 8), i // (2 ** 16), i // (2 ** 24)]
            ndata.extend(n)

        data = b''.join([bytes((i,)) for i in ndata])

        if compression:
            if compressionlevel is None:
                compressionlevel = -1
            data = zlib.compress(data, compressionlevel)

        return base64.b64encode(data).decode("latin1")
    else:
        e = 'Encoding type "{}" not supported.'.format(encoding)
        raise ValueError(e)


def clean_dict(d: dict) -> dict:
    """
    Remove all entries in dictionary ``d`` with a value of
    :const:`None`.

    This is a low-level function used internally by this library; you
    don't typically need to use it.
    """
    new_d = {}
    for i in d:
        if d[i] is not None:
            new_d[i] = str(d[i])
    return new_d


def read_list_elem(root, tag, cls, fd):
    """
    Read all elements with the tag ``tag`` under XML element ``root``
    and return a list of objects of class ``cls``, created by calling
    ``cls.read_elem(elem, fd)``.

    This is a low-level function used internally by this library; you
    don't typically need to use it.
    """
    objects = []
    for elem in root.findall(tag):
        objects.append(cls.read_elem(elem, fd))
    return objects


def get_list_elem(objects, tag, fd, encoding, compression):
    """
    Return an XML element with the tag ``tag``, appending XML elements
    generated by calling ``get_elem(fd, encoding, compression)`` for
    each member of ``objects``.

    This is a low-level function used internally by this library; you
    don't typically need to use it.
    """
    elem = ET.Element(tag)
    for obj in objects:
        elem.append(obj.get_elem(fd, encoding, compression))
    return elem


def read_tiles(elem, encoding, compression):
    """
    Read the tile data from XML element ``elem`` and return a list of
    :class:`LayerTile` objects.

    This is a low-level function used internally by this library; you
    don't typically need to use it.
    """
    tiles = []

    if encoding:
        tile_n = data_decode(elem.text, encoding, compression)
    else:
        tile_n = [int(tile.attrib.get("gid", 0))
                  for tile in elem.findall("tile")]

    for n in tile_n:
        gid = (n - (n & 2**31) - (n & 2**30) - (n & 2**29))
        hflip = bool(n & 2**31)
        vflip = bool(n & 2**30)
        dflip = bool(n & 2**29)
        tiles.append(LayerTile(gid, hflip, vflip, dflip))

    return tiles


def write_tiles(tiles, elem, encoding, compression, compressionlevel):
    """
    Write the list of tiles in ``tiles`` to XML element ``elem``.

    This is a low-level function used internally by this library; you
    don't typically need to use it.
    """
    tile_n = [int(i) for i in tiles]

    if encoding:
        elem.text = data_encode(tile_n, encoding, compression,
                                compressionlevel)
    else:
        for n in tile_n:
            elem.append(ET.Element("tile", attrib={"gid": n}))
