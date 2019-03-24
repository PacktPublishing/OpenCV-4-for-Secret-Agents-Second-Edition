import math


def dist2D(p0, p1):
    deltaX = p1[0] - p0[0]
    deltaY = p1[1] - p0[1]
    return math.sqrt(deltaX * deltaX +
                     deltaY * deltaY)

def intersects(rect0, rect1):
    x0, y0, w0, h0 = rect0
    x1, y1, w1, h1 = rect1
    if x0 > x1 + w1: # rect0 is wholly to right of rect1
        return False
    if x1 > x0 + w0: # rect1 is wholly to right of rect0
        return False
    if y0 > y1 + h1: # rect0 is wholly below rect1
        return False
    if y1 > y0 + h0: # rect1 is wholly below rect0
        return False
    return True

def difference(rects0, rects1):
    result = []
    for rect0 in rects0:
        anyIntersects = False
        for rect1 in rects1:
            if intersects(rect0, rect1):
                anyIntersects = True
                break
        if not anyIntersects:
            result += [rect0]
    return result
