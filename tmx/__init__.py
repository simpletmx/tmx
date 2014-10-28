# Simple TMX library
# Copyright (c) 2014 Julian Marchant <onpon4@riseup.net>
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
This library reads and writes the Tiles TMX format in a simple way.
This is useful for map editors or generic level editors, and it's also
useful for using a map editor or generic level editor like Tiles to edit
your game's levels.

To load a TMX file, use :meth:`tmx.TileMap.load`.  You can then read the
attributes of the returned :class:`tmx.TileMap` object, modify the
attributes to your liking, and save your changes with
:meth:`tmx.TileMap.save`.  That's it!  Simple, isn't it?

This documentation explains what each attribute means, but if you want
to read the TMX spec itself, see this page:

https://github.com/bjorn/tiled/wiki/TMX-Map-Format
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


__version__ = "0.1a1"


import xml.etree.ElementTree as ET
import base64
import gzip
import zlib

from . import six

__all__ = ["TileMap", "Image", "ImageLayer", "Layer", "Object", "ObjectGroup",
           "Property", "TerrainType", "Tile", "Tileset", "data_decode",
           "data_encode"]


class TileMap(object):

    """
    This class loads, stores, and saves TMX files.

    .. attribute:: version

       The TMX format version.

    .. attribute:: orientation

       Map orientation.  Can be "orthogonal", "isometric", or "staggered".

    .. attribute:: width

       The width of the map in tiles.

    .. attribute:: height

       The height of the map in tiles.

    .. attribute:: tilewidth

       The width of a tile.

    .. attribute:: tileheight

       The height of a tile.

    .. attribute:: backgroundcolor

       The background color of the map as a hex string (e.g.
       ``"FF0000"`` or ``"#00FF00"``), or :const:`None` if no background
       color is defined.

    .. attribute:: renderorder

       The order in which tiles are rendered.  Can be ``"right-down"``,
       ``"right-up"``, ``"left-down"``, or ``"left-up"``.  Default is
       ``"right-down"``.

    .. attribute:: properties

       A list of :class:`Property` objects indicating the map's
       properties.

    .. attribute:: tilesets

       A list of :class:`Tileset` objects indicating the map's tilesets.

    .. attribute:: layers

       A list of :class:`Layer` objects indicating the map's (tile)
       layers.

    .. attribute:: objectgroups

       A list of :class:`ObjectGroup` objects indicating the map's
       object groups (a.k.a. object layers).

    .. attribute:: imagelayers

       A list of :class:`ImageLayer` objects indicating the map's image
       layers.
    """

    def __init__(self):
        self.version = "1.0"
        self.orientation = "orthogonal"
        self.width = 0
        self.height = 0
        self.tilewidth = 32
        self.tileheight = 32
        self.backgroundcolor = None
        self.renderorder = "right-down"
        self.properties = []
        self.tilesets = []
        self.layers = []
        self.objectgroups = []
        self.imagelayers = []

    @classmethod
    def load(cls, fname):
        """
        Load the indicated TMX file and return a :class:`TileMap` object
        representing it.
        """
        self = cls()

        tree = ET.parse(fname)
        root = tree.getroot()
        self.version = root.attrib.get("version", self.version)
        self.orientation = root.attrib.get("orientation", self.orientation)
        self.width = int(root.attrib.get("width", self.width))
        self.height = int(root.attrib.get("height", self.height))
        self.tilewidth = int(root.attrib.get("tilewidth", self.tilewidth))
        self.tileheight = int(root.attrib.get("tileheight", self.tileheight))
        self.backgroundcolor = root.attrib.get("backgroundcolor")
        self.renderorder = root.attrib.get("renderorder", self.renderorder)

        def get_properties(properties_root):
            properties = []
            for prop in properties_root.findall("property"):
                name = prop.attrib.get("name")
                value = prop.attrib.get("value")
                properties.append(Property(name, value))
            return properties

        def get_image(image_root):
            format_ = image_root.attrib.get("format")
            source = image_root.attrib.get("source")
            trans = image_root.attrib.get("trans")
            width = image_root.attrib.get("width")
            height = image_root.attrib.get("height")
            data = None

            for child in image_root:
                if child.tag == "data":
                    data = child.text.strip()

            return Image(format_, source, trans, width, height, data)

        for child in root:
            if child.tag == "properties":
                self.properties.extend(get_properties(child))
            elif child.tag == "tileset":
                firstgid = child.attrib.get("firstgid")
                source = child.attrib.get("source")

                if source is not None:
                    tfname = os.path.join(os.path.dirname(fname), source)
                    ttree = ET.parse(tfname)
                    troot = ttree.getroot()
                else:
                    troot = child

                name = troot.attrib.get("name", ""),
                tilewidth = int(troot.attrib.get("tilewidth", 32))
                tileheight = int(troot.attrib.get("tileheight", 32))
                spacing = int(troot.attrib.get("spacing", 0))
                margin = int(troot.attrib.get("margin", 0))

                xoffset = 0
                yoffset = 0
                properties = []
                image = None
                terraintypes = []
                tiles = []

                for tchild in troot:
                    if tchild.tag == "tileoffset":
                        xoffset = int(tchild.attrib.get("x", xoffset))
                        yoffset = int(tchild.attrib.get("y", yoffset))
                    elif tchild.tag == "properties":
                        properties.extend(get_properties(tchild))
                    elif tchild.tag == "image":
                        image = get_image(tchild)
                    elif tchild.tag == "terraintypes":
                        for terrain in tchild.findall("terrain"):
                            trname = terrain.attrib.get("name")
                            trtile = terrain.attrib.get("tile")
                            trproperties = []
                            for trchild in terrain:
                                if trchild.tag == "properties":
                                    trproperties.extend(get_properties(
                                        trchild))
                            terraintypes.append(TerrainType(trname, trtile,
                                                            trproperties))
                    elif tchild.tag == "tile":
                        tid = tchild.attrib.get("id")
                        if tid is not None:
                            tid = int(tid)
                        titerrain = tchild.attrib.get("terrain")
                        tiprobability = tchild.attrib.get("probability")
                        tiproperties = []
                        timage = None
                        for tichild in tchild:
                            if tichild.tag == "properties":
                                tiproperties.extend(get_properties(tichild))
                            elif tichild.tag == "image":
                                timage = get_image(tichild)
                        tiles.append(Tile(tid, titerrain, tiprobability,
                                          tiproperties, timage))

                self.tilesets.append(Tileset(firstgid, name, tilewidth,
                                             tileheight, source, spacing,
                                             margin, xoffset, yoffset,
                                             properties, image, terraintypes,
                                             tiles))
            elif child.tag == "layer":
                name = child.attrib.get("name", "")
                opacity = float(child.attrib.get("opacity", 1))
                visible = bool(int(child.attrib.get("visible", True)))
                properties = []
                tiles = []

                for lchild in child:
                    if lchild.tag == "properties":
                        properties.extend(get_properties(lchild))
                    elif lchild.tag == "data":
                        encoding = lchild.attrib.get("encoding")
                        compression = lchild.attrib.get("compression")
                        if encoding:
                            tiles = data_decode(lchild.text, encoding,
                                                compression)
                        else:
                            tiles = [tile.attrib.get("gid", 0)
                                     for tile in lchild.findall("tile")]

                self.layers.append(Layer(name, opacity, visible, properties,
                                         tiles))
            elif child.tag == "objectgroup":
                name = child.attrib.get("name", "")
                color = child.attrib.get("color")
                opacity = float(child.attrib.get("opacity", 1))
                visible = bool(int(child.attrib.get("visible", True)))
                properties = []
                objects = []

                for ogchild in child:
                    if ogchild.tag == "properties":
                        properties.extend(get_properties(ogchild))
                    elif ogchild.tag == "object":
                        oname = ogchild.attrib.get("name", "")
                        otype = ogchild.attrib.get("type", "")
                        ox = int(ogchild.attrib.get("x", 0))
                        oy = int(ogchild.attrib.get("y", 0))
                        owidth = int(ogchild.attrib.get("width", 0))
                        oheight = int(ogchild.attrib.get("height", 0))
                        orotation = float(ogchild.attrib.get("rotation", 0))
                        ogid = ogchild.attrib.get("gid")
                        if ogid is not None:
                            ogid = int(ogid)
                        ovisible = bool(int(ogchild.attrib.get("visible",
                                                               True)))
                        oproperties = []
                        oellipse = False
                        opolygon = None
                        opolyline = None

                        for ochild in ogchild:
                            if ochild.tag == "properties":
                                oproperties.extend(get_properties(ochild))
                            elif ochild.tag == "ellipse":
                                oellipse = True
                            elif ochild.tag == "polygon":
                                s = ochild.attrib.get("points", "").strip()
                                opolygon = [tuple(c.split(','))
                                            for c in s.split()]
                            elif ochild.tag == "polyline":
                                s = ochild.attrib.get("points", "").strip()
                                opolyline = [tuple(c.split(','))
                                             for c in s.split()]

                        objects.append(Object(oname, otype, ox, oy, owidth,
                                              oheight, orotation, ogid,
                                              ovisible, oproperties, oellipse,
                                              opolygon, opolyline))

                self.objectgroups.append(ObjectGroup(name, color, opacity,
                                                     visible, properties,
                                                     objects))
            elif child.tag == "imagelayer":
                name = child.attrib.get("name", "")
                x = int(child.attrib.get("x", 0))
                y = int(child.attrib.get("y", 0))
                opacity = float(child.attrib.get("opacity", 1))
                visible = bool(int(child.attrib.get("visible", True)))
                properties = []
                image = None

                for ilchild in child:
                    if ilchild.tag == "properties":
                        properties.extend(get_properties(ilchild))
                    elif ilchild.tag == "image":
                        image = get_image(ilchild)

                self.imagelayers.append(ImageLayer(name, x, y, opacity,
                                                   visible, properties, image))

        return self


class Image(object):

    """
    .. attribute:: format

       Indicates the format of image data if embedded.  Should be an
       extension like ``"png"``, ``"gif"``, ``"jpg"``, or ``"bmp"``.
       Set to :const:`None` to not specify the format.

    .. attribute:: source

       The location of the image file relative to the directory of the
       relevant TMX file.  If set to :const:`None`, the image data is
       embedded.

    .. attribute:: trans

       The transparent color of the image as a hex string (e.g.
       ``"FF0000"`` or ``"#00FF00"``), or :const:`None` if no color is
       treated as transparent.

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


class ImageLayer(object):

    """
    .. attribute:: name

       The name of the image layer.

    .. attribute:: x

       The x position of the image layer in pixels.

    .. attribute:: y

       The y position of the image layer in pixels.

    .. attribute:: opacity

       The opacity of the image layer as a value from 0 to 1.

    .. attribute:: visible

       Whether or not the image layer is visible.

    .. attribute:: properties

       A list of :class:`Property` objects indicating the properties of
       the image layer.

    .. attribute:: image

       An :class:`Image` object indicating the image of the image layer.
    """

    def __init__(self, name, x, y, opacity=1, visible=True, properties=None,
                 image=None):
        self.name = name
        self.x = x
        self.y = y
        self.opacity = opacity
        self.visible = visible
        self.properties = properties if properties else []
        self.image = image


class Layer(object):

    """
    .. attribute:: name

       The name of the layer.

    .. attribute:: opacity

       The opacity of the layer as a value from 0 to 1.

    .. attribute:: visible

       Whether or not the layer is visible.

    .. attribute:: properties

       A list of :class:`Property` objects indicating the properties of
       the layer.

    .. attribute:: tiles

       A list of global tile IDs indicating the tiles of the layer.  A
       value of ``0`` indicates no tile at the respective position.
    """

    def __init__(self, name, opacity=1, visible=True, properties=None,
                 tiles=None):
        self.name = name
        self.opacity = opacity
        self.visible = visible
        self.properties = properties if properties else []
        self.tiles = tiles if tiles else []


class Object(object):

    """
    .. attribute:: name

       The name of the object.  An arbitrary string.

    .. attribute:: type

       The type of the object.  An arbitrary string.

    .. attribute:: x

       The x coordinate of the object in pixels.

    .. attribute:: y

       The y coordinate of the object in pixels.

    .. attribute:: width

       The width of the object in pixels.

    .. attribute:: height

       The height of the object in pixels.

    .. attribute:: rotation

       The rotation of the object in degrees clockwise.

    .. attribute:: gid

       The tile to use as the object's image.  Set to :const:`None` for
       no reference to a tile.

    .. attribute:: visible

       Whether or not the object is visible.

    .. attribute:: properties

       A list of :class:`Property` objects indicating the object's
       properties.

    .. attribute:: ellipse

       Whether or not the object should be an ellipse.

    .. attribute:: polygon

       A list of coordinate pair tuples relative to the object's
       position indicating the points of the object's representation as
       a polygon.  Set to :const:`None` to not represent the object as a
       polygon.

    .. attribute:: polyline

       A list of coordinate pair tuples relative to the object's
       position indicating the points of the object's representation as
       a polyline.  Set to :const:`None` to not represent the object as
       a polyline.
    """

    def __init__(self, name, type_, x, y, width=0, height=0, rotation=0,
                 gid=None, visible=True, properties=None, ellipse=False,
                 polygon=None, polyline=None):
        self.name = name
        self.type = type_
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rotation = rotation
        self.gid = gid
        self.visible = visible
        self.properties = properties if properties else []
        self.ellipse = ellipse
        self.polygon = polygon
        self.polyline = polyline


class ObjectGroup(object):

    """
    .. attribute:: name

       The name of the object group.

    .. attribute:: color

       The color used to display the objects in this group as a hex
       string (e.g. ``"FF0000"`` or ``"#00FF00"``).  Set to
       :const:`None` for no color definition.

    .. attribute:: opacity

       The opacity of the object group as a value from 0 to 1.

    .. attribute:: visible

       Whether or not the object group is visible.

    .. attribute:: properties

       A list of :class:`Property` objects indicating the object group's
       properties
    """

    def __init__(self, name, color=None, opacity=1, visible=True,
                 properties=None, objects=None):
        self.name = name
        self.color = color
        self.opacity = opacity
        self.visible = visible
        self.properties = properties if properties else []
        self.objects = objects if objects else []


class Property(object):

    """
    .. attribute:: name

       The name of the property.

    .. attribute:: value

       The value of the property.
    """

    def __init__(self, name, value):
        self.name = name
        self.value = value


class TerrainType(object):

    """
    .. attribute:: name

       The name of the terrain type.

    .. attribute:: tile

       The local tile ID of the tile that represents the terrain
       visually.

    .. attribute:: properties

       A list of :class:`Property` objects indicating the terrain type's
       properties.
    """

    def __init__(self, name, tile, properties=None):
        self.name = name
        self.tile = tile
        self.properties = properties if properties else []


class Tile(object):

    """
    .. attribute:: id

       The local tile ID within its tileset.

    .. attribute:: terrain

       Defines the terrain type of each corner of the tile, given as
       comma-separated indexes in the list of terrain types in the order
       top-left, top-right, bottom-left, bottom-right.  Leaving out a
       value means that corner has no terrain.

       For example, a value of ``"0,3,,1"`` indicates that the top-left
       corner has the first terrain type, the top-right corner has the
       fourth terrain type, the bottom-left corner has no terrain type,
       and the bottom-right corner has the second terrain type.

       Set to :const:`None` for no terrain.

    .. attribute:: probability

       A percentage indicating the probability that this tile is chosen
       when it competes with others while editing with the terrain tool.
       Set to :const:`None` to not define this.

    .. attribute:: properties

       A list of :class:`Property` objects indicating the tile's
       properties.

    .. attribute:: image

       An :class:`Image` object indicating the tile's image.
    """

    def __init__(self, id_, terrain=None, probability=None, properties=None,
                 image=None):
        self.id = id_
        self.terrain = terrain
        self.probability = probability
        self.properties = properties if properties else []
        self.image = image


class Tileset(object):

    """
    .. attribute:: firstgid

       The first global tile ID of this tileset (this global ID maps to
       the first tile in this tileset).

    .. attribute:: name

       The name of this tileset.

    .. attribute:: tilewidth

       The (maximum) width of the tiles in this tileset.

    .. attribute:: tileheight

       The (maximum) height of the tiles in this tileset.

    .. attribute:: source

       The external TSX (Tile Set XML) file to store this tileset in
       relative to the directory of the relevant TMX file.  If set to
       :const:`None`, this tileset is stored in the TMX file.

    .. attribute:: spacing

       The spacing in pixels between the tiles in this tileset (applies
       to the tileset image).

    .. attribute:: margin

       The margin around the tiles in this tileset (applies to the
       tileset image).

    .. attribute:: xoffset

       The horizontal offset of the tileset in pixels (positive is
       right).

    .. attribute:: yoffset

       The vertical offset of the tileset in pixels (positive is down).

    .. attribute:: properties

       A list of :class:`Property` objects indicating the tileset's
       properties.

    .. attribute:: image

       An :class:`Image` object indicating the tileset's image.

    .. attribute:: terraintypes

       A list of :class:`TerrainType` objects indicating the tileset's
       terrain types.

    .. attribute:: tiles

       A list of :class:`Tile` objects indicating the tileset's tile
       properties.
    """

    def __init__(self, firstgid, name, tilewidth, tileheight, source=None,
                 spacing=0, margin=0, xoffset=0, yoffset=0, properties=None,
                 image=None, terraintypes=None, tiles=None):
        self.firstgid = firstgid
        self.name = name
        self.tilewidth = tilewidth
        self.tileheight = tileheight
        self.source = source
        self.spacing = spacing
        self.margin = margin
        self.xoffset = xoffset
        self.yoffset = yoffset
        self.properties = properties if properties else []
        self.image = image
        self.terraintypes = terraintypes if terraintypes else []
        self.tiles = tiles if tiles else []


def data_decode(data, encoding, compression=None):
    """
    Decode encoded data and return a list of integers it represents.

    Arguments:

    - ``data`` -- The data to decode.
    - ``encoding`` -- The encoding of the data.  Can be ``"base64"`` or
      ``"csv"``.
    - ``compression`` -- The compression method used.  Valid compression
      methods are ``"gzip"`` and ``"zlib"``.  Set to :const:`None` for
      no compression.
    """
    if encoding == "csv":
        return [int(i) for i in data.strip().split(",")]
    elif encoding == "base64":
        data = base64.b64decode(data.strip().encode("ascii"))

        if compression == "gzip":
            # data = gzip.decompress(data)
            with gzip.GzipFile(fileobj=six.BytesIO(data)) as f:
                data = f.read()
        elif compression == "zlib":
            data = zlib.decompress(data)
        elif compression:
            e = 'Compression type "{}" not supported.'.format(compression)
            raise ValueError(e)

        if six.PY2:
            return [ord(c) for c in data]
        else:
            return [i for i in data]
    else:
        e = 'Encoding type "{}" not supported.'.format(encoding)
        raise ValueError(e)


def data_encode(data, encoding, compression=None):
    """
    Encode a list of integers and return the encoded data.

    Arguments:

    - ``data`` -- The list of integers to encode.
    - ``encoding`` -- The encoding of the data.  Can be ``"base64"`` or
      ``"csv"``.
    - ``compression`` -- The compression method used.  Valid compression
      methods are ``"gzip"`` and ``"zlib"``.  Set to :const:`None` for
      no compression.
    """
    if encoding == "csv":
        return ','.join(data)
    elif encoding == "base64":
        data = b''.join([six.int2byte(i) for i in data])

        if compression == "gzip":
            # data = gzip.compress(data)
            fileobj = six.BytesIO()
            with gzip.GzipFile(mode='w', fileobj=fileobj) as f:
                f.write(data)
            with open(mode='rb', fileobj=fileobj) as f:
                data = f.read()
        elif compression == "zlib":
            data = zlib.compress(data)
        elif compression:
            e = 'Compression type "{}" not supported.'.format(compression)
            raise ValueError(e)

        return base64.b64encode(data)
    else:
        e = 'Encoding type "{}" not supported.'.format(encoding)
        raise ValueError(e)
