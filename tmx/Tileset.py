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


import pathlib
import os
import xml.etree.ElementTree as ET

from . import local
from .Image import Image
from .Property import Property
from .TerrainType import TerrainType
from .Tile import Tile
from .Wangset import Wangset


class Tileset:

    """
    .. attribute:: firstgid

       The first global tile ID of this tileset (this global ID maps to
       the first tile in this tileset).

    .. attribute:: name

       The name of this tileset.

    .. attribute:: tilewidth

       The (maximum) width of the tiles in this tileset.

    .. attribute:: tileheight

       The (maximum) height of the tiles in this tileset.

    .. attribute:: source

       The external TSX (Tile Set XML) file to store this tileset in.
       If set to :const:`None`, this tileset is stored in the TMX file.

    .. attribute:: spacing

       The spacing in pixels between the tiles in this tileset (applies
       to the tileset image).

    .. attribute:: margin

       The margin around the tiles in this tileset (applies to the
       tileset image).

    .. attribute:: xoffset

       The horizontal offset of the tileset in pixels (positive is
       right).

    .. attribute:: yoffset

       The vertical offset of the tileset in pixels (positive is down).

    .. attribute:: tilecount

       The number of tiles in this tileset.  Set to :const:`None` to not
       specify this.

    .. attribute:: columns

       The number of tile columns in the tileset.  Set to :const:`None`
       to not specify this.

    .. attribute:: gridorientation

       Orientation of the grid for the tiles in this tileset
       (``"orthogonal"`` or ``"isometric"``).  Set to :const:`None` to
       not specify this.

    .. attribute:: gridwidth

       Width of a grid cell.  Set to :const:`None` to not specify this.

    .. attribute:: gridheight

       Height of a grid cell.  Set to :const:`None` to not specify this.

    .. attribute:: properties

       A list of :class:`Property` objects indicating the tileset's
       properties.

    .. attribute:: image

       An :class:`Image` object indicating the tileset's image.  Set to
       :const:`None` for no image.

    .. attribute:: terraintypes

       A list of :class:`TerrainType` objects indicating the tileset's
       terrain types.

    .. attribute:: tiles

       A list of :class:`Tile` objects indicating the tileset's tile
       properties.

    .. attribute:: wangsets

       A list of :class:`Wangset` objects indicating the Wang sets
       defined for the tileset.
    """

    def __init__(self, firstgid, name, tilewidth, tileheight, source=None,
                 spacing=0, margin=0, xoffset=0, yoffset=0, tilecount=None,
                 columns=None, properties=None, image=None, terraintypes=None,
                 tiles=None, gridorientation=None, gridwidth=None,
                 gridheight=None, wangsets=None):
        self.firstgid = firstgid
        self.name = name
        self.tilewidth = tilewidth
        self.tileheight = tileheight
        self.source = source
        self.spacing = spacing
        self.margin = margin
        self.xoffset = xoffset
        self.yoffset = yoffset
        self.tilecount = tilecount
        self.columns = columns
        self.properties = properties or []
        self.image = image
        self.terraintypes = terraintypes or []
        self.tiles = tiles or []
        self.gridorientation = gridorientation
        self.gridwidth = gridwidth
        self.gridheight = gridheight
        self.wangsets = wangsets or []

    @classmethod
    def read_elem(cls, elem, fd):
        """
        Read XML element ``elem`` and return an object of this class.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        firstgid = int(elem.attrib.get("firstgid"))
        source = elem.attrib.get("source")
        if source is not None:
            source = os.path.join(fd, source)
            root = ET.parse(source).getroot()
            fd = os.path.dirname(source)
        else:
            root = elem

        name = root.attrib.get("name", "")
        tilewidth = int(root.attrib.get("tilewidth", 32))
        tileheight = int(root.attrib.get("tileheight", 32))
        spacing = int(root.attrib.get("spacing", 0))
        margin = int(root.attrib.get("margin", 0))
        tilecount = root.attrib.get("tilecount")
        if tilecount is not None:
            tilecount = int(tilecount)
        columns = root.attrib.get("columns")
        if columns is not None:
            columns = int(columns)
        xoffset = 0
        yoffset = 0
        image = None
        gridorientation = None
        gridwidth = None
        gridheight = None
        properties = []
        terraintypes = []
        tiles = []
        wangsets = []
        

        for child in root:
            if child.tag == "grid":
                gridorientation = child.attrib.get("orientation",
                                                   gridorientation)
                gridwidth = child.attrib.get("width", gridwidth)
                if gridwidth is not None:
                    gridwidth = int(gridwidth)
                gridheight = child.attrib.get("height", gridheight)
                if gridheight is not None:
                    gridheight = int(gridheight)
            elif child.tag == "image":
                image = Image.read_elem(child, fd)
            elif child.tag == "properties":
                properties.extend(local.read_list_elem(child, "property",
                                                       Property, fd))
            elif child.tag == "terraintypes":
                terraintypes.extend(local.read_list_elem(child, "terrain",
                                                         TerrainType, fd))
            elif child.tag == "tile":
                tiles.append(Tile.read_elem(child, fd))
            elif child.tag == "wangsets":
                wangsets.extend(local.read_list_elem(child, "wangset",
                                                     Wangset, fd))

        return cls(firstgid, name, tilewidth, tileheight, source, spacing,
                   margin, xoffset, yoffset, tilecount, columns, properties,
                   image, terraintypes, tiles, gridorientation, gridwidth,
                   gridheight, wangsets)

    def get_elem(self, fd):
        """
        Return an XML element for the object.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        def append_elems(root, fd, self=self):
            if self.xoffset or self.yoffset:
                attr = {"x": self.xoffset, "y": self.yoffset}
                root.append(ET.Element(
                    "tileoffset", attrib=local.clean_dict(attr)))
            if (self.gridorientation is not None or
                    self.gridwidth is not None or self.gridheight is not None):
                attr = {"orientation": self.gridorientation,
                        "width": self.gridwidth, "height": self.gridheight}
                root.append(ET.Element("grid", attrib=local.clean_dict(attr)))
            if self.properties:
                root.append(local.get_list_elem(self.properties, "properties",
                                                fd))
            if self.image is not None:
                root.append(self.image.get_elem(fd))
            if self.terraintypes:
                root.append(local.get_list_elem(self.terraintypes,
                                                "terraintypes", fd))
            if self.wangsets:
                root.append(local.get_list_elem(self.wangsets, "wangsets", fd))
            for tile in self.tiles:
                root.append(tile.get_elem(fd))

        if self.source:
            pth = os.path.relpath(self.source, fd)
            source = pathlib.PurePath(pth).as_posix()
            fd = os.path.dirname(pth)

            # Write main element
            attr = {"firstgid": self.firstgid, "source": source}
            elem = ET.Element("tileset", attrib=local.clean_dict(attr))

            # Write external tileset
            attr = {"name": self.name, "tilewidth": self.tilewidth,
                    "tileheight": self.tileheight,
                    "spacing": self.spacing or None,
                    "margin": self.margin or None, "tilecount": self.tilecount,
                    "columns": self.columns or None}
            child = ET.Element("tileset", attrib=local.clean_dict(attr))
            elem.append(child)
            append_elems(child, fd) 
        else:
            attr = {"firstgid": self.firstgid, "name": self.name,
                    "tilewidth": self.tilewidth, "tileheight": self.tileheight,
                    "spacing": self.spacing or None,
                    "margin": self.margin or None, "tilecount": self.tilecount,
                    "columns": self.columns or None}
            elem = ET.Element("tileset", attrib=local.clean_dict(attr))
            append_elems(elem, fd)

        return elem
