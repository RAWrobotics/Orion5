def wrap360f(angle):
    if angle < 0:
        angle += 360
    elif angle > 360:
        angle -= 360
    return angle

angle = 120
sequence = []

with open('Fight.txt', 'r') as file:
    for line in file:
        sequence.append(line.split(' '))

for i in range(len(sequence)):
    sequence[i][1] = str(wrap360f(float(sequence[i][1]) - angle))
    sequence[i][13] = str(wrap360f(float(sequence[i][13]) + angle))

with open('Fight-rotated.txt', 'w') as file:
    for line in sequence:
        file.write(' '.join(line))
