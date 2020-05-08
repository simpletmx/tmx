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


import xml.etree.ElementTree as ET

from . import local


class LayerChunk:

    """
    .. attribute:: x

       The x coordinate of the chunk in tiles.

    .. attribute:: y

       The y coordinate of the chunk in tiles.

    .. attribute:: width

       The width of the chunk in tiles.

    .. attribute:: height

       The height of the chunk in tiles.

    .. attribute:: tiles

       A list of :class:`LayerTile` objects indicating the tiles of the
       chunk.

       The coordinates of each tile is determined by the tile's index
       within this list.  Exactly how the tiles are positioned is
       determined by the map orientation.
    """

    def __init__(self, x, y, width, height, tiles=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.tiles = tiles or []

    @classmethod
    def read_elem(cls, elem, fd, encoding, compression):
        """
        Read XML element ``elem`` and return an object of this class.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        x = int(elem.attrib.get("x", 0))
        y = int(elem.attrib.get("y", 0))
        width = int(elem.attrib.get("width", 0))
        height = int(elem.attrib.get("height", 0))
        tiles = local.read_tiles(elem, encoding, compression)

    def get_elem(self, fd, encoding, compression):
        """
        Return an XML element for the object.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        attr = {"x": self.x, "y": self.y, "width": self.width,
                "height": self.height}
        elem = ET.Element("chunk", attrib=local.clean_dict(attr))

        local.write_tiles(self.tiles, elem, encoding, compression)

        return elem
