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
from .Property import Property


class TerrainType:

    """
    .. attribute:: name

       The name of the terrain type.

    .. attribute:: tile

       The local tile ID of the tile that represents the terrain
       visually.

    .. attribute:: properties

       A list of :class:`Property` objects indicating the terrain type's
       properties.
    """

    def __init__(self, name, tile, properties=None):
        self.name = name
        self.tile = tile
        self.properties = properties or []

    @classmethod
    def read_elem(cls, elem, fd):
        """
        Read XML element ``elem`` and return an object of this class.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        name = elem.attrib.get("name", "")
        tile = int(elem.attrib.get("tile", 0))
        properties = []

        for child in elem:
            if child.tag == "properties":
                properties.extend(local.read_list_elem(child, "property",
                                                       Property, fd))

        return cls(name, tile, properties)

    def get_elem(self, fd, encoding, compression, compressionlevel):
        """
        Return an XML element for the object.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        attr = {"name": self.name, "tile": self.tile}
        elem = ET.Element("terrain", attrib=local.clean_dict(attr))

        if self.properties:
            elem.append(local.get_list_elem(
                self.properties, "properties", fd, encoding, compression,
                compressionlevel))

        return elem
