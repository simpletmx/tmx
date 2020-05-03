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
from .WangColor import WangColor
from .WangTile import WangTile


class WangSet:

    """
    .. attribute:: name

       The name of the Wang set.

    .. attribute:: tile

       The tile ID of the tile representing this Wang set.

    .. attribute:: wangcornercolors

       A list of :class:`WangColor` objects representing colors used to
       define the corners of Wang tiles.

    .. attribute:: wangedgecolors

       A list of :class:`WangColor` objects representing colors used to
       define the edges of Wang tiles.

    .. attribute:: wangtiles

       A list of :class:`WangTile` objects representing Wang tiles in
       the Wang set.
    """

    def __init__(self, name, tile, wangcornercolors=None, wangedgecolors=None,
                 wangtiles=None):
        self.name = name
        self.tile = tile
        self.wangcornercolors = wangcornercolors or []
        self.wangedgecolors = wangedgecolors or []
        self.wangtiles = wangtiles or []

    @classmethod
    def read_elem(cls, elem, fd):
        """
        Read XML element ``elem`` and return an object of this class.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        name = elem.attrib.get("name", "")
        tile = int(elem.attrib.get("tile", 0))
        wangcornercolors = []
        wangedgecolors = []
        wangtiles = []

        for child in elem:
            if child.tag == "wangcornercolor":
                wangcornercolors.append(WangColor.read_elem(child, fd))
            elif child.tag == "wangedgecolor":
                wangedgecolors.append(WangColor.read_elem(child, fd))
            elif child.tag == "wangtile":
                wangtiles.append(WangTile.read_elem(child, fd))

        return cls(name, tile, wangcornercolors, wangedgecolors, wangtiles)

    def get_elem(self, fd):
        """
        Return an XML element for the object.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        attr = {"name": self.name, "tile": self.tile}
        elem = ET.Element("wangset", attrib=local.clean_dict(attr))

        for wangcolor in self.wangcornercolors:
            elem.append(wangcolor.get_elem(fd, "wangcornercolor"))

        for wangcolor in self.wangedgecolors:
            elem.append(wangcolor.get_elem(fd, "wangedgecolor"))

        for wangtile in self.wangtiles:
            elem.append(wangtile.get_elem(fd))

        return elem
