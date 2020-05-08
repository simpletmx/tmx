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


class WangColor:

    """
    .. attribute:: name

       The name of this color.

    .. attribute:: color

       A :class:`Color` object representing the color.

    .. attribute:: tile

       The tile ID of the tile representing this color.

    .. attribute:: probability

       The relative probability that this color is chosen over others in
       case of multiple options.
    """

    def __init__(self, name, color, tile, probability):
        self.name = name
        self.color = color
        self.tile = tile
        self.probability = probability

    @classmethod
    def read_elem(cls, elem, fd):
        """
        Read XML element ``elem`` and return an object of this class.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        name = elem.attrib.get("name", "")
        color = Color(elem.attrib.get("color", "#000000"))
        tile = int(elem.attrib.get("tile", 0))
        probability = int(elem.attrib.get("probability", 1))

        return cls(name, color, tile, probability)

    def get_elem(self, fd, encoding, compression, compressionlevel,
                 tag="wangcolor"):
        """
        Return an XML element for the object.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        attr = {"name": self.name, "color": self.color.hex_string,
                "tile": self.tile, "probability": self.probability}
        elem = ET.Element(tag, attrib=local.clean_dict(attr))

        return elem
