import time
import copy
import socket
import select
import traceback
from threading import Thread, Lock
import sys
import argparse
import random

import orion5
import orion5.utils as utils


def getRandomID():
    return '{:x}'.format(random.randint(1, 2**64))


def floatArray2Str(array):
    return '[' + ''.join(['{:.2f},'.format(e) for e in array]) + ']'


def tryConversion(data):
    try:
        if '.' in data[3]:
            value = float(data[3])
        else:
            value = int(data[3])
    except ValueError as e:
        print(e, data)
        print("Orion5_Server: ValueError in conversion 1")
        print('client error in read:', e)
        return None
    return value


class SocketThread(Thread):
    def __init__(self, id, orion, socket, flag):
        Thread.__init__(self)
        self.flag = flag
        self.orion = orion
        self.socket = socket
        self.id = id
        self.connected = True
        self.timeouts = 0

    def stop(self):
        self.connected = False
        self.socket.close()
        print('{} - Disconnected'.format(self.id))

    def run(self):
        try:
            read_buffer = ''
            while self.connected:
                data = ''

                ready = select.select([self.socket], [], [], 1)

                if ready[0]:
                    data = self.socket.recv(1024).decode()
                    # print('{} - {}'.format(self.id, data))

                    if len(data) > 0:
                        read_buffer += data

                        if '$' in read_buffer:
                            split = read_buffer.split('$')
                            for e in split:
                                if len(e) > 4:
                                    e = e.split('&')
                                    length = int(e[0])
                                    if len(e[1]) == length:
                                        read_buffer = read_buffer[5+length:]
                                        self.timeouts = 0
                                        self.process(e[1])
                    else:
                        self.timeouts += 1
                        if self.timeouts > utils.SOCKET_MAX_TIMEOUTS:
                            print('{} - Timeout'.format(self.id))
                            self.stop()

                else:
                    self.timeouts += 1
                    if self.timeouts > utils.SOCKET_MAX_TIMEOUTS:
                        print('{} - Timeout'.format(self.id))
                        self.stop()

        except Exception as e:
            print('client error in read:', e)
            traceback.print_tb(e.__traceback__)
        finally:
            self.stop()

    def write(self, data):
        self.socket.sendall(('$' + '{:03d}'.format(len(data)) + '&' + str(data)).encode())

    def process(self, data):
        if data == 'p':
            if self.orion.serial is not None and self.orion.serial.running:
                self.write('c')
            else:
                self.write('d')
        elif data == 'q':
            self.connected = False
        else:

            # if self.orion == None:
            #     return

            try:
                data = data.split('+')
                data_dict = {
                    'jointID': int(data[0]),
                    'id1': data[1],
                    'id2': data[2]
                }
            except ValueError:
                print('{} - {}'.format(self.id, data))
                print('{} - Orion5_Server: ValueError in conversion 2'.format(self.id))
                return

            if data_dict['id1'] == 'posFeedback':
                self.write((data_dict['id1'] + '+' + floatArray2Str(self.orion.getAllJointsPosition())))

            elif data_dict['id1'] == 'velFeedback':
                self.write((data_dict['id1'] + '+' + floatArray2Str(self.orion.getAllJointsSpeed())))

            elif data_dict['id1'] == 'torFeedback':
                self.write((data_dict['id1'] + '+' + floatArray2Str(self.orion.getAllJointsLoad())))

            elif data_dict['id1'] == 'errFeedback':
                self.write((data_dict['id1'] + '+' + str(self.orion.getAllJointsError())))

            elif data_dict['id1'] == 'firmwareVersion':
                if self.orion.serial is not None:
                    self.orion.serial.RequestFirmwareVersion()
                self.write((data_dict['id1'] + '+' + str(self.orion.getVariable('firmwareVersion'))))

            elif data_dict['id1'] == 'posControl':
                self.orion.setAllJointsPosition(eval(data[3]))

            elif data_dict['id1'] == 'velControl':
                self.orion.setAllJointsSpeeds(eval(data[3]))

            elif data_dict['id1'] == 'enControl':
                self.orion.setAllJointsTorqueEnable(eval(data[3]))

            elif data_dict['id1'] == 'simulator':
                if data[3] == 'activate':
                    self.orion.simulator.Start()
                elif data[3] == 'deactivate':
                    self.orion.simulator.Stop()
                elif data[3] == 'continue':
                    self.orion.simulator.Update()

            elif data_dict['id1'] == 'serial':
                print(data[2], data[3])
                if data[3] == '':
                    self.orion.restartSerial(data[2])
                else:
                    self.orion.restartSerial(data[2], data[3])

                if data[2] == 'stop':
                    self.orion.serialName = None

            elif data_dict['id1'] == 'serialName':
                print('serialName', data[2])
                if data[2] == '':
                    self.orion.serialName = None
                else:
                    self.orion.serialName = data[2]

            elif data_dict['id1'] == 'setConfig':
                value = tryConversion(data)
                if value == None:
                    return
                self.orion.setVariable(data_dict['id2'], value)

            elif data_dict['id1'] == 'readConfig':
                var = self.orion.getVariable(data_dict['id2'])
                self.write((data_dict['id2'] + '+' + str(var)))

            elif data_dict['id1'] == 'getID':
                self.write((data_dict['id1'] + '+"' + self.id + '"'))

            elif data_dict['id1'] == 'getFlag':
                self.write((data_dict['id1'] + '+"' + str(self.flag.get())) + '"')

            elif data_dict['id1'] == 'trySetFlag':
                success = 1 if self.flag.trySet(self.id) else 0
                self.write((data_dict['id1'] + '+' + str(success)))

            elif len(data) == 4:
                value = tryConversion(data)
                if value == None:
                    return
                self.orion.joints[data_dict['jointID']].setVariable(data_dict['id1'], data_dict['id2'], value)

            elif len(data) == 3:
                var = self.orion.joints[data_dict['jointID']].getVariable(data_dict['id1'], data_dict['id2'])
                self.socket.sendall(str(var))


class Flag(object):
    def __init__(self):
        # the flag holds the id of the thread that is holding it
        # if the flag is 0, no thread owns the flag
        self.flag = 0
        self.lock = Lock()

    def get(self):
        with self.lock:
            val = copy.copy(self.flag)
        return val

    def trySet(self, id):
        fail = False
        with self.lock:
            if self.flag == 0 or self.flag == id:
                self.flag = id
                fail = True
        return fail

    def reset(self):
        with self.lock:
            self.flag = 0


parser = argparse.ArgumentParser(description='Orion5 Server', epilog='By default the server will connect to whatever Orion5 is plugged in')
parser.add_argument('--simulator', dest='simulator', action='store_const',
    const=True, default=False, help='Set this flag to enter simulator mode first, and you control the serial connection from client side.')
args = parser.parse_args()


socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
socket_server.bind((utils.SOCKET_HOST, utils.SOCKET_PORT))
socket_server.settimeout(None)
socket_server.listen(2)

print('\nOrion5 Server Started')
print('\nWaiting for Connections')

flag = Flag()
orion = orion5.Orion5(mode='standalone', serialName=None, useSimulator=args.simulator)
threads = []
running = True

try:

    while running:
        # check every second for new sockets trying to connect
        ready, _, _ = select.select([socket_server], [], [], 0.25)

        # if a new is connected
        for socket in ready:
            if socket is socket_server:

                # if flag.check():
                #     continue

                connection, (ip, port) = socket_server.accept()
                connection.settimeout(0)

                print('\nConnection from: {}:{}!'.format(ip, port))

                # add a new thread for this socket
                thread = SocketThread(getRandomID(), orion, connection, flag)
                thread.start()
                threads.append(thread)


        # remove dead threads
        i = 0
        while i < len(threads):
            if not threads[i].connected:
                print(threads[i].id, flag.get())
                if threads[i].id == flag.get():
                    print('flag reset')
                    flag.reset()
                threads.pop(i)
                print('thread removed')
            else:
                i += 1


        if not args.simulator:
            #####   Serial Stuff   #####
            # check for connected Orion5's
            # if not orion.simulator.value:
            new_comport = utils.ComQuery()

            # if one was found
            if new_comport is not None:
                new_comport = new_comport.device

                # if there was no comport connected before
                if new_comport != orion.serialName and orion.serialName == None and (orion.simulator is None or not orion.simulator.value):
                    print('starting serial')
                    orion.restartSerial('start', new_comport)

                # if this is a new comport
                elif new_comport != orion.serialName and (orion.simulator is None or not orion.simulator.value):
                    print('restarting serial')
                    orion.restartSerial('restart', new_comport)

                # if we are still in simulator mode, save comport until it is time to restartSerial
                else:
                    orion.serialName = new_comport

            # if no orion5's found and existing port is not None, Orion5 has been disconnected
            elif orion.serialName is not None:
                print('Disconnecting...')
                orion.restartSerial('stop')
                orion.serialName = None
            ############################

except KeyboardInterrupt:
    print('exiting SIGINT')

except Exception as e:
    print(e)
    traceback.print_tb(e.__traceback__)
    print('exiting EXCEPTION')

finally:
    print('Waiting for threads to finish')
    for thread in threads:
        thread.stop()
        thread.join()
    print('Exiting!')
    socket_server.close()
    orion.exit()
