import datetime as dt

DEBUG = False
DEBUG_MODE = 'PRINT'

SERIAL_BAUD_RATE = 1000000
SERIAL_TIMEOUT = 1  # seconds
READ_INTERVAL = 0.1  # seconds

READ_PACKET_LEN = 7

CLAW_OPEN_POS = 300
CLAW_CLOSE_POS = 120

class ErrorIDs:
    INSTRUCTION_ERROR = 0x40
    OVERLOAD_ERROR = 0x20
    CHECKSUM_ERROR = 0x10
    RANGE_ERROR = 0x08
    OVERHEATING_ERROR = 0x04
    ANGLE_LIMIT_ERROR = 0x02
    INPUT_VOLTAGE_ERROR = 0x01

class ControlModes:
    SPEED, TIME, WHEEL = range(3)

class JointVars:
    CURRENT_POS, CURRENT_SPEED, CURRENT_LOAD, GOAL_POS, SPEED, \
        TORQUE_ENABLE, CW_SLOPE, CCW_SLOPE, CW_MARGIN, CCW_MARGIN, \
        PUNCH, CW_LIMIT, CCW_LIMIT, LED, MAX_TORQUE, MODE = range(16)

class GlobalConstants:
    BASE_OFFSET, SHOULDER_OFFSET, ELBOW_OFFSET, WRIST_OFFSET, CLAW_OFFSET, \
    BASE_DIRECTION, SHOULDER_DIRECTION, ELBOW_DIRECTION, WRIST_DIRECTION, \
    CLAW_DIRECTION, CLAW_LOAD_LIMIT, FIELD_INFLATION, CLAW_HOME_POS, FIRMWARE_UPDATE, MODE = range(15)

def debug(message):
    if DEBUG:
        timestamp = dt.datetime.now().strftime("%x-%X: ")
        if DEBUG_MODE == "FILE":
            with open('log.txt', 'a') as log:
                log.write(timestamp + message + "\n")
        elif DEBUG_MODE == "PRINT":
            print(timestamp + message)
