clear all

orion = Orion5();

orion.setAllJointsTorqueEnable([1 0 0 0 0]);

orion.setJointControlMode(Orion5.BASE, Orion5.POS_SPEED);
orion.setJointSpeed(Orion5.BASE, 120);

orion.setJointPosition(Orion5.BASE, 0);
pause(4);
orion.setJointPosition(Orion5.BASE, 90);
pause(2);
orion.setJointPosition(Orion5.BASE, 180);
pause(2);
orion.setJointPosition(Orion5.BASE, 270);
pause(2);
orion.setJointPosition(Orion5.BASE, 0);
pause(2);

orion.stop();
