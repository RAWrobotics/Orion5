import time

import orion5
from orion5.utils.general import waitForOrion5Forever
from orion5.math import absdiff, wrap360, ikinematics

# program variables
arriveThreshold = 30
waitTime = 2

# load and parse path
# path = []
# with open('path.txt', 'r') as file:
#     for line in file:
#         path.append([wrap360(float(e)) for e in line.rstrip().split(',')])

# initialise Orion5 library
comport = waitForOrion5Forever()
orion = orion5.Orion5(comport)
time.sleep(3)

def arrived(desired, actual):
    diff = absdiff(joints, orion.getAllJointsPosition())
    diff[0] = abs((diff[0] + 180) % 360 - 180)
    return max(absdiff(joints, orion.getAllJointsPosition())) < arriveThreshold

# [radius, theta, height, attack, claw]
path = [
    [200, 0, 50, 300, 120, 1],
    [200, 0, 150, 300, 120, 1],
    [300, 0, 150, 300, 120, 1],
    [300, 0, 150, 0, 120, 1],
    [200, 0, 300, 0, 120, 1],
    [200, 0, 300, 0, 60, 1],
    [200, 0, 300, 0, 280, 1],
    [200, 0, 150, 0, 120, 1],
    [200, 0, 50, 300, 120, 0]
]

# main loop
try:

    for point in path:
        joints = ikinematics(point[0], point[1], point[2], point[3], point[4])

        print("Moving to:", point, "Joints:", [int(e) for e in joints])

        while not arrived(joints, orion.getAllJointsPosition()):
            orion.setAllJointsPosition(joints)
            time.sleep(0.25)

        if point[5]:
            time.sleep(waitTime)

except KeyboardInterrupt:
    print('Stopping...')
except Exception as e:
    print(e)
finally:
    orion.exit()
    print('Stopped')
