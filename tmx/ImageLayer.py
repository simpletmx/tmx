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
from .Image import Image
from .Property import Property


class ImageLayer:

    """
    .. attribute:: name

       The name of the image layer.

    .. attribute:: offsetx

       The x position of the image layer in pixels.

    .. attribute:: offsety

       The y position of the image layer in pixels.

    .. attribute:: opacity

       The opacity of the image layer as a value from 0 to 1.

    .. attribute:: visible

       Whether or not the image layer is visible.

    .. attribute:: properties

       A list of :class:`Property` objects indicating the properties of
       the image layer.

    .. attribute:: image

       An :class:`Image` object indicating the image of the image layer.
    """

    def __init__(self, name, offsetx, offsety, opacity=1, visible=True,
                 properties=None, image=None):
        self.name = name
        self.offsetx = offsetx
        self.offsety = offsety
        self.opacity = opacity
        self.visible = visible
        self.properties = properties or []
        self.image = image

    @classmethod
    def read_elem(cls, elem, fd):
        """
        Read XML element ``elem`` and return an object of this class.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        name = elem.attrib.get("name", "")
        offsetx = int(elem.attrib.get("offsetx", 0))
        offsety = int(elem.attrib.get("offsety", 0))
        opacity = float(elem.attrib.get("opacity", 1))
        visible = bool(int(elem.attrib.get("visible", True)))
        properties = []
        image = None

        for child in elem:
            if child.tag == "properties":
                properties.extend(local.read_list_elem(child, "property",
                                                       Property, fd))
            elif child.tag == "image":
                image = Image.read_elem(child, fd)

        return cls(name, offsetx, offsety, opacity, visible, properties, image)

    def get_elem(self, fd):
        """
        Return an XML element for the object.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        attr = {"name": self.name, "offsetx": self.offsetx,
                "offsety": self.offsety}
        if self.opacity < 1:
            attr["opacity"] = self.opacity
        if not self.visible:
            attr["visible"] = "0"

        elem = ET.Element("imagelayer", attrib=local.clean_dict(attr))

        if self.properties:
            elem.append(local.get_list_elem(self.properties, "properties", fd))

        if self.image is not None:
            elem.append(self.image.get_elem(fd))

        return elem
