# Orion5 Robotic Arm

_Please read through the Quick Start Guide and watch the videos before using Orion5_
### Orion5 Quick Start Guide: https://goo.gl/DQm3x3
### Orion5 User Manual: https://goo.gl/h3i2br
### Orion5 Tutorial Videos: https://goo.gl/5tkjUF

## MATLAB Library
Libraries directory contains `Orion5.m`, this MATLAB library interfaces with a Python server that will need to be launched before using the MATLAB library.
1. Ensure your machine has python3.6 installed.
2. Install dependencies for Python server using `pip3 install pyserial`.
3. Launch the Python server using `python3 Orion5_Server.py`.
4. Now when the `Orion5.m` class is used in MATLAB it will interface with Python.

### Basic Usage 
The library pings the Python server every second if no other library functions are being called, this is like a watchdog timer, if Python server doesn't hear anything for 5 seconds, it will return to waiting for a new connection.  
The MATLAB script `test_script.m` demonstrates some of the functionality.

#### Create an instance of the library
```matlab
orion = Orion5();
```

#### Cleanup and quit an instance
```matlab
orion.stop();
```

#### Joint ID constants
Use these constants to select which joint to interact with.
```matlab
Orion5.BASE
Orion5.SHOULDER
Orion5.ELBOW
Orion5.WRIST
Orion5.CLAW
```

#### Notes about control mode
The smart servos used in Orion5 have a number of control modes; namely `POS_SPEED`, `POS_TIME` and `VELOCITY`.

**POS_SPEED:** The servo will move towards the desired goal position (set using `setJointPosition`) at the desired speed (set using `setJointSpeed`) after moving through its acceleration profile.

**POS_TIME:** The servo will move towards the desired goal position (set using `setJointPosition`) and arrive there in a specified amount of time (set using `setJointTimeToPosition`). Time is passed to the function as seconds, and the time can have a resolution of 100ms.

**VELOCITY:** In this mode the servo will move at the speed set by `setJointSpeed` or `setAllJointsSpeed` and ignore desired position and hard angle limits set in the servo by the embedded electronics. Users must make sure to read servo positions in a high frequency control loop to avoid driving joints through each other. There is no acceleration profile in this mode; so users will have to consider this in their control system implementations - Otherwise inertia of moving joints will damage gearboxes and make for not-very-smooth motion.

_(Embedded processor enables Orion5 to prevent users from driving joints through each other. However do not rely on this in your control loop as it enables emergency stop mode, requiring user intervention to resolve. See the user manual (https://goo.gl/h3i2br) for more details.)_

#### To set the control mode for each joint
The following constants are available in the Orion5.m library.

```matlab
Orion5.POS_SPEED
Orion5.POS_TIME
Orion5.VELOCITY

```
This function will set the desired control mode for a specified joint.
```matlab
orion.setJointControlMode(Orion5.BASE, Orion5.POS_TIME);
```

### Getters and Setters for all joints

#### Read all joint positions
This will return an array of 5 angles in degrees in the range 0-359 for all joints.  
You can use the Joint ID constants to index this array.
```matlab
all_positions = orion.getAllJointsPosition();
```

#### Read all joint speeds
This will return an array of 5 speeds, servo speed is represented as a 10 bit number (0-1023).  
The conversion to RPM is shown in the example below.  
You can use the Joint ID constants to index this array.
```matlab
all_speeds = orion.getAllJointsSpeed();
shoulder_speed_RPM = all_speeds(Orion5.SHOULDER) * 0.110293;
```

#### Read all joint loads
This will return an array of 5 values representing the current load on each joint.  
Load for the G15 servos is an arbitrary value representing the electrical current through the motor.  
The load value is a 10 bit number (0-1023).  
You can use the Joint ID constants to index this array.
```matlab
all_loads = orion.getAllJointsLoad();
```

#### Set all joint positions
This function takes an array of 5 angles in degrees, in the range 0-359, and sets the position for all joints in one function call.  
This method is several times faster than calling the `setJointPosition` function separately for each joint.
```matlab
positions = [0 216.8 62.5 225.94 30];
orion.setAllJointsPosition(positions);
```

#### Set all joint speeds
This function takes an array of 5 speeds, in the range 0-1023, and sets the speed for all joints in one function call.  
This method is several times faster than calling the `setJointSpeed` function separately for each joint.  
**Set the direction of the velocity by wrapping the desired speed with the `CWVelocity(v)` and `CCWVelocity(v)` functions - for clockwise, and counter-clockwise movement respectively.**  
_(A future update will use the sign of the velocity to determine the direction)_  
**Make sure to set control mode to `Orion5.POS_SPEED` or `Orion5.VELOCITY` before calling this function.**  
_Read more about control mode at the top of this file_
```matlab
speeds = [0 0 CWVelocity(120) CCWVelocity(90) 0];
orion.setAllJointsSpeed(speeds);
```

#### Set all joints torque enable setting
The G15 servos have a torque enable setting, if enabled in position mode this means the servos will hold their position using motor torque.  
Be aware that if torque is disabled in position mode the servo will still move.  
If torque is disabled in velocity mode, the servo should stop moving suddenly, the same effect as setting speed to 0.
```matlab
orion.setAllJointsTorqueEnable([1 1 1 1 0]);
```

### Getters and Setters for one joint

#### Read a joint position
This will return an angle in degrees in the range 0-359 for one joint specified using the Joint ID constants.
```matlab
shoulder_pos = orion.getJointPosition(Orion5.SHOULDER)
```

#### Read a joint Speed
This will return a speed as a 10 bit number for one joint. Find the conversion factor for RPM above.
```matlab
elbow_speed = orion.getJointSpeed(Orion5.ELBOW)
```

#### Read a joint load
This will return the load for a single joint - represented as a 10 bit number. Read above for more information.
```matlab
shoulder_pos = orion.getJointPosition(Orion5.SHOULDER)
```

#### Set a joint position
This takes an angle in degrees in the range 0-359.
```matlab
orion.setJointPosition(Orion5.ELBOW, 135)
```

#### Set a joint speed
This function sets the speed for the specified servo.  
**Please read the notes about `setAllJointsSpeed` above**  
_Read more about control mode at the top of this file_
```matlab
orion.setJointPosition(Orion5.ELBOW, 135)
```

#### Set a time to position
This function will set the speed such that the specified joint will arrive at the goal position in `time` seconds.  
**Make sure to set control mode to `Orion5.POS_TIME` before calling this function**
```matlab
orion.setJointTimeToPosition(Orion5.SHOULDER, time)
```

#### Turn on/off torque for one servo
```matlab
% turn on
orion.setJointTorqueEnable(Orion5.WRIST, 1)

% turn off
orion.setJointTorqueEnable(Orion5.BASE, 0)
```

### Known Issues & Future Work
* If user MATLAB code calling the library crashes, the *keep alive* ping will keep happening in the background. Users can stop this by running `<library_instance>.stop()` in MATLAB console. It would be best to surround your code with a try/catch structure.
* Most functionality is implemented, we are working on making a nicer interface for setting/getting positions in deg360, deg180 and radians.
* We are considering adding the capability to alter the acceleration profile and torque settings etc from MATLAB.

## Python Visualiser Controller
The `Orion5 Controller.py` program is a 3d controller and visualiser made in Python; it implements OpenGL for graphics rendering.
The visualiser is designed as an aid to understand the 5 degrees of freedom of Orion5, and also as a way to control the robotic arm visually.

On launch the program will ask you to select a serial port, if you have an Orion5 connected select its serial port.  
Users can drag the white squares (they are like scroll bars) to move the arm around using our 6 DoF controller.  
The controller sets the tool-point of the robotic arm in cylindrical coordinates, along with tool attack configuration.

The scrollbar controls are:
* **Far-left:** Z height
* **Inner-left:** Tool attack angle in plane of joints
* **Middle-top:** Rotation of arm
* **Middle-bottom:** Tool-point radius
* **Inner-right:** Tool attack distance (sets the point at which tool attack rotates about)
* **Far-right:** Claw open/close

### Dependencies:
* Python 3.6
* pip
* pyserial
* pyglet

Install these dependencies with:

```
pip3.6 install pyglet, pyserial
```

### Keyboard Controls:
* Right - Extends tool point
* Left - Retracts tool point
* Up - Tool point up
* Down - Tool point down
* Home - Attack angle down
* PageUp - Attack angle up
* PageDown - Claw close
* END - Claw open
* Delete - Attack distance out
* Backspace - Attack distance in
* CTRL_Left - Slew left
* CTRL_Right - Slew right
* CTRL_END - Read from arm
* CTRL_HOME - Write to arm
* A - toggle - Put the visualiser into "Arm controls model" mode
* Q - toggle - Put the visualiser into "Model controls arm" mode

### Mouse Controls
* Left click drag: Rotates model by X/Y axis
* Shift + Left click drag: Rotates model by X/Z axis
* Right click drag: Pans the model around
* Scroll wheel: Zoom

### Experimental Controls
* D - Record position to current sequence in memory
* E - Force current position to be current sequence element
* S - cycle sequence toward the end (wraps)
* W - Cycle sequence toward the start (wraps)
* C - Save current sequence set to the txt file in the sequence folder TODOs here
* X - Read the sequence in the sequence.txt in the sequence folder TODOs here
* Z - Play sequence currently loaded... Major TODOs as it relies as it needs the joint to get within X of angle to tick the sequence as having been reached
