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


class EditorSettings:

    """
    .. attribute:: chunkwidth

       The width of chunks used for infinite maps, or :const:`None` to
       not specify.

    .. attribute:: chunkheight

       The height of chunks used for infinite maps, or :const:`None` to
       not specify.

    .. attribute:: exporttarget

       The last file this map was exported to, or :const:`None` to not
       specify.

    .. attribute:: exportformat

       The short name of the last format this map was exported as, or
       :const:`None` to not specify.
    """

    def __init__(self, chunkwidth=None, chunkheight=None, exporttarget=None,
                 exportformat=None):
        self.chunkwidth = chunkwidth
        self.chunkheight = chunkheight
        self.exporttarget = exporttarget
        self.exportformat = exportformat

    @classmethod
    def read_elem(cls, elem, fd):
        """
        Read XML element ``elem`` and return an object of this class.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        chunkwidth = None
        chunkheight = None
        exporttarget = None
        exportformat = None

        for child in elem:
            if child.tag == "chunksize":
                chunkwidth = child.attrib.get("width", chunkwidth)
                chunkheight = child.attrib.get("height", chunkheight)
            elif child.tag == "export":
                exporttarget = child.attrib.get("target", exporttarget)
                exportformat = child.attrib.get("format", exportformat)

        if chunkwidth is not None:
            chunkwidth = int(chunkwidth)
        if chunkheight is not None:
            chunkheight = int(chunkheight)

        return cls(chunkwidth, chunkheight, exporttarget, exportformat)

    def get_elem(self, fd):
        """
        Return an XML element for the object.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        attr = {}
        elem = ET.Element("editorsettings", attrib=local.clean_dict(attr))

        if self.chunkwidth is not None or self.chunkheight is not None:
            attr = {"width": self.chunkwidth, "height": self.chunkheight}
            elem.append(ET.Element("chunksize", attrib=local.clean_dict(attr)))

        if self.exporttarget is not None or self.exportformat is not None:
            attr = {"target": self.exporttarget, "format": self.exportformat}
            elem.append(ET.Element("export", attrib=local.clean_dict(attr)))

        return elem
