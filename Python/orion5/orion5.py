import copy
import time
import threading

from . import utils
from . import orion5_serial

class Joint(object):
    def __init__(self, name, ID, cwAngleLimit, ccwAngleLimit, margin, slope, punch, speed, mode):
        self._jointLock = threading.Lock()
        self._datam = {
            'constants': {
                'ID': [ID, 1],
                'name': [name, 1]
            },
            'misc variables': {
                'cwAngleLimit': [cwAngleLimit, 1],
                'ccwAngleLimit': [ccwAngleLimit, 1],
                'cwMargin': [margin, 1],
                'cwwMargin': [margin, 1],
                'cwSlope': [slope, 1],
                'cwwSlope': [slope, 1],
                'punch': [punch, 1],
                'error': [None, 0]
            },
            'control variables': {
                'enable': [0, 1],
                'goalPosition': [None, 0],
                'desiredSpeed': [speed, 1],
                'controlMode': [mode, 1]
            },
            'feedback variables': {
                'currentPosition': [None, 0],
                'currentVelocity': [None, 0],
                'currentLoad': [None, 0]
            }
        }

    def setVariable(self, id1, id2, datum):
        self._jointLock.acquire()
        self._datam[id1][id2] = [datum, 1]
        self._jointLock.release()
        return

    def getVariable(self, id1, id2):
        self._jointLock.acquire()
        retValue = copy.copy(self._datam[id1][id2][0])
        self._jointLock.release()
        return retValue

    def checkVariable(self, id1, id2):
        self._jointLock.acquire()
        retValue = copy.copy(self._datam[id1][id2][1])
        self._jointLock.release()
        return retValue

    def TickVariable(self, id1, id2):
        self._jointLock.acquire()
        if self._datam[id1][id2][1] == 0:
            self._datam[id1][id2][1] = 1
        else:
            self._datam[id1][id2][1] = 0
        self._jointLock.release()
        return

    # SETTERS
    def setTorqueEnable(self, enable):
        self.setVariable('control variables', 'enable', int(enable))

    def setControlMode(self, mode):
        self.setVariable('control variables', 'controlMode', mode)

    def setPosition(self, goalPosition):
        self.setVariable('control variables', 'goalPosition', goalPosition)

    def setTimeToGoal(self, seconds):
        seconds = int(seconds * 10)
        assert self.getVariable('control variables', 'controlMode') == utils.ControlModes.TIME, "Control mode not set to time"
        assert 0 <= seconds <= 1023, "Time outside valid range: 0-1024"
        self.setVariable('control variables', 'desiredSpeed', seconds)

    def setSpeed(self, RPM):
        assert self.getVariable('control variables', 'controlMode') in [utils.ControlModes.WHEEL, utils.ControlModes.SPEED], "Control mode set to time"
        assert 0 <= RPM <= 100, "RPM value outside valid range: 0-100"
        self.setVariable('control variables', 'desiredSpeed', int(1023.0 * RPM / 112.83))

    # GETTERS
    def getPosition(self):
        retValue = self.getVariable('feedback variables', 'currentPosition')
        if retValue == None:
            retValue = 0.0
        return retValue

    def getSpeed(self):
        retValue = self.getVariable('feedback variables', 'currentVelocity')
        if retValue == None:
            retValue = 0.0
        return retValue

    def getLoad(self):
        retValue = self.getVariable('feedback variables', 'currentLoad')
        if retValue == None:
            retValue = 0.0
        return retValue

class Orion5(object):
    def __init__(self, serialName):
        self._constantLock = threading.Lock()
        # name, ID, cwAngleLimit, ccwAngleLimit, margin, slope, punch, speed, mode
        self.base =     Joint('base',     0,   0, 1087, 1, 120,  35, 100, 0)
        self.shoulder = Joint('shoulder', 1,  30, 1057, 1, 120,  35, 150, 0)
        self.elbow =    Joint('elbow',    2,  60, 1027, 1, 120,  35,  80, 0)
        self.wrist =    Joint('wrist',    3, 136,  951, 1, 120,  35, 120, 0)
        self.claw =     Joint('claw',     4,  60, 1087, 1, 120,  35, 100, 0)
        self.joints = [self.base, self.shoulder, self.elbow, self.wrist, self.claw]
        self._globalConstants = {
            'baseOffset':        [0, 1],
            'shoulderOffset':    [0, 1],
            'elbowOffset':       [0, 1],
            'wristOffset':       [0, 1],
            'clawOffset':        [0, 1],
            'baseDirection':     [1, 1],
            'shoulderDirection': [-1, 1],
            'elbowDirection':    [1, 1],
            'wristDirection':    [-1, 1],
            'clawDirection':     [1, 1],
            'clawLoadLimit':     [200, 1],
            'fieldInflation':    [5, 1],
            'clawHomePos':       [362, 1],
            'firmwareUpdate':    [0, 0],
            'mode':              [0, 0]
        }

        self.firmwareVersion = -1
        self.serial = orion5_serial.SerialThread(self, serialName)
        self.serial.start()

    def setVariable(self, key, value):
        self._constantLock.acquire()
        self._globalConstants[key] = [value, 1]
        self._constantLock.release()
        return

    def getVariable(self, key):
        self._constantLock.acquire()
        retValue = copy.copy(self._globalConstants[key][0])
        self._constantLock.release()
        return retValue

    def checkVariable(self, key):
        self._constantLock.acquire()
        retValue = copy.copy(self._globalConstants[key][1])
        self._constantLock.release()
        return retValue

    def TickVariable(self, key):
        self._constantLock.acquire()
        if self._globalConstants[key][1] == 0:
            self._globalConstants[key][1] = 1
        else:
            self._globalConstants[key][1] = 0
        self._constantLock.release()
        return

    # SETTERS FOR ALL JOINTS
    def setAllJointsPosition(self, angles):
        for i in range(len(angles)):
            self.joints[i].setPosition(angles[i])

    def setAllJointsSpeed(self, speeds):
        for i in range(len(speeds)):
            self.joints[i].setSpeed(speeds[i])

    def setAllJointsTimeToGoal(self, times):
        for i in range(len(times)):
            self.joints[i].setTimeToGoal(times[i])

    def setAllJointsTorqueEnable(self, enables):
        for i in range(len(enables)):
            self.joints[i].setTorqueEnable(enables[i])

    # GETTERS FOR ALL JOINTS
    def getAllJointsPosition(self):
        return [joint.getPosition() for joint in self.joints]

    def getAllJointsSpeed(self):
        return [joint.getSpeed() for joint in self.joints]

    def getAllJointsLoad(self):
        return [joint.getLoad() for joint in self.joints]

    # ENABLE/DISABLE TORQUE FOR ALL JOINTS
    def releaseTorque(self):
        for joint in self.joints:
            joint.setTorqueEnable(0)

    def enableTorque(self):
        for joint in self.joints:
            joint.setTorqueEnable(1)

    def exit(self):
        utils.debug("Orion5: exit: joining threads")
        self.serial.stop()
        self.serial.join()
        utils.debug("Orion5: exit: finished")
