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
from .Text import Text


class Object:

    """
    .. attribute:: id

       Unique ID of the object as a string if set, or :const:`None`
       otherwise.

    .. attribute:: name

       The name of the object.  An arbitrary string.

    .. attribute:: type

       The type of the object.  An arbitrary string.

    .. attribute:: x

       The x coordinate of the object in pixels.  This is the
       left edge of the object in orthogonal orientation, and the center
       of the object otherwise.

    .. attribute:: y

       The y coordinate of the object in pixels.  This is the bottom
       edge of the object.

    .. attribute:: width

       The width of the object in pixels.

    .. attribute:: height

       The height of the object in pixels.

    .. attribute:: rotation

       The rotation of the object in degrees clockwise.

    .. attribute:: gid

       The tile to use as the object's image.  Set to :const:`None` for
       no reference to a tile.

    .. attribute:: visible

       Whether or not the object is visible.

    .. attribute:: properties

       A list of :class:`Property` objects indicating the object's
       properties.

    .. attribute:: ellipse

       Whether or not the object should be an ellipse.

    .. attribute:: polygon

       A list of coordinate pair tuples relative to the object's
       position indicating the points of the object's representation as
       a polygon.  Set to :const:`None` to not represent the object as a
       polygon.

    .. attribute:: polyline

       A list of coordinate pair tuples relative to the object's
       position indicating the points of the object's representation as
       a polyline.  Set to :const:`None` to not represent the object as
       a polyline.

    .. attribute:: text

       A :class:`Text` object indicating the object's representation as
       text.  Set to :const:`None` to not represent the object as text.
    """

    def __init__(self, name, type_, x, y, width=0, height=0, rotation=0,
                 gid=None, visible=True, properties=None, ellipse=False,
                 polygon=None, polyline=None, id_=None, text=None):
        self.name = name
        self.type = type_
        self.x = x
        self.y = y
        self.id = id_
        self.width = width
        self.height = height
        self.rotation = rotation
        self.gid = gid
        self.visible = visible
        self.properties = properties or []
        self.ellipse = ellipse
        self.polygon = polygon
        self.polyline = polyline
        self.text = text

    @classmethod
    def read_elem(cls, elem, fd):
        """
        Read XML element ``elem`` and return an object of this class.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        id_ = elem.attrib.get("id")
        name = elem.attrib.get("name", "")
        type_ = elem.attrib.get("type", "")
        x = int(elem.attrib.get("x", 0))
        y = int(elem.attrib.get("y", 0))
        width = int(elem.attrib.get("width", 0))
        height = int(elem.attrib.get("height", 0))
        rotation = float(elem.attrib.get("rotation", 0))
        gid = elem.attrib.get("gid")
        if gid is not None:
            gid = int(gid)
        visible = bool(int(elem.attrib.get("visible", True)))
        properties = []
        ellipse = False
        polygon = None
        polyline = None
        text = None

        for child in elem:
            if child.tag == "properties":
                properties.extend(local.read_list_elem(child, "property",
                                                       Property, fd))
            elif child.tag == "ellipse":
                ellipse = True
            elif child.tag == "polygon":
                s = child.attrib.get("points", "").strip()
                polygon = []
                for coord in s.split():
                    pos = []
                    for n in coord.aplit(','):
                        if n.isdigit():
                            pos.append(int(n))
                        else:
                            pos.append(float(n))
                    polygon.append(tuple(pos))
            elif child.tag == "polyline":
                s = child.attrib.get("points", "").strip()
                polyline = []
                for coord in s.split():
                    pos = []
                    for n in coord.aplit(','):
                        if n.isdigit():
                            pos.append(int(n))
                        else:
                            pos.append(float(n))
                    polyline.append(tuple(pos))
            elif child.tag == "text":
                text = Text.read_elem(child, fd)

        return cls(name, type_, x, y, width, height, rotation, gid, visible,
                   properties, ellipse, polygon, polyline, id_, text)

    def get_elem(self, fd):
        """
        Return an XML element for the object.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        attr = {"id": self.id, "name": self.name, "type": self.type,
                "x": self.x, "y": self.y, "width": self.width,
                "height": self.height, "rotation": self.rotation,
                "gid": self.gid}
        if not self.visible:
            attr["visible"] = 0
        elem = ET.Element("object", attrib=local.clean_dict(attr))

        elem.append(local.get_list_elem(self.properties, "properties", fd))

        if self.ellipse:
            elem.append(ET.Element("ellipse"))
        elif self.polygon is not None:
            points = ' '.join(["{},{}".format(*T) for T in self.polygon])
            elem.append(ET.Element("polygon", attrib={"points": points}))
        elif self.polyline is not None:
            points = ' '.join(["{},{}".format(*T) for T in self.polyline])
            elem.append(ET.Element("polyline", attrib={"points": points}))
        elif self.text:
            elem.append(self.text.get_elem(fd))

        return elem
