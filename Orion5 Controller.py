import sys
if not './Libraries/' in sys.path:
    sys.path.append('./Libraries/')
from MathADV import *
from General import *
from pyglet.gl import *
from pyglet.window import key
import Orion5
import copy, ctypes

print('KEYBOARD CONTROLS:',
      '\n   Right - Extends tool point',
      '\n   Left - Retracts tool point\nUp - Tool point up',
      '\n   Down - Tool point down\nHome - Attack angle down',
      '\n   PageUp - Attack angle up\nPageDown - Claw close',
      '\n   END - Claw open\nDelete - Attack distance out',
      '\n   Backspace - Attack distance in',
      '\n   CTRL_Left - Slew left\nCTRL_Right - Slew right',
      '\n   CTRL_END - Read from arm',
      '\n   CTRL_HOME - Write to arm',
      '\n   A - toggle - Put the visualiser into "Arm controls model" mode',
      '\n   Q - toggle - Put the visualiser into "Model controls arm" mode',
      '\nMOUSE CONTROLS',
      '\n   Left click drag rotates model by X/Y axis',
      '\n   Shift+ Left click drag rotates model by X/Z axis',
      '\n   Right click drag moves the model around',
      '\nEXPERIMENTAL BELOW',
      '\n   D - Record position to current sequence in memory',
      '\n   E - Force current position to be current sequence element',
      '\n   S - cycle sequence toward the end (wraps)',
      '\n   W - Cycle sequence toward the start (wraps)',
      '\n   C - Save current sequence set to the txt file in the sequence folder TODOs here',
      '\n   X - Read the sequence in the sequence.txt in the sequence folder TODOs here',
      '\n   Z - Play sequence currently loaded...  major TODOs as it relies as it needs',
      '\n       the joint to get within X of angle to tick the sequence as having been reached')

ZONEWIDTH = 25
WindowProps = [800, 600]
WINDOW   = [WindowProps[0] + 4 * ZONEWIDTH, WindowProps[1] + 2 * ZONEWIDTH]
INCREMENT = 5
CONTROLZPOSITION = -100
CONTROLSCALER = 0.097
CONTROLSIZE = ZONEWIDTH*CONTROLSCALER

seeder = [{'Trans': {'x': 0, 'y': -700, 'z': 0}, 'Rot': {'x': 0, 'y': 0, 'z': 180}}]
arm = {'id':0, 'coms':['COM8'], 'arms':[{'arm':None, 'Trans':{'x':0, 'y':0, 'z':0}, 'Rot':{'x':0, 'y':0, 'z':0}}]} #arm['arms'][arm['id']]['arm'].
ORION5 = None
SEQUENCEFOLDER = './Sequences/'
SEQUENCEBASENAME = 'Sequence'
SEQUENCEEXTENSION = '.txt'
SCALER = 10

class Window(pyglet.window.Window):
    _Widgets = {'Selected':None, 'Widgets':[]}
    _cameraVector = {'xOffset':160, 'yOffset':-100, 'zOffset':-300*SCALER, 'xRotation':-80, 'yRotation':0, 'zRotation':-150, 'scaler':SCALER}
    _windowConstants = [50, -100*SCALER, 0.097, None,
                        [['Claw', 'Attack Angle', 'X', 'Y', 'Attack Depth', 'Turret'], None,
                         [[0, 0, True, key.MOTION_END_OF_LINE, key.MOTION_NEXT_PAGE],
                          [0, 0, True, key.MOTION_PREVIOUS_PAGE, key.MOTION_BEGINNING_OF_LINE],
                          [0, 0, False, key.MOTION_LEFT, key.MOTION_RIGHT],
                          [0, 0, True, key.MOTION_UP, key.MOTION_DOWN],
                          [0, 0, True, key.MOTION_BACKSPACE, key.MOTION_DELETE],
                          [0, 0, False, key.MOTION_PREVIOUS_WORD, key.MOTION_NEXT_WORD]]]] #_windowConstants[4]
    _controlState = [-1, -1, -1, False, False, False, False, None, None, None, [0,0], None] #_controlState[11]
    _armConstants = [{'Shoulder': (1+(52/28))},
                     [{'Turret':100.0,'Shoulder':100.0,'Elbow':100.0,'Wrist':100.0,'Claw':100.0},
                      ['Turret','Shoulder','Elbow','Wrist','Claw']],
                     {'X lims': [500.0, 1.0, -250.0, False],
                      'Z lims': [500.0, 1.0, -250.0, False],
                      'Attack Angle lims': [360.0, 1.0, 0.0, True],
                      'Attack Depth lims': [500.0, 1.0, -250.0, False],
                      'Claw lims': [250.0, 1.0, 20.0, False],
                      'Turret lims': [360.0, 1.0, 0.0, True],
                      'Shoulder lims': [360.0, 1.0, 0.0, True],
                      'Bicep lims': [360.0, 1.0, 0.0, True],
                      'Wrist lims': [360.0, 1.0, 0.0, True],
                      'Bicep Len': 170.384,
                      'Forearm Len': 136.307,
                      'Wrist 2 Claw': 85.25,
                      'Key IDs': [[key.MOTION_END_OF_LINE, 'Claw', True],
                                  [key.MOTION_NEXT_PAGE, 'Claw', False],
                                  [key.MOTION_UP, 'Z', True],
                                  [key.MOTION_DOWN, 'Z', False],
                                  [key.MOTION_LEFT, 'X', True],
                                  [key.MOTION_RIGHT, 'X', False],
                                  [key.MOTION_PREVIOUS_WORD, 'Turret', True],
                                  [key.MOTION_NEXT_WORD, 'Turret', False],
                                  [key.MOTION_PREVIOUS_PAGE, 'Attack Angle', True],
                                  [key.MOTION_BEGINNING_OF_LINE, 'Attack Angle', False],
                                  [key.MOTION_BACKSPACE, 'Attack Depth', True],
                                  [key.MOTION_DELETE, 'Attack Depth', False]]}] #self._armConstants[2]
    _armVARS = [{'X': 400.0,
                'Z': 50.0,
                'Attack Angle': 0.0,
                'Attack Depth': 50.0,
                'Wrist Pos': [0.0, 0.0, 0.0],
                'Elbow Pos': [0.0, 0.0, 0.0],
                'Shoulder Pos': [-30.309, 0.0, 53.0],
                'Elbow Angle': 0.0,
                'Turret': 180.0,
                'Shoulder': 0.0,
                'Elbow': 0.0,
                'Wrist': 0.0,
                'Claw': 200.0,
                'OLD': {'X': 400.0,
                        'Z': 50.0,
                        'Attack Angle': 0.0,
                        'Attack Depth': 50.0,
                        'Wrist Pos': [0.0, 0.0, 0.0],
                        'Elbow Pos': [0.0, 0.0, 0.0],
                        'Shoulder Pos': [-30.309, 0.0, 53.0],
                        'Elbow Angle': 0.0,
                        'Turret': 180.0,
                        'Shoulder': 0.0,
                        'Elbow': 0.0,
                        'Wrist': 0.0,
                        'Claw': 200.0, },
                'Iter': ['X',
                         'Z',
                         'Attack Angle',
                         'Attack Depth',
                         'Wrist Pos',
                         'Elbow Pos',
                         'Shoulder Pos',
                         'Elbow Angle',
                         'Turret',
                         'Shoulder',
                         'Elbow',
                         'Wrist',
                         'Claw']}] #_armVARS[arm['id']]
    _armObjects = [[], None, []] #_armObjects[2] #_armObjects
    _sequence = [[[]], -1] #_sequence[1][0]
    _objects = [[], None, [], []]

    class Widgets():
        _fontSizeScroll = 15
        _fontSizeMenu = 10
        _scrollDimensions = {'w':50}
        _menuDimensions = {'x':50, 'y':20}
        _textShift = -6
        _3dFactor = 0.097
        def __init__(self):
            self._menuDimensions['x1'] = (self._menuDimensions['x'] * self._3dFactor) / 2
            self._menuDimensions['y1'] = (self._menuDimensions['y'] * self._3dFactor) / 2
            self._scrollDimensions['w1'] = (self._scrollDimensions['w'] * self._3dFactor) / 2
            self._scrollDimensions['w2'] = self._scrollDimensions['w'] * self._3dFactor
        def ScrollButton(self):
            self._scrollButton = pyglet.graphics.Batch()
            div = 2.2
            vertices = [-self._scrollDimensions['w2'] / div, -self._scrollDimensions['w2'] / div, 0,
                        self._scrollDimensions['w2'] / div, -self._scrollDimensions['w2'] / div, 0,
                        -self._scrollDimensions['w2'] / div, self._scrollDimensions['w2'] / div, 0,
                        -self._scrollDimensions['w2'] / div, self._scrollDimensions['w2'] / div, 0,
                        self._scrollDimensions['w2'] / div, -self._scrollDimensions['w2'] / div, 0,
                        self._scrollDimensions['w2'] / div, self._scrollDimensions['w2'] / div, 0]
            normals = [0.0, 0.0, 1.0,
                       0.0, 0.0, 1.0,
                       0.0, 0.0, 1.0,
                       0.0, 0.0, 1.0,
                       0.0, 0.0, 1.0,
                       0.0, 0.0, 1.0]
            indices = range(6)
            self._scrollButton.add_indexed(len(vertices) // 3,
                                                    GL_TRIANGLES,
                                                    None,  # group,
                                                    indices,
                                                    ('v3f/static', vertices),
                                                    ('n3f/static', normals))
        def MenuButton(self):
            self._menuButton = pyglet.graphics.Batch()
            div = 2.2
            vertices = [-self._menuDimensions['x1'] / div, -self._menuDimensions['y1'] / div, 0,
                        self._menuDimensions['x1'] / div, -self._menuDimensions['y1'] / div, 0,
                        -self._menuDimensions['x1'] / div, self._menuDimensions['y1'] / div, 0,
                        -self._menuDimensions['x1'] / div, self._menuDimensions['y1'] / div, 0,
                        self._menuDimensions['x1'] / div, -self._menuDimensions['y1'] / div, 0,
                        self._menuDimensions['x1'] / div, self._menuDimensions['y1'] / div, 0]
            normals = [0.0, 0.0, 1.0,
                       0.0, 0.0, 1.0,
                       0.0, 0.0, 1.0,
                       0.0, 0.0, 1.0,
                       0.0, 0.0, 1.0,
                       0.0, 0.0, 1.0]
            indices = range(6)
            self._menuButton.add_indexed(len(vertices) // 3,
                                                    GL_TRIANGLES,
                                                    None,  # group,
                                                    indices,
                                                    ('v3f/static', vertices),
                                                    ('n3f/static', normals))

    class ScrollBar(Widgets):
        Datum = None
        def __init__(self, Input = {'Vertical':True, 'Text':'Yolo', 'x':0, 'y':0}):
            Window.Widgets.__init__(self)
            self.Datum = Input
            if Input['Vertical']:
                temp = Input['Text'][0]
                for iterator in range(1, len(Input['Text'])):
                    temp = temp + '\n' + Input['Text'][iterator]
                Input['Text'] = temp
                self.Label = pyglet.text.Label(Input['Text'], font_name='ARIAL', font_size=15,
                                            x=self._textShift, y=0, align = 'center',
                                            anchor_x='center', anchor_y='center', multiline=True, width=1)

    class SubMenu(Widgets):
        _datum = None
        _options = []
        def __init__(self, Input = {'Text':'Yolo', 'x':0, 'y':0}):
            Window.Widgets.__init__(self)
            self.Datum = Input

    class MenuOption(Widgets):
        _datum = None
        def __init__(self, Input = {'Text':'Yolo', 'x':0, 'y':0}):
            Window.Widgets.__init__(self)
            self.Datum = Input

    def __init__(self, width, height, title=''):
        image = pyglet.image.load('./Libraries/RR_logo_60x60.png')
        shift = -6
        self.thing = [pyglet.text.Label('C\nL\nA\nW\n \nO\nP\nE\nN\nI\nN\nG', font_name='ARIAL', font_size=15,
                                        x=shift, y=0, align = 'center',
                                        anchor_x='center', anchor_y='center', multiline=True, width=1),
                      pyglet.text.Label('W\nR\nI\nS\nT\n \nA\nN\nG\nL\nE', font_name='ARIAL', font_size=15,
                                        x=shift, y=0, align = 'center',
                                        anchor_x='center', anchor_y='center', multiline=True, width=1),
                      pyglet.text.Label('TOOL RADIUS', font_name='ARIAL', font_size=15,
                                        x=shift, y=0, align = 'center',
                                        anchor_x='center', anchor_y='center'),
                      pyglet.text.Label('T O O L\n \nH E I G H T', font_name='ARIAL', font_size=15,
                                        x=shift, y=0, align = 'center',
                                        anchor_x='center', anchor_y='center', multiline = True, width = 1),
                      pyglet.text.Label('T\nO\nO\nL\n \nD\nI\nS\nT\nA\nN\nC\nE', font_name='ARIAL', font_size=15,
                                        x=shift, y=0, align = 'center',
                                        anchor_x='center', anchor_y='center', multiline=True, width=1),
                      pyglet.text.Label('TURRET ANGLE', font_name='ARIAL', font_size=15,
                                        x=shift, y=0, align = 'center',
                                        anchor_x='center', anchor_y='center'),
                      pyglet.sprite.Sprite(image, x=0, y=0)]

        global arm
        pyglet.window.Window.__init__(self, width, height, title, resizable=True, style = pyglet.window.Window.WINDOW_STYLE_DEFAULT )
        # select libExtension based on platform
        libExtension = '.dll' # windows as default
        if sys.platform == 'darwin':
            libName = '.dylib' # Mac OS
        elif 'linux' in sys.platform:
            libExtension = '.so'# linux based
        # load functions from C dynamic library
        clib = ctypes.cdll.LoadLibrary('Libraries/libOrion5Kinematics' + libExtension)
        self.IKinematics = clib.IKinematics
        self.IKinematics.restype = C_ArmVars
        self.CollisionCheck = clib.CollisionCheck
        self.CollisionCheck.restype = ctypes.c_int
        self._controlState[8] = [WINDOW[0], WINDOW[1]]
        self.set_minimum_size(self._controlState[8][0], self._controlState[8][1])
        self._controlState[9] = [['Claw', [self._controlState[8][0] - self._windowConstants[0],
                                           self._windowConstants[0],
                                           self._controlState[8][0],
                                           self._controlState[8][1]],
                                  [0, 0]],
                                 ['Attack Angle', [self._windowConstants[0],
                                                   2 * self._windowConstants[0],
                                                   2 * self._windowConstants[0],
                                                   self._controlState[8][1]],
                                  [0, 0]],
                                 ['X', [0,
                                        0,
                                        self._controlState[8][0],
                                        self._windowConstants[0]],
                                  [0, 0]],
                                 ['Y', [0,
                                        self._windowConstants[0],
                                        self._windowConstants[0],
                                        self._controlState[8][1]],
                                  [0, 0]],
                                 ['Attack Depth', [self._controlState[8][0] - 2 * self._windowConstants[0],
                                                   2 * self._windowConstants[0],
                                                   self._controlState[8][0] - self._windowConstants[0],
                                                   self._controlState[8][1]],
                                  [0, 0]],
                                 ['Turret', [self._windowConstants[0],
                                             self._windowConstants[0],
                                             self._controlState[8][0] - self._windowConstants[0],
                                             2 * self._windowConstants[0]],
                                  [0, 0]]]
        self._controlState[11] = {'Claw':[(self._controlState[8][0]/2)-self._windowConstants[0]/2,
                                          (self._windowConstants[0] - self._controlState[8][1] / 2) + self._windowConstants[0] / 2,
                                          0,
                                          abs((self._windowConstants[0] - self._controlState[8][1] / 2) + self._windowConstants[0]/2)*2 + self._windowConstants[0],
                                          self._armConstants[2]['Claw lims'][2],
                                          self._armConstants[2]['Claw lims'][0]-self._armConstants[2]['Claw lims'][2],
                                          0],
                                'Attack Angle':[(self._windowConstants[0]-self._controlState[8][0]/2)+self._windowConstants[0]/2,
                                                (2 * self._windowConstants[0] - self._controlState[8][1] / 2) + self._windowConstants[0] / 2,
                                                0,
                                                abs((2 * self._windowConstants[0] - self._controlState[8][1] / 2) + self._windowConstants[0] / 2)*2 + 2 * self._windowConstants[0],
                                                self._armConstants[2]['Attack Angle lims'][2],
                                                self._armConstants[2]['Attack Angle lims'][0] - self._armConstants[2]['Attack Angle lims'][2],
                                                'Attack Angle',
                                                0.5],
                                'X':[(-self._controlState[8][0]/2)+self._windowConstants[0]/2,
                                     (-self._controlState[8][1]/2)+self._windowConstants[0]/2,
                                     abs((-self._controlState[8][0]/2)+self._windowConstants[0]/2)*2,
                                     0,
                                     self._armConstants[2]['X lims'][2],
                                     self._armConstants[2]['X lims'][0] - self._armConstants[2]['X lims'][2],
                                     'X',
                                     0],
                                'Y':[(-self._controlState[8][0]/2)+self._windowConstants[0]/2,
                                     (self._windowConstants[0] - self._controlState[8][1] / 2) + self._windowConstants[0] / 2,
                                     0,
                                     abs((self._windowConstants[0] - self._controlState[8][1] / 2) + self._windowConstants[0] / 2)*2 + self._windowConstants[0],
                                     self._armConstants[2]['Z lims'][2],
                                     self._armConstants[2]['Z lims'][0] - self._armConstants[2]['Z lims'][2],
                                     'Z',
                                     0],
                                'Attack Depth':[(self._controlState[8][0]/2-self._windowConstants[0])-self._windowConstants[0]/2,
                                                (2*self._windowConstants[0]-self._controlState[8][1] / 2) + self._windowConstants[0] / 2,
                                                0,
                                                abs((2*self._windowConstants[0]-self._controlState[8][1] / 2) + self._windowConstants[0] / 2)*2 + 2 * self._windowConstants[0],
                                                self._armConstants[2]['Attack Depth lims'][2],
                                                self._armConstants[2]['Attack Depth lims'][0] - self._armConstants[2]['Attack Depth lims'][2],
                                                'Attack Depth',
                                                0],
                                'Turret':[(self._windowConstants[0]-self._controlState[8][0]/2)+self._windowConstants[0]/2,
                                                (self._windowConstants[0]-self._controlState[8][1]/2)+self._windowConstants[0]/2,
                                                abs((self._windowConstants[0] - self._controlState[8][0] / 2) + self._windowConstants[0] / 2) * 2,
                                                0,
                                                  self._armConstants[2]['Turret lims'][2],
                                                  self._armConstants[2]['Turret lims'][0] - self._armConstants[2]['Turret lims'][2],
                                                'Turret',
                                                0]}
        self._controlState[7] = self._windowConstants[0] * self._windowConstants[2]
        glClearColor(0, 0, 0, 1)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_NORMALIZE)
        factor = [.1,.5,.1]
        glLightfv(GL_LIGHT1, GL_SPECULAR, vec(1.0*factor[1],1.0*factor[1],1.0*factor[1],1.0*factor[1]))
        glEnable(GL_LIGHT1)
        arm['arms'][arm['id']]['arm'] = Orion5.Orion5(arm['coms'][arm['id']])
        self.on_text_motion(False)
        self._windowConstants[4][1] = pyglet.graphics.Batch()
        div = 2.2
        vertices = [-self._controlState[7] / div, -self._controlState[7] / div, 0,
                    self._controlState[7] / div, -self._controlState[7] / div, 0,
                    -self._controlState[7] / div, self._controlState[7] / div, 0,
                    -self._controlState[7] / div, self._controlState[7] / div, 0,
                    self._controlState[7] / div, -self._controlState[7] / div, 0,
                    self._controlState[7] / div, self._controlState[7] / div, 0]
        normals = [0.0,0.0,1.0,
                   0.0,0.0,1.0,
                   0.0,0.0,1.0,
                   0.0,0.0,1.0,
                   0.0,0.0,1.0,
                   0.0,0.0,1.0]
        indices = range(6)
        self._windowConstants[4][1].add_indexed(len(vertices) // 3,
                                      GL_TRIANGLES,
                                      None,  # group,
                                      indices,
                                      ('v3f/static', vertices),
                                      ('n3f/static', normals))
        ModelSets = PolyRead('STLs/3dObjects.SAM', self._cameraVector['scaler'])
        self._armObjects[1] = len(ModelSets)
        for iterator1 in range(self._armObjects[1]):
            self._armObjects[2].append(ModelSets[iterator1][0][0])
            self._armObjects[0].append([pyglet.graphics.Batch(), [ModelSets[iterator1][0][1][0],
                                                            ModelSets[iterator1][0][1][1],
                                                            ModelSets[iterator1][0][1][2],
                                                            ModelSets[iterator1][0][1][3]]])
            vertices = []
            normals = []
            for iterator2 in range(len(ModelSets[iterator1][1])):
                for iterator3 in range(1, 4):
                    vertices.extend(ModelSets[iterator1][1][iterator2][iterator3])
                    normals.extend(ModelSets[iterator1][1][iterator2][0])
            # Create a list of triangle indices.
            indices = range(3 * len(ModelSets[iterator1][1]))  # [[3*i, 3*i+1, 3*i+2] for i in xrange(len(facets))]
            self._armObjects[0][-1][0].add_indexed(len(vertices) // 3,
                                             GL_TRIANGLES,
                                             None,  # group,
                                             indices,
                                             ('v3f/static', vertices),
                                             ('n3f/static', normals))
        pyglet.clock.schedule_interval(self.update, 1 / 20.0)
        Offsets = [[0.0, 0.0, 0.0], [200.0, 200.0, 200.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0],
                   [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
        Rotations = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0],
                     [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]

        ModelSets = PopulateModels(PullFileNames('stl', './STLs/'), self._cameraVector['scaler'])
        self._objects[1] = len(ModelSets)
        for iterator1 in range(self._objects[1]):
            self._objects[3].append({'Trans': {'x': Offsets[ModelSets[iterator1][0][0]][0],
                                               'y': Offsets[ModelSets[iterator1][0][0]][1],
                                               'z': Offsets[ModelSets[iterator1][0][0]][2]},
                                     'Rot': {'x': Rotations[ModelSets[iterator1][0][0]][0],
                                             'y': Rotations[ModelSets[iterator1][0][0]][1],
                                             'z': Rotations[ModelSets[iterator1][0][0]][2]}})
            self._objects[2].append(ModelSets[iterator1][0][0])
            self._objects[0].append([pyglet.graphics.Batch(), [ModelSets[iterator1][0][1][0],
                                                               ModelSets[iterator1][0][1][1],
                                                               ModelSets[iterator1][0][1][2],
                                                               ModelSets[iterator1][0][1][3]]])
            vertices = []
            normals = []
            for iterator2 in range(len(ModelSets[iterator1][1])):
                for iterator3 in range(1, 4):
                    vertices.extend(ModelSets[iterator1][1][iterator2][iterator3])
                    normals.extend(ModelSets[iterator1][1][iterator2][0])
            # Create a list of triangle indices.
            indices = range(3 * len(ModelSets[iterator1][1]))  # [[3*i, 3*i+1, 3*i+2] for i in xrange(len(facets))]
            self._objects[0][-1][0].add_indexed(len(vertices) // 3,
                                                GL_TRIANGLES,
                                                None,  # group,
                                                indices,
                                                ('v3f/static', vertices),
                                                ('n3f/static', normals))
        for item1 in self._windowConstants[4][2]:
            self.on_text_motion(item1[3])
            self.on_text_motion(item1[4])

    def on_resize(self, width, height):
        # set the Viewport
        glViewport(0, 0, width, height)
        self._controlState[8] = [width, height]
        #self.set_size(width, height)
        self._controlState[7] = self._windowConstants[0] * self._windowConstants[2]
        self._controlState[9] = [['Claw', [self._controlState[8][0] - self._windowConstants[0],
                                 self._windowConstants[0],
                                 self._controlState[8][0],
                                 self._controlState[8][1]],
                        [0, 0]],  # Third Zone Second Left, Claw Open?
                       ['Attack Angle', [self._windowConstants[0],
                                         2 * self._windowConstants[0],
                                         2 * self._windowConstants[0],
                                         self._controlState[8][1]],
                        [0, 0]],  # Fifth Zone Second from Right, Attack Angle
                       ['X', [0,
                              0,
                              self._controlState[8][0],
                              self._windowConstants[0]],
                        [0, 0]],  # Second zone bottom, X Position
                       ['Y', [0,
                              self._windowConstants[0],
                              self._windowConstants[0],
                              self._controlState[8][1]],
                        [0, 0]],  # First Zone Left, Y Position
                       ['Attack Depth', [self._controlState[8][0] - 2 * self._windowConstants[0],
                                         2 * self._windowConstants[0],
                                         self._controlState[8][0] - self._windowConstants[0],
                                         self._controlState[8][1]],
                        [0, 0]],  # Sixth Zone Right, Attack Depth
                       ['Turret', [self._windowConstants[0],
                                   self._windowConstants[0],
                                   self._controlState[8][0] - self._windowConstants[0],
                                   2 * self._windowConstants[0]],
                        [0, 0]]]  # Fourth Zone Second from Bottom, Turret Angle
        self._controlState[11] = {'Claw': [(self._controlState[8][0] / 2) - self._windowConstants[0] / 2,
                                      (self._windowConstants[0] - self._controlState[8][1] / 2) + self._windowConstants[0] / 2,
                                      0,
                                      abs((self._windowConstants[0] - self._controlState[8][
                                          1] / 2) + self._windowConstants[0] / 2) * 2 + self._windowConstants[0],
                                      self._armConstants[2]['Claw lims'][2],
                                      self._armConstants[2]['Claw lims'][0] - self._armConstants[2]['Claw lims'][2],
                                      'Claw',
                                      0],
                             'Attack Angle': [(self._windowConstants[0] - self._controlState[8][0] / 2) + self._windowConstants[0] / 2,
                                              (2 * self._windowConstants[0] - self._controlState[8][1] / 2) + self._windowConstants[0] / 2,
                                              0,
                                              abs((2 * self._windowConstants[0] - self._controlState[8][
                                                  1] / 2) + self._windowConstants[0] / 2) * 2 + 2 * self._windowConstants[0],
                                              self._armConstants[2]['Attack Angle lims'][2],
                                              self._armConstants[2]['Attack Angle lims'][0] - self._armConstants[2]['Attack Angle lims'][
                                                  2],
                                              'Attack Angle',
                                              .5],
                             'X': [(-self._controlState[8][0] / 2) + self._windowConstants[0] / 2,
                                   (-self._controlState[8][1] / 2) + self._windowConstants[0] / 2,
                                   abs((-self._controlState[8][0] / 2) + self._windowConstants[0] / 2) * 2,
                                   0,
                                   self._armConstants[2]['X lims'][2],
                                   self._armConstants[2]['X lims'][0] - self._armConstants[2]['X lims'][2],
                                   'X',
                                   0],
                             'Y': [(-self._controlState[8][0] / 2) + self._windowConstants[0] / 2,
                                   (self._windowConstants[0] - self._controlState[8][1] / 2) + self._windowConstants[0] / 2,
                                   0,
                                   abs((self._windowConstants[0] - self._controlState[8][
                                       1] / 2) + self._windowConstants[0] / 2) * 2 + self._windowConstants[0],
                                   self._armConstants[2]['Z lims'][2],
                                   self._armConstants[2]['Z lims'][0] - self._armConstants[2]['Z lims'][2],
                                   'Z',
                                   0],
                             'Attack Depth': [(self._controlState[8][0] / 2 - self._windowConstants[0]) - self._windowConstants[0] / 2,
                                              (2 * self._windowConstants[0] - self._controlState[8][1] / 2) + self._windowConstants[0] / 2,
                                              0,
                                              abs((2 * self._windowConstants[0] - self._controlState[8][
                                                  1] / 2) + self._windowConstants[0] / 2) * 2 + 2 * self._windowConstants[0],
                                              self._armConstants[2]['Attack Depth lims'][2],
                                              self._armConstants[2]['Attack Depth lims'][0] - self._armConstants[2]['Attack Depth lims'][
                                                  2],
                                              'Attack Depth',
                                              0],
                             'Turret': [(self._windowConstants[0] - self._controlState[8][0] / 2) + self._windowConstants[0] / 2,
                                        (self._windowConstants[0] - self._controlState[8][1] / 2) + self._windowConstants[0] / 2,
                                        abs((self._windowConstants[0] - self._controlState[8][0] / 2) + self._windowConstants[0] / 2) * 2,
                                        0,
                                        self._armConstants[2]['Turret lims'][2],
                                        self._armConstants[2]['Turret lims'][0] - self._armConstants[2]['Turret lims'][2],
                                        'Turret',
                                        0]}
        smaller = width
        if width > height:
            smaller = height
        self._windowConstants[1] = - (100 + ((smaller-650)*.153))

        # using Projection mode
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspectRatio = width / height
        gluPerspective(35, aspectRatio, 1, 20000*self._cameraVector['scaler'])
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, -500)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self._cameraVector['zOffset'] += scroll_y*50*self._cameraVector['scaler']
        self._controlState[10][0] = x
        self._controlState[10][1] = y

    def on_mouse_press(self, x, y, button, modifiers):
        self._controlState[0] = button
        self._controlState[2] = modifiers
        self._controlState[1] = 0#iterator1
        self._controlState[10][0] = x
        self._controlState[10][1] = y
        for iterator1 in range(len(self._controlState[9])):
            if ((abs((x - self._controlState[8][0] / 2) * self._windowConstants[2] - self._windowConstants[4][2][iterator1][0]) < (self._windowConstants[0] / 2)*self._windowConstants[2])
                and (abs((y - self._controlState[8][1] / 2) * self._windowConstants[2] - self._windowConstants[4][2][iterator1][1]) < (self._windowConstants[0] / 2)*self._windowConstants[2])):
                self._controlState[1] = iterator1 + 1
        self._controlState[10][0] = x
        self._controlState[10][1] = y

    def on_mouse_release(self, x, y, button, modifiers):
        self._controlState[0] = -1
        self._controlState[1] = -1
        self._controlState[2] = -1
        self._controlState[10][0] = x
        self._controlState[10][1] = y

    def on_key_press(self, symbol, modifiers):
        if symbol == key.Q:
            self._controlState[4] = False
            self._controlState[3] = not self._controlState[3]
            if self._controlState[3]:
                arm['arms'][arm['id']]['arm'].enableTorque()
            else:
                arm['arms'][arm['id']]['arm'].releaseTorque()
        elif symbol == key.A:
            arm['arms'][arm['id']]['arm'].releaseTorque()
            self._controlState[3] = False
            self._controlState[4] = not self._controlState[4]
        elif symbol == key.E:
            if len(self._sequence[0][0]) != 0:
                #Show entry toggle
                self._controlState[5] = not self._controlState[5]
        elif symbol == key.W:
            if len(self._sequence[0][0]) != 0:
                self._sequence[1] -= 1
            if self._sequence[1] < -1:
                self._sequence[1] = len(self._sequence[0][0])-2
        elif symbol == key.S:
            if len(self._sequence[0][0]) != 0:
                self._sequence[1] += 1
            if self._sequence[1] > len(self._sequence[0][0])-2:
                self._sequence[1] = -1
        elif symbol == key.D:
            # record entry
            for iterator1 in range(len(self._sequence[0])):
                self._sequence[0][iterator1].append([['Turret', copy.copy(self._armVARS[iterator1]['Turret'])],
                                                     ['Shoulder', copy.copy(self._armVARS[iterator1]['Shoulder'])],
                                                     ['Elbow', copy.copy(self._armVARS[iterator1]['Elbow'])],
                                                     ['Wrist', copy.copy(self._armVARS[iterator1]['Wrist'])],
                                                     ['Claw', copy.copy(self._armVARS[iterator1]['Claw'])],
                                                     [0,2]])
        elif symbol == key.Z:
            if len(self._sequence[0][0]) != 0:
                #run sequence toggle
                self._controlState[6] = not self._controlState[6]
                if self._controlState[6]:
                    self._controlState[5] = True
        elif symbol == key.X:
            temp = SaveLoadSequence()
            if type(temp[0]) == bool and not temp[0]:
                ID = ''
                entry = ''
                entryList = []
                self._sequence[0] = []
                for iter1 in range(len(arm['arms'])):
                    self._sequence[0].append([])
                filePipe = open(SEQUENCEFOLDER + temp[1], 'r')
                while True:
                    entryList = []
                    entry = filePipe.readline()
                    if entry == '':
                        filePipe.close()
                        break
                    else:
                        iter1 = 0
                        while True:
                            entryList = []
                            if len(entry) < 5:
                                break
                            for iterator in range(5):
                                ID = entry[:entry.find(' ')]
                                entry = entry[entry.find(' ') + 1:]
                                entryList.append([ID, float(entry[:entry.find(' ')])])
                                entry = entry[entry.find(' ') + 1:]
                            entry = entry[entry.find(' ') + 1:]
                            entryList.append([0,float(entry[:entry.find(' ')])])
                            entry = entry[entry.find(' ') + 1:]
                            self._sequence[0][iter1].append(entryList)
                            iter1 += 1
                for item in self._sequence[0]:
                    print(item)
            elif type(temp[0]) == bool and temp[0]:
                if len(self._sequence[0][0]) != 0:
                    filePipe = open(SEQUENCEFOLDER + temp[1], 'w')
                    for iterator1 in range(len(self._sequence[0][0])):
                        for iterator2 in range(len(self._sequence[0])):
                            for item in self._sequence[0][iterator2][iterator1]:
                                if type(item[0]) == str:
                                    filePipe.write(item[0] + ' ' + str(item[1]) + ' ')
                                else:
                                    filePipe.write('TimeDelay ' + str(item[1]) + ' ')
                        filePipe.write('\n')
                    filePipe.close()
        elif symbol == key.ESCAPE:
            self._controlState = [-1, -1, -1, False, False, False, False]
            arm['arms'][arm['id']]['arm'].releaseTorque()
            pyglet.app.exit()
        elif symbol == key.R:
            arm['id'] += 1
            if arm['id'] >= len(arm['arms']):
                arm['id'] = 0
        elif symbol == key.T:
            arm['id'] -= 1
            if arm['id'] < 0:
                arm['id'] = len(arm['arms']) - 1
        elif symbol == key.G:
            # TODO make sure multple arms cant be assigned the same com port by removing entities from the list of comports that already exist in the arm
            for iterator in range(len(arm['coms'])):
                try:
                    arm['coms'][iterator] = str(ComQuery().device)
                    print(arm['coms'][iterator])
                except:
                    pass
            for iterator1 in range(len(arm['arms'])):
                arm['arms'][iterator1]['arm'].exit()
                arm['arms'][iterator1]['arm'] = Orion5.Orion5(arm['coms'][iterator1])
        elif symbol == key.F:
            arm['coms'].append(str(ComQuery().device))
            if len(seeder) > len(arm['arms'])-1:
                arm['arms'].append(newARM(seeder[len(arm['arms'])-1]))
            else:
                arm['arms'].append(newARM())
            arm['arms'][-1]['arm'] = Orion5.Orion5(arm['coms'][-1])

            self._armVARS.append({'X': 400.0,
                                    'Z': 50.0,
                                    'Attack Angle': 0.0,
                                    'Attack Depth': 50.0,
                                    'Wrist Pos': [0.0, 0.0, 0.0],
                                    'Elbow Pos': [0.0, 0.0, 0.0],
                                    'Shoulder Pos': [-30.309, 0.0, 53.0],
                                    'Elbow Angle': 0.0,
                                    'Turret': 180.0,
                                    'Shoulder': 0.0,
                                    'Elbow': 0.0,
                                    'Wrist': 0.0,
                                    'Claw': 200.0,
                                    'OLD': {'X': 400.0,
                                            'Z': 50.0,
                                            'Attack Angle': 0.0,
                                            'Attack Depth': 50.0,
                                            'Wrist Pos': [0.0, 0.0, 0.0],
                                            'Elbow Pos': [0.0, 0.0, 0.0],
                                            'Shoulder Pos': [-30.309, 0.0, 53.0],
                                            'Elbow Angle': 0.0,
                                            'Turret': 180.0,
                                            'Shoulder': 0.0,
                                            'Elbow': 0.0,
                                            'Wrist': 0.0,
                                            'Claw': 200.0, },
                                    'Iter': ['X',
                                             'Z',
                                             'Attack Angle',
                                             'Attack Depth',
                                             'Wrist Pos',
                                             'Elbow Pos',
                                             'Shoulder Pos',
                                             'Elbow Angle',
                                             'Turret',
                                             'Shoulder',
                                             'Elbow',
                                             'Wrist',
                                             'Claw']})
            self._sequence[0].append([])
            for item in self._sequence[0]:
                item = []
            temp = 0 + arm['id']
            arm['id'] = len(arm['arms'])-1
            for item1 in self._windowConstants[4][2]:
                self.on_text_motion(item1[3])
                self.on_text_motion(item1[4])
            arm['id'] = temp
        elif symbol == key.V:
            temp = newARM({'Trans':arm['arms'][arm['id']]['Trans'], 'Rot':arm['arms'][arm['id']]['Rot']})
            arm['arms'][arm['id']]['Trans'] = temp['Trans']
            arm['arms'][arm['id']]['Rot'] = temp['Rot']
        elif symbol == key.B:
            self._armConstants[1][0] = EditDictionary(self._armConstants[1][0])

    def update(self, yoyo):
        if self._controlState[4]:
            for iterator1 in range(len(self._sequence[0])):
                self._armVARS[iterator1]['Turret'] = wrap360f(-arm['arms'][iterator1]['arm'].base.getPosition())
                self._armVARS[iterator1]['Shoulder'] = arm['arms'][iterator1]['arm'].shoulder.getPosition() / self._armConstants[0]['Shoulder']
                self._armVARS[iterator1]['Elbow'] = arm['arms'][iterator1]['arm'].elbow.getPosition()
                self._armVARS[iterator1]['Wrist'] = arm['arms'][iterator1]['arm'].wrist.getPosition()
                self._armVARS[iterator1]['Claw'] = arm['arms'][iterator1]['arm'].claw.getPosition()
        elif self._controlState[5]:
            for iterator1 in range(len(self._sequence[0])):
                self._armVARS[iterator1]['Turret'] = copy.copy(self._sequence[0][iterator1][self._sequence[1]][0][1])
                self._armVARS[iterator1]['Shoulder'] = copy.copy(self._sequence[0][iterator1][self._sequence[1]][1][1])
                self._armVARS[iterator1]['Elbow'] = copy.copy(self._sequence[0][iterator1][self._sequence[1]][2][1])
                self._armVARS[iterator1]['Wrist'] = copy.copy(self._sequence[0][iterator1][self._sequence[1]][3][1])
                self._armVARS[iterator1]['Claw'] = copy.copy(self._sequence[0][iterator1][self._sequence[1]][4][1])
        if ((self._controlState[4] or self._controlState[5]) and self._armVARS[arm['id']]['Turret'] != None):
            for iterator1 in range(len(self._sequence[0])):
                self._armVARS[iterator1]['Elbow Angle'] = self._armVARS[iterator1]['Elbow'] + self._armVARS[iterator1]['Shoulder'] - 180.0
                self._armVARS[iterator1]['Attack Angle'] = self._armVARS[iterator1]['Wrist'] - 180.0 + self._armVARS[iterator1]['Elbow Angle']
                self._armVARS[iterator1]['Elbow Pos'][0] = self._armVARS[iterator1]['Shoulder Pos'][0] + pol2rect(-self._armConstants[2]['Bicep Len'],-self._armVARS[iterator1]['Shoulder'], True)
                self._armVARS[iterator1]['Elbow Pos'][2] = self._armVARS[iterator1]['Shoulder Pos'][2] + pol2rect(-self._armConstants[2]['Bicep Len'],-self._armVARS[iterator1]['Shoulder'], False)
                self._armVARS[iterator1]['Wrist Pos'][0] = self._armVARS[iterator1]['Elbow Pos'][0] - pol2rect(self._armConstants[2]['Forearm Len'],-self._armVARS[iterator1]['Elbow Angle'],True)
                self._armVARS[iterator1]['Wrist Pos'][2] = self._armVARS[iterator1]['Elbow Pos'][2] - pol2rect(self._armConstants[2]['Forearm Len'],-self._armVARS[iterator1]['Elbow Angle'],False)
                self._armVARS[iterator1]['X'] = -self._armVARS[iterator1]['Wrist Pos'][0] + pol2rect((85.25 + self._armVARS[iterator1]['Attack Depth']),self._armVARS[iterator1]['Attack Angle'], True)
                self._armVARS[iterator1]['Z'] = self._armVARS[iterator1]['Wrist Pos'][2] + pol2rect((85.25 + self._armVARS[iterator1]['Attack Depth']),self._armVARS[iterator1]['Attack Angle'], False)
        if self._controlState[6]:
            #sequencer
            if not self._sequence[0][0][self._sequence[1]][5][1] >= 0.0:
                if (abs(DifferentialWrapped360(self._armVARS[arm['id']]['Turret'], -arm['arms'][arm['id']]['arm'].base.getPosition()))
                        + abs(DifferentialWrapped360(self._armVARS[arm['id']]['Shoulder'], arm['arms'][arm['id']]['arm'].shoulder.getPosition() / self._armConstants[0]['Shoulder']) )
                        + abs(DifferentialWrapped360(self._armVARS[arm['id']]['Elbow'], arm['arms'][arm['id']]['arm'].elbow.getPosition()))
                        + abs(DifferentialWrapped360(self._armVARS[arm['id']]['Wrist'], arm['arms'][arm['id']]['arm'].wrist.getPosition()))
                        + abs(DifferentialWrapped360(self._armVARS[arm['id']]['Claw'], arm['arms'][arm['id']]['arm'].claw.getPosition()))) < 12:
                    self._sequence[1] += 1
                    if self._sequence[1] > len(self._sequence[0][0]) - 2: #yo
                        self._sequence[1] = -1
            else: #XXXX
                self._sequence[0][0][self._sequence[1]][5][0] += 0.05
                if self._sequence[0][0][self._sequence[1]][5][0] > self._sequence[0][0][self._sequence[1]][5][1]:
                    self._sequence[0][0][self._sequence[1]][5][0] = 0
                    self._sequence[1] += 1
                    if self._sequence[1] > len(self._sequence[0][0]) - 2:  # yo
                        self._sequence[1] = -1

        if (not self._controlState[4] and self._controlState[3]):
            for iterator1 in range(len(self._sequence[0])):
                temp1 = abs(self._armVARS[iterator1]['Turret'] - arm['arms'][iterator1]['arm'].base.getPosition())
                if temp1 > 180:
                    temp1 -= 180
                temp = [temp1 / self._armConstants[1][0]['Turret'],
                        abs(self._armVARS[iterator1]['Shoulder'] - (arm['arms'][iterator1]['arm'].shoulder.getPosition()/ self._armConstants[0]['Shoulder'])) / self._armConstants[1][0]['Shoulder'],
                        abs(self._armVARS[iterator1]['Elbow'] - arm['arms'][iterator1]['arm'].elbow.getPosition()) / self._armConstants[1][0]['Elbow'],
                        abs(self._armVARS[iterator1]['Wrist'] - arm['arms'][iterator1]['arm'].wrist.getPosition()) / self._armConstants[1][0]['Wrist'],
                        abs(self._armVARS[iterator1]['Claw'] - arm['arms'][iterator1]['arm'].claw.getPosition()) / self._armConstants[1][0]['Claw']]
                maxSpeed = 0
                for item in temp:
                    if item > maxSpeed:
                        maxSpeed = 0.0 + item
                #arm['arms'][iterator1]['arm'].setTimeToGoal(maxSpeed)
                arm['arms'][iterator1]['arm'].base.setGoalPosition(wrap360f(-self._armVARS[iterator1]['Turret']))
                arm['arms'][iterator1]['arm'].shoulder.setGoalPosition(wrap360f(self._armVARS[iterator1]['Shoulder'] * self._armConstants[0]['Shoulder']))
                arm['arms'][iterator1]['arm'].elbow.setGoalPosition(wrap360f(self._armVARS[iterator1]['Elbow']))
                arm['arms'][iterator1]['arm'].wrist.setGoalPosition(wrap360f(self._armVARS[iterator1]['Wrist']))
                arm['arms'][iterator1]['arm'].claw.setGoalPosition(wrap360f(self._armVARS[iterator1]['Claw']))

    def on_draw(self):
        global arm
        # Clear the current GL Window
        self.clear()

        for iterator0 in range(len(arm['arms'])):
            for iterator1 in range(self._armObjects[1]):
                glLoadIdentity()
                glTranslatef(self._cameraVector['xOffset'],
                             self._cameraVector['yOffset'],
                             self._cameraVector['zOffset'] - 650*self._cameraVector['scaler'])
                glRotatef(self._cameraVector['xRotation'], 1, 0, 0)
                glRotatef(self._cameraVector['yRotation'], 0, 1, 0)
                glRotatef(self._cameraVector['zRotation'], 0, 0, 1)
                glTranslatef(arm['arms'][iterator0]['Trans']['x']*self._cameraVector['scaler'],
                             arm['arms'][iterator0]['Trans']['y']*self._cameraVector['scaler'],
                             arm['arms'][iterator0]['Trans']['z']*self._cameraVector['scaler'])
                glRotatef(arm['arms'][iterator0]['Rot']['x'], 1, 0, 0)
                glRotatef(arm['arms'][iterator0]['Rot']['y'], 0, 1, 0)
                glRotatef(arm['arms'][iterator0]['Rot']['z'], 0, 0, 1)

                #Turret Rotate
                if self._armObjects[2][iterator1] > 0:
                    glRotatef(self._armVARS[iterator0]['Turret'], 0, 0, 1)

                #Part Move
                if self._armObjects[2][iterator1] == 2:
                    glTranslatef(self._armVARS[iterator0]['Shoulder Pos'][0]*self._cameraVector['scaler'],
                                 self._armVARS[iterator0]['Shoulder Pos'][1]*self._cameraVector['scaler'],
                                 self._armVARS[iterator0]['Shoulder Pos'][2]*self._cameraVector['scaler'])
                elif self._armObjects[2][iterator1] == 3:
                    glTranslatef(self._armVARS[iterator0]['Elbow Pos'][0]*self._cameraVector['scaler'],
                                 self._armVARS[iterator0]['Elbow Pos'][1]*self._cameraVector['scaler'],
                                 self._armVARS[iterator0]['Elbow Pos'][2]*self._cameraVector['scaler'])
                elif self._armObjects[2][iterator1] == 4:
                    glTranslatef(self._armVARS[iterator0]['Wrist Pos'][0]*self._cameraVector['scaler'],
                                 self._armVARS[iterator0]['Wrist Pos'][1]*self._cameraVector['scaler'],
                                 self._armVARS[iterator0]['Wrist Pos'][2]*self._cameraVector['scaler'])
                elif self._armObjects[2][iterator1] == 5:
                    glTranslatef(self._armVARS[iterator0]['Wrist Pos'][0]*self._cameraVector['scaler'],
                                 (- (self._armVARS[iterator0]['Claw'] - 20) / 11)*self._cameraVector['scaler'],
                                 self._armVARS[iterator0]['Wrist Pos'][2]*self._cameraVector['scaler'])
                elif self._armObjects[2][iterator1] == 6:
                    glTranslatef(self._armVARS[iterator0]['Wrist Pos'][0]*self._cameraVector['scaler'],
                                 ((self._armVARS[iterator0]['Claw'] - 20) / 11)*self._cameraVector['scaler'],
                                 self._armVARS[iterator0]['Wrist Pos'][2]*self._cameraVector['scaler'])

                #Part Rotate
                if self._armObjects[2][iterator1] > 3:
                    glRotatef(self._armVARS[iterator0]['Attack Angle'], 0, 1, 0)
                elif self._armObjects[2][iterator1] == 2:
                    glRotatef(self._armVARS[iterator0]['Shoulder'], 0, 1, 0)
                elif self._armObjects[2][iterator1] == 3:
                    glRotatef(self._armVARS[iterator0]['Elbow Angle'], 0, 1, 0)

                #Draw the Thing
                glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
                glEnable(GL_COLOR_MATERIAL)
                scaler = 1
                if iterator0 == arm['id']:
                    scaler = 1.2
                glColor3f(self._armObjects[0][iterator1][1][0] * scaler,
                          self._armObjects[0][iterator1][1][1] * scaler,
                          self._armObjects[0][iterator1][1][2] * scaler)
                self._armObjects[0][iterator1][0].draw()
                glDisable(GL_COLOR_MATERIAL)

        for iterator1 in range(self._objects[1]):
            glLoadIdentity()
            glTranslatef(self._cameraVector['xOffset'],
                         self._cameraVector['yOffset'],
                         self._cameraVector['zOffset'] - 650*self._cameraVector['scaler'])
            glRotatef(self._cameraVector['xRotation'], 1, 0, 0)
            glRotatef(self._cameraVector['yRotation'], 0, 1, 0)
            glRotatef(self._cameraVector['zRotation'], 0, 0, 1)
            glTranslatef(self._objects[3][iterator1]['Trans']['x']*self._cameraVector['scaler'],
                         self._objects[3][iterator1]['Trans']['y']*self._cameraVector['scaler'],
                         self._objects[3][iterator1]['Trans']['z']*self._cameraVector['scaler'])
            glRotatef(self._objects[3][iterator1]['Rot']['x'], 1, 0, 0)
            glRotatef(self._objects[3][iterator1]['Rot']['y'], 0, 1, 0)
            glRotatef(self._objects[3][iterator1]['Rot']['z'], 0, 0, 1)

            # Draw the Thing
            glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
            glEnable(GL_COLOR_MATERIAL)
            glColor3f(self._objects[0][iterator1][1][0],
                      self._objects[0][iterator1][1][1],
                      self._objects[0][iterator1][1][2])
            self._objects[0][iterator1][0].draw()
            glDisable(GL_COLOR_MATERIAL)
        '''glLoadIdentity()
        glTranslatef(0, 0, self._windowConstants[1]*self._cameraVector['scaler'])
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
        glEnable(GL_COLOR_MATERIAL)
        glColor3f(1, 1, 1)
        for item in self.thing:
            item.draw()
        glDisable(GL_COLOR_MATERIAL)'''

        for iterator1 in range(len(self._windowConstants[4][0])):
            for iterator2 in [False, True]:
                glLoadIdentity()
                scaler = 0.5
                if iterator2:
                    scaler = ((self._armVARS[arm['id']][self._controlState[11][self._windowConstants[4][0][iterator1]][6]]
                               - self._controlState[11][self._windowConstants[4][0][iterator1]][4])
                              / self._controlState[11][self._windowConstants[4][0][iterator1]][5]
                              + self._controlState[11][self._windowConstants[4][0][iterator1]][7])
                if scaler > 1:
                    scaler -= 1
                self._windowConstants[4][2][iterator1][0] = ((self._controlState[11][self._windowConstants[4][0][iterator1]][0]
                                                   * self._windowConstants[2])
                                                  + (self._controlState[11][self._windowConstants[4][0][iterator1]][2]
                                                     * self._windowConstants[2]
                                                     * scaler))
                self._windowConstants[4][2][iterator1][1] = ((self._controlState[11][self._windowConstants[4][0][iterator1]][1]
                                                   * self._windowConstants[2])
                                                  + (self._controlState[11][self._windowConstants[4][0][iterator1]][3]
                                                     * self._windowConstants[2]
                                                     * scaler))
                if iterator2:
                    glTranslatef(self._windowConstants[4][2][iterator1][0],
                                 self._windowConstants[4][2][iterator1][1],
                                 self._windowConstants[1])
                    glEnable(GL_COLOR_MATERIAL)
                    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
                    glEnable(GL_BLEND)
                    glColor4f(.6,.6,.6,.5)
                    self._windowConstants[4][1].draw()
                    glDisable(GL_BLEND)
                else:
                    glTranslatef(self._windowConstants[4][2][iterator1][0] * self._cameraVector['scaler'],
                                 self._windowConstants[4][2][iterator1][1] * self._cameraVector['scaler'],
                                 self._windowConstants[1] * self._cameraVector['scaler'])
                    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
                    glEnable(GL_COLOR_MATERIAL)
                    glColor3f(1,1,1)
                    self.thing[iterator1].draw()
                glDisable(GL_COLOR_MATERIAL)

    def on_text_motion(self, motion, BLAH = False, Setting = None):
        global arm
        #Check the keypress
        '''
        TODO: build a temporary holder for the old value of the thing being changed, 
        along with a loop around this entire thing
        '''
        for item in self._armVARS[arm['id']]['Iter']:
            if ((type(self._armVARS[arm['id']]['OLD'][item]) == float) or (type(self._armVARS[arm['id']]['OLD'][item]) == int)):
                self._armVARS[arm['id']]['OLD'][item] = 0.0 + self._armVARS[arm['id']][item]
            elif (type(self._armVARS[arm['id']]['OLD'][item]) == list):
                for iterator in range(len(self._armVARS[arm['id']][item])):
                    self._armVARS[arm['id']]['OLD'][item][iterator] = 0.0 + self._armVARS[arm['id']][item][iterator]
        for item in self._armConstants[2]['Key IDs']:
            if motion == item[0]:
                if Setting == None:
                    Setting = self._armConstants[2][item[1]+' lims'][1]
                    if not item[2]:
                        Setting *= -1
                    self._armVARS[arm['id']][item[1]] += Setting
                else:
                    self._armVARS[arm['id']][item[1]] = Setting
                if self._armVARS[arm['id']][item[1]] > self._armConstants[2][item[1] + ' lims'][0]:
                    if self._armConstants[2][item[1] + ' lims'][3]:
                        self._armVARS[arm['id']][item[1]] -= self._armConstants[2][item[1] + ' lims'][0]
                    else:
                        self._armVARS[arm['id']][item[1]] = self._armConstants[2][item[1] + ' lims'][0]
                elif self._armVARS[arm['id']][item[1]] < self._armConstants[2][item[1]+ ' lims'][2]:
                    if self._armConstants[2][item[1] + ' lims'][3]:
                        self._armVARS[arm['id']][item[1]] += self._armConstants[2][item[1] + ' lims'][0]
                    else:
                        self._armVARS[arm['id']][item[1]] = self._armConstants[2][item[1] + ' lims'][2]
        try:

            c_armVars = self.IKinematics(self.PythonArmVarsToC());
            self.CArmVarsToPython(c_armVars);

        except Exception as e:
            for item in self._armVARS[arm['id']]['Iter']:
                if ((type(self._armVARS[arm['id']]['OLD'][item]) == float) or (type(self._armVARS[arm['id']]['OLD'][item]) == int)):
                    self._armVARS[arm['id']][item] = 0.0 + self._armVARS[arm['id']]['OLD'][item]
                elif (type(self._armVARS[arm['id']]['OLD'][item]) == list):
                    for iterator in range(len(self._armVARS[arm['id']][item])):
                        self._armVARS[arm['id']][item][iterator] = 0.0 + self._armVARS[arm['id']]['OLD'][item][iterator]
            return

        if self.CollisionCheck(self.PythonArmVarsToC()):
            for item in self._armVARS[arm['id']]['Iter']:
                if ((type(self._armVARS[arm['id']]['OLD'][item]) == float) or (type(self._armVARS[arm['id']]['OLD'][item]) == int)):
                    self._armVARS[arm['id']][item] = 0.0 + self._armVARS[arm['id']]['OLD'][item]
                elif (type(self._armVARS[arm['id']]['OLD'][item]) == list):
                    for iterator in range(len(self._armVARS[arm['id']][item])):
                        self._armVARS[arm['id']][item][iterator] = 0.0 + self._armVARS[arm['id']]['OLD'][item][iterator]

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self._controlState[10][0] = x
        self._controlState[10][1] = y
        if (self._controlState[0] == 1
            and self._controlState[1] == 0):
            self._cameraVector['xRotation'] -= dy * 0.25
            if self._controlState[2] == 0:
                self._cameraVector['yRotation'] += dx * 0.25
            else:
                self._cameraVector['zRotation'] += dx * 0.25
        if (self._controlState[0] == 4
            and self._controlState[1] == 0):
            self._cameraVector['xOffset'] += dx * 1.5 *self._cameraVector['scaler']
            self._cameraVector['yOffset'] += dy * 1.5 *self._cameraVector['scaler']
        if self._controlState[1] > 0:
            if self._windowConstants[4][2][self._controlState[1] - 1][2]:
                thepercent = (((y - self._controlState[9][self._controlState[1] - 1][1][1]
                                +(self._windowConstants[0]/2)-25)
                               / (self._controlState[9][self._controlState[1] - 1][1][3] - self._controlState[9][self._controlState[1] - 1][1][1]))
                              +  self._controlState[11][self._windowConstants[4][0][self._controlState[1] - 1]][7])
            else:
                thepercent = (((x - self._controlState[9][self._controlState[1] - 1][1][0] + (self._windowConstants[0] / 2))
                              / (self._controlState[9][self._controlState[1] - 1][1][2] - self._controlState[9][self._controlState[1] - 1][1][0]))
                              + self._controlState[11][self._windowConstants[4][0][self._controlState[1] - 1]][7])
            if ((self._controlState[11][self._windowConstants[4][0][self._controlState[1] - 1]][7] != 0) and (thepercent > 1)):
                thepercent -= 1
            self.on_text_motion(self._windowConstants[4][2][self._controlState[1] - 1][3], False,
                                (self._controlState[11][self._windowConstants[4][0][self._controlState[1] - 1]][5]
                                 * thepercent
                                 + self._controlState[11][self._windowConstants[4][0][self._controlState[1] - 1]][4])
                                )

    def PythonArmVarsToC(self):
        c_armVars = C_ArmVars()
        for key in self._armVARS[arm['id']]['Iter']:
            value = self._armVARS[arm['id']][key]
            if type(value) == list:
                value = (ctypes.c_double * 3)(value[0], value[1], value[2])
            else:
                value = ctypes.c_double(value)
            setattr(c_armVars, key.replace(' ', ''), value)
        return c_armVars

    def CArmVarsToPython(self, c_armVars):
        for key in self._armVARS[arm['id']]['Iter']:
            value = getattr(c_armVars, key.replace(' ', ''))
            if type(value) == float:
                self._armVARS[arm['id']][key] = value
            else:
                self._armVARS[arm['id']][key] = [value[0], value[1], value[2]]

# C compatible structure from armVARS dictionary
# not including the OLD and Iter sections
class C_ArmVars(ctypes.Structure):
    _fields_ = []
    for key in Window._armVARS[arm['id']]['Iter']:
        cType = ctypes.c_double
        if type(Window._armVARS[arm['id']][key]) == list:
            cType = ctypes.POINTER(ctypes.c_double)
        _fields_.append((key.replace(' ', ''), cType))

def Main():
    global arm
    comObj = ComQuery()
    print(comObj)
    try:
        arm['coms'][arm['id']] = str(comObj.device)
        #if comObj != None:
        print(comObj.device, comObj.name, comObj.vid, comObj.pid)
    except:
        pass
    import pyglet
    global ORION5
    ORION5 = Window(WINDOW[0], WINDOW[1], 'Orion5 Visualiser and Controller')
    icon1 = pyglet.image.load('./Libraries/RR_logo_512x512.png')
    ORION5.set_icon(icon1)
    ORION5.set_location(50,50)
    pyglet.app.run()

if __name__ == '__main__':
    Main()

for item in arm['arms']:
    item['arm'].exit()
