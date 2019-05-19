import time
import orion5
from orion5 import orion5_math


# returns true if the element-wise difference between desired/actual is less than threshold
def arrived(desired, actual, threshold):
    diff = orion5_math.absdiff(joints, actual)
    diff[0] = abs((diff[0] + 180) % 360 - 180)
    return max(diff) < threshold


# 2d list that holds the sequence
# radius, theta, height, attack, claw
path = [
    [175, 0, 165, 290, 250],
    [175, 0, 80, 270, 250],
    [175, 0, 80, 270, 190],
    [175, 0, 165, 290, 190],
    [210, 270, 165, 290, 190],
    [210, 270, 80, 270, 190],
    [210, 270, 80, 270, 250],
    [210, 270, 165, 290, 250],
    [175, 0, 165, 290, 250],
    [175, 0, 50, 270, 250],
    [175, 0, 50, 270, 190],
    [175, 0, 165, 290, 190],
    [210, 270, 165, 290, 190],
    [210, 270, 110, 270, 190],
    [210, 270, 110, 270, 250],
    [210, 270, 165, 290, 250],
    [175, 0, 165, 290, 250],
    [175, 0, 50, 270, 80],
    [280, 0, 140, 348, 250],
]


arriveThreshold = 12
waitTime = 0.5
index = 0


# create Orion5 object
orion = orion5.Orion5()

for index in range(len(path)):

    joints = orion5_math.ikinematics(path[index][0], path[index][1], path[index][2], path[index][3], path[index][4])

    print("Moving to:", joints)

    # keep writing the desired position until we arrive
    while not arrived(joints, orion.getAllJointsPosition(), arriveThreshold):
        orion.setAllJointsPosition(joints)
        time.sleep(0.1)

    time.sleep(waitTime)

orion.stop()
