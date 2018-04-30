import math

bicepLength = 170.384
forearmLength = 136.307
wristLength = 85.25
shoulderXOffset = 30.309
shoulderZOffset = 53.0

def pol2rect(r, t):
    x = r * math.cos(t)
    y = r * math.sin(t)
    return x, y

def rect2pol(x, y):
    r = math.sqrt(x*x + y*y)
    t = math.atan2(y, x)
    return r, t

def wrap360(angle):
    if angle < 0:
        angle += 360.0
    elif angle > 360:
        angle -= 360.0
    return angle

def ikinematics(radius, theta, height, attackAngle, claw):
    # tool point in cylindrical coordinates
    toolPoint = [radius, theta, height]

    # find vector from tool point to wrist origin along angle of attack
    x, y = pol2rect(wristLength, math.radians(attackAngle - 180.0))
    wristPoint = [toolPoint[0] + x, toolPoint[2] + y]

    # find length of vector from shoulder origin to wrist point
    c, theta = rect2pol(wristPoint[0] - shoulderXOffset, wristPoint[1] - shoulderZOffset)
    theta = math.degrees(theta)

    # use cosine rule to solve shoulder and elbow joint angles
    a = forearmLength
    b = bicepLength
    
    if c >= (a+b) - 5:
        print('forearm + bicep over extended')
        c = a + b
    
    A = math.degrees(math.acos((b**2 + c**2 - a**2) / (2.0*b*c)))
    C = math.degrees(math.acos((a**2 + b**2 - c**2) / (2.0*a*b)))
    B = 180.0 - A - C

    # find joint angles relative to each joint
    joints = []
    joints.append(wrap360(toolPoint[1])) # base
    joints.append((A + theta) * 2.857) # shoulder
    joints.append(C) # elbow
    joints.append(wrap360(attackAngle + B + (180 - theta))) # wrist
    joints.append(claw) # claw
    
    return joints

if __name__ == '__main__':
    print(ikinematics(100, 0, 200, 270, 20))
    path = [
        [100, 100],
        [-100, 100],
        [-100, -100],
        [100, -100],
        [100, 100]
    ]

    path_index = 0

    point_interval = 20
    points = []

    for i in range(len(path) - 1):
        points.append(path[i])
        goal = path[i]
        dist = math.sqrt((goal[0] - points[-1][0])**2 + (goal[1] - points[-1][1])**2)
        
        for ii in range(int(dist/point_interval)):
            x, y = pol2rect(point_interval, math.atan2(goal[1] - points[-1][1], goal[0] - points[-1][0]))
            points.append([points[-1][0] + x, points[-1][1] + y])

    for i in range(len(points)):
        r, t = rect2pol(points[i][0], points[i][1])
        print(ikinematics(r, math.degrees(t), 20, 270, 20))
