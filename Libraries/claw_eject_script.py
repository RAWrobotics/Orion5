import time
from Orion5 import Orion5
from General import ComQuery

# search for an Orion5
comport = None
print('\nSearching for Orion5...')
while True:
    comport = ComQuery()
    if comport is not None:
        print('Found Orion5, serial port name:', comport.device)
        break
    time.sleep(2)

orion = Orion5(comport.device)
time.sleep(3)

def gotoPositionBlocking(pos):
    orion.claw.setVariable('control variables', 'goalPosition', pos)
    while abs(pos - orion.claw.getVariable('feedback variables', 'currentPosition')) > 2:
        print('%.2f' % orion.claw.getVariable('feedback variables', 'currentPosition'))
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

    input('\nPosition claws now - press enter when ready')

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
