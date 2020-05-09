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
Test for the Simple TMX Library.  Run ``python3 -m tmx`` to run the
tests and examine the resulting tmxtest output files for errors. Used
to ensure that the library isn't shipped out into the wild with
embarrassing bugs.
"""


import datetime
import os
import xml.etree.ElementTree as ET

import tmx


T = datetime.datetime.now()
test_fname = f"tmxtest_{T.year}-{T.month}-{T.day}.{T.hour}.{T.minute}"
test_n = 0


# Standard test function: save, load, and save again.
def test(desc, tilemap, encoding, compression):
    global test_n
    print(f"Test {test_n}: {desc}")

    fname = f"{test_fname}_{test_n}A.tmx"
    tilemap.save(fname, encoding, compression)
    print(f"Write test results: {fname}")

    tilemap = tmx.TileMap.load(fname)
    fname = f"{test_fname}_{test_n}B.tmx"
    tilemap.save(fname, encoding, compression)
    print(f"Read test results: {fname}")

    test_n += 1


desc = "bare-bones tile map"
tilemap = tmx.TileMap()
test(desc, tilemap, None, False)
test(desc, tilemap, "csv", False)


desc = "bare tilesets and layers"

color = tmx.Color("#FF0000")
str_prop = tmx.Property("s", "Hello, world!")
int_prop = tmx.Property("i", 42)
float_prop = tmx.Property("f", 6.66)
color_prop = tmx.Property("c", color)
path_prop = tmx.Property("p", pathlib.PurePath("egg", "spam.txt"))
tileset = tmx.Tileset(0, "egg", 64, 16)
layer = tmx.Layer("bacon")
objectgroup = tmx.ObjectGroup("spam")
grouplayer = tmx.GroupLayer("sausage")
imagelayer = tmx.ImageLayer("baked beans", 4, 5)

tilemap.tiledversion = "1.2"
tilemap.width = 10
tilemap.height = 8
tilemap.backgroundcolor = color
tilemap.editorsettings.chunkwidth = 3
tilemap.editorsettings.chunkheight = 2
tilemap.editorsettings.exporttarget = "export.png"
tilemap.editorsettings.exportformat = "png"
tilemap.properties = [str_prop, int_prop, float_prop, color_prop, path_prop]
tilemap.tilesets = [tileset]
tilemap.layers = [layer, objectgroup, grouplayer, imagelayer]

test(desc, tilemap, None, False)
test(desc, tilemap, "csv", False)


desc = "populated tilesets and layers"

terraintype = tmx.TerrainType("spam", 0)
tile = tmx.Tile(0)

tileset.terraintypes.append(terraintype)
tileset.tiles.append(tile)

layertile = tmx.LayerTile(0)
layerchunk = tmx.LayerChunk(1, 2, 3, 4)

layer.id = 0
layer.width = 11
layer.height = 12
layer.opacity = 0.5
layer.visible = False
layer.offsetx = 13
layer.offsety = 14
layer.properties.append(str_prop)
layer.tiles.append(layertile)
layer.chunks.append(layerchunk)

test(desc, tilemap, None, False)
test(desc, tilemap, "csv", False)
test(desc, tilemap, "base64", False)
test(desc, tilemap, "base64", True)

print(f"{test_n} tests completed. Please review the generated files.")
