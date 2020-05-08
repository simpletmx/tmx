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


class WangTile:

    """
    .. attribute:: tileid

       The tile ID.

    .. attribute:: wangid

       The Wang ID.
    """
    
    def __init__(self, tileid, wangid):
        self.tileid = tileid
        self.wangid = wangid

    @classmethod
    def read_elem(cls, elem, fd):
        """
        Read XML element ``elem`` and return an object of this class.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        tileid = int(elem.attrib.get("tileid", "0"))
        wangid = elem.attrib.get("wangid")

        return cls(tileid, wangid)

    def get_elem(self, fd, encoding, compression, compressionlevel):
        """
        Return an XML element for the object.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        attr = {"tileid": self.tileid, "wangid": self.wangid}
        elem = ET.Element("wangtile", attrib=local.clean_dict(attr))

        return elem
