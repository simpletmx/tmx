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
    fname = f"{test_fname}_{test_n}A"
    tilemap.save(fname, encoding, compression)
    tilemap = tmx.TileMap.load(fname)
    fname = f"{test_fname}_{test_n}B"
    tilemap.save(fname, encoding, compression)
    test_n += 1


desc = "bare-bones tile map"
tilemap = tmx.TileMap()
test(desc, tilemap, None, False)
test(desc, tilemap, "csv", False)
test(desc, tilemap, "base64", False)
test(desc, tilemap, "base64", True)

desc = ""
tilemap.tiledversion = "1.2"
