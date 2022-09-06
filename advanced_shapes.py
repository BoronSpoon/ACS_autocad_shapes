"""
Functions that defines advanced shapes, which is an conbination of the basic shapes
"""

from basic_shapes import *
from itertools import accumulate, count
from math import pi

# APIs

def alignment_mark(layer=None):
    """[creates maskless alignment mark consisting of crosses, "top left" indicator and corner cross indicator]

    """
    # assertions
    check_data_type(layer, "layer", [str, None])

    # crosses
    # center points for crosses (exclude x or y = 0)
    # -5000,-4500,...,5000
    center_points = [i for i in range(-5000,5001,500) if i not in [0]] # exclude 0
    # define all the center coordinates for the crosses
    cross_centers = []
    for i in center_points:
        cross_centers.extend([[-5000,i],[5000,i],[i,-5000],[i,5000]]) # 4 sides of square
    # create cross with centers defined above
    for cross_center in cross_centers:
        x,y = cross_center
        cross(x,y,layer=layer)    

    # top left indicator
    font_data = load_font()
    text(-5200,5200,1000,"Top-Left", font_data, layer=layer) # write "Top-Left" at top left corner

    # corner cross indicator (located at 4 corners)
    triangle(-4850,4850,300,300,pi*3/2,0, layer=layer) # top left
    triangle(-4850,-4850,300,300,0,pi/2, layer=layer)  # bottom left
    triangle(4850,-4850,300,300,pi/2,pi, layer=layer)  # bottom right
    triangle(4850,4850,300,300,pi,pi*3/2, layer=layer) # top right


def straight_lines(x0,y0,length,widths,gaps,parallel_axis="x",layer=None): 
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

def bend_1(x0,y0,r,r1s,r2s,angle1,angle2):
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
    points[0:3] = circular_sector(x0,y0,r,angle1,angle2)
            
    # annular sectors
    for i in range(N):
        points[4*i+3 : 4*(i+1)+3] = annular_sector(x0,y0,r1s[i],r2s[i],angle1,angle2)
    return points

def bend_2(x0,y0,r1s,r2s,angle1,angle2):
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
        points[4*i : 4*(i+1)] = annular_sector(x0,y0,r1s[i],r2s[i],angle1,angle2)
    return points

def bend_3(x0,y0,r,r1s,r2s,angle1,angle2):
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
    points[0:3] = circular_sector(x0,y0,r,angle1,angle2)
            
    # annular sectors
    for i in range(N-1):
        points[4*i+3 : 4*(i+1)+3] = annular_sector(x0,y0,r1s[i],r2s[i],angle1,angle2)
    
    # annular square
    i = N-1
    points[4*i+3 : 4*(i+1)+4] = annular_square_1(x0,y0,r1s[i],r2s[i],angle1,angle2)

    return points

def bend_4(x0,y0,r,r1s,r2s,angle1,angle2):
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
    points[0:3] = circular_sector(x0,y0,r,angle1,angle2)
            
    # annular sectors
    for i in range(N-1):
        points[4*i+3 : 4*(i+1)+3] = annular_sector(x0,y0,r1s[i],r2s[i],angle1,angle2)
    
    # annular square
    i = N-1
    points[4*i+3 : 4*(i+1)+3] = annular_square_2(x0,y0,r1s[i],r2s[i],angle1,angle2)

    return points

def tapers(x0,y0,height,width1s,gap1s,width2s,gap2s,parallel_axis="x"):
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
            points[4*i : 4*(i+1)] = trapezoid(x0+bottom_left_offsets[i],y0,widths,top_bottom_offsets[i],height,xy0_position="bottom_left",parallel_axis="x")
        elif (parallel_axis == "y"):
            points[4*i : 4*(i+1)] = trapezoid(x0,y0+bottom_left_offsets[i],widths,top_bottom_offsets[i],height,xy0_position="left_top",parallel_axis="y")

    return points

# coplanar parts

def termination_coplanar(x0,y0,gnd_width,sig_width,sig_gnd_gap,overlap1,overlap2,termination_length,parallel_axis="x"):
    """[termination of coplanar waveguide]
 
    p8 . . . . . .p11. .p13
    .             .     .
    .             .     .
    p9 . . . . . .p10   .
                  .     .
    p4 . .p7 . . . . . .p15
    .     .       .     .
    p5 . .p6 . . . . . .p14
      ov1     tl  . ov2 .
    p0 . . . . . .p3    .
    .             .     .
    .             .     .
    p1 . . . . . .p2 . .p12

    Args:
        x0 ([type]): [bottom left x coordinate]
        y0 ([type]): [bottom left x coordinate]
        gnd_width ([type]): [gnd line width]
        sig_width ([type]): [sig line width]
        sig_gnd_gap ([type]): [gap between signal and gnd lines]
        overlap1 ([type]): [length of overlap between sig and gnd lines at left side]
        overlap2 ([type]): [length of overlap between sig and gnd lines at right side]
        termination_length ([type]): [length of termination line]
        parallel_axis (str, optional): [defines whether x or y sides are parallel]. Defaults to "x".
    """
    termination_layer = "Ti%0_LPC_"
    points = [0 for i in range(16)]
    x = [0 for i in range(5)]; y = [0 for i in range(5)]
    x[0], y[0] = termination_length+overlap1, gnd_width # bottom gnd
    x[1], y[1] = overlap1, sig_width # sig
    x[2], y[2] = termination_length+overlap1+overlap2, sig_width # termination
    x[3], y[3] = termination_length+overlap1, gnd_width # top gnd
    x[4], y[4] = overlap2, gnd_width+sig_gnd_gap+sig_width+sig_gnd_gap+gnd_width # right gnd
    points[0:4]                                   = square(x0,y0,x[0],y[0],xy0_position="bottom_left") # bottom gnd
    points[4:8]                                   = square(x0,y0+gnd_width+sig_gnd_gap,x[1],y[1],xy0_position="bottom_left") # sig
    points[4], points[5], points[14], points[15]  = square(x0,y0+gnd_width+sig_gnd_gap,x[2],y[2],xy0_position="bottom_left",layer=termination_layer) # termination
    points[8:12]                                  = square(x0,y0+gnd_width+sig_gnd_gap+sig_width+sig_gnd_gap,x[3],y[3],xy0_position="bottom_left") # top gnd
    points[11], points[2], points[12], points[13] = square(x0+termination_length+overlap1,y0,x[4],y[4],xy0_position="bottom_left") # right gnd
    return points

def straight_coplanar(x0,y0,length,gnd_width,sig_width,sig_gnd_gap,parallel_axis="x"):
    """[creates straight coplanar waveguide]

    [parallel_axis = "x"]
    p8 . . . . . . . . . . p11
     .        line2         .  gnd
    p9 . . . . . . . . . . p10
                               gap 
    p4 . . . . . . . . . . p7
     .        line1         .  sig
    p5 . . . . . . . . . . p6
                               gap
    p0 . . . . . . . . . . p3
     .        line0         .  gnd
    p1 . . . . . . . . . . p2
              length

    [parallel_axis = "y"]
    p0 . . . p3    p4 . . . p7    p8 . . . p11 
    .         .    .         .    .         . 
    .  line0  .    .  line1  .    .  line2  . 
    .         .    .         .    .         . 
    p1 . . . p2    p5 . . . p6    p9 . . . p10 
        gnd     gap    sig     gap    gnd

    Args:
        x0 ([float]): [bottom left x coordinate]
        y0 ([float]): [bottom left y coordinate]
        gnd_width ([float]): [width of gnd lines]
        length ([float]): [length of coplanar line]
        sig_width ([float]): [width of sig line]
        sig_gnd_gap ([float]): [gap between sig and gnd lines]
    """

    widths = [gnd_width, sig_width, gnd_width] # width list from bottom to top
    gaps = [sig_gnd_gap, sig_gnd_gap] # gap list from bottom to top
    points = straight_lines(x0,y0,length,widths,gaps,parallel_axis)
    return points

def pads_1(x0,y0,length,width,gap,parallel_axis="y"):
    """[creates 3 pads for probing]

    [parallel_axis = "y"]
    p0 . . . p3    p4 . . . p7    p8 . . . p11 
    .         .    .         .    .         . 
    .  line0  .    .  line1  .    .  line2  . 
    .         .    .         .    .         . 
    p1 . . . p2    p5 . . . p6    p9 . . . p10 
        width   gap 


    [parallel_axis = "x"]
    p8 . . . .  . p11
     .   line2    .  
    p9 . . . .  . p10
                
    p4 . . . .  . p7
     .   line1    .  
    p5 . . . .  . p6
              　　　　gap
    p0 . . . .  . p3
     .   line0    .  width
    p1 . . . .  . p2
    　　length

    Args:
        x0 ([float]): [bottom left x coordinate]
        y0 ([float]): [bottom left y coordinate]
        gnd_width ([float]): [width of gnd lines]
        length ([float]): [length of coplanar line]
        sig_width ([float]): [width of sig line]
        sig_gnd_gap ([float]): [gap between sig and gnd lines]
    """

    widths = [width, width, width] # width list from bottom to top
    gaps = [gap, gap] # gap list from bottom to top
    points = straight_lines(x0,y0,length,widths,gaps,parallel_axis)
    return points

def pads_2(x0,y0,length,width,gap,parallel_axis="y"):
    """[creates 5 pads for probing]

    [parallel_axis = "y"]
    p0 . . . p3    p4 . . . p7    p8 . . . p11    p12. . . p15   p16. . . p19 
    .         .    .         .    .         .     .         .    .         . 
    .  line0  .    .  line1  .    .  line2  .     .  line3  .    .  line4  . 
    .         .    .         .    .         .     .         .    .         . 
    p1 . . . p2    p5 . . . p6    p9 . . . p10    p13. . . p14   p17. . . p18 
        width   gap 


    [parallel_axis = "x"]
    p16. . . .  . p19
     .   line4    .  
    p17. . . .  . p18
                
    p12. . . .  . p15
     .   line3    .  
    p13. . . .  . p14

    p8 . . . .  . p11
     .   line2    .  
    p9 . . . .  . p10
                
    p4 . . . .  . p7
     .   line1    .  
    p5 . . . .  . p6
              　　　　gap
    p0 . . . .  . p3
     .   line0    .  width
    p1 . . . .  . p2
    　　length

    Args:
        x0 ([float]): [bottom left x coordinate]
        y0 ([float]): [bottom left y coordinate]
        gnd_width ([float]): [width of gnd lines]
        length ([float]): [length of coplanar line]
        sig_width ([float]): [width of sig line]
        sig_gnd_gap ([float]): [gap between sig and gnd lines]
    """

    widths = [width, width, width, width, width] # width list from bottom to top
    gaps = [gap, gap, gap, gap] # gap list from bottom to top
    points = straight_lines(x0,y0,length,widths,gaps,parallel_axis)
    return points

def coplanar_tapers_1(x0,y0,height,pad_width,pad_gap,gnd_width,sig_width,sig_gnd_gap,parallel_axis="x"):
    """[creates tapers API. type 1: 3pin]

    [parallel_axis = "x"]
             gnd  gap  sig
          p0 . . p3 p4 . . p7 p8 . . p11 
        .       .   .       .   .      . 
      .  line0 .    . line1 .    . line2 .  height
    .         .    .         .    .        . 
    p1 . . . p2    p5 . . . p6    p9 . . . p10 
     pad_width  gap

    [parallel_axis = "y"]
    p8 . . . .
     .  line2  . p11
    p9 . . .      .  
             . . p10
    p4 . . .             
     .       . . p7
     .  line1     . 
     .       . . p6
    p5 . . .        gap
             . . p3
    p0 . . .      . width
     .  line0  . p2
    p1 . . . .
         height
    
    Args:
        x0 ([float]): [bottom left x coordinate]
        y0 ([float]): [bottom left y coordinate]
        height ([float]): [height of trapezoids]
        pad_width ([float]): [width of pads]
        pad_gap ([float]): [gap between pads]
        gnd_width ([float]): [width of gnd line]
        signal_width ([float]): [width of signal line]
        sig_gnd_gap ([float]): [gap between signal and gnd lines]
        parallel_axis (str, optional): [defines whether x or y sides are parallel]. Defaults to "x".
    """

    width1s = [gnd_width, sig_width, gnd_width]
    gap1s = [sig_gnd_gap, sig_gnd_gap]
    width2s = [pad_width, pad_width, pad_width]
    gap2s = [pad_gap, pad_gap]
    if (parallel_axis == "x"):
        points = tapers(x0,y0,height,width1s,gap1s,width2s,gap2s,parallel_axis="x")
    elif (parallel_axis == "y"):
        points = tapers(x0,y0,height,width1s,gap1s,width2s,gap2s,parallel_axis="y")

    return points

def coplanar_tapers_2(x0,y0,height,pad_width,pad_gap,gnd_width,sig_width,sig_gnd_gap,parallel_axis="x"):
    """[creates tapers API. type 2: 5pin]

    [parallel_axis = "x"]
             gnd    gap   sig   gap  gnd    gap  sig  gap  gnd
          p0 . . p3    p4 . . p7  p8 . .p11  p12. . p15  p16. .p19
         .       .    .       .   .       .   .      .    .      . 
       .  line0 .   .  line1 .    . line2 .    . line3 .   . line4 . 
     .         .  .         .    .        .    .        .  .        . 
    p1 . . . p2  p5 . . . p6    p9 . . . p10   p13. . . p14 p17. . . p18
     pad_width  gap

    [parallel_axis = "y"]
    p16. . . .
     .  line4  . p19
    p17. . .      . 
             . . p18
    p12 . . . .
     .  line3  . p15
    p13 . . .      .  
             . . p14
    p8 . . .             
     .       . . p11
     .  line2     . 
     .       . . p10
    p9 . . .        gap
             . . p7
    p4 . . .      . width
     .  line1  . p6
    p5 . . . .
             . . p3
    p0 . . .      . width
     .  line0  . p2
    p1 . . . .
         height

    Args:
        x0 ([float]): [bottom left x coordinate]
        y0 ([float]): [bottom left y coordinate]
        height ([float]): [height of trapezoids]
        pad_width ([float]): [width of pads]
        pad_gap ([float]): [gap between pads]
        gnd_width ([float]): [width of gnd line]
        signal_width ([float]): [width of signal line]
        sig_gnd_gap ([float]): [gap between signal and gnd lines]
        parallel_axis (str, optional): [defines whether x or y sides are parallel]. Defaults to "x".
    """

    width1s = [gnd_width, sig_width, gnd_width, sig_width, gnd_width]
    gap1s = [sig_gnd_gap, sig_gnd_gap, sig_gnd_gap, sig_gnd_gap]
    width2s = [pad_width, pad_width, pad_width, pad_width, pad_width]
    gap2s = [pad_gap, pad_gap, pad_gap, pad_gap]
    if (parallel_axis == "x"):
        points = tapers(x0,y0,height,width1s,gap1s,width2s,gap2s,parallel_axis="x")
    elif (parallel_axis == "y"):
        points = tapers(x0,y0,height,width1s,gap1s,width2s,gap2s,parallel_axis="y")

    return points

def bend_coplanar_1(x0,y0,gnd_width,sig_width,sig_gnd_gap,angle1,angle2):
    """[creates bent coplanar waveguide (type1: most inner is circular_sector)]

        gnd    gap  sig  gap  gnd
    p0  . .  p2   p6 . p5  p10 . p9  angle2
     .       .    .    .    .    .
     .    .     .     .   .    .
    p1 .      .     .   .    .
           .      .    .    .
    p3 .       .    .     .
     .     .     .     .
    p4 .      .      .
           .      .
    p7 .       .
     .     .
    p8 .  angle1

    Args:
        x0 ([float]): [bottom left x coordinate]
        y0 ([float]): [bottom left y coordinate]
        gnd_width ([float]): [width of gnd lines]
        sig_width ([float]): [width of sig line]
        sig_gnd_gap ([float]): [gap between sig and gnd lines]
        angle1 ([float]): [angle 1 of the arcs]
        angle2 ([float]): [angle 2 of the arcs]
    """

    r1s = [gnd_width+sig_gnd_gap, gnd_width+sig_gnd_gap+sig_width+sig_gnd_gap] # inner radii list from inside to outside
    r2s = [gnd_width+sig_gnd_gap+sig_width, gnd_width+sig_gnd_gap+sig_width+sig_gnd_gap+gnd_width] # outer radii list from inside to outside
    r = gnd_width # radius of the most inner circular sectors
    points = bend_1(x0,y0,r,r1s,r2s,angle1,angle2)
    return points

def bend_coplanar_2(x0,y0,r,gnd_width,sig_width,sig_gnd_gap,angle1,angle2):
    """[creates bent coplanar waveguide (type2: most inner is NOT circular_sector)]

        r  gnd   gap  sig  gap  gnd
        p3 . . p2   p7 . p6  p11 . p10  angle2
    p0 .      .     .    .    .    .
     .       .     .    .    .    .
     .    .      .     .   .    .
    p1 .      .      .   .    .
           .      .    .    .
    p4 .       .    .     .
     .     .     .     .
    p5 .      .      .
           .      .
    p8 .       .
     .     .
    p9 .  angle1

    Args:
        x0 ([float]): [bottom left x coordinate]
        y0 ([float]): [bottom left y coordinate]
        r ([float]): [inner radius of the most inner annular sector]
        gnd_width ([float]): [width of gnd lines]
        sig_width ([float]): [width of sig line]
        sig_gnd_gap ([float]): [gap between sig and gnd lines]
        angle1 ([float]): [angle 1 of the arcs]
        angle2 ([float]): [angle 2 of the arcs]
    """

    r1s = [r, r+gnd_width+sig_gnd_gap, r+gnd_width+sig_gnd_gap+sig_width+sig_gnd_gap] # inner radii list from inside to outside
    r2s = [r+gnd_width, r+gnd_width+sig_gnd_gap+sig_width, r+gnd_width+sig_gnd_gap+sig_width+sig_gnd_gap+gnd_width] # outer radii list from inside to outside
    points = bend_2(x0,y0,r1s,r2s,angle1,angle2)
    return points

def bend_coplanar_3(x0,y0,gnd_width,sig_width,sig_gnd_gap,angle1,angle2):
    """[creates bent coplanar waveguide (type3: most inner is circular_sector, most outer is square)]

        gnd    gap  sig  gap  gnd
    p0  . .  p2   p6 . p5   p11 .p10  angle2
     .       .    .    .    .    . 
     .    .     .     .   .      .    
    p1 .      .     .   .        .   
           .      .    .         .  
    p3 .       .    .            .  
     .     .     .               .    
    p4 .      .                  .  
           .                     .  
    p7 .                         . 
     .                           .  
    p8 . . . . . . . . . . . . . p9  
    angle1

    Args:
        x0 ([float]): [bottom left x coordinate]
        y0 ([float]): [bottom left y coordinate]
        gnd_width ([float]): [width of gnd lines]
        sig_width ([float]): [width of sig line]
        sig_gnd_gap ([float]): [gap between sig and gnd lines]
        angle1 ([float]): [angle 1 of the arcs]
        angle2 ([float]): [angle 2 of the arcs]
    """

    r1s = [gnd_width+sig_gnd_gap, gnd_width+sig_gnd_gap+sig_width+sig_gnd_gap] # inner radii list from inside to outside
    r2s = [gnd_width+sig_gnd_gap+sig_width, gnd_width+sig_gnd_gap+sig_width+sig_gnd_gap+gnd_width] # outer radii list from inside to outside
    r = gnd_width # radius of the most inner circular sectors
    points = bend_3(x0,y0,r,r1s,r2s,angle1,angle2)
    return points

def bend_coplanar_4(x0,y0,gnd_width,sig_width,sig_gnd_gap,angle1,angle2):
    """[creates bent coplanar waveguide (type3: most inner is circular_sector, most outer is part square)]

        gnd    gap  sig  gap  
    p0  . .  p2   p6 . p5   p10 angle2
     .       .    .    .   . . 
     .    .     .     .   .  .    
    p1 .      .     .   .    .   
           .      .    .     .  
    p3 .       .    .        .  
     .     .     .           .    
    p4 .      .              .  
           .                 .  
    p7 .                     . 
     .                       .  
    p8 . . . . . . . . . . . p9  
    angle1

    Args:
        x0 ([float]): [bottom left x coordinate]
        y0 ([float]): [bottom left y coordinate]
        gnd_width ([float]): [width of gnd lines]
        sig_width ([float]): [width of sig line]
        sig_gnd_gap ([float]): [gap between sig and gnd lines]
        angle1 ([float]): [angle 1 of the arcs]
        angle2 ([float]): [angle 2 of the arcs]
    """

    r1s = [gnd_width+sig_gnd_gap, gnd_width+sig_gnd_gap+sig_width+sig_gnd_gap] # inner radii list from inside to outside
    r2s = [gnd_width+sig_gnd_gap+sig_width, gnd_width+sig_gnd_gap+sig_width+sig_gnd_gap+gnd_width] # outer radii list from inside to outside
    r = gnd_width # radius of the most inner circular sectors
    points = bend_4(x0,y0,r,r1s,r2s,angle1,angle2)
    return points

# single line parts

def straight_single_line(x0,y0,length,width,gap,count,parallel_axis="x"):
    """[creates straight single line]

    [parallel_axis = "x"]
    p8 . . . . . . . . . . p11
     .        cp2     sl2   .
    p9 . . . . . . . . . . p10
                          
    p4 . . . . . . . . . . p7
     .        cp1     sl1   .  width
    p5 . . . . . . . . . . p6
                               gap
    p0 . . . . . . . . . . p3
     .        cp0     sl0  .  width
    p1 . . . . . . . . . . p2
              length

    [parallel_axis = "y"]
    p0 . . . p3    p4 . . . p7    p8 . . . p11 
    .         .    .         .    .         . 
    .  line0  .    .  line1  .    .  line2  . 
    .         .    .         .    .         . 
    p1 . . . p2    p5 . . . p6    p9 . . . p10 
        width   gap 

    Args:
        x0 ([float]): [bottom left x coordinate]
        y0 ([float]): [bottom left y coordinate]
        length ([float]): [length of single line]
        width ([float]): [width of single lines]
        gap ([type]): [gap between single lines]
        count ([type]): [count of loops of single line]
    """

    widths = [width for i in range(count)] # width list from bottom to top
    gaps = [gap for i in range(count-1)] # gap list from bottom to top
    points = straight_lines(x0,y0,length,widths,gaps,parallel_axis)
    return points

def bend_aligner_single_line(x0,y0,alignment_length,r1s,r2s,loops=5,sl_width=6,sl_gap=3):
    """[aligns the bends at pad transitions]
                      
                          . p5 . . . .  p9
                    .        .    2      .
                .         . p4 . . . .  p8    
             .   1   .     alignment_length 
           .     .                    . p1 r2
         .     .                  .      .
        .     .                .      . p0 r1
       .    .                .  0  .        
      .    .               .     . 
     .    .               .    .   
    p6 . p7              p2 . p3

    Args:
        x0 ([float]): [bottom left center x coordinate]
        y0 ([float]): [bottom left center y coordinate]
        alignment_length ([float]): [length difference of center of outer loop and inner loops]
        r1s ([float]): [inner radius counted from the most inner annular sectors]
        r2s ([float]): [outer radius counted from the most inner annular sectors]
        loops (float, optional): [number of loops]. Defaults to 5.
        sl_width (float, optional): [width of single line]. Defaults to 6.
        sl_gap (float, optional): [gap between single lines]. Defaults to 3.
    """
    points = [0 for i in range(2+4*loops)]
    # right annular sectors
    center_x, center_y = x0 + r2s[loops-1] + alignment_length, y0
    for i in range(loops-1): 
        points[4*i:4*(i+1)] = annular_sector(center_x,center_y,r1s[i],r2s[i],pi/2,pi)

    # left annular sector
    center_x, center_y = x0 + r2s[loops-1], y0
    points[4*(loops-1):4*loops] = annular_sector(center_x,center_y,r1s[loops-1],r2s[loops-1],pi/2,pi) 

    points[4] = x0 + r2s[loops-1], y0 + r1s[loops-1]
    x,y = alignment_length, r2s[loops-1]-r1s[loops-1]
    points[5], points[4], points[8], points[9] = square(points[4][0],points[4][1],x,y,xy0_position="bottom_left")

    return points

def pad_single_line(x0,y0,pad_width=50,pad_gap=50):
    """[pad for single line]

       width    gap      
    p4 . . . p7    p8 . . . p11   p12 . . .p14 
    .         .    .         .    .         . 
    .    1    .    .    2    .    .    3    .
    .         .    p9 . . . p10   .         . 
    .         .                   .         .
    p0 . . . p6 . . . . . . . . . p13 . . . p3
    .                                       .
    .                   0                   .
    p1 . . . . . . . . . . . . . . . . . . p2

    Args:
        x0 ([float]): [bottom left x coordinate]
        y0 ([float]): [bottom left x coordinate]
        pad_width (float, optional): [width of pad]. Defaults to 50.
        pad_gap (float, optional): [gap between pads]. Defaults to 50.
    """

    points = [0 for i in range(15)]
    points[1]  = x0, y0
    x, y = pad_width + pad_gap + pad_width + pad_gap + pad_width, pad_width
    points[0:4] = square(points[1][0],points[1][1],x,y,xy0_position="bottom_left")

    points[0]  = x0, y0 + pad_width
    x, y = pad_width, pad_width + pad_gap
    points[4], points[0], points[6], points[7] = square(points[0][0],points[0][1],x,y,xy0_position="bottom_left")

    points[9]  = x0 + pad_width + pad_gap, y0 + pad_width + pad_gap
    x, y = pad_width, pad_width
    points[8:12] = square(points[9][0],points[9][1],x,y,xy0_position="bottom_left")

    points[13] = x0 + pad_width + pad_gap + pad_width + pad_gap, y0 + pad_width
    x, y = pad_width, pad_width + pad_gap
    points[12], points[13], points[3], points[14] = square(points[13][0],points[13][1],x,y,xy0_position="bottom_left")

    return points

def pad_changeable_length(x0,y0,pad_width=80,pad_length=200,pad_gap=20,short_width=100,layer=None):
    """[pad with changeable length]

       width    gap      
    p4 . . . p7    p8 . . . p11   p12 . . .p14 
    .         .    .         .    .         .  
    .    1    .    .    2    .    .    3    .  length
    .         .    .         .    .         .
    .         .    p9 . . . p10   .         . 
    .         .                   .         .
    p0 . . . p6 . . . . . . . . . p13 . . . p3
    .                                       .  short_width
    .                   0                   .
    p1 . . . . . . . . . . . . . . . . . . p2

    Args:
        x0 ([float]): [bottom left x coordinate]
        y0 ([float]): [bottom left x coordinate]
        pad_width (float, optional): [width of pad]. Defaults to 80.
        pad_length (float, optional): [length of pad]. Defaults to 200.
        pad_gap (float, optional): [gap between pads]. Defaults to 20.
        short_width (float, optional): [width of short section]. Defaults to 100.
    """

    points = [0 for i in range(15)]
    points[1]  = x0, y0
    x, y = pad_width + pad_gap + pad_width + pad_gap + pad_width, short_width
    points[0:4] = square(points[1][0],points[1][1],x,y,xy0_position="bottom_left",layer=layer)

    points[0]  = x0, y0 + short_width
    x, y = pad_width, pad_length + pad_gap
    points[4], points[0], points[6], points[7] = square(points[0][0],points[0][1],x,y,xy0_position="bottom_left",layer=layer)

    points[9]  = x0 + pad_width + pad_gap, y0 + short_width + pad_gap
    x, y = pad_width, pad_length
    points[8:12] = square(points[9][0],points[9][1],x,y,xy0_position="bottom_left",layer=layer)

    points[13] = x0 + pad_width + pad_gap + pad_width + pad_gap, y0 + short_width
    x, y = pad_width, pad_length + pad_gap
    points[12], points[13], points[3], points[14] = square(points[13][0],points[13][1],x,y,xy0_position="bottom_left",layer=layer)

    return points

def tapers_single_line(x0,y0,height,pad_width,pad_gap,sl_width,sl_gap,parallel_axis="x",layer=None):
    """[creates tapers API]

    [parallel_axis = "x"]
      sl_width sl_gap
     p0 . . p3      p4 . . p7  
     .       .      .       .   
    .  line0  .    .  line1  . height
    .         .    .         .  
    p1 . . . p2    p5 . . . p6  
    pad_width pad_gap

    [parallel_axis = "y"] 
        p4 . . .             
        .       . . p7
    pad .  line1     . sl_width
    width.      . . p6
        p5 . . .        sl_gap
    gap
        p0 . . .             
        .       . . p3
        .  line0     . 
        .       . . p2
        p1 . . .        
           height

    Args:
        x0 ([float]): [bottom left x coordinate]
        y0 ([float]): [bottom left y coordinate]
        height ([float]): [height of trapezoids]
        pad_width ([float]): [width of pads]
        pad_gap ([float]): [gap between pads]
        sl_width ([float]): [width of single line]
        sl_gap ([float]): [gap between single lines]
        parallel_axis (str, optional): [defines whether x or y sides are parallel]. Defaults to "x".
    """
    
    widths = [sl_width, pad_width]
    offset = 0
    points = [0 for i in range(8)]
    if parallel_axis == "x":
        points[0:4] = trapezoid(x0,y0,widths,offset,height,xy0_position="bottom_left",parallel_axis="x",layer=layer)
        points[4:8] = trapezoid(x0+pad_width+pad_gap,y0,widths,offset,height,xy0_position="bottom_left",parallel_axis="x",layer=layer)
    elif parallel_axis == "y":
        points[0:4] = trapezoid(x0,y0,widths,offset,height,xy0_position="bottom_left",parallel_axis="y",layer=layer)
        points[4:8] = trapezoid(x0,y0+pad_width+pad_gap,widths,offset,height,xy0_position="bottom_left",parallel_axis="y",layer=layer)

    return points

def bend_single_line_2(x0,y0,r1s,r2s,sl_width,sl_gap,angle1,angle2):
    """[creates bent single line (type2: most inner is NOT circular_sector)]

        r1     r2   
        p3 . . p2   p7 . p6  p11 . p10  angle2
    p0 .      .     .    .    .    .
     .       .     .    .    .    .
     .    .      .     .   .    .
    p1 .      .      .   .    .
           .      .    .    .
    p4 .       .    .     .
     .     .     .     .
    p5 .      .      .
           .      .
    p8 .       .
     .     .
    p9 .  angle1

    Args:
        x0 ([float]): [bottom left x coordinate]
        y0 ([float]): [bottom left y coordinate]
        r1s ([float]): [inner radii of the annular sectors]
        r2s ([float]): [outer radii of the annular sectors]
        sl_width ([float]): [width of single line]
        sl_gap ([float]): [gap between single lines]
        angle1 ([float]): [angle 1 of the arcs]
        angle2 ([float]): [angle 2 of the arcs]
    """
    points = bend_2(x0,y0,r1s,r2s,angle1,angle2)
    return points

# coplanars

def coplanar_1(x0,y0,pad_length=80,pad_width=80,pad_gap=20,taper_length=50,gnd_width=50,sig_width=13.6,sig_gnd_gap=6,straight_length=100,overlap1=20,overlap2=20,termination_length=42.8):
    """[coplanar waveguide: type1 with 90 deg bend. 3pin terminal resistor]

    Args:
        x0 ([float]): [bottom left x coordinate of pad]
        y0 ([float]): [bottom left y coordinate of pad]
        pad_length (int, optional): [length of pad]. Defaults to 80.
        pad_width (int, optional): [width of pad]. Defaults to 80.
        pad_gap (int, optional): [gap between pads]. Defaults to 20.
        taper_length (int, optional): [length of pads]. Defaults to 50.
        gnd_width (int, optional): [gnd line width]. Defaults to 50.
        sig_width (float, optional): [signal line widths]. Defaults to 13.6.
        sig_gnd_gap (int, optional): [gap between signal and gnd lines]. Defaults to 6.
        straight_length (int, optional): [length of straight waveguides]. Defaults to 100.
        overlap1 (int, optional): [length of overlap between sig and gnd lines at left side]. Defaults to 20.
        overlap2 (int, optional): [length of overlap between sig and gnd lines at right side]. Defaults to 20.
        termination_length (float, optional): [length of termination line]. Defaults to 42.8.
    """
    all_points = {}    
    points = pads_1(x0,y0,pad_length,pad_width,pad_gap,parallel_axis="y")
    all_points["pads_0"] = points
    # top left -> bottom center
    x0 = (points[0][0]+points[11][0])/2
    y0 = (points[0][1]+points[11][1])/2
    points = coplanar_tapers_1(x0,y0,taper_length,pad_width,pad_gap,gnd_width,sig_width,sig_gnd_gap,parallel_axis="x")
    all_points["coplanar_tapers_0"] = points
    x0, y0 = points[11] # top right -> center of arc
    points = bend_coplanar_1(x0,y0,gnd_width,sig_width,sig_gnd_gap,pi/2,pi)
    all_points["bend_coplanar_0"] = points
    x0, y0 = points[0] # center of arc -> bottom left
    points = straight_coplanar(x0,y0,straight_length,gnd_width,sig_width,sig_gnd_gap,parallel_axis="x")
    all_points["straight_coplanar_0"] = points
    x0, y0 = points[2] # bottom right -> bottom left
    points = termination_coplanar(x0,y0,gnd_width,sig_width,sig_gnd_gap,overlap1,overlap2,termination_length,parallel_axis="x")
    all_points["termination_coplanar_0"] = points
    return all_points

# coplanar_2
def coplanar_2(x0,y0,pad_length=80,pad_width=80,pad_gap=20,taper_length=50,gnd_width=50,sig_width=13.6,sig_gnd_gap=6,straight_length=1000,overlap1=20,overlap2=20,termination_length=42.8):
    """[coplanar waveguide: type2 with 3x90 deg bend to locate pad and termination at the same y level. 3pin terminal resistor]

    Args:
        x0 ([float]): [bottom left x coordinate of pad]
        y0 ([float]): [bottom left y coordinate of pad]
        pad_length (int, optional): [length of pad]. Defaults to 80.
        pad_width (int, optional): [width of pad]. Defaults to 80.
        pad_gap (int, optional): [gap between pads]. Defaults to 20.
        taper_length (int, optional): [length of pads]. Defaults to 50.
        gnd_width (int, optional): [gnd line width]. Defaults to 50.
        sig_width (float, optional): [signal line widths]. Defaults to 13.6.
        sig_gnd_gap (int, optional): [gap between signal and gnd lines]. Defaults to 6.
        straight_length (int, optional): [length of straight waveguides]. Defaults to 100.
        overlap1 (int, optional): [length of overlap between sig and gnd lines at left side]. Defaults to 20.
        overlap2 (int, optional): [length of overlap between sig and gnd lines at right side]. Defaults to 20.
        termination_length (float, optional): [length of termination line]. Defaults to 42.8.
    """
    all_points = {}    
    points = pads_1(x0,y0,pad_length,pad_width,pad_gap,parallel_axis="y")
    all_points["pads_0"] = points
    # top left -> bottom center
    x0 = (points[0][0]+points[11][0])/2
    y0 = (points[0][1]+points[11][1])/2
    points = coplanar_tapers_1(x0,y0,taper_length,pad_width,pad_gap,gnd_width,sig_width,sig_gnd_gap,parallel_axis="x")
    all_points["coplanar_tapers_0"] = points
    x0, y0 = points[11] # top right -> center of arc
    points = bend_coplanar_1(x0,y0,gnd_width,sig_width,sig_gnd_gap,pi/2,pi)
    all_points["bend_coplanar_0"] = points
    x0, y0 = points[0] # center of arc -> bottom left
    length = 100
    points = straight_coplanar(x0,y0,length,gnd_width,sig_width,sig_gnd_gap,parallel_axis="x")
    all_points["straight_coplanar_0"] = points
    x0, y0 = points[2] # bottom right -> center of arc
    points = bend_coplanar_1(x0,y0,gnd_width,sig_width,sig_gnd_gap,0,pi/2)
    all_points["bend_coplanar_1"] = points
    x0, y0 = points[0] # center of arc -> top left
    length = (pad_length/2+taper_length)-(gnd_width+sig_gnd_gap+sig_width/2) # for aligning pad center and terminal resistance in y direction
    y0 = y0-length # top left -> bottom left
    points = straight_coplanar(x0,y0,length,gnd_width,sig_width,sig_gnd_gap,parallel_axis="y")
    all_points["straight_coplanar_1"] = points
    x0, y0 = points[10] # bottom right -> center of arc
    points = bend_coplanar_1(x0,y0,gnd_width,sig_width,sig_gnd_gap,pi,pi*3/2)
    all_points["bend_coplanar_2"] = points
    x0, y0 = points[9] # center of arc -> top left
    y0 = y0 # bottom left
    points = straight_coplanar(x0,y0,straight_length,gnd_width,sig_width,sig_gnd_gap,parallel_axis="x")
    all_points["straight_coplanar_2"] = points
    x0, y0 = points[2] # bottom right -> bottom left
    points = termination_coplanar(x0,y0,gnd_width,sig_width,sig_gnd_gap,overlap1,overlap2,termination_length,parallel_axis="x")
    all_points["termination_coplanar_0"] = points
    return all_points

def coplanar_3(x0,y0,pad_length=80,pad_width=80,pad_gap=20,taper_length=50,gnd_width=50,sig_width=13.6,sig_gnd_gap=6,straight_length_1=200,straight_length_2=100):
    """[coplanar waveguide: type3 5pin two arms]

    Args:
        x0 ([float]): [bottom left x coordinate of pad]
        y0 ([float]): [bottom left y coordinate of pad]
        pad_length (int, optional): [length of pad]. Defaults to 80.
        pad_width (int, optional): [width of pad]. Defaults to 80.
        pad_gap (int, optional): [gap between pads]. Defaults to 20.
        taper_length (int, optional): [length of pads]. Defaults to 50.
        gnd_width (int, optional): [gnd line width]. Defaults to 50.
        sig_width (float, optional): [signal line widths]. Defaults to 13.6.
        sig_gnd_gap (int, optional): [gap between signal and gnd lines]. Defaults to 6.
        straight_length_1 (int, optional): [length of x direction straight waveguides]. Defaults to 200.
        straight_length_2 (int, optional): [length of y direction straight waveguides]. Defaults to 100.
        overlap1 (int, optional): [length of overlap between sig and gnd lines at left side]. Defaults to 20.
        overlap2 (int, optional): [length of overlap between sig and gnd lines at right side]. Defaults to 20.
        termination_length (float, optional): [length of termination line]. Defaults to 42.8.
    """
    all_points = {}    
    # pad
    points = pads_2(x0,y0,pad_length,pad_width,pad_gap,parallel_axis="y")
    all_points["pads_0"] = points
    # taper
    x0 = (points[8][0]+points[11][0])/2 # top center of center pad 
    y0 = (points[8][1]+points[11][1])/2 # top center of center pad 
    points = coplanar_tapers_2(x0,y0,taper_length,pad_width,pad_gap,gnd_width,sig_width,sig_gnd_gap,parallel_axis="x")
    all_points["coplanar_tapers_0"] = points

    # bottom left bend
    x0, y0 = points[19] # top right -> center of arc
    points = bend_coplanar_3(x0,y0,gnd_width,sig_width,sig_gnd_gap,pi/2,pi)
    all_points["bend_coplanar_0"] = points

    # bottom straight coplanar
    x0, y0 = points[0] # center of arc -> bottom left
    points = straight_coplanar(x0,y0,straight_length_1,gnd_width,sig_width,sig_gnd_gap,parallel_axis="x")
    all_points["straight_coplanar_0"] = points

    # bottom right bend
    x0, y0 = points[11] # top right -> bottom left
    points = bend_coplanar_1(x0,y0,gnd_width,sig_width,sig_gnd_gap,pi*3/2,2*pi)
    all_points["bend_coplanar_1"] = points

    # right straight coplanar
    x0, y0 = points[0] # center of arc -> bottom left
    points = straight_coplanar(x0,y0,straight_length_2,gnd_width,sig_width,sig_gnd_gap,parallel_axis="y")
    all_points["straight_coplanar_1"] = points
    
    # bottom right bend
    x0, y0 = points[0] # top left -> center of arc
    points = bend_coplanar_1(x0,y0,gnd_width,sig_width,sig_gnd_gap,0,pi/2)
    all_points["bend_coplanar_2"] = points

    # top straight coplanar
    x0, y0 = points[0] # center of arc -> bottom right
    straight_length_3 = straight_length_1 + (sig_gnd_gap + sig_width + sig_gnd_gap + gnd_width)
    x0 = x0 - straight_length_3 # bottom right -> bottom left
    points = straight_coplanar(x0,y0,straight_length_3,gnd_width,sig_width,sig_gnd_gap,parallel_axis="x")
    all_points["straight_coplanar_2"] = points

    # top left bend
    x0, y0 = points[1] # bottom left -> center of arc
    points = bend_coplanar_1(x0,y0,gnd_width,sig_width,sig_gnd_gap,pi/2,pi)
    all_points["bend_coplanar_3"] = points

    # right straight coplanar
    x0, y0 = points[0] # center of arc -> top right
    x0 = x0 - (gnd_width + sig_gnd_gap + sig_width + sig_gnd_gap + gnd_width) # right -> left
    y0 = y0 - straight_length_2 # top -> bottom
    points = straight_coplanar(x0,y0,straight_length_2,gnd_width,sig_width,sig_gnd_gap,parallel_axis="y")
    all_points["straight_coplanar_3"] = points

    straight_length_5 = (gnd_width + sig_gnd_gap + sig_width + sig_gnd_gap + gnd_width)
    # left gnd
    x0,y0 = all_points["coplanar_tapers_0"][0] # top left of gnd -> bottom left
    points = square(x0,y0,gnd_width,straight_length_5,xy0_position="bottom_left")
    all_points["square_0"] = points

    # left sig
    x0,y0 = all_points["coplanar_tapers_0"][4] # top left of sig -> bottom left
    points = square(x0,y0,sig_width,straight_length_5,xy0_position="bottom_left")
    all_points["square_1"] = points

    # check alignment
    x1,y1 = all_points["square_0"][0]
    x2,y2 = all_points["straight_coplanar_3"][1]
    assert (x1-x2)**2 + (y1-y2)**2 < 0.01, f"coplanar alignment error: error={(x1-x2)**2 + (y1-y2)**2}" # notify if too much misalignment 

    return all_points

def coplanar_4(x0,y0,pad_length=80,pad_width=80,pad_gap=20,taper_length=50,gnd_width=50,sig_width=13.6,sig_gnd_gap=6,straight_length_1=200,straight_length_2=100,extra_width=100):
    """[coplanar waveguide: type4 5pin two arms with better tapers]

    Args:
        x0 ([float]): [bottom left x coordinate of pad]
        y0 ([float]): [bottom left y coordinate of pad]
        pad_length (int, optional): [length of pad]. Defaults to 80.
        pad_width (int, optional): [width of pad]. Defaults to 80.
        pad_gap (int, optional): [gap between pads]. Defaults to 20.
        taper_length (int, optional): [length of pads]. Defaults to 50.
        gnd_width (int, optional): [gnd line width]. Defaults to 50.
        sig_width (float, optional): [signal line widths]. Defaults to 13.6.
        sig_gnd_gap (int, optional): [gap between signal and gnd lines]. Defaults to 6.
        straight_length_1 (int, optional): [length of x direction straight waveguides]. Defaults to 200.
        straight_length_2 (int, optional): [length of y direction straight waveguides]. Defaults to 100.
        overlap1 (int, optional): [length of overlap between sig and gnd lines at left side]. Defaults to 20.
        overlap2 (int, optional): [length of overlap between sig and gnd lines at right side]. Defaults to 20.
        termination_length (float, optional): [length of termination line]. Defaults to 42.8.
        extra_width (float, optional): [extra width to add to gnd line taper]. Defaults to 100.
    """
    all_points = {}    
    # pad
    points = pads_2(x0,y0,pad_length,pad_width,pad_gap,parallel_axis="y")
    all_points["pads_0"] = points
    # taper
    x0 = (points[8][0]+points[11][0])/2 # top center of center pad 
    y0 = (points[8][1]+points[11][1])/2 # top center of center pad
    height = taper_length
    width1s = [gnd_width, sig_width, gnd_width+extra_width, sig_width, gnd_width]
    gap1s = [sig_gnd_gap, sig_gnd_gap, sig_gnd_gap, sig_gnd_gap]
    width2s = [pad_width, pad_width, pad_width, pad_width, pad_width]
    gap2s = [pad_gap, pad_gap, pad_gap, pad_gap]
    points = tapers(x0,y0,height,width1s,gap1s,width2s,gap2s,parallel_axis="x")
    all_points["tapers_0"] = points

    # bottom left bend
    x0, y0 = points[19] # top right -> center of arc
    points = bend_coplanar_4(x0,y0,gnd_width,sig_width,sig_gnd_gap,pi/2,pi)
    all_points["bend_coplanar_0"] = points

    # bottom straight coplanar
    x0, y0 = points[0] # center of arc -> bottom left
    points = straight_coplanar(x0,y0,straight_length_1,gnd_width,sig_width,sig_gnd_gap,parallel_axis="x")
    all_points["straight_coplanar_0"] = points

    # bottom right bend
    x0, y0 = points[11] # top right -> bottom left
    points = bend_coplanar_1(x0,y0,gnd_width,sig_width,sig_gnd_gap,pi*3/2,2*pi)
    all_points["bend_coplanar_1"] = points

    # right straight coplanar
    x0, y0 = points[0] # center of arc -> bottom left
    points = straight_coplanar(x0,y0,straight_length_2,gnd_width,sig_width,sig_gnd_gap,parallel_axis="y")
    all_points["straight_coplanar_1"] = points
    
    # bottom right bend
    x0, y0 = points[0] # top left -> center of arc
    points = bend_coplanar_1(x0,y0,gnd_width,sig_width,sig_gnd_gap,0,pi/2)
    all_points["bend_coplanar_2"] = points

    # top straight coplanar
    x0, y0 = points[0] # center of arc -> bottom right
    straight_length_3 = straight_length_1 + (sig_gnd_gap + sig_width + sig_gnd_gap + gnd_width + extra_width)
    x0 = x0 - straight_length_3 # bottom right -> bottom left
    points = straight_coplanar(x0,y0,straight_length_3,gnd_width,sig_width,sig_gnd_gap,parallel_axis="x")
    all_points["straight_coplanar_2"] = points

    # top left bend
    x0, y0 = points[1] # bottom left -> center of arc
    points = bend_coplanar_1(x0,y0,gnd_width,sig_width,sig_gnd_gap,pi/2,pi)
    all_points["bend_coplanar_3"] = points

    straight_length_5 = straight_length_2 + (gnd_width + sig_gnd_gap + sig_width + sig_gnd_gap + gnd_width)
    # left gnd,sig,gnd
    x0, y0 = points[9] # bottom left -> top left
    y0 = y0 - straight_length_5
    points = straight_coplanar(x0,y0,straight_length_5,gnd_width,sig_width,sig_gnd_gap,parallel_axis="y")
    all_points["straight_coplanar_3"] = points

    length = (gnd_width + sig_gnd_gap + sig_width + sig_gnd_gap + gnd_width)
    # fill extra width with square
    x0, y0 = all_points["tapers_0"][11] # top right -> bottom right
    points = square(x0,y0,extra_width,length,xy0_position="bottom_right")
    all_points["square_0"] = points

    # check alignment
    x1,y1 = all_points["straight_coplanar_3"][0]
    x2,y2 = all_points["bend_coplanar_3"][9]
    assert (x1-x2)**2 + (y1-y2)**2 < 0.01, f"coplanar alignment error: error={(x1-x2)**2 + (y1-y2)**2}" # notify if too much misalignment 

    return all_points


def dc_pad_1(all_points,pad_width=80,pad_gap=20,taper_length=50):
    # 3 pin pad for dc input (center pad is signal 1, outer pads are connected and are signal 2)
    x0,y0 = all_points["pads_0"][9] # center gnd bottom left -> top? left
    y0 = y0 - taper_length - pad_width - pad_gap - pad_width # top? -> bottom
    points = pad_single_line(x0,y0,pad_width=pad_width,pad_gap=pad_gap)
    all_points["pad_single_line_0"] = points

    # taper for connecting left signal
    x0,y0 = points[4] # top left -> bottom left
    widths = [pad_width, pad_width] # top and bottom
    offset = -(pad_width + pad_gap)
    height = taper_length
    points = trapezoid(x0,y0,widths,offset,height,xy0_position="bottom_left",parallel_axis="x")
    all_points["trapezoid_0"] = points
    
    # taper for connecting right signal
    x0,y0 = all_points["pad_single_line_0"][8] # top left -> bottom left
    points = square(x0,y0,pad_width,taper_length,xy0_position="bottom_left")
    all_points["square_2"] = points

    return all_points

def dc_pad_2(all_points,pad_width=80,pad_gap=20,taper_length=50):
    # 3 pin pad for dc input (center pad is signal 1, outer pads are connected and are signal 2)
    x0,y0 = all_points["pads_0"][1] # bottom left -> top? left
    y0 = y0 - taper_length - pad_width - pad_gap - pad_width # top? -> bottom
    points = pad_single_line(x0,y0,pad_width=pad_width,pad_gap=pad_gap)
    all_points["pad_single_line_0"] = points

    # taper for connecting right signal
    x0,y0 = points[12] # top left -> bottom left
    widths = [pad_width, pad_width] # top and bottom
    offset = (pad_width + pad_gap)
    height = taper_length
    points = trapezoid(x0,y0,widths,offset,height,xy0_position="bottom_left",parallel_axis="x")
    all_points["trapezoid_0"] = points
    
    # taper for connecting left signal
    x0,y0 = all_points["pad_single_line_0"][8] # top left -> bottom left
    points = square(x0,y0,pad_width,taper_length,xy0_position="bottom_left")
    all_points["square_2"] = points

    return all_points

def dc_pad_3(all_points,pad_width=80,pad_gap=20,taper_length=50):
    # 3 pin pad for dc input (center pad is signal 1, outer pads are connected and are signal 2: more compact than type 2)
    x0,y0 = all_points["pads_0"][1] # bottom left -> top? left
    y0 = y0 - (pad_gap + pad_width + pad_gap + pad_width) # top? -> bottom
    points = pad_single_line(x0,y0,pad_width=pad_width,pad_gap=pad_gap)
    all_points["pad_single_line_0"] = points

    # taper for connecting left signal
    x0,y0 = all_points["pad_single_line_0"][8] # top left -> bottom left
    points = square(x0,y0,pad_width,taper_length,xy0_position="bottom_left")
    all_points["square_2"] = points

    # taper for connecting right signal
    # taper 1
    x0,y0 = all_points["pads_0"][13] # bottom left -> top left
    points = square(x0,y0,pad_width,pad_gap,xy0_position="top_left")
    all_points["square_3"] = points
    # taper 2
    x0,y0 = all_points["pad_single_line_0"][14] # top left -> bottom left
    points = square(x0,y0,pad_width+pad_gap,pad_width,xy0_position="top_left")
    all_points["square_4"] = points    

    return all_points

def dc_pad_4(all_points,pad_width=80,pad_gap=20,taper_length=50):
    # 3 pin pad for dc input (center pad is signal 1, outer pads are connected and are signal 2: more compact than type 3)
    x0,y0 = all_points["pads_0"][1] # bottom left -> top? left
    y0 = y0 - (pad_gap + pad_width + pad_gap + pad_width) # top? -> bottom
    points = pad_single_line(x0,y0,pad_width=pad_width,pad_gap=pad_gap)
    all_points["pad_single_line_0"] = points

    # taper for connecting left signal
    x0,y0 = all_points["pad_single_line_0"][8] # top left -> bottom left
    points = square(x0,y0,pad_width,taper_length,xy0_position="bottom_left")
    all_points["square_2"] = points

    # taper for connecting right signal
    # taper 1
    x0,y0 = all_points["pads_0"][13] # bottom left -> top left
    points = square(x0,y0,pad_width,pad_gap,xy0_position="top_left")
    all_points["square_3"] = points
    # taper 2
    x0,y0 = all_points["pad_single_line_0"][14] # top left -> bottom left
    points = triangle(x0,y0,pad_width,pad_width+pad_gap,pi*3/2,pi*2)
    all_points["triangle_0"] = points    

    return all_points

def coplanar_2_magnet(x0,y0,magnet_x=12,magnet_y=12,magnet_gap=6,offset1=10,offset2=5,magnet_layer=None):
    """[coplanar waveguide with magnet array]

    Args:
        x0 ([float]): [bottom left x coordinate of pad]
        y0 ([float]): [bottom left y coordinate of pad]
        magnet_x ([float]): [magnet x length]
        magnet_y ([float]): [magnet y length]
        magnet_gap ([float]): [gap in x direction between magnets]
        offset1 (int, optional): [offset in x direction of magnet from signal line edge]. Defaults to 10.
        offset2 (int, optional): [offset in x direction of magnet from termination resistior edge]. Defaults to 5.
    """
    sig_width = 13.6
    length = 100
    termination_length = 42.8
    all_points = coplanar_2(x0,y0,straight_length=length,termination_length=termination_length)
    offset_y = (sig_width - magnet_y)/2
    # signal line magnet
    x1, y1 = all_points["straight_coplanar_2"][5] # get bottom left of signal line
    x1 = x1 + offset1 # left offset
    y1 = y1 + offset_y # y offset from bottom
    N = int((length-2*offset1+magnet_gap)/(magnet_x+magnet_gap))
    widths = [magnet_x for i in range(N)]
    gaps = [magnet_gap for i in range(N-1)]
    points = straight_lines(x1,y1,magnet_y,widths,gaps,parallel_axis="y",layer=magnet_layer)
    all_points["signal_magnet"] = points
    # termination magnet
    x1, y1 = all_points["termination_coplanar_0"][6] # get bottom left of termination resistor
    x1 = x1 + offset2 # left offset
    y1 = y1 + offset_y # y offset from bottom
    N = int((termination_length-2*offset2+magnet_gap)/(magnet_x+magnet_gap))
    widths = [magnet_x for i in range(N)]
    gaps = [magnet_gap for i in range(N-1)]
    points = straight_lines(x1,y1,magnet_y,widths,gaps,parallel_axis="y",layer=magnet_layer)
    all_points["termination_magnet"] = points
    return all_points

def circular_polyline(x0, y0, points, layer=None):
    """[create polyline consisting of arcs]

    Args:
        x0 ([float]): [x coordinate of starting point]
        y0 ([float]): [y coordinate of starting point]
        points ([list]): [list of points(x,y,r,angle1,angle2)]
        layer (str, optional): [definers the layer of the square]. Defaults to None

    Returns:
        [2d list]: [list of x,y coordinates]
    """
    # assertions
    check_data_type(x0, "x0", [int, float])
    check_data_type(y0, "y0", [int, float])
    for x,y,r,angle1,angle2 in points:
        check_data_type(x, "x", [int, float])
        check_data_type(y, "y", [int, float])
        check_data_type(r, "r", [int, float])
        check_data_type(angle1, "angle1", [int, float])
        check_data_type(angle2, "angle2", [int, float])
        check_data_type(layer, "layer", [str, None])

    polyline_points = []
    for count, (x,y,r,angle1,angle2) in enumerate(points):
        polyline_points.append([x0 + x + r*cos(angle1), y0 + y + r*sin(angle1)])
    polyline_obj = polyline(polyline_points, layer)
    for count, (x,y,r,angle1,angle2) in enumerate(points):
        polyline_obj.SetBulge(count, calculate_bulge(angle2 - angle1))
    return points
