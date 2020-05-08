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
from .Color import Color
from .EditorSettings import EditorSettings
from .GroupLayer import GroupLayer
from .ImageLayer import ImageLayer
from .Layer import Layer
from .ObjectGroup import ObjectGroup
from .Property import Property
from .Tileset import Tileset


class TileMap:

    """
    This class loads, stores, and saves TMX files.

    .. attribute:: version

       The TMX format version.

    .. attribute:: tiledversion

       The tiled version used to save the file, or :const:`None` if
       unspecified.

    .. attribute:: orientation

       Map orientation.  Can be "orthogonal", "isometric", "staggered",
       or "hexagonal".

    .. attribute:: renderorder

       The order in which tiles are rendered.  Can be ``"right-down"``,
       ``"right-up"``, ``"left-down"``, or ``"left-up"``.  Default is
       ``"right-down"``.

    .. attribute:: compressionlevel

       The compression level to use for the tile layer, or
       :const:`None` to use the algorithm default.

    .. attribute:: width

       The width of the map in tiles.

    .. attribute:: height

       The height of the map in tiles.

    .. attribute:: tilewidth

       The width of a tile.

    .. attribute:: tileheight

       The height of a tile.

    .. attribute:: staggeraxis

       Determines which axis is staggered.  Can be "x" or "y".  Set to
       :const:`None` to not set it.  Only meaningful for staggered and
       hexagonal maps.

    .. attribute:: staggerindex

       Determines what indexes along the staggered axis are shifted.
       Can be "even" or "odd".  Set to :const:`None` to not set it.
       Only meaningful for staggered and hexagonal maps.

    .. attribute:: hexsidelength

       Side length of the hexagon in hexagonal tiles.  Set to
       :const:`None` to not set it.  Only meaningful for hexagonal maps.

    .. attribute:: backgroundcolor

       A :class:`Color` object indicating the background color of the
       map, or :const:`None` if no background color is defined.

    .. atribute:: nextlayerid

       The next available ID for new layers. Set to :const:`None` to not
       set it.

    .. attribute:: nextobjectid

       The next available ID for new objects.  Set to :const:`None` to
       not set it.

    .. attribute:: editorsettings

       An :class:`EditorSettings` object indicating the map's
       editor-specific settings.

    .. attribute:: properties

       A list of :class:`Property` objects indicating the map's
       properties.

    .. attribute:: tilesets

       A list of :class:`Tileset` objects indicating the map's tilesets.

    .. attribute:: layers

       A list of :class:`Layer`, :class:`ObjectGroup`,
       :class:`GroupLayer`, and :class:`ImageLayer` objects indicating
       the map's tile layers, object groups, group layers, and image
       layers, respectively.  Those that appear in this list first are
       rendered first (i.e. furthest in the back).

    .. attribute:: layers_list

       :attr:`layers`, but with all :class:`GroupLayer` objects
       replaced recursively with their respective layer lists.  Use this
       to ignore the layer hierarchy and treat it as a simple list of
       layers instead.

       (Read-only)
    """

    @property
    def layers_list(self):
        def expand_layers(layers):
            new_layers = []
            for layer in layers:
                if isinstance(layer, GroupLayer):
                    new_layers.extend(expand_layers(layer.layers))
                else:
                    new_layers.append(layer)
            return new_layers

        return expand_layers(self.layers)

    def __init__(self):
        self.version = "1.0"
        self.tiledversion = None
        self.orientation = "orthogonal"
        self.renderorder = "right-down"
        self.compressionlevel = None
        self.width = 0
        self.height = 0
        self.tilewidth = 32
        self.tileheight = 32
        self.staggeraxis = None
        self.staggerindex = None
        self.hexsidelength = None
        self.backgroundcolor = None
        self.nextlayerid = None
        self.nextobjectid = None
        self.editorsetttings = EditorSettings()
        self.properties = []
        self.tilesets = []
        self.layers = []

    @classmethod
    def load(cls, fname):
        """
        Load the TMX file with the indicated name and return a
        :class:`TileMap` object representing it.
        """
        self = cls()

        tree = ET.parse(fname)
        root = tree.getroot()
        fd = os.path.dirname(fname)
        self.version = root.attrib.get("version", self.version)
        self.tiledversion = root.attrib.get("tiledversion", self.tiledversion)
        self.orientation = root.attrib.get("orientation", self.orientation)
        self.renderorder = root.attrib.get("renderorder", self.renderorder)
        self.compressionlevel = root.attrib.get("compressionlevel",
                                                self.compressionlevel)
        self.width = int(root.attrib.get("width", self.width))
        self.height = int(root.attrib.get("height", self.height))
        self.tilewidth = int(root.attrib.get("tilewidth", self.tilewidth))
        self.tileheight = int(root.attrib.get("tileheight", self.tileheight))
        self.staggeraxis = root.attrib.get("staggeraxis", self.staggeraxis)
        self.staggerindex = root.attrib.get("staggerindex", self.staggerindex)
        self.hexsidelength = root.attrib.get("hexsidelength",
                                             self.hexsidelength)
        if self.hexsidelength is not None:
            self.hexsidelength = int(self.hexsidelength)
        self.backgroundcolor = root.attrib.get("backgroundcolor")
        if self.backgroundcolor:
            self.backgroundcolor = Color(self.backgroundcolor)
        self.nextlayerid = root.attrib.get("nextlayerid", self.nextlayerid)
        if self.nextlayerid is not None:
            self.nextlayerid = int(self.nextlayerid)
        self.nextobjectid = root.attrib.get("nextobjectid", self.nextobjectid)
        if self.nextobjectid is not None:
            self.nextobjectid = int(self.nextobjectid)

        for child in root:
            if child.tag == "editorsettings":
                self.editorsettings = EditorSettings.read_elem(child, fd)
            elif child.tag == "properties":
                self.properties.extend(local.read_list_elem(
                    child, "property", Property, fd))
            elif child.tag == "tileset":
                self.tilesets.append(Tileset.read_elem(child, fd))
            elif child.tag == "layer":
                self.layers.append(Layer.read_elem(child, fd))
            elif child.tag == "objectgroup":
                self.layers.append(ObjectGroup.read_elem(child, fd))
            elif child.tag == "imagelayer":
                self.layers.append(ImageLayer.read_elem(child, fd))
            elif child.tag == "group":
                self.layers.append(GroupLayer.read_elem(child, fd))

        return self

    def save(self, fname, data_encoding="base64", data_compression=True):
        """
        Save the object to the file with the indicated name.

        Arguments:

        - ``data_encoding`` -- The encoding to use for layers.  Can be
          ``"base64"`` or ``"csv"``.  Set to :const:`None` for the
          default encoding (currently ``"base64"``).
        - ``data_compression`` -- Whether or not compression should be
          used on layers if possible (currently only possible for
          base64-encoded data).
        """
        if data_encoding is None:
            data_encoding = "base64"

        bgc = str(self.backgroundcolor) if self.backgroundcolor else None
        attr = {"version": self.version, "tiledversion": self.tiledversion,
                "orientation": self.orientation,
                "renderorder": self.renderorder,
                "compressionlevel": self.compressionlevel, "width": self.width,
                "height": self.height, "tilewidth": self.tilewidth,
                "tileheight": self.tileheight, "staggeraxis": self.staggeraxis,
                "staggerindex": self.staggerindex,
                "hexsidelength": self.hexsidelength, "backgroundcolor": bgc,
                "nextlayerid": self.nextlayerid,
                "nextobjectid": self.nextobjectid}
        root = ET.Element("map", attrib=local.clean_dict(attr))
        fd = os.path.dirname(fname)

        if self.editorsettings is not None:
            root.append(self.editorsettings.get_elem(fd, data_encoding,
                                                     data_compression))

        if self.properties:
            root.append(local.get_list_elem(self.properties, "properties", fd,
                                            data_encoding, data_compression))

        for tileset in self.tilesets:
            root.append(tileset.get_elem(fd, data_encoding, data_compression))

        for layer in self.layers:
            root.append(layer.get_elem(fd, data_encoding, data_compression))

        tree = ET.ElementTree(root)
        tree.write(fname, encoding="UTF-8", xml_declaration=True)
