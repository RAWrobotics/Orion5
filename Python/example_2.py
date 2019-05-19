import time
import orion5
from orion5 import orion5_math


# returns true if the element-wise difference between desired/actual is less than threshold
def arrived(desired, actual, threshold):
    diff = orion5_math.absdiff(joints, actual)
    diff[0] = abs((diff[0] + 180) % 360 - 180)
    return max(diff) < threshold


# 2d list that holds the sequence
# base, shoulder, elbow, wrist, claw
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


# variables
arriveThreshold = 10
waitTime = 0
index = 0


# create Orion5 object
orion = orion5.Orion5()


# main loop
while True:

    joints = path[index]

    print("Moving to:", joints)

    # keep writing the desired position until we arrive
    while not arrived(joints, orion.getAllJointsPosition(), arriveThreshold):
        orion.setAllJointsPosition(joints)
        time.sleep(0.1)

    # increment and wrap the current position within the sequence
    index += 1
    if index >= len(path):
        index = 0

    time.sleep(waitTime)

orion.stop()

