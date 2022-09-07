import mypy
from typing import Union
from pyautocad import Autocad
from pyautocad import APoint as P
import ezdxf
import array, itertools
from math import atan, tan, sin, cos
import pickle
from math import pi, sqrt
import datetime
import os
# coordinates: micrometers
# angles: radians

def init(
    writer: str = "pyautocad",
    filename: Union[str, None] = None,
    reset: bool = False,
):
    """[initialize ACS]

    for the writers:
    "pyautocad" is slow but you can see the effect in real time. 
    "ezdxf" is fast but you must close file while using it.

    Args:
        writer (str, optional): describes which writer to use to write to cad. Defaults to "pyautocad".
    """
    global msp, writer_, doc, path
    writer_ = writer
    if writer == "pyautocad":
        msp = Autocad()
        msp.prompt("ACS running\n")
        print(f"applying changes in file: {msp.doc.Name}")
    elif writer == "ezdxf":
        cwd = os.path.dirname(__file__)
        if filename is not None:
            try:
                doc = ezdxf.readfile(filename)
                msp = doc.modelspace()
                path = filename
                if reset:            
                    doc = ezdxf.new('R2018') # delete all components of a dxf file
                    msp = doc.modelspace()
                    doc.saveas(path)
                return None
            except Exception as e:
                print(e)
                path = os.path.join(cwd, "test", filename)    
        elif filename is None:
            path = os.path.join(cwd, "test", f"{datetime.datetime.now().strftime('%Y-%d-%m_%H-%M-%S')}.dxf")

        directory = os.path.join(cwd, "test")
        if not os.path.isdir(directory):
            os.mkdir(directory)
        doc = ezdxf.new("R2018")
        doc.saveas(path)
        msp = doc.modelspace()

def end():
    """[save dxf if writer=="ezdxf"]
    """
    if writer_ == "ezdxf":
        doc.save()

def add_layers(
    layers: list,
):
    """[add new layers]

    Args:
        layers (list): list of layer names
    """
    global msp, writer_, doc
    for layer in layers:
        if writer_ == "pyautocad":
            msp.ActiveDocument.Layers.Add(layer)
        elif writer_ == "ezdxf":
            try:
                doc.layers.add(name=layer)
            except Exception as e:
                print(e)

def calculate_bulge(
    angle: Union[int, float], 
):
    """[calculate bulge used in polyline_obj.SetBulge]

    Args:
        angle (Union[int, float]): angle to convert from
    """
    return tan(angle/4)

# drawing function

def polyline(
    VerticesList: list,
    layer: Union[str, None] = None,
):
    """[create polyline from 2d list]

    Args:
        VerticesList ([float 2d list]): [coordinates of the polyline]
        layer (str, optional): [layer of the polyline]. Defaults to None.
    """
    flatten = lambda list1: list(itertools.chain.from_iterable(list1)) # flatten n dim list
    global writer_
    if writer_ == "pyautocad":
        VerticesList = flatten(VerticesList)
        VerticesList = array.array("d", VerticesList) # convert to ActiveX compatible type
        polyline_obj = msp.model.AddLightWeightPolyline(VerticesList) # 2d polyline
        polyline_obj.Closed = True # close the polyline (required for dxf -> imask2 conversion)
        if layer is not None: # if layer is None, layer will be the currently selected layer in autocad
            polyline_obj.Layer = layer # set layer of polyline
    elif writer_ == "ezdxf":
        polyline_obj = msp.add_lwpolyline(VerticesList, dxfattribs={'layer': layer})
        polyline_obj.closed = True
    return polyline_obj

def set_bulge(polyline_obj, index, bulge):
    global writer_
    if writer_ == "pyautocad":
        polyline_obj.SetBulge(index, calculate_bulge(bulge))
    elif writer_ == "ezdxf":
        x, y, start_width, end_width, _ = polyline_obj[index]
        polyline_obj[index] = [x, y, start_width, end_width, calculate_bulge(bulge)]

# low level functions

def load_font(
    path: str = "font_data.pickle",
):
    """[loads font data]

    font_data = {
        "max_height": max_height,
        "widths": widths,
        "unicode_counts" : counts,
        "unicode_characters" : unicodes,
        "contour_coordinates": contours_list,
    }

    Args:
        path (str, optional): [path of font data pickle file]. Defaults to "font_data.pickle".

    Returns:
        [dict]: [font data]
    """
    # assertions

    with open(path, mode='rb') as f:
        font_data = pickle.load(f)
    return font_data

def text(
    x0: Union[int, float],
    y0: Union[int, float], 
    height: Union[int, float], 
    string: str, 
    font_data: dict, 
    layer: Union[str, None] = None,
):
    """[write text as polyline]

    Args:
        x0 ([int]): [bottom left x coordinate]
        y0 ([int]): [bottom left y coordinate]
        height ([int]): [max height of texts]
        string ([str]): [text]
        font_data ([dict]): [font data including coordinates]
    """

    unicode_characters = font_data["unicode_characters"]
    unicode_counts = font_data["unicode_counts"]
    contour_coordinates = font_data["contour_coordinates"]
    max_height = font_data["max_height"]
    widths = font_data["widths"]
    offset_x = x0 # bottom left x coordinate of char
    offset_y = y0 # bottom left y coordinate of char
    ratio = height/max_height # magnification ratio
    for char in string:
        if ord(char) in unicode_counts: # if unicode is valid and exists in font_data
            index = unicode_counts.index(ord(char))
            contours = contour_coordinates[index] # get coordinates for each points in polyline
            width = widths[index] # get width of char
            index = unicode_characters.index(char) # index of char
            contours = [[[offset_x + x*ratio, offset_y + y*ratio] for (x,y) in contour] for contour in contours] # consider magnification ratio and calculate coordinates
            offset_x += width*ratio # set bottom left x coordinate of next char
            for contour in contours:    
                polyline_obj = polyline(contour, layer)
        else: # if unicode doesnt exist in font_data, ignore and move x coordinate by 5
            print(f"character {char}(unicode:{ord(char)}) doesn't exist in font_data")
            offset_x += 5

# define basic shapes

def cross(
    x0: Union[int, float],
    y0: Union[int, float],
    w: Union[int, float] = 25.0,
    l: Union[int, float] = 125.0,
    layer: Union[str, None] = None,
):
    """[cross for maskless alignment]

        p0  p11
    p2  p1  p10 p9
    p3  p4  p7  p8
        p5  p6

    Args:
        x0 ([float]): [center x coordinate]
        y0 ([float]): [center y coordinate]
        w (float, optional): [width of arm]. Defaults to 25.0.
        l (float, optional): [length of arm from the center point]. Defaults to 125.0
        layer (str, optional): [layer of the polyline]. Defaults to None.

    Returns:
        [2d list]: [list of x,y coordinates]
    """

    # define point coordinates with offset (x,y)
    points = [0 for i in range(12)]
    points[0]  = [x0 + -w/2, y0 + l]
    points[1]  = [x0 + -w/2, y0 + w/2]
    points[2]  = [x0 + -l  , y0 + w/2]
    points[3]  = [x0 + -l  , y0 + -w/2]
    points[4]  = [x0 + -w/2, y0 + -w/2]
    points[5]  = [x0 + -w/2, y0 + -l]
    points[6]  = [x0 + w/2 , y0 + -l]
    points[7]  = [x0 + w/2 , y0 + -w/2]
    points[8]  = [x0 + l   , y0 + -w/2]
    points[9]  = [x0 + l   , y0 + w/2]
    points[10] = [x0 + w/2 , y0 + w/2]
    points[11] = [x0 + w/2 , y0 + l]
    # define connections
    polyline_obj = polyline(points, layer) # connect points with polyline
    return points

def square(
    x0: Union[int, float],
    y0: Union[int, float],
    x: Union[int, float],
    y: Union[int, float],
    xy0_position: str = "center",
    layer: Union[str, None] = None,
):
    """[create square]

    p0  p3
    p1  p2

    Args:
        x0 ([float]): [center x coordinate]
        y0 ([float]): [center y coordinate]
        x ([float]): [x length]
        y ([float]): [y length]
        xy0_position (str, optional): [defines where x0,y0 are located]. Defaults to "bottom_left"
        layer (str, optional): [definers the layer of the square]. Defaults to None

    Returns:
        [2d list]: [list of x,y coordinates]
    """

    start_coordinates = {
        "bottom_left":   [x0,       y0],
        "bottom_center": [x0 - x/2, y0],
        "bottom_right":  [x0 - x,   y0],
        "top_left":      [x0,       y0 - y],
        "top_center":    [x0 - x/2, y0 - y],
        "top_right":     [x0 - x,   y0 - y],
        "center_left":   [x0,       y0 - y/2],
        "center":        [x0 - x/2, y0 - y/2],
        "center_right":  [x0 - x,   y0 - y/2],
    }
    start_coordinate = start_coordinates[xy0_position]
    # define point coordinates with offset (x0,y0)
    points = [0 for i in range(4)]
    points[0] = [start_coordinate[0],     start_coordinate[1] + y]
    points[1] = [start_coordinate[0],     start_coordinate[1]]
    points[2] = [start_coordinate[0] + x, start_coordinate[1]]
    points[3] = [start_coordinate[0] + x, start_coordinate[1] + y]
    # define connections
    polyline_obj = polyline(points, layer) # connect points with polyline
    return points

def circle(
    x0: Union[int, float],
    y0: Union[int, float],
    r: Union[int, float],
    xy0_position: str = "center",
    layer: Union[str, None] = None,
):
    """[create circular sector (pizza shape)]

    p0 . . . p2 angle2
     .       .
     .      . 
     .    .
    p1 .
    angle1

    Args:
        x0 ([float]): [center x coordinate of the arc]
        y0 ([float]): [center y coordinate of the arc]
        r ([float]): [radius of the arc]
        angle1 ([float]): [angle 1 of the arc]
        angle2 ([float]): [angle 2 of the arc]
        xy0_position (str, optional): [defines where x0,y0 are located]. Defaults to "center"
        layer (str, optional): [definers the layer of the square]. Defaults to None

    Returns:
        [2d list]: [list of x,y coordinates]
    """

    start_coordinates = {
        "center": [x0, y0],
    }
    start_coordinate = start_coordinates[xy0_position]
    points = [0 for i in range(2)]
    points[0] = [start_coordinate[0]+r/2, start_coordinate[1]]
    points[1] = [start_coordinate[0]-r/2, start_coordinate[1]]
    polyline_obj = polyline(points, layer)
    set_bulge(polyline_obj, 0, pi)
    set_bulge(polyline_obj, 1, pi)
    return points

def triangle(
    x0: Union[int, float],
    y0: Union[int, float],
    r1: Union[int, float],
    r2: Union[int, float],
    angle1: Union[int, float],
    angle2: Union[int, float],
    xy0_position: str = "center",
    layer: Union[str, None] = None,
):
    """[create triangle]

    p0 . . . p2 angle2 r2
     .     .
     .   . 
     . .
    p1
    angle1 r1

    Args:
        x0 ([float]): [x coordinate of point 0]
        y0 ([float]): [y coordinate of point 0]
        r1 ([float]): [length at angle 1]
        r2 ([float]): [length at angle 2]
        angle1 ([float]): [angle 1 of point1]
        angle2 ([float]): [angle 2 of point2]
        xy0_position (str, optional): [defines where x0,y0 are located]. Defaults to "center"
        layer (str, optional): [definers the layer of the square]. Defaults to None

    Returns:
        [2d list]: [list of x,y coordinates]
    """

    start_coordinates = {
        "center": [x0, y0],
        "point1": [x0 - r1*cos(angle1), y0 - r1*sin(angle1)],
        "point2": [x0 - r2*cos(angle1), y0 - r2*sin(angle1)],
    }
    start_coordinate = start_coordinates[xy0_position]
    points = [0 for i in range(3)]
    points[0] = [start_coordinate[0],                  start_coordinate[1]]
    points[1] = [start_coordinate[0] + r1*cos(angle1), start_coordinate[1] + r1*sin(angle1)]
    points[2] = [start_coordinate[0] + r2*cos(angle2), start_coordinate[1] + r2*sin(angle2)]
    polyline_obj = polyline(points, layer)
    return points

def circular_sector(
    x0: Union[int, float],
    y0: Union[int, float],
    r: Union[int, float],
    angle1: Union[int, float],
    angle2: Union[int, float],
    xy0_position: str = "center",
    layer: Union[str, None] = None,
):
    """[create circular sector (pizza shape)]

    p0 . . . p2 angle2
     .       .
     .      . 
     .    .
    p1 .
    angle1

    Args:
        x0 ([float]): [center x coordinate of the arc]
        y0 ([float]): [center y coordinate of the arc]
        r ([float]): [radius of the arc]
        angle1 ([float]): [angle 1 of the arc]
        angle2 ([float]): [angle 2 of the arc]
        xy0_position (str, optional): [defines where x0,y0 are located]. Defaults to "center"
        layer (str, optional): [definers the layer of the square]. Defaults to None

    Returns:
        [2d list]: [list of x,y coordinates]
    """

    start_coordinates = {
        "center": [x0, y0],
        "point1": [x0 - r*cos(angle1), y0 - r*sin(angle1)],
        "point2": [x0 - r*cos(angle2), y0 - r*sin(angle2)],
    }
    start_coordinate = start_coordinates[xy0_position]
    points = [0 for i in range(3)]
    points[0] = [start_coordinate[0],                 start_coordinate[1]]
    points[1] = [start_coordinate[0] + r*cos(angle1), start_coordinate[1] + r*sin(angle1)]
    points[2] = [start_coordinate[0] + r*cos(angle2), start_coordinate[1] + r*sin(angle2)]
    polyline_obj = polyline(points, layer)
    set_bulge(polyline_obj, 1, calculate_bulge(angle2 - angle1)) # inner_arc
    return points

def annular_sector(
    x0: Union[int, float],
    y0: Union[int, float],
    r1: Union[int, float],
    r2: Union[int, float],
    angle1: Union[int, float],
    angle2: Union[int, float],
    xy0_position: str = "center",
    layer: Union[str, None] = None,
):
    """[create annular sector (baumkuchen German tree cake shape)]

     .      p3 .  p2 angle2
            .     .
          .      .
    p0 .       .
     .      .
    p1  .    
    angle 1

    Args:
        x0 ([float]): [center x coordinate of the arc]
        y0 ([float]): [center y coordinate of the arc]
        r1 ([float]): [inner radius of the arc]
        r2 ([float]): [outer radius of the arc]
        angle1 ([float]): [angle 1 of the arc]
        angle2 ([float]): [angle 2 of the arc]
        xy0_position (str, optional): [defines where x0,y0 are located]. Defaults to "center"
        layer (str, optional): [definers the layer of the square]. Defaults to None

    Returns:
        [2d list]: [list of x,y coordinates]
    """

    start_coordinates = {
        "center": [x0,                  y0],
        "point0": [x0 - r1*cos(angle1), y0 - r1*sin(angle1)],
        "point1": [x0 - r2*cos(angle1), y0 - r2*sin(angle1)],
        "point2": [x0 - r2*cos(angle2), y0 - r2*sin(angle2)],
        "point3": [x0 - r1*cos(angle2), y0 - r1*sin(angle2)],
    }
    start_coordinate = start_coordinates[xy0_position]
    points = [0 for i in range(4)]
    points[0] = [start_coordinate[0] + r1*cos(angle1), start_coordinate[1] + r1*sin(angle1)]
    points[1] = [start_coordinate[0] + r2*cos(angle1), start_coordinate[1] + r2*sin(angle1)]
    points[2] = [start_coordinate[0] + r2*cos(angle2), start_coordinate[1] + r2*sin(angle2)]
    points[3] = [start_coordinate[0] + r1*cos(angle2), start_coordinate[1] + r1*sin(angle2)]
    polyline_obj = polyline(points, layer)
    set_bulge(polyline_obj, 3, calculate_bulge(angle1 - angle2)) # inner_arc
    set_bulge(polyline_obj, 1, calculate_bulge(angle2 - angle1)) # outer_arc
    return points

def annular_sector_with_anchor_points(
    x0: Union[int, float],
    y0: Union[int, float],
    r1: Union[int, float],
    r2: Union[int, float],
    r3: Union[int, float],
    angle1: Union[int, float],
    angle2: Union[int, float],
    xy0_position: str = "center",
    layer: Union[str, None] = None,
):
    """[create annular sector (baumkuchen German tree cake shape)]

     .     p4      p3 .  p2 angle2
                   .     .
                  .    .
    p5          .     . 
              .     . 
           .      .
    p0 .       .
     .      .
    p1  .    
    angle 1

    Args:
        x0 ([float]): [center x coordinate of the arc]
        y0 ([float]): [center y coordinate of the arc]
        r1 ([float]): [inner radius of the arc]
        r2 ([float]): [outer radius of the arc]
        r3 ([float]): [radius of the anchor points' arc]
        angle1 ([float]): [angle 1 of the arc]
        angle2 ([float]): [angle 2 of the arc]
        xy0_position (str, optional): [defines where x0,y0 are located]. Defaults to "center"
        layer (str, optional): [definers the layer of the square]. Defaults to None

    Returns:
        [2d list]: [list of x,y coordinates]
    """

    start_coordinates = {
        "center": [x0,                  y0],
        "point0": [x0 - r1*cos(angle1), y0 - r1*sin(angle1)],
        "point1": [x0 - r2*cos(angle1), y0 - r2*sin(angle1)],
        "point2": [x0 - r2*cos(angle2), y0 - r2*sin(angle2)],
        "point3": [x0 - r1*cos(angle2), y0 - r1*sin(angle2)],
        "point4": [x0 - r3*cos(angle2), y0 - r3*sin(angle2)],
        "point5": [x0 - r3*cos(angle1), y0 - r3*sin(angle1)],
    }
    start_coordinate = start_coordinates[xy0_position]
    points = [0 for i in range(4)]
    points[0] = [start_coordinate[0] + r1*cos(angle1), start_coordinate[1] + r1*sin(angle1)]
    points[1] = [start_coordinate[0] + r2*cos(angle1), start_coordinate[1] + r2*sin(angle1)]
    points[2] = [start_coordinate[0] + r2*cos(angle2), start_coordinate[1] + r2*sin(angle2)]
    points[3] = [start_coordinate[0] + r1*cos(angle2), start_coordinate[1] + r1*sin(angle2)]
    points[4] = [start_coordinate[0] + r3*cos(angle2), start_coordinate[1] + r3*sin(angle2)]
    points[5] = [start_coordinate[0] + r3*cos(angle1), start_coordinate[1] + r3*sin(angle1)]
    polyline_obj = polyline(points, layer)
    set_bulge(polyline_obj, 3, calculate_bulge(angle1 - angle2)) # inner_arc
    set_bulge(polyline_obj, 1, calculate_bulge(angle2 - angle1)) # outer_arc
    return points

def annular_square_1(
    x0: Union[int, float],
    y0: Union[int, float],
    r1: Union[int, float],
    r2: Union[int, float],
    angle1: Union[int, float],
    angle2: Union[int, float],
    xy0_position: str = "center",
    layer: Union[str, None] = None,
):
    """[create annular sector with square]

     .      p4 . . p3 angle2
            .      .
          .        .
    p0 .           .
     .             .
    p1  . .  . . . p2  
    angle 1

    Args:
        x0 ([float]): [center x coordinate of the arc]
        y0 ([float]): [center y coordinate of the arc]
        r1 ([float]): [inner radius of the arc]
        r2 ([float]): [outer radius of the arc]
        angle1 ([float]): [angle 1 of the arc]
        angle2 ([float]): [angle 2 of the arc]
        xy0_position (str, optional): [defines where x0,y0 are located]. Defaults to "center"
        layer (str, optional): [definers the layer of the square]. Defaults to None

    Returns:
        [2d list]: [list of x,y coordinates]
    """

    start_coordinates = {
        "center": [x0,                                       y0],
        "point0": [x0 - r1*cos(angle1),                      y0 - r1*sin(angle1)],
        "point1": [x0 - r2*cos(angle1),                      y0 - r2*sin(angle1)],
        "point2": [x0 - (r2*sqrt(2))*cos((angle1+angle2)/2), y0 - (r2*sqrt(2))*sin((angle1+angle2)/2)],
        "point3": [x0 - r2*cos(angle2),                      y0 - r2*sin(angle2)],
        "point4": [x0 - r1*cos(angle2),                      y0 - r1*sin(angle2)],
    }
    start_coordinate = start_coordinates[xy0_position]
    points = [0 for i in range(5)]
    points[0] = [start_coordinate[0] + r1*cos(angle1),                      start_coordinate[1] + r1*sin(angle1)]
    points[1] = [start_coordinate[0] + r2*cos(angle1),                      start_coordinate[1] + r2*sin(angle1)]
    points[2] = [start_coordinate[0] + (r2*sqrt(2))*cos((angle1+angle2)/2), start_coordinate[1] + (r2*sqrt(2))*sin((angle1+angle2)/2)]
    points[3] = [start_coordinate[0] + r2*cos(angle2),                      start_coordinate[1] + r2*sin(angle2)]
    points[4] = [start_coordinate[0] + r1*cos(angle2),                      start_coordinate[1] + r1*sin(angle2)]
    polyline_obj = polyline(points, layer)
    set_bulge(polyline_obj, 4, calculate_bulge(angle1 - angle2)) # inner_arc
    return points

def annular_square_2(
    x0: Union[int, float],
    y0: Union[int, float],
    r1: Union[int, float],
    r2: Union[int, float],
    angle1: Union[int, float],
    angle2: Union[int, float],
    xy0_position: str = "center",
    layer: Union[str, None] = None,
):
    """[create annular sector with part square]

     .      p3 angle2
            .
          . .
    p0 .    .
     .      .
    p1  . . p2
    angle 1

    Args:
        x0 ([float]): [center x coordinate of the arc]
        y0 ([float]): [center y coordinate of the arc]
        r1 ([float]): [inner radius of the arc]
        r2 ([float]): [outer radius of the arc]
        angle1 ([float]): [angle 1 of the arc]
        angle2 ([float]): [angle 2 of the arc]
        xy0_position (str, optional): [defines where x0,y0 are located]. Defaults to "center"
        layer (str, optional): [definers the layer of the square]. Defaults to None

    Returns:
        [2d list]: [list of x,y coordinates]
    """

    start_coordinates = {
        "center":  [x0,                                   y0],
        "points0": [x0 - r1*cos(angle1),                  y0 - r1*sin(angle1)],
        "points1": [x0 - r2*cos(angle1),                  y0 - r2*sin(angle1)],
        "points2": [x0 - r1*cos(angle1) - r1*cos(angle2), y0 - r1*sin(angle1) - r1*sin(angle2)],
        "points3": [x0 - r1*cos(angle2),                  y0 - r1*sin(angle2)],
    }
    start_coordinate = start_coordinates[xy0_position]

    points = [0 for i in range(4)]
    points[0] = [start_coordinate[0] + r1*cos(angle1),                  start_coordinate[1] + r1*sin(angle1)]
    points[1] = [start_coordinate[0] + r2*cos(angle1),                  start_coordinate[1] + r2*sin(angle1)]
    points[2] = [start_coordinate[0] + r2*cos(angle1) + r1*cos(angle2), start_coordinate[1] + r2*sin(angle1) + r1*sin(angle2)]
    points[3] = [start_coordinate[0] + r1*cos(angle2),                  start_coordinate[1] + r1*sin(angle2)]

    polyline_obj = polyline(points, layer)
    set_bulge(polyline_obj, 3, calculate_bulge(angle1 - angle2)) # inner_arc
    return points

def trapezoid(
    x0: Union[int, float],
    y0: Union[int, float],
    widths: list,
    offset: Union[int, float],
    height: Union[int, float],
    parallel_axis: str = "x",
    xy0_position: str = "center",
    layer: Union[str, None] = None,
):
    """[create trapezoid]

    parallel_axis = "x"
     p0  p3
    p1     p2

    parallel_axis = "y"
    p0
         p3
         p2
    p1

    Args:
        x0 ([float]): [offset x coordinate (position in trapezoid is defined by xy0_position)]
        y0 ([float]): [offset y coordinate (position in trapezoid is defined by xy0_position)]
        widths ([list]): [top and bottom side length]
        offset = ([float]): [offset of the center of the top side with regards to the bottom side]
        height ([float]): [height of trapezoid]
        xy0_position (str, optional): [defines where x0,y0 are located]. Defaults to "bottom_left".
        parallel_axis (str, optional): [defines whether x or y sides are parallel]. Defaults to "x".
        layer (str, optional): [definers the layer of the square]. Defaults to None

    Returns:
        [2d list]: [list of x,y coordinates]
    """

    if parallel_axis == "x":
        # assertions

        x1,x2 = widths # top, bottom
        x12 = offset # offset of top and bottom (top center - bottom center x coordinate)
        y = height # height of trapezoid
        start_coordinates = {
            "bottom_left":   [x0,                     y0],
            "bottom_center": [x0 - x2/2,              y0],
            "bottom_right":  [x0 - x2,                y0],
            "top_left":      [x0 - x2/2 - x12 + x1/2, y0 - y],
            "top_center":    [x0 - x2/2 - x12,        y0 - y],
            "top_right":     [x0 - x2/2 - x12 - x1/2, y0 - y],
        }
        start_coordinate = start_coordinates[xy0_position]

        # define point coordinates with start coordinate (p1 is at start coordinate)
        points = [0 for i in range(4)]
        points[0] = [start_coordinate[0] + x2/2 + x12 - x1/2, start_coordinate[1] + y]
        points[1] = [start_coordinate[0], start_coordinate[1]]
        points[2] = [start_coordinate[0] + x2 , start_coordinate[1]]
        points[3] = [start_coordinate[0] + x2/2 + x12 + x1/2 , start_coordinate[1] + y]
    elif parallel_axis == "y":
        y1,y2 = widths # right, left
        y12 = offset # offset of right and left (right center - left center y coordinate)
        x = height # height of trapezoid
        start_coordinates = {
            "left_top":     [x0,     y0],
            "left_center":  [x0,     y0 + y2/2],
            "left_bottom":  [x0,     y0 + y2],
            "right_top"   : [x0 - x, y0 + y2/2 - y12 - y1/2],
            "right_center": [x0 - x, y0 + y2/2 - y12],
            "right_bottom": [x0 - x, y0 + y2/2 - y12 + y1/2],
        }
        start_coordinate = start_coordinates[xy0_position]

        # define point coordinates with start coordinate (p0 is at start coordinate)
        points = [0 for i in range(4)]
        points[0] = [start_coordinate[0],     start_coordinate[1]]
        points[1] = [start_coordinate[0],     start_coordinate[1] - y2]
        points[2] = [start_coordinate[0] + x, start_coordinate[1] - y2/2 + y12 - y1/2]
        points[3] = [start_coordinate[0] + x, start_coordinate[1] - y2/2 + y12 + y1/2]
    # define connections
    polyline(points, layer) # connect points with polyline
    return points

def alignment_mark(
    layer: Union[str, None] = None,
):
    """[creates maskless alignment mark consisting of crosses, "top left" indicator and corner cross indicator]

    """

    # crosses
    # center points for crosses (exclude x or y = 0)
    # -6000,-5500,...,6000
    center_points = [i for i in range(-6000,6001,500) if i not in [0]] # exclude 0
    # define all the center coordinates for the crosses
    cross_centers = []
    for i in center_points:
        cross_centers.extend([[-6000,i],[6000,i],[i,-6000],[i,6000]]) # 4 sides of square
    # create cross with centers defined above
    for cross_center in cross_centers:
        x,y = cross_center
        cross(x,y,layer=layer)    

    # top left indicator
    font_data = load_font()
    text(-6200,6200,2000,"Top-Left", font_data, layer=layer) # write "Top-Left" at top left corner

    # corner cross indicator (located at 4 corners)
    triangle(-5850,5850,300,300,pi*3/2,0, layer=layer) # top left
    triangle(-5850,-5850,300,300,0,pi/2, layer=layer)  # bottom left
    triangle(5850,-5850,300,300,pi/2,pi, layer=layer)  # bottom right
    triangle(5850,5850,300,300,pi,pi*3/2, layer=layer) # top right

def straight_lines(
    x0: Union[int, float],
    y0: Union[int, float],
    length: Union[int, float],
    widths: list,
    gaps: list,
    parallel_axis: str = "x",
    layer: Union[str, None] = None,
): 
    """[creates straight lines API]

    [parallel_axis = "x"]
    p4*(N-1) . . . p4*(N-1)+3
     .      line(N-1)       . width(N-1)
    p4*(N-1)+1 . . p4*(N-1)+2
        ~ ~ ~ ~ ~ ~ ~ ~ ~            
    p4 . . . . . . . . . . p7
     .        line1         .  width1
    p5 . . . . . . . . . . p6
                               gap0
    p0 . . . . . . . . . . p3
     .        line0         .  width0
    p1 . . . . . . . . . . p2
              length

    [parallel_axis = "y"]
    p0 . . . p3    p4 . . . p7     p4*(N-1) . . . p4*(N-1)+3
    .         .    .         .  ~  .              . 
    .  line0  .    .  line1  .  ~  .   line(N-1)  .  length
    .         .    .         .  ~  .              . 
    p1 . . . p2    p5 . . . p6     p4*(N-1)+1 . . p4*(N-1)+2
      width0   gap0   width1

    Args:
        x0 ([float]): [bottom left x coordinate]
        y0 ([float]): [bottom left y coordinate]
        length ([float]): [length of line]
        width ([float]): [width of lines]
        gap ([float]): [gap between lines]
        parallel_axis (str, optional): [defines whether x or y sides are parallel]. Defaults to "x".
    """

    N = len(widths)
    if parallel_axis == "x":
        # define center_point coordinates with offset (x0,y0)
        center_points = [0 for i in range(N)]
        for i in range(N):
            x = x0 + length/2
            y = y0 + sum(widths[:i]) + sum(gaps[:i]) + widths[i]/2 # widths[0~(i-1)] + widths[i]/2
            center_points[i] = [x, y] # single line i

        # define point coordinates
        points = [0 for i in range(4*N)]
        for i in range(N):
            points[4*i+0 : 4*i+4]  = square(center_points[i][0], center_points[i][1], length, widths[i], xy0_position="center", layer=layer)

    elif parallel_axis == "y":
        # define center_point coordinates with offset (x0,y0)
        center_points = [0 for i in range(N)]
        for i in range(N):
            y = y0 + length/2
            x = x0 + sum(widths[:i]) + sum(gaps[:i]) + widths[i]/2 # widths[0~(i-1)] + widths[i]/2
            center_points[i] = [x, y] # single line i

        # define point coordinates
        points = [0 for i in range(4*N)]
        for i in range(N):
            points[4*i+0 : 4*i+4]  = square(center_points[i][0], center_points[i][1], widths[i], length, xy0_position="center", layer=layer)
    return points

def bend_1(
    x0: Union[int, float],
    y0: Union[int, float],
    r: Union[int, float],
    r1s: list,
    r2s: list,
    angle1: Union[int, float],
    angle2: Union[int, float],
    layer: Union[str, None] = None,
):
    """[creates bend API (type1: most inner is circular_sector)]

            r   r1s[0]  r2s[0]
    p0 . . . p2   p6 . . p5 angle2
     .     .     .      .
     .   .     .      .
    p1 .     .      .
          .       .
    p3 .       .   
     .      .
     .    .
    p4 .  angle 1

    Args:
        x0 ([float]): [center x coordinate of the arcs]
        y0 ([float]): [center y coordinate of the arcs]
        r ([float]): [radius of the most inner circular sector]
        r1s ([float]): [inner radius of the annular sectors]
        r2s ([float]): [outer radius of the annular sectors]
        angle1 ([float]): [angle 1 of the arcs]
        angle2 ([float]): [angle 2 of the arcs]
    """

    # define point coordinates
    N = len(r1s) # number of annular sectors
    points = [0 for i in range(3+4*N)] # circular sector has 3 points instead of 4
    # circular sector
    points[0:3] = circular_sector(x0,y0,r,angle1,angle2,layer=layer)
            
    # annular sectors
    for i in range(N):
        points[4*i+3 : 4*(i+1)+3] = annular_sector(x0,y0,r1s[i],r2s[i],angle1,angle2,layer=layer)
    return points

def bend_2(
    x0: Union[int, float],
    y0: Union[int, float],
    r1s: list,
    r2s: list,
    angle1: Union[int, float],
    angle2: Union[int, float],
    layer: Union[str, None] = None,
):
    """[creates bend API (type2: most inner is NOT circular_sector)]

      r1s[0] r2s[0] r1s[1] r2s[1]
        p3 . . p2   p7 . . p6 angle2
    p0 .      .     .      .
     .       .     .      .
     .    .      .      .
    p1 .      .       .
           .        .
    p4 .         .   
     .        .
     .    .
    p5 .  angle 1

    Args:
        x0 ([float]): [center x coordinate of the arcs]
        y0 ([float]): [center y coordinate of the arcs]
        r1s ([float]): [inner radius of the annular sectors]
        r2s ([float]): [outer radius of the annular sectors]
        angle1 ([float]): [angle 1 of the arcs]
        angle2 ([float]): [angle 2 of the arcs]
    """
    
    N = len(r1s)
    points = [0 for i in range(4*N)]
    # annular sectors
    for i in range(N):
        points[4*i : 4*(i+1)] = annular_sector(x0,y0,r1s[i],r2s[i],angle1,angle2,layer=layer)
    return points

def bend_3(
    x0: Union[int, float],
    y0: Union[int, float],
    r: Union[int, float],
    r1s: list,
    r2s: list,
    angle1: Union[int, float],
    angle2: Union[int, float],
    layer: Union[str, None] = None,
):
    """[creates bend API (type3: most inner is circular_sector, most outer is square)]

            r   r1s[0]  r2s[0]
    p0 . . . p2   p6 . . p5  p11 . p10 angle2
     .     .     .      .    .      .
     .   .     .      .    .        .
    p1 .     .      .    .          .
          .       .    .            .
    p3 .       .     .              .
     .      .      .                .
     .    .     .                   .
    p4 .     .                      .
          .                         .
    p7 .                            .
     .                              .
    p8 . . . . . . . . . . . . . . p9
    angle 1

    Args:
        x0 ([float]): [center x coordinate of the arcs]
        y0 ([float]): [center y coordinate of the arcs]
        r ([float]): [radius of the most inner circular sector]
        r1s ([float]): [inner radius of the annular sectors]
        r2s ([float]): [outer radius of the annular sectors]
        angle1 ([float]): [angle 1 of the arcs]
        angle2 ([float]): [angle 2 of the arcs]
    """

    # define point coordinates
    N = len(r1s) # number of annular sectors
    points = [0 for i in range(4+4*N)] # circular sector has 3 points instead of 4, outer square has 5 points instead of 4
    # circular sector
    points[0:3] = circular_sector(x0,y0,r,angle1,angle2,layer=layer)
            
    # annular sectors
    for i in range(N-1):
        points[4*i+3 : 4*(i+1)+3] = annular_sector(x0,y0,r1s[i],r2s[i],angle1,angle2,layer=layer)
    
    # annular square
    i = N-1
    points[4*i+3 : 4*(i+1)+4] = annular_square_1(x0,y0,r1s[i],r2s[i],angle1,angle2,layer=layer)

    return points

def bend_4(
    x0: Union[int, float],
    y0: Union[int, float],
    r: Union[int, float],
    r1s: list,
    r2s: list,
    angle1: Union[int, float],
    angle2: Union[int, float],
    layer: Union[str, None] = None,
):
    """[creates bend API (type4: most inner is circular_sector, most outer is part square)]

            r   r1s[0]  r2s[0]
    p0 . . . p2   p6 . . p5  p10 angle2
     .     .     .      .    .
     .   .     .      .    . .
    p1 .     .      .    .   .
          .       .    .     .
    p3 .       .     .       .
     .      .      .         .
     .    .     .            .
    p4 .     .               .
          .                  .
    p7 .                     .
     .                       .
    p8 . . . . . . . . . . . p9
    angle 1

    Args:
        x0 ([float]): [center x coordinate of the arcs]
        y0 ([float]): [center y coordinate of the arcs]
        r ([float]): [radius of the most inner circular sector]
        r1s ([float]): [inner radius of the annular sectors]
        r2s ([float]): [outer radius of the annular sectors]
        angle1 ([float]): [angle 1 of the arcs]
        angle2 ([float]): [angle 2 of the arcs]
    """

    # define point coordinates
    N = len(r1s) # number of annular sectors
    points = [0 for i in range(3+4*N)] # circular sector has 3 points instead of 4, outer square has 4 points
    # circular sector
    points[0:3] = circular_sector(x0,y0,r,angle1,angle2,layer=layer)
            
    # annular sectors
    for i in range(N-1):
        points[4*i+3 : 4*(i+1)+3] = annular_sector(x0,y0,r1s[i],r2s[i],angle1,angle2,layer=layer)
    
    # annular square
    i = N-1
    points[4*i+3 : 4*(i+1)+3] = annular_square_2(x0,y0,r1s[i],r2s[i],angle1,angle2,layer=layer)

    return points

def tapers(
    x0: Union[int, float],
    y0: Union[int, float],
    height: Union[int, float],
    width1s: list,
    gap1s: list,
    width2s: list,
    gap2s: list,
    parallel_axis: str = "x",
    layer: Union[str, None] = None,
):
    """[creates tapers API]

    [parallel_axis = "x"]
           width1 gap1
          p0 . . p3 p4 . . p7 p8 . . p11 
        .       .   .       .   .      . 
      .  line0 .    . line1 .    . line2 .  height
    .         .    .         .    .        . 
    p1 . . . p2    p5 . . . p6    p9 . . . p10 
     width2   gap2

    [parallel_axis = "y"]
            p8 . . . .
            .  line2  . p11
            p9 . . .      .   
                    . . p10
            p4 . . .             
            .       . . p7
            .  line1     . 
            .       . . p6
            p5 . . .        gap1
       gap2         . . p3
            p0 . . .     .  width1
     width2 .  line0  . p2
            p1 . . . .
                height
    
    Args:
        x0 ([float]): [bottom left x coordinate]
        y0 ([float]): [bottom left y coordinate]
        height ([float]): [height of trapezoids]
        width1s ([list of floats]): [top side lengths from left to right, top to bottom]
        gap1s ([list of floats]): [top gaps from left to right, top to bottom]
        width2s ([list of floats]): [bottom side lengths from left to right, top to bottom]
        gap2s ([list of floats]): [bottom gaps from left to right, top to bottom]
        parallel_axis (str, optional): [defines whether x or y sides are parallel]. Defaults to "x".
    """
    N = len(width1s)
    if N % 2 == 0: # even tapers
        # [left_offset].width0. gap0 .width1. [gap1] .width2. gap2 .width3.
        center = int((N-2)/2)
        # top sides
        left_gap1s = gap1s[:center]
        center_gap1 = gap1s[center]
        left_width1s = width1s[:center+1]
        left_offset1 = -(sum(left_width1s) + sum(left_gap1s) + center_gap1/2)
        # bottom sides
        left_gap2s = gap2s[:center]
        center_gap2 = gap2s[center]
        left_width2s = width2s[:center+1]
        left_offset2 = -(sum(left_width2s) + sum(left_gap2s) + center_gap2/2)
    elif N % 2 == 1: # odd tapers
        # [left_offset].width0. gap0 .width1. gap1 .[width2]. gap2 .width3. gap3 .width4.
        center = int((N-1)/2)
        # top sides
        left_gap1s = gap1s[:center]
        left_width1s = width1s[:center]
        center_width1 = width1s[center]
        left_offset1 = -(sum(left_width1s) + sum(left_gap1s) + center_width1/2)
        # bottom sides
        left_gap2s = gap2s[:center]
        left_width2s = width2s[:center]
        center_width2 = width2s[center]
        left_offset2 = -(sum(left_width2s) + sum(left_gap2s) + center_width2/2)
    points = [0 for i in range(4*N)]
    top_left_offsets = [0 for i in range(N)]
    bottom_left_offsets = [0 for i in range(N)]
    top_bottom_offsets = [0 for i in range(N)]
    for i in range(N): # calculate offset between top and bottom centers
        top_left_offsets[i] = left_offset1 + sum(width1s[:i]) + sum(gap1s[:i])
        bottom_left_offsets[i] = left_offset2 + sum(width2s[:i]) + sum(gap2s[:i])
        top_bottom_offsets[i] = top_left_offsets[i] - bottom_left_offsets[i] + (width1s[i]-width2s[i])/2
    for i in range(N):
        top_width, bottom_width = width1s[i], width2s[i]
        widths = [top_width, bottom_width]
        if (parallel_axis == "x"):
            points[4*i : 4*(i+1)] = trapezoid(x0+bottom_left_offsets[i],y0,widths,top_bottom_offsets[i],height,xy0_position="bottom_left",parallel_axis="x",layer=layer)
        elif (parallel_axis == "y"):
            points[4*i : 4*(i+1)] = trapezoid(x0,y0+bottom_left_offsets[i],widths,top_bottom_offsets[i],height,xy0_position="left_top",parallel_axis="y",layer=layer)

    return points

if __name__ == "__main__":
    init(writer="ezdxf")
    add_layers(["layer0"])
    
    # test circular_sector
    circular_sector(200,200,100,3.14/6,3.14/2,layer="layer0")

    # test annular_sector
    annular_sector(0,0,50,100,3.14/6,3.14/2,layer="layer0")

    # test triangle
    triangle(100,100,50,75,3.14/6,3.14/2,layer="layer0")

    # test text
    font_data = load_font()
    text(0,0,100,"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", font_data,layer="layer0")
    text(0,150,100,"1234567890-^\@[;:],./\\=~|`{+*}<>?_", font_data,layer="layer0")
    text(0,300,100,"あいうえおかきくけこさしすせそなにぬねのはひふへほまみむめもやゆよわをん", font_data,layer="layer0")
    end()