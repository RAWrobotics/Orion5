clear all

orion = Orion5();

orion.setAllJointsTorqueEnable([1 0 0 0 0]);

for id=Orion5.BASE:Orion5.CLAW
    orion.setJointControlMode(id, Orion5.POS_TIME);
    orion.setJointTimeToPosition(id, 1.5); % 1.5 seconds
end

orion.setJointPosition(Orion5.BASE, 0);
pause(2);
orion.setJointPosition(Orion5.BASE, 90);
pause(2);
orion.setJointPosition(Orion5.BASE, 180);
pause(2);
orion.setJointPosition(Orion5.BASE, 270);
pause(2);

orion.stop();