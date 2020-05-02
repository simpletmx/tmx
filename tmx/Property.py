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

import local
import Color


class Property:

    """
    .. attribute:: name

       The name of the property.

    .. attribute:: value

       The value of the property.
       
       The following types are specially recognized by the TMX format
       and preserved when saving:

       - Integers
       - Floats
       - Booleans
       - :class:`Color` objects
       - :class:`pathlib.PurePath` objects

       Any other type is implicitly converted to and stored as a string
       when the TMX file is saved.
    """

    def __init__(self, name, value):
        self.name = name
        self.value = value

    @classmethod
    def read_elem(cls, elem, fd):
        """
        Read XML element ``elem`` and return an object of this class.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        name = elem.attrib.get("name")
        value = elem.attrib.get("value")
        if not value:
            value = elem.text

        type_ = elem.attrib.get("type", "string")
        if type_ == "bool":
            value = (value.lower() == "true")
        elif type_ == "int":
            value = int(value)
        elif type_ == "float":
            value = float(value)
        elif type_ == "file":
            value = pathlib.PurePath(os.path.join(fd, value))
        elif type_ == "color":
            value = Color(value)

        return cls(name, value)

    def get_elem(self, fd):
        """
        Return an XML element for the object.

        This is a low-level method used internally by this library; you
        don't typically need to use it.
        """
        attr = {"name": self.name}

        value = str(self.value)
        type_ = None
        text = None

        if isinstance(self.value, bool):
            value = "true" if self.value else "false"
            attr["type"] = "bool"
        elif isinstance(self.value, int):
            attr["type"] = "int"
        elif isinstance(self.value, float):
            attr["type"] = "float"
        elif isinstance(self.value, Color):
            attr["type"] = "color"
        elif isinstance(self.value, pathlib.PurePath):
            value = self.value.as_posix()
            attr["type"] = "file"

        if '\n' in value:
            text = value
        else:
            attr["value"] = value

        elem = ET.Element("property", attrib=local.clean_dict(attr))

        return elem
