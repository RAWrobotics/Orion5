%% Orion5 MATLAB Sequence Example
% Provided by RAWrobotics 
% https://rawrobotics.com.au/
% info@rawroboics.com.au

%% Variables
% 2d array to hold joint angles for a sequence
% numbers are all degrees wrapped to 0-360
% [base, shoulder, elbow, wrist, claw]

sequence = [
    [0   82  126 62  250];
    [0   83  72  115 250];
    [0   83  72  115 190];
    [0   82  126 62  190];
    [270 67  146 57  190];
    [270 72  87  112 190];
    [270 72  87  112 250];
    [270 67  146 57  250];
    [0   82  126 62  250];
    [0   77  65  128 250];
    [0   77  65  128 190];
    [0   82  126 62  190];
    [270 67  146 57  190];
    [270 75  96  99  190];
    [270 75  96  99  250];
    [270 67  146 57  250];
    [0   82  126 62  250];
    [0   77  65  128 80];
    [0   75  79  194 250];
];

% when the rotational distance (degrees) for all joints is less than
% this threshold, we move to the next point in the sequence.
arriveThreshold = 15;

% set this to 1 to see a 3d plot of the robot and 2d plot of toolpoint
% on the XY plane
draw_plot = 0;

%% Main Loop
% create a connection to Orion5Server.py
orion = Orion5();

% turn on torque for all the joints
orion.setAllJointsTorqueEnable([1 1 1 1 1]);

% for each element in the sequence
for i = 1:size(sequence, 1)

    % index the target point from the sequence
    target = sequence(i, :);

    while 1
        % write the target joint angles to the robot
        orion.setAllJointsPosition(target);

        % read the current joint angles from the robot
        current = orion.getAllJointsPosition();
        
        % display the current robot position on a 3d plot
        if draw_plot
            graphing(current);
        end

        % find the remaining rotational distance left to go for each joint
        diff = abs(target - current);

        % wrap the base angle difference to 0-180
        diff(1) = abs(wrapTo180(diff(1)));

        % if we're close enough to the target, go to next point in sequence
        if (max(diff) < arriveThreshold)
            break;
        end

        % wait a bit between itterations
        pause(0.1);
    end

    % wait briefly at each point
    pause(1.0);
end

% turn off torque for all the joints
orion.setAllJointsTorqueEnable([0 0 0 0 0]);

orion.stop();
