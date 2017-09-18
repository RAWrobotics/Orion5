import socket
import select
import Orion5

orion = Orion5.Orion5('COM4')

HOST = 'localhost'
PORT = 42000

max_timeouts = 5
timeouts = 0

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)

def tryConversion(data):
    try:
        if '.' in data[3]:
            value = float(data[3])
        else:
            value = int(data[3])
    except ValueError:
        print(data)
        print("Orion5_Server: ValueError in conversion")
        return None
    return data

while True:
    print('waiting for connection')
    s.settimeout(None)
    conn, addr = s.accept()
    s.settimeout(0)

    connected = True
    print('connected')

    while connected:
        data = ''

        ready = select.select([conn], [], [], 1)

        if ready[0]:
            data = conn.recv(1024).decode()
        
        if not data or len(data) == 0 or not ready[0]:
            timeouts += 1
            if timeouts > max_timeouts:
                connected = False
                print('timeout')
        else:
            timeouts = 0

            if data == 'p':
                conn.sendall('p'.encode())
            elif data == 'q':
                break
            else:
                try:
                    data = data.split('+')
                    data_dict = {
                        'jointID': int(data[0]),
                        'id1': data[1],
                        'id2': data[2]
                    }
                except ValueError:
                    continue
                
                if data_dict['id1'] == 'posFeedback':
                    conn.sendall(str(orion.getJointAngles()).encode())
                elif data_dict['id1'] == 'velFeedback':
                    conn.sendall(str(orion.getJointSpeeds()).encode())
                elif data_dict['id1'] == 'torFeedback':
                    conn.sendall(str(orion.getJointLoads()).encode())
                elif data_dict['id1'] == 'posControl':
                    conn.sendall('r'.encode())
                    orion.setJointAnglesArray(eval(data[3]))
                elif data_dict['id1'] == 'velControl':
                    conn.sendall('r'.encode())
                    orion.setJointSpeedsArray(eval(data[3]))
                elif data_dict['id1'] == 'enControl':
                    conn.sendall('r'.encode())
                    orion.setJointTorqueEnablesArray(eval(data[3]))
                elif data_dict['id1'] == 'config':
                    conn.sendall('r'.encode())
                    value = tryConversion(data)
                    if value == None:
                        continue
                    orion.setVariable(data_dict['id2'], value)
                elif len(data) == 4:
                    conn.sendall('r'.encode())
                    value = tryConversion(data)
                    if value == None:
                        continue
                    orion.joints[data_dict['jointID']].setVariable(data_dict['id1'], data_dict['id2'], value)
                elif len(data) == 3:
                    var = orion.joints[data_dict['jointID']].getVariable(data_dict['id1'], data_dict['id2'])
                    conn.sendall(str(var).encode())

    conn.close()
s.close()
