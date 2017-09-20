from os import listdir
from os.path import isfile, join
import struct
def PullFileNames(extension, subFolder):
    ''' Pulls a list of STL files in, provided they start
    with a number 000 up to 010'''
    fileNames = [f for f in listdir(subFolder) if isfile(join(subFolder, f))]
    iterator = 0
    while iterator < len(fileNames):
        if fileNames[iterator].find(extension) == -1:
            del fileNames[iterator]
        else:
            iterator +=1
    fileSets = [[], [], [], [], [], [], [], [], [], [], []]
    for iterator1 in range(len(fileNames)):
        fileSets[int(fileNames[iterator1][:3])].append(subFolder+'/'+fileNames[iterator1])
    return fileSets

def PopulateModels(fileSets, scaler = 1):
    Models = []
    for iterator1 in range(len(fileSets)):
        for iterator2 in range(len(fileSets[iterator1])):
            try:
                Models = STLRead(Models, fileSets[iterator1][iterator2], iterator1, int(fileSets[iterator1][iterator2][7:10]), scaler)
            except:
                Models = STLRead(Models, fileSets[iterator1][iterator2], iterator1, 1, scaler)
    return Models

def PolyRead(fileName, scaler = 1):
    Models = []
    filePipe = open(fileName, 'rb')
    ModelsNo = struct.unpack('I', filePipe.read(4))[0]
    for iter1 in range(ModelsNo):
        Models.append([[0, [.12, .12, .12, 1.0]], []])
        #Read the Model Header
        #read the ModelNo
        Models[-1][0][0] = struct.unpack('I', filePipe.read(4))[0]
        #read the colour
        for iter2 in range(4):
            Models[-1][0][1][iter2] = struct.unpack('f', filePipe.read(4))[0]
        # Read the number of Polygons
        FacetsNo = struct.unpack('I', filePipe.read(4))[0]
        for data in range(FacetsNo):
            try:
                Normal = [struct.unpack('f', filePipe.read(4))[0],
                          struct.unpack('f', filePipe.read(4))[0],
                          struct.unpack('f', filePipe.read(4))[0]]
                Vertex1 = [struct.unpack('f', filePipe.read(4))[0]*scaler,
                           struct.unpack('f', filePipe.read(4))[0]*scaler,
                           struct.unpack('f', filePipe.read(4))[0]*scaler]
                Vertex2 = [struct.unpack('f', filePipe.read(4))[0]*scaler,
                           struct.unpack('f', filePipe.read(4))[0]*scaler,
                           struct.unpack('f', filePipe.read(4))[0]*scaler]
                Vertex3 = [struct.unpack('f', filePipe.read(4))[0]*scaler,
                           struct.unpack('f', filePipe.read(4))[0]*scaler,
                           struct.unpack('f', filePipe.read(4))[0]*scaler]
                Models[-1][1].append([Normal, Vertex1, Vertex2, Vertex3])
            except:
                print("error reading facets")
                break
    filePipe.close()
    return Models

def ComQuery():
    #TODO make sure multple arms cant be assigned the same com port by removing entities from the list of comports that already exist in the arm
    global comListObj, comObj
    comObj = None
    import serial.tools.list_ports
    comListObj = serial.tools.list_ports.comports()
    thing2 = ['None']
    for item in comListObj:
        thing2.append(str(item))
    for iterator1 in range(len(thing2)):
        if iterator1 == 0:
            thing3 = ('0 None',)
        elif (comListObj[iterator1 - 1].vid == 1027 and comListObj[iterator1 - 1].pid == 24597):
            thing3 = thing3 + (str(iterator1) + ' ' + thing2[iterator1],)
    if len(thing3) == 1:
        return None
    elif len(thing3) == 2:
        for iter1 in range(len(comListObj)-1,-1,-1):
            if not (comListObj[iter1].vid == 1027 and comListObj[iter1].pid == 24597):
                del comListObj[iter1]
        return comListObj[0]
    import tkinter, tkinter.ttk
    font_size = 14
    comQuery = tkinter.Tk()
    comQuery.title('Com port selector')
    comQuery.minsize(width=100, height=100)
    goButton = tkinter.Button(comQuery, text="Select", font = ("Arial", font_size, "bold"))
    comList = tkinter.StringVar()
    comPorts = tkinter.ttk.Combobox(comQuery, font = ("Arial", font_size, "bold"), width = 40, textvariable = comList, state = 'readonly')
    comListObj = None
    def RefreshComs(pokeThrough):
        global comListObj
        import serial.tools.list_ports
        comListObj = serial.tools.list_ports.comports()
        thing2 = ['None']
        for item in comListObj:
            thing2.append(str(item))
        for iterator1 in range(len(thing2)):
            if iterator1 == 0:
                thing3 = (str(iterator1)+' '+thing2[iterator1],)
            elif (comListObj[iterator1-1].vid == 1027 and comListObj[iterator1-1].pid == 24597):
                thing3 = thing3 + (str(iterator1)+' '+thing2[iterator1],)
        comPorts['values'] = thing3
    RefreshComs('pelicanCase')
    comPorts.grid(row=1, column=1, columnspan=4)
    goButton.grid(row=2, column=1, columnspan=3)
    comPorts.bind('<<ComboboxSelected>>', RefreshComs)
    def GoButton():
        global comListObj, comObj
        try:
            comListObj.append(None)
            comObj = comListObj[int(comList.get()[:comList.get().find(' ')]) - 1]
        except:
            print('Error picking com port')
        comQuery.quit()
        comQuery.destroy()
    goButton.configure(command=GoButton)
    comQuery.mainloop()
    return comObj

def STLRead(Models, fileName, ModelID, ColorID = 1, scaler = 1):
    filePipe = open(fileName, 'rb')
    colorcodes = [[.16, .16, .16, 1.0], [.12, .12, .12, 1.0], [.5, 0, 0, 0.1], [.38, .37, .4, 1],[.35, .2, .53, 1]]
    headerLength = 80
    floatLength = 4
    endLength = 2
    header = filePipe.read(headerLength)
    facetNo = struct.unpack('I', filePipe.read(4))[0]
    Models.append( [[ModelID, colorcodes[ColorID]],[]] )
    for data in range(facetNo):
        try:
            Normal = [struct.unpack('f', filePipe.read(floatLength))[0],
                      struct.unpack('f', filePipe.read(floatLength))[0],
                      struct.unpack('f', filePipe.read(floatLength))[0]]
            Vertex1 = [struct.unpack('f', filePipe.read(floatLength))[0]*scaler,
                       struct.unpack('f', filePipe.read(floatLength))[0]*scaler,
                       struct.unpack('f', filePipe.read(floatLength))[0]*scaler]
            Vertex2 = [struct.unpack('f', filePipe.read(floatLength))[0]*scaler,
                       struct.unpack('f', filePipe.read(floatLength))[0]*scaler,
                       struct.unpack('f', filePipe.read(floatLength))[0]*scaler]
            Vertex3 = [struct.unpack('f', filePipe.read(floatLength))[0]*scaler,
                       struct.unpack('f', filePipe.read(floatLength))[0]*scaler,
                       struct.unpack('f', filePipe.read(floatLength))[0]*scaler]
            filePipe.read(endLength)
            Models[-1][1].append([Normal, Vertex1, Vertex2, Vertex3])
        except:
            print("error reading facets")
            break
    filePipe.close()
    return Models

def newARM(seeder = {'Trans':{'x':0, 'y':0, 'z':0}, 'Rot':{'x':0, 'y':0, 'z':0}}):
    import tkinter, tkinter.ttk
    font_size = 14
    newArm = tkinter.Tk()
    newArm.title('New arm placement vector')
    newArm.minsize(width=100, height=100)
    goButton = tkinter.Button(newArm, text="Select", font=("Arial", font_size, "bold"))
    armStringVars = {'Trans': {'x': tkinter.StringVar(),
                               'y': tkinter.StringVar(),
                               'z': tkinter.StringVar()},
                     'Rot': {'x': tkinter.StringVar(),
                             'y': tkinter.StringVar(),
                             'z': tkinter.StringVar()}}
    for item1 in armStringVars.keys() :
        for item2 in armStringVars[item1].keys():
            armStringVars[item1][item2].set(str(seeder[item1][item2]))
    armEntries = {'Trans': {'x': tkinter.Entry(newArm, textvariable=armStringVars['Trans']['x']),
                            'y': tkinter.Entry(newArm, textvariable=armStringVars['Trans']['y']),
                            'z': tkinter.Entry(newArm, textvariable=armStringVars['Trans']['z'])},
                  'Rot': {'x': tkinter.Entry(newArm, textvariable=armStringVars['Rot']['x']),
                          'y': tkinter.Entry(newArm, textvariable=armStringVars['Rot']['y']),
                          'z': tkinter.Entry(newArm, textvariable=armStringVars['Rot']['z'])}}
    armEntries['Trans']['x'].grid(row=1, column=1, columnspan=2)
    armEntries['Trans']['y'].grid(row=1, column=3, columnspan=2)
    armEntries['Trans']['z'].grid(row=1, column=5, columnspan=2)
    armEntries['Rot']['x'].grid(row=2, column=1, columnspan=2)
    armEntries['Rot']['y'].grid(row=2, column=3, columnspan=2)
    armEntries['Rot']['z'].grid(row=2, column=5, columnspan=2)
    goButton.grid(row=3, column=2, columnspan=3)
    armPos = None
    def GoButton():
        #global armStringVars, newArm
        newArm.quit()
        newArm.destroy()
    goButton.configure(command=GoButton)
    newArm.mainloop()
    print(armStringVars)
    for item1 in armStringVars.keys():
        for item2 in armStringVars[item1].keys():
            armStringVars[item1][item2] = float(armStringVars[item1][item2].get())
    print(armStringVars)
    return armStringVars

def EditDictionary(data):
    import tkinter
    from tkinter import ttk
    def Cancel():
        root.destroy()
    def Save():
        for i in range(len(keys)):
            try:
                data[keys[i]] = float(valueStringVars[i].get())
            except:
                pass
        root.destroy()
    root = tkinter.Tk()
    root.title("Edit Dictionary")
    frame = ttk.Frame(root, padding="3 3 12 12")
    frame.grid(column=0, row=0)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)
    keys = list(data.keys())
    valueStringVars = []
    valueEntries = []
    for i in range(len(keys)):
        valueStringVars.append(tkinter.StringVar(value=data[keys[i]]))
        valueEntries.append(ttk.Entry(frame, textvariable=valueStringVars[i], width='10'))
        valueEntries[i].grid(column=i+1, row=2)
        ttk.Label(frame, text=keys[i]).grid(column=i + 1, row=1)
    ttk.Button(frame, text="Save", command=Save).grid(column=1, row=3)
    ttk.Button(frame, text="Cancel", command=Cancel).grid(column=2, row=3)
    for child in frame.winfo_children():
        child.grid_configure(padx=5, pady=5)
    root.protocol("WM_DELETE_WINDOW", Cancel)
    root.mainloop()
    return data


def SaveLoadSequence():
    import tkinter
    from tkinter import ttk

    global save
    save = None

    def Load():
        global save
        save = False
        root.destroy()

    def Save():
        global save
        save = True
        root.destroy()

    root = tkinter.Tk()
    root.title("Save/Load Sequence")

    frame = ttk.Frame(root, padding="3 3 12 12")
    frame.grid(column=0, row=0)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    filename = tkinter.StringVar(value='Sequence.txt')
    ttk.Label(frame, text='Filename').grid(column=2, row=1)
    ttk.Entry(frame, textvariable=filename, width='20').grid(column=2, row=2)

    ttk.Button(frame, text="Save", command=Save).grid(column=1, row=3)
    ttk.Button(frame, text="Load", command=Load).grid(column=3, row=3)

    for child in frame.winfo_children():
        child.grid_configure(padx=5, pady=5)

    root.mainloop()
    return [save, filename.get()]