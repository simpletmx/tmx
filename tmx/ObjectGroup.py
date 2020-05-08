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
from .Object import Object
from .Property import Property


class ObjectGroup:

    """
    .. attribute:: id

       Unique ID of the object group, or :const:`None` if unspecified.

    .. attribute:: name

       The name of the object group.

    .. attribute:: color

       A :class:`Color` object indicating the color used to display the
       objects in this group.  Set to :const:`None` for no color
       definition.

    .. attribute:: opacity

       The opacity of the object group as a value from 0 to 1.

    .. attribute:: visible

       Whether or not the object group is visible.

    .. attribute:: offsetx

       Rendering offset for this layer in pixels.

    .. attribute:: offsety

       Rendering offset for this layer in pixels.

    .. attribute:: draworder

       Can be "topdown" or "index".  Set to :const:`None` to not define
       this.

    .. attribute:: properties

       A list of :class:`Property` objects indicating the object group's
       properties

    .. attribute:: objects

       A list of :class:`Object` objects indicating the object group's
       objects.
    """

    def __init__(self, name, color=None, opacity=1, visible=True, offsetx=0,
                 offsety=0, draworder=None, properties=None, objects=None,
                 id_=None):
        self.name = name
        self.color = color
        self.opacity = opacity
        self.visible = visible
        self.offsetx = offsetx
        self.offsety = offsety
        self.draworder = draworder
        self.properties = properties or []
        self.objects = objects or []
        self.id = id_

    @classmethod
    def read_elem(cls, elem, fd):
        """
        Read XML element ``elem`` and return an object of this class.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        id_ = elem.attrib.get("id")
        name = elem.attrib.get("name", "")
        color = elem.attrib.get("color")
        if color:
            color = Color(color)
        opacity = float(elem.attrib.get("opacity", 1))
        visible = bool(int(elem.attrib.get("visible", True)))
        offsetx = int(elem.attrib.get("offsetx", 0))
        offsety = int(elem.attrib.get("offsety", 0))
        draworder = elem.attrib.get("draworder")
        properties = []
        objects = []

        for child in elem:
            if child.tag == "properties":
                properties.extend(local.read_list_elem(child, "property",
                                                       Property, fd))
            elif child.tag == "object":
                objects.append(Object.read_elem(child, fd))

        return cls(name, color, opacity, visible, offsetx, offsety, draworder,
                   properties, objects, id_)

    def get_elem(self, fd, encoding, compression, compressionlevel):
        """
        Return an XML element for the object.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        attr = {"id": self.id, "name": self.name, "color": self.color,
                "offsetx": self.offsetx or None,
                "offsety": self.offsety or None, "draworder": self.draworder}
        if not self.visible:
            attr["visible"] = 0
        elem = ET.Element("objectgroup", attrib=local.clean_dict(attr))

        if self.properties:
            elem.append(local.get_list_elem(
                self.properties, "properties", fd, encoding, compression,
                compressionlevel))

        for obj in self.objects:
            elem.append(obj.get_elem(fd, encoding, compression,
                                     compressionlevel))

        return elem
