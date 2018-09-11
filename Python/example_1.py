import time
import orion5
from orion5 import orion5_math

orion = orion5.Orion5()

time.sleep(2)

def arrived(desired, actual):
    diff = orion5_math.absdiff(joints, actual)
    diff[0] = abs((diff[0] + 180) % 360 - 180)
    return max(diff) < arriveThreshold

# radius, theta, height, attack, claw
path = [
    [175, 0, 200, 270, 250],
    [175, 0, 80, 270, 250],
    [175, 0, 80, 270, 190],
    [175, 0, 200, 270, 190],
    [210, 270, 200, 270, 190],
    [210, 270, 80, 270, 190],
    [210, 270, 80, 270, 250],
    [210, 270, 200, 270, 250],
    [175, 0, 200, 270, 250],
    [175, 0, 50, 270, 250],
    [175, 0, 50, 270, 190],
    [175, 0, 200, 270, 190],
    [210, 270, 200, 270, 190],
    [210, 270, 110, 270, 190],
    [210, 270, 110, 270, 250],
    [210, 270, 200, 270, 250],
    [175, 0, 200, 270, 250],
    [175, 0, 50, 270, 80],
    [280, 0, 140, 348, 250],
]

arriveThreshold = 12
waitTime = 2
pathIndex = 0

for pathIndex in range(len(path)):

    joints = orion5_math.ikinematics(*path[pathIndex])

    print("Moving to:", [int(e) for e in joints])

    while not arrived(joints, orion.getAllJointsPosition()):
        orion.setAllJointsPosition(joints)
        time.sleep(0.1)

    time.sleep(0.5)

orion.stop()
