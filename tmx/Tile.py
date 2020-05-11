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
from .Frame import Frame
from .Image import Image
from .Property import Property


class Tile:

    """
    An individual tileset tile definition.

    .. attribute:: id

       The local tile ID within its tileset, where ``0`` is the first
       tile of the tileset.  In other words, this value is equal to the
       global ID of the tile minus the :attr:`firstgid` value of the
       applicable :class:`tmx.Tileset` object.

    .. attribute:: type

       The type of the tile.  An arbitrary string.  Set to :const:`None`
       to not define a type.

    .. attribute:: terrain_topleft
    .. attribute:: terrain_topright
    .. attribute:: terrain_bottomleft
    .. attribute:: terrain_bottomright

       Defines the terrain type of each corner of the tile, given as
       indexes within the list of terrain types found in the applicable
       :class:`tmx.Tileset` object (where 0 is the first
       index).  Set any of these to :const:`None` for no terrain type on
       the respective corner.

    .. attribute:: probability

       A value from 0 to 1 indicating probability that this tile is
       chosen when it competes with others while editing with the
       terrain tool in Tiled.  Set to :const:`None` to not define this.

    .. attribute:: properties

       A list of :class:`Property` objects indicating the tile's
       properties.

    .. attribute:: image

       A :class:`tmx.Image` object indicating the tile's image.  Set to
       :const:`None` for no tile-specific image (to use a portion of the
       tileset image instead; see the documentation for
       :class:`tmx.Tileset.image` for more information).

    .. attribute:: collisionshapes

       A :class:`tmx.ObjectGroup` object containing objects (shapes) for
       indicating collision boundaries of this tile in whatever way is
       appropriate for the game.

    .. attribute:: animation

       A list of :class:`tmx.Frame` objects indicating frames of this
       tile's animation.  Set to :const:`None` for no animation.
    """

    def __init__(self, id_, type_=None, terrain_topleft=None,
                 terrain_topright=None, terrain_bottomleft=None,
                 terrain_bottomright=None, probability=None,
                 properties=None, image=None, animation=None):
        self.id = id_
        self.type = type_
        self.terrain_topleft = terrain_topleft
        self.terrain_topright = terrain_topright
        self.terrain_bottomleft = terrain_bottomleft
        self.terrain_bottomright = terrain_bottomright
        self.probability = probability
        self.properties = properties or []
        self.image = image
        self.animation = animation

    @classmethod
    def read_elem(cls, elem, fd):
        """
        Read XML element ``elem`` and return an object of this class.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        id_ = int(elem.attrib.get("id", 0))
        type_ = elem.attrib.get("type")
        terrain_s = elem.attrib.get("terrain")
        probability = elem.attrib.get("probability")
        if probability is not None:
            probability = float(probability)
        properties = []
        image = None
        animation = None

        if terrain_s:
            terrain_list = terrain_s.split(',')
            terrain = [None, None, None, None]
            for i in range(len(terrain_list)):
                if i < len(terrain):
                    terrain[i] = terrain_list[i]

            terrain_topleft = terrain[0]
            terrain_topright = terrain[1]
            terrain_bottomleft = terrain[2]
            terrain_bottomright = terrain[3]
        else:
            terrain_topleft = None
            terrain_topright = None
            terrain_bottomleft = None
            terrain_bottomright = None

        for child in elem:
            if child.tag == "properties":
                properties.extend(local.read_list_elem(child, "property",
                                                       Property, fd))
            elif child.tag == "image":
                image = Image.read_elem(child, fd)
            elif child.tag == "animation":
                animation = local.read_list_elem(child, "animation", Frame, fd)

        return cls(id_, type_, terrain, probability, properties, image,
                   animation)

    def get_elem(self, fd, encoding, compression, compressionlevel):
        """
        Return an XML element for the object.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        terrain = ','.join([self.terrain_topleft, self.terrain_topright,
                            self.terrain_bottomleft, self.terrain_bottomright])
        attr = {"id": self.id, "terrain": terrain,
                "probability": self.probability}
        if self.type:
            attr["type"] = self.type
        elem = ET.Element("tile", attrib=local.clean_dict(attr))

        if self.properties:
            elem.append(local.get_list_elem(
                self.properties, "properties", fd, encoding, compression,
                compressionlevel))

        if self.image:
            elem.append(self.image.get_elem(fd, encoding, compression,
                                            compressionlevel))

        if self.animation:
            elem.append(local.get_list_elem(
                self.animation, "animation", fd, encoding, compression,
                compressionlevel))

        return elem
