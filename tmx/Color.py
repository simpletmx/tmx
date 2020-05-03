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


class Color:

    """
    .. attribute:: red

       The red component of the color as an integer, where ``0``
       indicates no red intensity and ``255`` indicates full red
       intensity.

    .. attribute:: green

       The green component of the color as an integer, where ``0``
       indicates no green intensity and ``255`` indicates full green
       intensity.

    .. attribute:: blue

       The blue component of the color as an integer, where ``0``
       indicates no blue intensity and ``255`` indicates full blue
       intensity.

    .. attribute:: alpha

       The alpha transparency of the color as an integer, where ``0``
       indicates full transparency and ``255`` indicates full opacity.

    .. attribute:: hex_string

       The hex string representation of the color used by the TMX file.
       The format of the string is either ``"#RRGGBB"`` or
       ``"#AARRGGBB"``.  The hash at the beginning is optional.
    """

    def __init__(self, hex_string="#000000"):
        self.hex_string = hex_string

    @property
    def red(self):
        return self.__r

    @red.setter
    def red(self, value):
        self.__r = max(0, min(value, 255))

    @property
    def green(self):
        return self.__g

    @green.setter
    def green(self, value):
        self.__g = max(0, min(value, 255))

    @property
    def blue(self):
        return self.__b

    @blue.setter
    def blue(self, value):
        self.__b = max(0, min(value, 255))

    @property
    def alpha(self):
        return self.__a

    @alpha.setter
    def alpha(self, value):
        self.__a = max(0, min(value, 255))

    @property
    def hex_string(self):
        if self.alpha == 255:
            r, g, b = [hex(c)[2:].zfill(2) for c in (self.red, self.green,
                                                     self.blue)]
            return f"#{r}{g}{b}"
        else:
            r, g, b, a = [hex(c)[2:].zfill(2) for c in (self.red, self.green,
                                                        self.blue, self.alpha)]
            return f"#{a}{r}{g}{b}"

    @hex_string.setter
    def hex_string(self, value):
        if value.startswith("#"):
            value = value[1:]

        if len(value) == 6:
            r, g, b = [int(value[i:(i + 2)], 16) for i in range(0, 6, 2)]
            self.red, self.green, self.blue = r, g, b
            self.alpha = 255
        elif len(value) == 8:
            a, r, g, b = [int(value[i:(i + 2)], 16) for i in range(0, 8, 2)]
            self.red, self.green, self.blue, self.alpha = r, g, b, a
        else:
            raise ValueError("Invalid color string.")

    def __iter__(self):
        return str(self)

    def __repr__(self):
        return self.hex_string

    def __str__(self):
        return self.hex_string

    def __getitem__(self, index):
        return str(self)[index]
