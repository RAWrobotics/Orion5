import time
import orion5
from orion5 import orion5_math

orion = orion5.Orion5()

time.sleep(1)

print('Connected')

def arrived(desired, actual):
    diff = orion5_math.absdiff(joints, actual)
    diff[0] = abs((diff[0] + 180) % 360 - 180)
    return max(diff) < arriveThreshold

path = [
    [  0,  90, 180, 180, 120],
    [ 90,  90, 180, 180, 120],
    [180,  90, 180, 180, 120],
    [270,  90, 180, 180, 120],
    [  0,  90, 180, 180, 120],
    [  0, 115, 160, 180, 120],
    [  0,  45, 225, 180, 120],
    [  0,   5, 270, 180, 120],
    [  0,  45, 225, 180, 120],
    [  0,  90, 180, 180, 120],
]

arriveThreshold = 30
waitTime = 2
pathIndex = 0

while True:

    joints = path[pathIndex]

    print("Moving to:", [int(e) for e in joints])

    while not arrived(joints, orion.getAllJointsPosition()):
        orion.setAllJointsPosition(joints)
        time.sleep(0.1)

    pathIndex += 1
    if pathIndex >= len(path):
        pathIndex = 0

orion.stop()

