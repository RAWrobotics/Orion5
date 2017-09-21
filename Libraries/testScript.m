clear all

orion = Orion5();

orion.setAllJointsTorqueEnable([0 0 0 0 0]);

% for id=Orion5.BASE:Orion5.CLAW
%     orion.setJointControlMode(id, Orion5.POS_TIME);
%     orion.setJointTimeToPosition(id, 1.5); % 1.5 seconds
% end

while 1
    orion.setJointPosition(Orion5.WRIST, 90);
    pause(3);
    orion.setJointPosition(Orion5.WRIST, 180);
    pause(3);
end

orion.stop();