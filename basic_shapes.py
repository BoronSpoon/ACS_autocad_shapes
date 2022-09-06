"""
Functions that defines basic shapes
"""

from pyautocad import Autocad, APoint
import array, itertools
from math import atan, tan, sin, cos
import pickle
from pyautocad import APoint as P
from math import pi, sqrt

acad = Autocad()
acad.prompt("pyautocad: ActiveX automation of AutoCAD using Python\n")
print(f"applying changes in file: {acad.doc.Name}")

# coordinates: micrometers
# angles: radians

# very low level functions
flatten = lambda list1: list(itertools.chain.from_iterable(list1)) # flatten n dim list
calculate_bulge = lambda angle: tan(angle/4) # calculate bulge used in polyline_obj.SetBulge

def check_data_type(variable, variable_name, types):
    """[assert data type of variable]

    Args:
        variable ([variable]): [variable to check data type]
        variable_name ([str]): [name of the variable]
        types ([list]): [list containing types]
    """
    # check if variable is one of types
    types = [type(None) if type_ == None else type_ for type_ in types] # convert None to NoneType (to use in isinstance)
    assert any([isinstance(variable, type_) for type_ in types]), f"'{variable_name}' must be in {types}"

def check_value(variable, variable_name, values):
    """[check if variable is one of the values]

    Args:
        variable ([variable]): [variable to check value]
        variable_name ([str]): [name of the variable]
        values ([list]): [list containing values]
    """
    assert variable in values, f"'{variable_name}' must be one of the following: {values}"

def check_length(variable, variable_name, length):
    """[check length of variable]

    Args:
        variable ([variable]): [variable to check length]
        variable_name ([str]): [name of the variable]
        length ([int]): [length of variable]
    """
    assert len(variable) == length, f"'{variable_name}' must be list of length {length}"

# low level functions

def load_font(path="font_data.pickle"):
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
    check_data_type(path, "path", [str])

    with open(path, mode='rb') as f:
        font_data = pickle.load(f)
    return font_data

def text(x0, y0, height, string, font_data, layer=None):
    """[write text as polyline]

    Args:
        x0 ([int]): [bottom left x coordinate]
        y0 ([int]): [bottom left y coordinate]
        height ([int]): [max height of texts]
        string ([str]): [text]
        font_data ([dict]): [font data including coordinates]
    """
    # assertions
    check_data_type(x0, "x0", [int, float])
    check_data_type(y0, "y0", [int, float])
    check_data_type(height, "height", [int, float])
    check_data_type(string, "string", [str])
    check_data_type(font_data, "font_data", [dict])
    check_data_type(layer, "layer", [str, None])

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

def polyline(VerticesList, layer=None):
    """[create polyline from 2d list]

    Args:
        VerticesList ([float 2d list]): [coordinates of the polyline]
        layer (str, optional): [layer of the polyline]. Defaults to None.
    """
    # assertions
    check_data_type(VerticesList, "VerticesList", [list])
    check_data_type(layer, "layer", [str, None])

    VerticesList = flatten(VerticesList)
    VerticesList = array.array("d", VerticesList) # convert to ActiveX compatible type
    polyline_obj = acad.model.AddLightWeightPolyline(VerticesList) # 2d polyline
    polyline_obj.Closed = True # close the polyline (required for dxf -> imask2 conversion)
    if layer is not None: # if layer is None, layer will be the currently selected layer in autocad
        polyline_obj.Layer = layer # set layer of polyline
    return polyline_obj

# define basic shapes
def cross(x0,y0,w=25.0,l=125.0,layer=None):
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
    # assertions
    check_data_type(x0, "x0", [int, float])
    check_data_type(y0, "y0", [int, float])
    check_data_type(w, "w", [int, float])
    check_data_type(l, "l", [int, float])
    check_data_type(layer, "layer", [str, None])

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

def square(x0,y0,x,y,xy0_position="center",layer=None):
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
    # assertions
    check_data_type(x0, "x0", [int, float])
    check_data_type(y0, "y0", [int, float])
    check_data_type(x, "x", [int, float])
    check_data_type(y, "y", [int, float])
    check_data_type(xy0_position, "xy0_position", [str])
    check_data_type(layer, "layer", [str, None])
    xy0_positions = ["bottom_left", "bottom_center", "bottom_right", "top_left", "top_center", "top_right", "center_left", "center", "center_right"]
    check_value(xy0_position, "xy0_position", xy0_positions)

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

def circle(x0,y0,r,xy0_position="center",layer=None):
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
    # assertions
    check_data_type(x0, "x0", [int, float])
    check_data_type(y0, "y0", [int, float])
    check_data_type(r, "r", [int, float])
    check_data_type(xy0_position, "xy0_position", [str])
    check_data_type(layer, "layer", [str, None])
    xy0_positions = ["center", "point1", "point2"]
    check_value(xy0_position, "xy0_position", xy0_positions)

    start_coordinates = {
        "center": [x0, y0],
    }
    start_coordinate = start_coordinates[xy0_position]
    points = [0 for i in range(2)]
    points[0] = [start_coordinate[0]+r/2, start_coordinate[1]]
    points[1] = [start_coordinate[0]-r/2, start_coordinate[1]]
    polyline_obj = polyline(points, layer)
    polyline_obj.SetBulge(0, calculate_bulge(pi))
    polyline_obj.SetBulge(1, calculate_bulge(pi))
    return points

def triangle(x0,y0,r1,r2,angle1,angle2,xy0_position="center",layer=None):
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
    # assertions
    check_data_type(x0, "x0", [int, float])
    check_data_type(y0, "y0", [int, float])
    check_data_type(r1, "r1", [int, float])
    check_data_type(r2, "r2", [int, float])
    check_data_type(angle1, "angle1", [int, float])
    check_data_type(angle2, "angle2", [int, float])
    check_data_type(xy0_position, "xy0_position", [str])
    check_data_type(layer, "layer", [str, None])
    xy0_positions = ["center", "point1", "point2"]
    check_value(xy0_position, "xy0_position", xy0_positions)

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

def circular_sector(x0,y0,r,angle1,angle2,xy0_position="center",layer=None):
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
    # assertions
    check_data_type(x0, "x0", [int, float])
    check_data_type(y0, "y0", [int, float])
    check_data_type(r, "r", [int, float])
    check_data_type(angle1, "angle1", [int, float])
    check_data_type(angle2, "angle2", [int, float])
    check_data_type(xy0_position, "xy0_position", [str])
    check_data_type(layer, "layer", [str, None])
    xy0_positions = ["center", "point1", "point2"]
    check_value(xy0_position, "xy0_position", xy0_positions)

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
    polyline_obj.SetBulge(1, calculate_bulge(angle2 - angle1)) # inner_arc
    return points

def annular_sector(x0,y0,r1,r2,angle1,angle2,xy0_position="center",layer=None):
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
    # assertions
    check_data_type(x0, "x0", [int, float])
    check_data_type(y0, "y0", [int, float])
    check_data_type(r1, "r1", [int, float])
    check_data_type(r2, "r2", [int, float])
    check_data_type(angle1, "angle1", [int, float])
    check_data_type(angle2, "angle2", [int, float])
    check_data_type(xy0_position, "xy0_position", [str])
    check_data_type(layer, "layer", [str, None])
    xy0_positions = ["center", "point0", "point1", "point2", "point3"]
    check_value(xy0_position, "xy0_position", xy0_positions)

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
    polyline_obj.SetBulge(3, calculate_bulge(angle1 - angle2)) # inner_arc
    polyline_obj.SetBulge(1, calculate_bulge(angle2 - angle1)) # outer_arc
    return points


def annular_sector_with_anchor_points(x0,y0,r1,r2,r3,angle1,angle2,xy0_position="center",layer=None):
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
    # assertions
    check_data_type(x0, "x0", [int, float])
    check_data_type(y0, "y0", [int, float])
    check_data_type(r1, "r1", [int, float])
    check_data_type(r2, "r2", [int, float])
    check_data_type(angle1, "angle1", [int, float])
    check_data_type(angle2, "angle2", [int, float])
    check_data_type(xy0_position, "xy0_position", [str])
    check_data_type(layer, "layer", [str, None])
    xy0_positions = ["center", "point0", "point1", "point2", "point3"]
    check_value(xy0_position, "xy0_position", xy0_positions)

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
    polyline_obj.SetBulge(3, calculate_bulge(angle1 - angle2)) # inner_arc
    polyline_obj.SetBulge(1, calculate_bulge(angle2 - angle1)) # outer_arc
    return points

def annular_square_1(x0,y0,r1,r2,angle1,angle2,xy0_position="center",layer=None):
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
    # assertions
    check_data_type(x0, "x0", [int, float])
    check_data_type(y0, "y0", [int, float])
    check_data_type(r1, "r1", [int, float])
    check_data_type(r2, "r2", [int, float])
    check_data_type(angle1, "angle1", [int, float])
    check_data_type(angle2, "angle2", [int, float])
    check_data_type(xy0_position, "xy0_position", [str])
    check_data_type(layer, "layer", [str, None])
    xy0_positions = ["center", "point0", "point1", "point2", "point3", "point4"]
    check_value(xy0_position, "xy0_position", xy0_positions)

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
    polyline_obj.SetBulge(4, calculate_bulge(angle1 - angle2)) # inner_arc
    return points

def annular_square_2(x0,y0,r1,r2,angle1,angle2,xy0_position="center",layer=None):
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
    # assertions
    check_data_type(x0, "x0", [int, float])
    check_data_type(y0, "y0", [int, float])
    check_data_type(r1, "r1", [int, float])
    check_data_type(r2, "r2", [int, float])
    check_data_type(angle1, "angle1", [int, float])
    check_data_type(angle2, "angle2", [int, float])
    check_data_type(xy0_position, "xy0_position", [str])
    check_data_type(layer, "layer", [str, None])
    xy0_positions = ["center", "point0", "point1", "point2", "point3"]
    check_value(xy0_position, "xy0_position", xy0_positions)

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
    polyline_obj.SetBulge(3, calculate_bulge(angle1 - angle2)) # inner_arc
    return points

def trapezoid(x0,y0,widths,offset,height,xy0_position="bottom_center",parallel_axis="x",layer=None):
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
    # assertions
    check_data_type(x0,     "x0",     [int, float])
    check_data_type(y0,     "y0",     [int, float])
    check_data_type(widths, "widths", [list])
    check_data_type(offset, "offset", [int, float])
    check_data_type(height, "height", [int, float])
    check_data_type(xy0_position, "xy0_position", [str])
    check_data_type(parallel_axis, "parallel_axis", [str])
    check_data_type(layer, "layer", [str, None])
    parallel_axes = ["x","y"]
    check_value(parallel_axis, "parallel_axis", parallel_axes)
    check_length(widths, "widths", 2)

    if parallel_axis == "x":
        # assertions
        xy0_positions = ["bottom_left", "bottom_center", "bottom_right", "top_left", "top_center", "top_right"]
        check_value(xy0_position, "xy0_position", xy0_positions)

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
        # assertions
        xy0_positions = ["left_top", "left_center", "left_bottom", "right_top", "right_center", "right_bottom"]
        check_value(xy0_position, "xy0_position", xy0_positions)

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

def trapezoid_test():
    """[test trapezoid generation function]
    """
    # debug: p0~p3 is (200,300),(50,200),(350,200),(300,300) from top left, counter clockwise
    y_offset = 0
    trapezoid(50,200+y_offset, [100,300,50],100,xy0_position="bottom_left",parallel_axis="x")
    y_offset = 200
    trapezoid(200,200+y_offset,[100,300,50],100,xy0_position="bottom_center",parallel_axis="x")
    y_offset = 400
    trapezoid(350,200+y_offset,[100,300,50],100,xy0_position="bottom_right",parallel_axis="x")
    y_offset = 600
    trapezoid(200,300+y_offset,[100,300,50],100,xy0_position="top_left",parallel_axis="x")
    y_offset = 800
    trapezoid(250,300+y_offset,[100,300,50],100,xy0_position="top_center",parallel_axis="x")
    y_offset = 1000
    trapezoid(300,300+y_offset,[100,300,50],100,xy0_position="top_right",parallel_axis="x")

    # debug: p0~p3 is (100,50),(100,-350),(250,-350),(250,-150) from top left, counter clockwise
    x_offset = 0
    trapezoid(100+x_offset,50,150,[200,400,-100],xy0_position="left_top",parallel_axis="y")
    x_offset = 200
    trapezoid(100+x_offset,-150,150,[200,400,-100],xy0_position="left_center",parallel_axis="y")
    x_offset = 400
    trapezoid(100+x_offset,-350,150,[200,400,-100],xy0_position="left_bottom",parallel_axis="y")
    x_offset = 600
    trapezoid(250+x_offset,-150,150,[200,400,-100],xy0_position="right_top",parallel_axis="y")
    x_offset = 800
    trapezoid(250+x_offset,-250,150,[200,400,-100],xy0_position="right_center",parallel_axis="y")
    x_offset = 1000
    trapezoid(250+x_offset,-350,150,[200,400,-100],xy0_position="right_bottom",parallel_axis="y")

def circular_sector_test():
    """[test circular_sector generation function]
    """
    circular_sector(200,200,100,3.14/6,3.14/2)

def annular_sector_test():
    """[test annular_sector generation function]
    """
    annular_sector(0,0,50,100,3.14/6,3.14/2)

def triangle_test():
    """[test triangle generation function]
    """
    triangle(100,100,50,75,3.14/6,3.14/2)

def text_test():
    """[test text generation function]
    """
    font_data = load_font()
    text(0,0,100,"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", font_data)
    text(0,150,100,"1234567890-^\@[;:],./\\=~|`{+*}<>?_", font_data)
    text(0,300,100,"あいうえおかきくけこさしすせそなにぬねのはひふへほまみむめもやゆよわをん", font_data)