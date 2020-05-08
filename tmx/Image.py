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


import os
import pathlib
import xml.etree.ElementTree as ET

from . import local


class Image:

    """
    .. attribute:: format

       Indicates the format of image data if embedded.  Should be an
       extension like ``"png"``, ``"gif"``, ``"jpg"``, or ``"bmp"``.
       Set to :const:`None` to not specify the format.

    .. attribute:: source

       The location of the image file referenced.  If set to
       :const:`None`, the image data is embedded.

    .. attribute:: trans

       A :class:`Color` object indicating the transparent color of the
       image, or :const:`None` if no color is treated as transparent.

    .. attribute:: width

       The width of the image in pixels; used for tile index correction
       when the image changes.  If set to :const:`None`, the image width
       is not explicitly specified.

    .. attribute:: height

       The height of the image in pixels; used for tile index correction
       when the image changes.  If set to :const:`None`, the image
       height is not explicitly specified.

    .. attribute:: data

       The image data if embedded, or :const:`None` if an external image
       is referenced.
    """

    def __init__(self, format_=None, source=None, trans=None, width=None,
                 height=None, data=None):
        self.format = format_
        self.source = source
        self.trans = trans
        self.width = width
        self.height = height
        self.data = data

    @classmethod
    def read_elem(cls, elem, fd):
        """
        Read XML element ``elem`` and return an object of this class.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        format_ = elem.attrib.get("format")
        source = elem.attrib.get("source")
        if source is not None:
            source = os.path.join(fd, source)
        trans = elem.attrib.get("trans")
        width = elem.attrib.get("width")
        height = elem.attrib.get("height")
        data = None

        for child in elem:
            if child.tag == "data":
                data = child.text.strip()

        return cls(format_, source, trans, width, height, data)

    def get_elem(self, fd, encoding, compression, compressionlevel):
        """
        Return an XML element for the object.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        attr = {"format": self.format, "trans": self.trans,
                "width": self.width, "height": self.height}
        if self.source:
            pth = pathlib.PurePath(os.path.relpath(self.source, fd))
            attr["source"] = pth.as_posix()
        elem = ET.Element("image", attrib=local.clean_dict(attr))

        if self.data is not None:
            child = ET.Element("data")
            child.text = self.data
            elem.append(child)

        return elem
