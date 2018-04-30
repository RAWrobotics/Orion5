import threading
import serial
import time
import struct

from . import utils
from . import math

class SerialThread(threading.Thread):
    '''
    Need to create an incoming and outgoing dynamic buffer.

    The main loop should first check if the usb is connected, if not then it should attempt connection
    If the main loop is connected, then the main functionality ensues, disconnection should be handled
    dynamically.
    In the main loop one of the modules should pull all of the incomming USB buffer into the software buffer
    A module after that one should pull all meaningful packets out of the software buffer
    Following this there is the outbound comms...   this will get complex:
    There should be an outgoing buffer, it will be something like [timeout, [bytes]], when a set of bytes
    is sent through, the timeout is set to current system time or whatever. After this we have almost start
    condition again; all messages to be sent will be polled up in this buffer, so the main loops requests
    to the ORION5 will go into here, any checkers to be returned will go into here, etc. If the buffer gets
     larger than 64bytes? then send the first/last... dyslexia 64bytes through and reset the timeout. If
     the timeout value vs the now time exceeds a certain time, then push what is in there through.

     The Checker...  The PC will send checker bytes in its packets, they will be handled the same on both
     pc and ORION5 sides...  When the pc side here receives a packet, it will take the checker and add it
     to a registry of checkers. a seperate module in the main loop called the bureaucrat, will look at this
     registry and build 'a' packet or multiple packets (if greater than 64bytes or some arbitrary number),
     of checkerlist packettypes which it will dump into the outbound buffer.

     when the pc receives a checkerlist packettype, it will go through the flag variable in the joint
     dictionaries and
    '''
    def __init__(self, orion5_reference, serialName):
        threading.Thread.__init__(self)
        self._outboxIterator = [
            [
                'misc variables', [
                    ['cwAngleLimit', utils.JointVars.CW_LIMIT, 2],
                    ['ccwAngleLimit', utils.JointVars.CCW_LIMIT, 2],
                    ['cwMargin', utils.JointVars.CW_MARGIN, 1],
                    ['cwwMargin', utils.JointVars.CCW_MARGIN, 1],
                    ['cwSlope', utils.JointVars.CW_SLOPE, 1],
                    ['cwwSlope', utils.JointVars.CCW_SLOPE, 1],
                    ['punch', utils.JointVars.PUNCH, 2]
                ]
            ],
            [
                'control variables', [
                    ['enable', utils.JointVars.TORQUE_ENABLE, 1],
                    ['goalPosition', utils.JointVars.GOAL_POS, 2],
                    ['desiredSpeed', utils.JointVars.SPEED, 2],
                    ['controlMode', utils.JointVars.MODE, 1]
                ]
            ]
        ]
        self._globalConstIterator = [
            ['baseOffset', utils.GlobalConstants.BASE_OFFSET],
            ['shoulderOffset', utils.GlobalConstants.SHOULDER_OFFSET],
            ['elbowOffset', utils.GlobalConstants.ELBOW_OFFSET],
            ['wristOffset', utils.GlobalConstants.WRIST_OFFSET],
            ['clawOffset', utils.GlobalConstants.CLAW_OFFSET],
            ['baseDirection', utils.GlobalConstants.BASE_DIRECTION],
            ['shoulderDirection', utils.GlobalConstants.SHOULDER_DIRECTION],
            ['elbowDirection', utils.GlobalConstants.ELBOW_DIRECTION],
            ['wristDirection', utils.GlobalConstants.WRIST_DIRECTION],
            ['clawDirection', utils.GlobalConstants.CLAW_DIRECTION],
            ['clawLoadLimit', utils.GlobalConstants.CLAW_LOAD_LIMIT],
            ['fieldInflation', utils.GlobalConstants.FIELD_INFLATION],
            ['clawHomePos', utils.GlobalConstants.CLAW_HOME_POS],
            ['firmwareUpdate', utils.GlobalConstants.FIRMWARE_UPDATE],
            ['mode', utils.GlobalConstants.CLAW_HOME_POS]
        ]

        self._iter = [0, 0, 0]
        self.arm = orion5_reference
        self.running = True
        self.uart = None
        self._lastFeedbackTime = 0
        self._requestFeedback = 1
        self._checker = [2, 0, 0, 0]
        try:
            self.uart = serial.Serial(
                port=serialName,
                baudrate=utils.SERIAL_BAUD_RATE,
                write_timeout=0,
                timeout=utils.SERIAL_TIMEOUT
            )
        except Exception as e:
            print(e)
            utils.debug("SerialThread: Unable to find serial device")
            utils.debug("SerialThread: Thread will immediately exit")
            self.stop()

    def run(self):
        if self.uart is None:
            return
        utils.debug("SerialThread: Thread started")
        self.main()
        self.uart.close()
        utils.debug("SerialThread: Thread stopped")

    def stop(self):
        if self.running:
            utils.debug("SerialThread: Stopping thread")
            self.running = False
        else:
            utils.debug("SerialThread: Thread already stopped")

    def main(self):

        self.SendPacket(self.BuildPacket(6, 0, []))

        while self.running:

            # if self._requestFeedback or (time.perf_counter() - self._lastFeedbackTime) > 0.1:
            #     self._lastFeedbackTime = time.perf_counter()
            #     self._requestFeedback = 0
            self.RequestFeedback()

            # for i in range(5):
            #     self.RequestErrorCodes(i)

            # look through joint registries for new data
            for i in range(20):
                self._iter[2] += 1
                if len(self._outboxIterator[self._iter[1]][1]) <= self._iter[2]:
                    self._iter[2] = 0
                    self._iter[1] += 1
                    if self._iter[1] > 1:
                        self._iter[1] = 0
                        self._iter[0] += 1
                        if self._iter[0] > 4:
                            self._iter[0] = 0
                jointPTR = self.arm.joints[self._iter[0]]
                itemSETPTR = self._outboxIterator[self._iter[1]]
                itemPTR = self._outboxIterator[self._iter[1]][1][self._iter[2]]
                if jointPTR.checkVariable(itemSETPTR[0], itemPTR[0]):
                    ID = jointPTR.getVariable('constants', 'ID')
                    value = jointPTR.getVariable(itemSETPTR[0], itemPTR[0])
                    # convert to G15 angle if var is a position update
                    if itemPTR[0] == 'goalPosition':
                        value = math.Deg360ToG15Angle(value)
                    # firmware workaround for time-to-goal mode
                    if itemPTR[0] == 'desiredSpeed' and jointPTR.getVariable('control variables', 'controlMode') == utils.ControlModes.TIME:
                        value = (int(value * 10) & 0x1FFF) | 0x8000
                    self.ProcessSend((ID, itemPTR[1], itemPTR[2], value, self._checker[0]))
                    jointPTR.TickVariable(itemSETPTR[0], itemPTR[0])
                    break

            # look through global constants for new data
            for item in self._globalConstIterator:
                if self.arm._globalConstants[item[0]][1]:
                    value = self.arm._globalConstants[item[0]][0]
                    if item[0] == 'mode':
                        packet = self.BuildPacket(5, 3, [0x45, value & 0xFF, (value & 0xFF00) >> 8])
                    else:
                        packet = self.BuildPacket(4, 3, [item[1], value & 0xFF, (value & 0xFF00) >> 8])
                    self.SendPacket(packet)
                    self.arm.TickVariable(item[0])

            while self.uart.in_waiting > 8:
                self.ProcessRead()

            time.sleep(0.01)

        #self.StopFeedback()
        #time.sleep(1)

    def CheckerAdvance(self):
        # Advance the Checker
        if self._checker[0] >= 255:
            self._checker[0] = 2
        else:
            self._checker[0] += 1

    def ProcessSend(self, command):
        data = [command[0], command[1], (command[3] & 0xFF)]
        if command[2] == 2:
            data.append((command[3] & 0xFF00) >> 8)
        packet = self.BuildPacket(0, 2 + command[2], data) #need to add checker in???  XXXX
        retValue = self.SendPacket(packet)
        return retValue

    def RequestFeedback(self):
        self.SendPacket(self.BuildPacket(2, 0, []))

    def RequestErrorCodes(self, index):
        self.SendPacket(self.BuildPacket(1, 2, [index, 16]))

    def StopFeedback(self):
        self.SendPacket(self.BuildPacket(3, 0, []))

    def GetChecksum(self, packet):
        checksum = 0
        for i in range(2, len(packet)):
            checksum += packet[i]
            if checksum > 0xFF:
                checksum -= 256
        return (~checksum) & 0xFF

    def ProcessRead(self):
        valid = 0
        state = 0
        reset = 0
        byte = 0
        packetType1 = 0
        packetType2 = 0
        checker = 0
        data = []

        while True:
            if self.uart.in_waiting == 0:
                break
            try:
                byte = struct.unpack('B', self.uart.read(1))[0]
            except Exception as e:
                print(e)
                print('could not read byte')
                break

            if state < 2:
                # grab header bytes
                if byte == 0xF0:
                    state += 1
                else:
                    reset = 1;
            elif state == 2:
                # grab packet type 1
                packetType1 = byte
                state += 1
            elif state == 3:
                # grab packet type 2
                packetType2 = byte
                state += 1
            elif state == 4:
                # grab data bytes
                if len(data) == packetType2:
                    state += 1
                else:
                    data.append(byte)
            if state == 5:
                checker = byte
                state += 1
            elif state == 6:
                # get checksum
                valid = (self.GetChecksum([0xFF, 0xFF, packetType1, packetType2, checker] + data) == byte)
                if not valid:
                    reset = 1

            if valid:
                break

            if reset:
                # reset state vars
                valid = 0
                state = 0
                reset = 0
                data = []

        if valid:
            if packetType1 == 0x36:
                # 0x36 is one register from G15
                # print(data)
                value = 0
                if len(data) == 3:
                    value = data[2] # struct.unpack('B', data[2])[0]
                elif len(data) == 4:
                    value = struct.unpack('<H', bytes(data[2:4]))[0]

                if data[1] == 0:
                    self.arm.joints[data[0]].setVariable('feedback variables', 'currentPosition', math.G15AngleTo360(value))
                elif data[1] == 1:
                    self.arm.joints[data[0]].setVariable('feedback variables', 'currentVelocity', value)
                elif data[1] == 2:
                    self.arm.joints[data[0]].setVariable('feedback variables', 'currentLoad', value)
                elif data[1] == 16:
                    self.arm.joints[data[0]].setVariable('misc variables', 'error', value)
                    # print('error from servo {0}: value: {1}'.format(data[0], value))
            elif packetType1 == 0x22:
                # 0x22 is all feedback vars from all G15s
                self._requestFeedback = 1
                unpacked = struct.unpack('HHHHHHHHHHHHHHH', bytes(data))
                for i in range(len(self.arm.joints)):
                    position = math.G15AngleTo360(unpacked[i*3+0])
                    self.arm.joints[i].setVariable('feedback variables', 'currentPosition', position)
                    self.arm.joints[i].setVariable('feedback variables', 'currentVelocity', unpacked[i*3+1])
                    self.arm.joints[i].setVariable('feedback variables', 'currentLoad', unpacked[i*3+2])
            elif packetType1 == 0x89:
                unpacked = struct.unpack('I', bytes(data))[0]
                self.arm.firmwareVersion = unpacked
                print(self.arm.firmwareVersion)


    def BuildPacket(self, type, length, data):
        # <0xF0> <0xF0> <packetType1> <packetType2> <data 1> ... <data n> <checksum>
        # 0x69 - set variable in registry
        # 0x36 - request a var from registry
        # 0x22 - request all feedback vars from all G15s
        # 0x24 - stop all feedback vars
        # 0x42 - write global constant

        hexReg = [0x69, 0x36, 0x22, 0x24, 0x42, 0x99, 0x89]
        packet = [0xF0, 0xF0, hexReg[type], length]
        for i in range(len(data)):
            packet.append(data[i])
        self.CheckerAdvance()
        packet.append(self._checker[0])
        packet.append(self.GetChecksum(packet))
        return bytes(packet)

    def SendPacket(self, packet):
        if self.uart is None:
            utils.debug("SerialThread: SendPacket: uart is None")
            return False
        try:
            self.uart.write(packet)
            return True
        except serial.SerialTimeoutException:
            utils.debug("SerialThread: SendPacket: timeout writing to serial port")
            return False
