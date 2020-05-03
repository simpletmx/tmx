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


class LayerTile:
    """
    .. attribute:: gid

       The global ID of the tile.  A value of ``0`` indicates no tile at
       this position.

    .. attribute:: hflip

       Whether or not the tile is flipped horizontally.

    .. attribute:: vflip

       Whether or not the tile is flipped vertically.

    .. attribute:: dflip

       Whether or not the tile is flipped diagonally (X and Y axis
       swapped).
    """

    def __init__(self, gid, hflip=False, vflip=False, dflip=False):
        self.gid = gid
        self.hflip = hflip
        self.vflip = vflip
        self.dflip = dflip

    def __int__(self):
        r = self.gid
        if self.hflip:
            r |= 2 ** 31
        if self.vflip:
            r |= 2 ** 30
        if self.dflip:
            r |= 2 ** 29

        return r

    def get_elem(self, fd):
        """
        Return an XML element for the object.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        attr = {"gid": int(self)}
        elem = ET.Element("tile", attrib=local.clean_dict(attr))

        return elem
