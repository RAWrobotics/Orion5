import time
import math
import random

import orion5
from orion5 import orion5_math


OUTER_RADIUS = 275.0
GRAB_BLOCK_RADIUS = 200.0
LOCALISE_RADIUS = 210.0
TABLE_HEIGHT = 20.0
CLAW_OPENED = 300
CLAW_CLOSED = 160


orion_object = orion5.Orion5()


def get_estop(orion):
    return bool(orion.getVar(0, 'readConfig', 'Estop'))


def set_estop(orion, state):

    if state:
        state = 1
    else:
        state = 0

    return orion.setVar(0, 'setConfig', 'Estop', state)


def arrived(desired, actual, threshold):
    """
    returns True if the largest element-wise difference
    between desired and actual is less than threshold, False otherwise

    desired and actual should be lists of joint angles in degrees
    """
    diff = orion5_math.absdiff(desired, actual)
    diff[2] *= 0.75
    diff[0] = abs((diff[0] + 180) % 360 - 180)
    return max(diff) < threshold


def test_chance(chance):
    """
    returns True with chance probability, False otherwise
    """
    return random.random() < chance


def get_random_start(spacing, last_gap):

    while True:
        start = random.randrange(0, 360, spacing)

        if start != last_gap:
            return start


def move_to_position(orion, joints, threshold=10.0):
    """
    move to a position defined by a list of joint angles
    [turret, shoulder, elbow, wrist, claw]

    returns current position after move
    """

    # wait until we arrive at position
    while not arrived(joints, orion.getAllJointsPosition(), threshold):
        orion.setAllJointsPosition(joints)
        time.sleep(0.05)

    return orion.getAllJointsPosition()

def move_to_pose(orion, pose, threshold=10.0):
    """
    move to a pose defined by a list of toolpoint pose
    [radius, theta, height, attack, claw]

    returns current position after move
    """

    # calculate inverse kinematics, to get joint angles from pose
    joints = orion5_math.ikinematics(*pose)

    return move_to_position(orion, joints, threshold)


def do_waka_waka(orion):
    joints = orion_object.getAllJointsPosition()

    wak_frequency = 30
    theta_start = joints[0]
    theta_change = random.randrange(90, 360, wak_frequency)
    theta_change *= random.choice([-1, 1])
    attack_change = random.randint(5, 30)

    waka_waka(orion_object, theta_start, theta_change, attack_change, wak_frequency)


def waka_waka(orion, theta_start, theta_change, attack_range, wak_frequency=15.0):
    """
    do the waka waka zig zag camera scan thing

    theta_start is the theta (turret rotation) position to start in
    theta_change is the angular range of the waka waka (can be +ve or -ve to set the direction)
    attack_range is the +ve and -ve motion of the wrist during a waka, should be +ve
    wak_frequency is the theta movement between each waka
    """

    print(f'doing waka - ts: {theta_start}, tc: {theta_change}, ar: {attack_range}')

    num_waks = int(abs(theta_change // wak_frequency))
    wak_frequency = math.copysign(wak_frequency, theta_change)

    # get the current position, to maintain the claw position
    joints = orion.getAllJointsPosition()

    # move to the starting position, attack angle 0
    position = orion5_math.ikinematics(180, theta_start, 300, 0, joints[4])
    joints = move_to_position(orion, position)

    sign = 1.5
    for i in range(num_waks):
        # change the turret position by +- wak_frequency
        position[0] = orion5_math.wrap360f(position[0] + wak_frequency)

        # change the wrist angle by attack_range, alternating the sign each itteration
        position[3] = joints[3] + sign * attack_range

        if sign > 0:
            sign = -0.75
        else:
            sign = 1.5

        move_to_position(orion, position, threshold=15.0)


def pickup(orion, start_theta):

    start_theta = float(start_theta)

    print(f'doing pickup - pos: {start_theta}')

    path = [
        [180.0, start_theta, 150.0, -30.0, CLAW_OPENED], # hover
        [250.0, start_theta, 100.0, -90.0, CLAW_OPENED], # swoop in
        [OUTER_RADIUS, start_theta, TABLE_HEIGHT, -90.0, CLAW_OPENED], # down to table
        [GRAB_BLOCK_RADIUS, start_theta, TABLE_HEIGHT, -90.0, CLAW_OPENED], # slide over block
        [GRAB_BLOCK_RADIUS, start_theta, TABLE_HEIGHT, -90.0, CLAW_CLOSED], # close claw around block
        [250.0, start_theta, 100.0, -90.0, CLAW_CLOSED], # swoop out
        [180.0, start_theta, 150.0, -30.0, CLAW_CLOSED], # hover
    ]

    for pos in path:
        move_to_pose(orion, pos)
        time.sleep(0.5)

    return


def putdown(orion, end_theta):

    end_theta = float(end_theta)

    print(f'doing putdown - pos: {end_theta}')

    path = [
        [180.0, end_theta, 150.0, -30.0, CLAW_CLOSED], # hover
        [250.0, end_theta, 100.0, -90.0, CLAW_CLOSED], # swoop in
        [OUTER_RADIUS, end_theta, TABLE_HEIGHT, -90.0, CLAW_CLOSED], # down to table
        [GRAB_BLOCK_RADIUS, end_theta, TABLE_HEIGHT, -90.0, CLAW_CLOSED], # slide over block
        [GRAB_BLOCK_RADIUS, end_theta, TABLE_HEIGHT, -90.0, CLAW_OPENED], # close claw around block
        [OUTER_RADIUS, end_theta, TABLE_HEIGHT, -90.0, CLAW_CLOSED], # slide away from block
        [OUTER_RADIUS, end_theta, TABLE_HEIGHT, -90.0, 20.0], # close claw
        [LOCALISE_RADIUS, end_theta, TABLE_HEIGHT, -90.0, 20.0], # localise maneuver
        [OUTER_RADIUS, end_theta, TABLE_HEIGHT, -90.0, CLAW_CLOSED], # slide away from block
        [250.0, end_theta, 100.0, -90.0, CLAW_CLOSED], # swoop out
        [180.0, end_theta, 150.0, -30.0, CLAW_CLOSED], # hover
    ]

    for pos in path:
        move_to_pose(orion, pos)
        time.sleep(0.5)

    return


def feedme(orion, locations):

    for putdown_theta in locations:

        print(f'feedme - putdown: {putdown_theta}')

        # goto waiting position
        wait_for_block_pos = [last_gap, 90.0, 180.0, 180.0, CLAW_OPENED]
        move_to_position(orion, wait_for_block_pos, 5.0)

        # play 'feed me' soundbyte
        if play_audio:
            sd.play(audio, fs)

        set_estop(orion, True)

        # wait for estop to be turned off
        while get_estop(orion):
            time.sleep(0.1)
        # time.sleep(1)

        # stop the playback
        if play_audio:
            sd.stop()

        # close the claw and grab block
        wait_for_block_pos[4] = CLAW_CLOSED
        move_to_position(orion, wait_for_block_pos)

        # move the block to the position
        putdown(orion, putdown_theta)


# MAIN LOOP
spacing = 30.0
last_gap = 0.0
waka_chance = 0.33
play_audio = False
audio_filename = 'C:\\Users\\linds\\Documents\\RAWrobotics Orion5\\Example Code\\feed_me.wav'

if play_audio:
    import soundfile as sf
    import sounddevice as sd
    audio, fs = sf.read(audio_filename)

try:
    locations = list(range(int(spacing), 360, int(spacing)))
    random.shuffle(locations)
    feedme(orion_object, locations)

    while True:

        start = get_random_start(spacing, last_gap)
        pickup(orion_object, start)

        time.sleep(1)

        if test_chance(waka_chance):
            do_waka_waka(orion_object)

        time.sleep(1)

        putdown(orion_object, last_gap)
        last_gap = start

        if test_chance(waka_chance):
            do_waka_waka(orion_object)

        time.sleep(1)

except Exception as e:
    raise e

finally:
    orion_object.stop()
