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

"""
This library reads and writes the Tiled TMX format in a simple way.
This is useful for map editors or generic level editors, and it's also
useful for using a map editor or generic level editor like Tiled to edit
your game's levels.

To load a TMX file, use :meth:`tmx.TileMap.load`.  You can then read the
attributes of the returned :class:`tmx.TileMap` object, modify the
attributes to your liking, and save your changes with
:meth:`tmx.TileMap.save`.  That's it!  Simple, isn't it?

At the request of the developer of Tiled, this documentation does not
explain in detail what each attribute means. For that, please see the
TMX format specification, found here:

http://doc.mapeditor.org/en/latest/reference/tmx-map-format/
"""


__version__ = "1.103a0"
__author__ = "Layla Marchant"
__all__ = [
    "TileMap",
    "Color",
    "Image",
    "Text",
    "Property",
    "EditorSettings",
    "Tileset",
    "TerrainType",
    "Tile",
    "Frame",
    "WangSet",
    "WangColor",
    "WangTile",
    "Layer",
    "LayerTile",
    "LayerChunk",
    "ObjectGroup",
    "Object",
    "ImageLayer",
    "GroupLayer",
]


import os
import xml.etree.ElementTree as ET
import base64
import gzip
import zlib
import warnings
import pathlib
import io

from . import local
from .Color import Color
from .EditorSettings import EditorSettings
from .Frame import Frame
from .GroupLayer import GroupLayer
from .Image import Image
from .ImageLayer import ImageLayer
from .Layer import Layer
from .LayerChunk import LayerChunk
from .LayerTile import LayerTile
from .Object import Object
from .ObjectGroup import ObjectGroup
from .Property import Property
from .TerrainType import TerrainType
from .Text import Text
from .Tile import Tile
from .TileMap import TileMap
from .Tileset import Tileset
from .WangColor import WangColor
from .WangSet import WangSet
from .WangTile import WangTile
