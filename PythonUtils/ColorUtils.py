import math


def hueFromBGR(color):
    b, g, r = color
    # Note: sqrt(3) = 1.7320508075688772
    hue = math.degrees(math.atan2(
        1.7320508075688772 * (g - b), 2 * r - g - b))
    if hue < 0.0:
        hue += 360.0
    return hue

def saturationFromBGR(color):
    return max(color) - min(color)
