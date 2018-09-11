import time

import orion5
from orion5.orion5_math import Deg360ToG15Angle, wrap360, wrap1088
from orion5.utils.general import waitForOrion5Forever

names = ['base', 'shoulder', 'elbow', 'wrist', 'claw']

CLAW_INCREMENT = 5

def applyOffsets(o5, offsets):
    time.sleep(1)
    o5.setVariable('baseOffset', offsets[0])
    time.sleep(1)
    o5.setVariable('shoulderOffset', offsets[1])
    time.sleep(1)
    o5.setVariable('elbowOffset', offsets[2])
    time.sleep(1)
    o5.setVariable('wristOffset', offsets[3])
    time.sleep(1)
    o5.setVariable('clawOffset', offsets[4])
    time.sleep(1)

def gotoPositionBlocking(o5, pos):
    while abs(pos - o5.claw.getPosition()) > 2:
        o5.claw.setPosition(pos)
        print('%.2f' % o5.claw.getPosition())
        time.sleep(0.2)

def clawEject(o5):
    o5.claw.setVariable('misc variables', 'cwAngleLimit', 60)
    o5.claw.setVariable('misc variables', 'ccwAngleLimit', 1087)

    gotoPositionBlocking(o5, 359.0)

    o5.claw.setVariable('misc variables', 'cwAngleLimit', 1060)
    o5.claw.setVariable('misc variables', 'ccwAngleLimit', 1059)

    gotoPositionBlocking(o5, 170.0)

    o5.claw.setVariable('misc variables', 'cwAngleLimit', 0)
    o5.claw.setVariable('misc variables', 'ccwAngleLimit', 1087)

    gotoPositionBlocking(o5, 359.0)

    input('\nPress enter if claws are ejected\nCtrl+C and relaunch if claws are not ejected yet')

    o5.claw.setVariable('misc variables', 'cwAngleLimit', 1060)
    o5.claw.setVariable('misc variables', 'ccwAngleLimit', 1059)

    gotoPositionBlocking(o5, 135.0)

    input('\nPosition claws around pinion gear\n80mm between inner faces\n40mm from centre of gear to claw face\npress enter when ready')

    gotoPositionBlocking(o5, 355.0)

    o5.claw.setVariable('misc variables', 'cwAngleLimit', 0)
    o5.claw.setVariable('misc variables', 'ccwAngleLimit', 1087)

    gotoPositionBlocking(o5, 120.0)

print('Waiting for Orion5 to be connected')
comport = waitForOrion5Forever()
orion = orion5.Orion5(mode='standalone', serialName=comport, useSimulator=False)

time.sleep(5)

a = input('Would you like to zero the existing offsets? (recommended for recalibrations) y/n\n> ').lower()
if a == 'y':
    applyOffsets(orion, [0, 0, 0, 0, 0])

try:
    a = input('\nWould you like to eject claws? y/n\n> ').lower()
    if a == 'y':
        clawEject(orion)

    print('\nMove Orion5 to calibration position, then hit enter')

    a = input('> ')
    positions = orion.getAllJointsPosition()
    for i in range(len(positions)):
        positions[i] = Deg360ToG15Angle(positions[i])

    positions[1] = int(positions[1] * 2.857)
    positions[2] = wrap1088(543 - positions[2])
    positions[3] = wrap1088(positions[3] + 543)

    print('\ncurrent positions (g15 angles):', positions)

    print('\nTime to calibrate the claw!')
    print('Move claws until they are touching')
    print('Type W or S and press enter to move claw, type D when you\'re done.')

    claw_pos = 0
    while True:
        a = input('> ').lower()
        claw_pos = orion.claw.getPosition();
        if a == 'w':
            orion.claw.setPosition(wrap360(claw_pos + CLAW_INCREMENT))
        elif a == 's':
            orion.claw.setPosition(wrap360(claw_pos - CLAW_INCREMENT))
        elif a == 'd':
            break

    positions[0] = int(1087 - positions[0])
    positions[4] = int(0) #Deg360ToG15Angle(wrap360(claw_pos))

    while True:
        print('\noffsets:', positions)
        print('0 - edit base\n1 - edit shoulder\n2 - edit elbow\n3 - edit wrist\n4 - edit claw\n5 - apply\n6 - cancel')
        try:
            a = int(input('> ').lower())
            if a < 5:
                n = int(input(names[a] + ' = '))
                positions[a] = n
            elif a == 5:
                applyOffsets(orion, positions)
                print('\nApplied!')
                time.sleep(10)
                break
            elif a == 6:
                print('\nCancelled!')
                break
        except ValueError:
            print('VALUE ERROR!!1!')

except KeyboardInterrupt:
        print('\nExiting')
finally:
    orion.exit()
    print('\nFinished')
