import Orion5
import time

orion = Orion5.Orion5('COM4')

time.sleep(5)

for joint in orion.joints:
    joint.setVariable('control variables', 'enable', 0)

time.sleep(1)

# orion.claw.setGoalPosition(250)
# while abs(orion.claw.getPosition() - 250) > 5:
#     time.sleep(0.1)
#
# orion.claw.setGoalPosition(20)

# runTime = 10.0
# data = []
# start = time.perf_counter()
# while True:
#     if time.perf_counter() - start > runTime:
#         break
#     data.append(orion.getJointAngles())
#     time.sleep(0.005)
#
# zeros = 0
# for i in range(1, len(data)):
#     diff = data[i][3] - data[i-1][3]
#     if diff == 0:
#         zeros += 1
#
# print(len(data))
# print(float(len(data) - zeros) / runTime, 'Hz')

# orion.base.setVariable('control variables', 'desiredSpeed', 0)
# orion.base.setVariable('control variables', 'controlMode', 2)
#
# time.sleep(2)
#
# speed = 0
# while True:
#     speed += 1
#     if speed > 250:
#         break
#     time.sleep(0.01)
#     orion.base.setVariable('control variables', 'desiredSpeed', int(speed))
#
# input('stop?')
#
# while True:
#     speed -= 10
#     if speed <= 0:
#         break
#     time.sleep(0.05)
#     orion.base.setVariable('control variables', 'desiredSpeed', int(speed))
#
# time.sleep(1)
# orion.base.setVariable('control variables', 'controlMode', 0)

while True:
    id = int(input('id: '))
    desiredPos = int(input('angle: '))
    orion.joints[id].setGoalPosition(desiredPos)

orion.exit()

# shoulder ratio 2.857... = 1 + (52 / 28)
