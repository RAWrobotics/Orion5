import math

def absdiff(a, b):
    """
    element-wise subtraction of lists
    """
    return [abs(c-d) for c, d in zip(a, b)]

def wrap180(angle):
    angle = (angle + 180) % 360
    if angle < 0:
        angle += 360
    return (angle - 180)

def wrap360(angle):
    if angle < 0:
        angle += 360
    elif angle > 360:
        angle -= 360
    return int(angle)

def wrap360f(angle):
    if angle < 0:
        angle += 360
    elif angle > 360:
        angle -= 360
    return angle

def pol2rect(r, t, boolean):
    if boolean:
        return r * math.cos(t * math.pi / 180.0) # x True
    else:
        return r * math.sin(t * math.pi / 180.0) # y False

def rect2pol(x, y, boolean):
    if boolean:
        return math.sqrt(x*x + y*y) # r True
    else:
        return math.atan2(y, x) * 180 / math.pi # Theta False

def RotateVector(TheSet, RotTemp):
    for iterator1 in range(len(RotTemp)):
        TheSet0 = TheSet[0]*RotTemp[iterator1][0][0]+TheSet[1]*RotTemp[iterator1][0][1]+TheSet[2]*RotTemp[iterator1][0][2]
        TheSet1 = TheSet[0]*RotTemp[iterator1][1][0]+TheSet[1]*RotTemp[iterator1][1][1]+TheSet[2]*RotTemp[iterator1][1][2]
        TheSet[2] = TheSet[0]*RotTemp[iterator1][2][0]+TheSet[1]*RotTemp[iterator1][2][1]+TheSet[2]*RotTemp[iterator1][2][2]
        TheSet[0] = TheSet0
        TheSet[1] = TheSet1

def DifferentialWrapped360(arg1, arg2):
    retValue = arg1-arg2
    if retValue > 180:
        retValue -= 360
    if retValue < -180:
        retValue +=360
    return retValue

def G15AngleTo360(g15Angle):
    return float(g15Angle) * 360.0 / 1088.0

def Deg360ToG15Angle(deg360):
    return int(deg360 * 1088.0 / 360.0)
