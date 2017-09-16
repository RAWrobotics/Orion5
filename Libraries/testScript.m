clear all; clc;

orion = Orion5();

while 1
    for id = Orion5.BASE:Orion5.WRIST
        orion.setJointTorqueEnable(id, 1);
        orion.setJointControlMode(id, Orion5.POS_TIME);
        orion.setJointTimeToPosition(id, 2);
        orion.setAllJointsPosition([90.00,320.00,110.00,140.00,190.00]);
        orion.setAllJointsPosition([90.00,320.00,110.00,140.00,190.00]);
        orion.getAllJointsPosition();
        orion.setAllJointsPosition([10.12,20.22,30.32,40.42,50.52]);
        orion.setAllJointsPosition([10.12,20.22,30.32,40.42,50.52]);
        if rand() < 0.05
            disp('pause');
            pause(rand()*10);
        end
        orion.setAllJointsPosition([10.12,20.22,30.32,40.42,50.52]);
        orion.setAllJointsPosition([90.00,320.00,110.00,140.00,190.00]);
        orion.setAllJointsPosition([90.00,320.00,110.00,140.00,190.00]);
        orion.getAllJointsPosition();
        orion.setAllJointsPosition([10.12,20.22,30.32,40.42,50.52]);
        orion.setAllJointsPosition([10.12,20.22,30.32,40.42,50.52]);
        orion.getAllJointsPosition();
        orion.setAllJointsPosition([10.12,20.22,30.32,40.42,50.52]);
        orion.getAllJointsPosition();
    end
end

% state = 0;
% angles = [];
% 
% tic;
% counts = 0;
% time = 0;
% times = [];
% while 1
%     disp(orion.getAllJointsPosition());
%     
%     if (toc - time) > 5
%         time = toc;
%         state = ~state;
%         counts = counts + 1;
%         if counts > 10
%             break
%         end
%         
%         if state
%             angles = ikinematics(100, 180, 300, 0, 250);
%         else
%             angles = ikinematics(150, 180, 100, 0, 20);
%         end
%         
%         orion.setAllJointsPosition(angles);
%     end
%     
%     pause(0.1); % pause so figure can update
% end

orion.stop();