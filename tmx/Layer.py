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
from .LayerChunk import LayerChunk
from .Property import Property


class Layer:

    """
    .. attribute:: id

       Unique ID of the layer if set, or :const:`None` otherwise.

    .. attribute:: name

       The name of the layer.

    .. attribute:: width

       The width of the layer in tiles, or :const:`None` if unspecified.

    .. attribute:: height

       The height of the layer in tiles, or :const:`None` if unspecified.

    .. attribute:: opacity

       The opacity of the layer as a value from 0 to 1.

    .. attribute:: visible

       Whether or not the layer is visible.

    .. attribute:: offsetx

       Rendering offset for this layer in pixels.

    .. attribute:: offsety

       Rendering offset for this layer in pixels.

    .. attribute:: properties

       A list of :class:`Property` objects indicating the properties of
       the layer.

    .. attribute:: tiles

       A list of :class:`LayerTile` objects indicating the tiles of the
       layer.

       The coordinates of each tile is determined by the tile's index
       within this list.  Exactly how the tiles are positioned is
       determined by the map orientation.

    .. attribute:: chunks

       A list of :class:`LayerChunk` objects indicating the chunks of
       the layer.
    """

    def __init__(self, name, opacity=1, visible=True, offsetx=0, offsety=0,
                 properties=None, tiles=None, id_=None, width=None,
                 height=None, chunks=None):
        self.id = id_
        self.name = name
        self.width = width
        self.height = height
        self.opacity = opacity
        self.visible = visible
        self.offsetx = offsetx
        self.offsety = offsety
        self.properties = properties or []
        self.tiles = tiles or []
        self.chunks = chunks or []

    @classmethod
    def read_elem(cls, elem, fd):
        """
        Read XML element ``elem`` and return an object of this class.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        id_ = elem.attrib.get("id")
        if id_ is not None:
            id_ = int(id_)
        name = elem.attrib.get("name", "")
        width = elem.attrib.get("width")
        if width is not None:
            width = int(width)
        height = elem.attrib.get("height")
        if height is not None:
            height = int(height)
        opacity = float(elem.attrib.get("opacity", 1))
        visible = bool(int(elem.attrib.get("visible", True)))
        offsetx = int(elem.attrib.get("offsetx", 0))
        offsety = int(elem.attrib.get("offsety", 0))
        properties = []
        tiles = []
        chunks = []

        for child in elem:
            if child.tag == "properties":
                properties.extend(local.read_list_elem(child, "property",
                                                       Property, fd))
            elif child.tag == "data":
                encoding = child.attrib.get("encoding")
                compression = child.attrib.get("compression")
                tiles = local.read_tiles(child, encoding, compression)

                for chunk in child.findall("chunk"):
                    chunks.append(LayerChunk.read_elem(chunk, fd, encoding,
                                                       compression))

        return cls(name, opacity, visible, offsetx, offsety, properties, tiles,
                   id_, width, height, chunks)

    def get_elem(self, fd, encoding, compression, compressionlevel):
        """
        Return an XML element for the object.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        attr = {"id": self.id, "name": self.name, "width": self.width,
                "height": self.height}
        if self.opacity < 1:
            attr["opacity"] = self.opacity
        if not self.visible:
            attr["visible"] = "0"
        if self.offsetx:
            attr["offsetx"] = self.offsetx
        if self.offsety:
            attr["offsety"] = self.offsety
        elem = ET.Element("layer", attrib=local.clean_dict(attr))

        if self.properties:
            elem.append(local.get_list_elem(self.properties, "properties", fd,
                                            encoding, compression))

        if self.tiles or self.chunks:
            attr = {"encoding": encoding, "compression": compression}
            child = ET.Element("data", attrib=local.clean_dict(attr))

            if self.tiles:
                local.write_tiles(self.tiles, child, encoding, compression,
                                  compressionlevel)

            for chunk in self.chunks:
                child.append(chunk.get_elem(fd, encoding, compression,
                                            compressionlevel))

        return elem
