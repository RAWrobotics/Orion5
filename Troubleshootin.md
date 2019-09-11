# Maintainence & Repair Procedures

## Firmware Update
The firmware update procedure is slightly different depending on the version of the Orion5.
For the newest version, the procedure is automated, requiring only one button press. For older versions, there is a button press required in the middle of the procedure.

### Automated Firmware Update
There are 2 ways to update the firmware, if everything is working (arm responds to e-stop, and communicates with simulator), then use the firmware update button inside the simulator settings. The Orion5 will reboot itself and begin the udpate. If this is an old version of Orion5, (black 3d printed parts with bolts), the middle button will need to be held for 2s as described by the status message on the updater. If this is a new Orion5, red 3d printed parts with bolts or ETM's (zip ties), do not press any buttons.

### Manual Bootloader Mode
If the arm is not responding to e-stop, or is otherwise unresponsive, hold the middle button while plugging in the power. All 3 LEDs will flash together, this indicates bootloader mode. Launch the `QUT_FIRST_UPDATE.py`, this is a special version of the `FirmwareUpdaterGUI.py` that works from manual bootloader mode. Press the update button once the firmware file and Orion5 is found.

### Can't find firmware file
Make sure the latest version of firmware is sitting in a directory one up, and one across from the firmware update program. So if `FirmwareUpdaterGUI.py` or `QUT_FIRST_UPDATE.py` are inside `Orion5-Private/Python`, then the `.bin` firmware files should be in `Orion5-private/Firmware`

## Debugging Issues
On powerup of the Orion5, all the servos will flash their LEDs once, this indicates power is good. This LED flash is built into the servo firmware, not a result of the Orion5 firmware communicating with the servos. If a servo is not lighting up when power is plugged in, it is either not getting power or its electronics are blown.

Following the power LED flash, the Orion5 firmware will initialise each servo, and flash each servos LED in sequence from the turret to the claw. Something is wrong when one or more don't light, or they light out of sequence or two or more light simultaneously.

**The power and comms to the 5 servos are daisy chained, which means an issue with a servo will cause issues for all servos after it.**

Common reasons for issues with the servo initialisation might be:
- A break or short in the wiring somewhere along the servo daisy chain (could be as simple as a loose crimp or connector)
- A servo with the incorrect ID
- A servo with failed electronics

The leftmost white LED on Orion5 is the main status indicator.
This LED comes on whether the initialisation sequence was successful or not.

### Test Comms
The two blue LEDs indicate activity on the TX and RX USB lines (left and right respectively).
If the Simulator or configGUI is open, and connected to the Orion5, both of these LEDs should be intermittently lit. 
If only the RX (right) blue LED is lighting, this means the arm is recieving comms but not transmitting anything back.
This usually means the arm did not make it past the initialisation step (see next section). Or the firmware is out of date, and is using an old comms protocol. Try a firmware update.

### Test Initialisation Success
In order to test whether the initialisation was successful and the arm is ready to communicate, press the middle or left buttons (e-stop).
If the status LED starts flashing, the arm is responding to e-stop, and the initialisation must have been successful, if there is no response, the arm is still trying to complete the initialisation. It will never complete unless all 5 servos are present and responding to their IDs.

### Test Loom Continuity
To test the comms and power to each servo, use a multimeter in resistance or continuity mode.
Start with a servo connector nearest the turret servo, check continuity between it and the claw servo, work your way up the arm until a break is found. Common places for breaks are inside the bicep on older Orion5's with bolts. There is the possibility that a bolt has been driven through the loom, causing a break or a short.

## Run-In, Initialise & ID Servos
The 5 servos have an ID number stored in their EEPROM. The ID numbers are:
- 1 - Turret
- 2 - Shoulder
- 3 - Elbow
- 4 - Wrist
- 5 - Claw

When a servo is replaced it will need to be run-in, initialised, and an ID assigned to it.
Out of the box the servos have EEPROM parameters such as baud rate, and various kinematic settings that must be set in order to function with the Orion5 firmware.

Any Orion5 PCB can be used as a servo ID/initialisation station. Using the `configGUI.py` script in `Orion5-private/Python`, a connected Orion5 PCB can be put into run-in, and ID mode.

### Special QUT ID and Run-In PCB
On boot, this PCB will go into ID mode by default.
Holding left button on boot, will put this board into run-in and initialisation mode.
Follow other instructions as normal disregarding any instructions about `configGUI.py`.

### Run-In & Initialisation
Connect Orion5 via USB, and launch `configGUI.py` with a version of Python that has the `rawrobotics-orion5` library installed. Try `pip install rawrobotics-orion5` if the library is not installed.

New servos must be run-in first, this is a 10 minute procedure that runs the servo at full speed in both directions. This is to test for any failure of the servo from manufacturing, and to wear in the gearbox a little. After clicking `Run In` on the configGUI, the connected servos will be flashed with the correct EEPROM params, and begin the run in sequence. So make sure to only connect servos that are able to rotate freely. If any joints or turret gearboxes are attached to the PCB they will spin violently. Ensure nothing is attached to the servo horns before hitting the `Run In` button. `configGUI.py` will be un-responsive after launching run-in, re-power the PCB and relaunch the program if you need to enter run-in again.

All servo LED's will flash together about 5 times before run-in begins, if a servo's LED flashes, this means it's EEPROM values were set correctly. If no flash, re-power the PCB and put into run-in mode again.

Leave the sequence until the servos come to a stop. 

### ID
*Note: If this is a fresh servo, perform the run-in sequence first, as it will apply some configuration values that need to be set before the ID process will work*

Re-power the PCB and launch the `configGUI.py` again.

This time hit the `ID` button - `configGUI.py` will be un-responsive after this, re-power the PCB and relaunch the program if you need to enter ID mode again. 

The rightmost white LED should start to flash, one short flash every 2 seconds.
This LED is displaying the ID number that is about to be written, when the left button is pressed.
One flash = ID 1 - Turret. Two flash = ID 2 - Shoulder, and so on.
Press the right button to increment the ID number to be written, and the middle button the decrement the ID number.
The number does not wrap.

When the correct number is selected, press the left button to write the ID. The servo LED should now flash in time with the white LED for a few cycles. If it does, the ID write was successful. If no flash, try launching the run-in program, the servo LED should flash serveral times and then the servo begins moving as part of the run-in. If this does not occur, servo has an unknown failure.
