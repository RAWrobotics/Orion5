import time

import orion5
from orion5.utils.general import waitForOrion5Forever

print('\nSearching for Orion5...')
comport = waitForOrion5Forever()
print('Found Orion5, serial port name:', comport)

orion = orion5.Orion5(comport)
time.sleep(3)

def gotoPositionBlocking(pos):
    orion.claw.setPosition(pos)
    while abs(pos - orion.claw.getPosition()) > 2:
        print('%.2f' % orion.claw.getPosition())
        time.sleep(0.2)

try:

    gotoPositionBlocking(359.0)

    orion.claw.setVariable('misc variables', 'cwAngleLimit', 1060)
    orion.claw.setVariable('misc variables', 'ccwAngleLimit', 1059)

    gotoPositionBlocking(170.0)

    orion.claw.setVariable('misc variables', 'cwAngleLimit', 0)
    orion.claw.setVariable('misc variables', 'ccwAngleLimit', 1087)

    gotoPositionBlocking(359.0)

    input('\nPress enter if claws are ejected\nCtrl+C and relaunch if claws are not ejected yet')

    orion.claw.setVariable('misc variables', 'cwAngleLimit', 1060)
    orion.claw.setVariable('misc variables', 'ccwAngleLimit', 1059)

    gotoPositionBlocking(135.0)

    input('\nPosition claws around pinion gear\n80mm between inner faces\n40mm from centre of gear to claw face\npress enter when ready')

    gotoPositionBlocking(355.0)

    orion.claw.setVariable('misc variables', 'cwAngleLimit', 0)
    orion.claw.setVariable('misc variables', 'ccwAngleLimit', 1087)

    gotoPositionBlocking(120.0)

except KeyboardInterrupt:
    print('Exiting...')
except Exception as e:
    print(e)
finally:
    orion.exit()
    print('Finished')
