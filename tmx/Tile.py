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

import local
from .Frame import Frame
from .Property import Property


class Tile:

    """
    .. attribute:: id

       The local tile ID within its tileset.

    .. attribute:: type

       The type of the tile.  An arbitrary string.  Set to :const:`None`
       to not define a type.

    .. attribute:: terrain

       Defines the terrain type of each corner of the tile, given as
       comma-separated indexes in the list of terrain types in the order
       top-left, top-right, bottom-left, bottom-right.  Leaving out a
       value means that corner has no terrain. Set to :const:`None` for
       no terrain.

    .. attribute:: probability

       A percentage indicating the probability that this tile is chosen
       when it competes with others while editing with the terrain tool.
       Set to :const:`None` to not define this.

    .. attribute:: properties

       A list of :class:`Property` objects indicating the tile's
       properties.

    .. attribute:: image

       An :class:`Image` object indicating the tile's image.  Set to
       :const:`None` for no image.

    .. attribute:: animation

       A list of :class:`Frame` objects indicating this tile's animation.
       Set to :const:`None` for no animation.
    """

    def __init__(self, id_, terrain=None, probability=None, properties=None,
                 image=None, animation=None, type_=None):
        self.id = id_
        self.type = type_
        self.terrain = terrain
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
        id_ = elem.attrib.get("id")
        if id_ is not None:
            id_ = int(id_)
        type_ = elem.attrib.get("type")
        terrain = elem.attrib.get("terrain")
        probability = elem.attrib.get("probability")
        properties = []
        image = None
        animation = None

        for child in elem:
            if child.tag == "properties":
                properties.extend(local.read_list_elem(child, "property",
                                                       Property, fd))
            elif child.tag == "image":
                image = Image.read_elem(child, fd)
            elif child.tag == "animation":
                animation = local.read_list_elem(child, "animation", Frame, fd)

        return cls(id_, terrain, probability, properties, image, animation,
                   type_)

    def get_elem(self, fd):
        """
        Return an XML element for the object.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        attr = {"id": self.id, "terrain": self.terrain,
                "probability": self.probability}
        if self.type:
            attr["type"] = self.type
        elem = ET.Element("tile", attrib=local.clean_dict(attr))

        if self.properties:
            elem.append(local.get_list_elem(self.properties, "properties", fd))

        if self.image:
            elem.append(self.image.get_elem(fd))

        if self.animation:
            elem.append(local.get_list_elem(self.animation, "animation", fd))

        return elem
