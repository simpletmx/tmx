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
from .ImageLayer import ImageLayer
from .Layer import Layer
from .ObjectGroup import ObjectGroup
from .Property import Property


class GroupLayer:

    """
    .. attribute:: name

       The name of the group layer.

    .. attribute:: offsetx

       Rendering offset for the group layer in pixels.

    .. attribute:: offsety

       Rendering offset for the group layer in pixels.

    .. attribute:: opacity

       The opacity of the group layer as a value from 0 to 1.

    .. attribute:: visible

       Whether or not the group layer is visible.

    .. attribute:: properties

       A list of :class:`Property` objects indicating the group layer's
       properties.

    .. attribute:: layers

       A list of :class:`Layer`, :class:`ObjectGroup`,
       :class:`GroupLayer`, and :class:`ImageLayer` objects indicating
       the map's tile layers, object groups, group layers, and image
       layers, respectively.  Those that appear in this list first are
       rendered first (i.e. furthest in the back).
    """

    def __init__(self, name, offsetx=0, offsety=0, opacity=1, visible=True,
                 properties=None, layers=None):
        self.name = name
        self.offsetx = offsetx
        self.offsety = offsety
        self.opacity = opacity
        self.visible = visible
        self.properties = properties or []
        self.layers = layers or []

    @classmethod
    def read_elem(cls, elem, fd):
        """
        Read XML element ``elem`` and return an object of this class.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        name = elem.attrib.get("name")
        offsetx = int(elem.attrib.get("offsetx", 0))
        offsety = int(elem.attrib.get("offsety", 0))
        opacity = float(elem.attrib.get("opacity", 1))
        visible = bool(int(elem.attrib.get("visible", True)))
        properties = []
        layers = []

        for child in elem:
            if child.tag == "properties":
                properties.extend(local.read_list_elem(child, "property",
                                                       Property, fd))
            elif child.tag == "layer":
                layers.append(Layer.read_elem(child, fd))
            elif child.tag == "objectgroup":
                layers.append(ObjectGroup.read_elem(child, fd))
            elif child.tag == "imagelayer":
                layers.append(ImageLayer.read_elem(child, fd))
            elif child.tag == "group":
                layers.append(GroupLayer.read_elem(child, fd))

        return cls(name, offsetx, offsety, opacity, visible, properties, layers)

    def get_elem(self, fd, encoding, compression):
        """
        Return an XML element for the object.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        attr = {"name": self.name, "offsetx": self.offsetx,
                "offsety": self.offsety}
        if not self.visible:
            attr["visible"] = 0
        if self.opacity != 1:
            attr["opacity"] = self.opacity
        elem = ET.Element("group", attrib=local.clean_dict(attr))

        if self.properties:
            elem.append(local.get_list_elem(self.properties, "properties", fd,
                                            encoding, compression))

        for layer in self.layers:
            elem.append(layer.get_elem(fd, encoding, compression))

        return elem
