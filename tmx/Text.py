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


class Text:

    """
    .. attribute:: text

       The text displayed.

    .. attribute:: fontfamily

       The font family used.

    .. attribute:: pixelsize

       The size of the font in pixels.

    .. attribute:: wrap

       Whether or not word wrapping is enabled.

    .. attribute:: color

       A :class:`Color` object indicating the color of the text.

    .. attribute:: bold

       Whether or not the font is bold.

    .. attribute:: italic

       Whether or not the font is italic.

    .. attribute:: underline

       Whether or not a line should be drawn below the text.

    .. attribute:: strikeout

       Whether or not a line should be drawn through the text.

    .. attribute:: kerning

       Whether or not kerning should be used.

    .. attribute:: halign

       Horizontal alignment of the text within the object (``"left"``,
       ``"center"``, or ``"right"``).

    .. attribute:: valign

       Vertical alignment of the text within the object (``"top"``,
       ``"center"``, or ``"bottom"``).
    """

    def __init__(self, text="", fontfamily="sans-serif", pixelsize=16,
                 wrap=False, color=None, bold=False, italic=False,
                 underline=False, strikeout=False, kerning=True, halign="left",
                 valign="top"):
        self.text = text
        self.fontfamily = fontfamily
        self.pixelsize = pixelsize
        self.wrap = wrap
        self.color = color or Color("#000000")
        self.bold = bold
        self.italic = italic
        self.underline = underline
        self.strikeout = strikeout
        self.kerning = kerning
        self.halign = halign
        self.valign = valign

    @classmethod
    def read_elem(cls, elem, fd):
        """
        Read XML element ``elem`` and return an object of this class.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        text = elem.text
        fontfamily = elem.attrib.get("fontfamily", "sans-serif")
        pixelsize = int(elem.attrib.get("pixelsize", 16))
        wrap = bool(int(elem.attrib.get("wrap", False)))
        color = Color(elem.attrib.get("color", "#000000"))
        bold = bool(int(elem.attrib.get("bold", False)))
        italic = bool(int(elem.attrib.get("italic", False)))
        underline = bool(int(elem.attrib.get("underline", False)))
        strikeout = bool(int(elem.attrib.get("strikeout", False)))
        kerning = bool(int(elem.attrib.get("kerning", True)))
        halign = elem.attrib.get("halign", "left")
        valign = elem.attrib.get("valign", "top")

        return cls(text, fontfamily, pixelsize, wrap, color, bold, italic,
                   underline, strikeout, kerning, halign, valign)

    def get_elem(self, fd, encoding, compression, compressionlevel):
        """
        Return an XML element for the object.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        attr = {}
        if self.fontfamily != "sans-serif":
            attr["fontfamily"] = self.fontfamily
        if self.pixelsize != 16:
            attr["pixelsize"] = self.pixelsize
        if self.wrap:
            attr["wrap"] = "1"
        if self.color.hex_string != "#000000":
            attr["color"] = self.color.hex_string
        if self.bold:
            attr["bold"] = "1"
        if self.italic:
            attr["italic"] = "1"
        if self.underline:
            attr["underline"] = "1"
        if self.strikeout:
            attr["strikeout"] = "1"
        if not self.kerning:
            attr["kerning"] = "0"
        if self.halign != "left":
            attr["halign"] = self.halign
        if self.valign != "top":
            attr["valign"] = self.valign

        elem = ET.Element("text", attrib=local.clean_dict(attr))
        elem.text = self.text

        return elem
