%% Orion5 MATLAB Graphing Function
% Provided by RAWrobotics 
% https://rawrobotics.com.au/
% info@rawroboics.com.au

function graphing(joints)
    % constants (mm)
    bicep_length = 170.384;
    forearm_length = 136.307;
    wrist_length = 85;
    shoulder_radial_offset = 30.309;
    shoulder_z_offset = 53;
    
    % negate the base angle for graphing reasons
    joints(1) = wrapTo360(360 - joints(1));
    
    % find the location of the shoulder axis in 3d rectangular coords
    [t, r] = cart2pol(shoulder_radial_offset, shoulder_z_offset);
    [x0, y0, z0] = sph2cart(deg2rad(joints(1)), t, r);
    
    % Draw a 3d plot of all the joints
    % (Look away if you don't like 3d geometry)
    figure(1);
    [x1, y1, z1] = sph2cart(deg2rad(joints(1)), deg2rad(joints(2)), bicep_length);
    [x2, y2, z2] = sph2cart(deg2rad(joints(1)), deg2rad(joints(2)+joints(3)-180), forearm_length);
    [x3, y3, z3] = sph2cart(deg2rad(joints(1)), deg2rad(joints(2)+joints(3)+joints(4)), wrist_length);
    plot3([0 x0 x0+x1 x0+x1+x2 x0+x1+x2+x3], [0 y0 y0+y1 y0+y1+y2 y0+y1+y2+y3], [0 z0 z0+z1 z0+z1+z2 z0+z1+z2+z3], '-bo'); hold on;
    plot3([x0 x0+x1+x2], [y0 y0+y1+y2], [z0 z0+z1+z2], '-r');
    hold off;
    xlim([-300 300]); ylim([-300 300]); zlim([0 600]);
    xlabel('X'); ylabel('Y'); zlabel('Z');
    grid on; grid minor;
    axis vis3d;
    
    % Draw a 2d plot of the tool point on the XY plane
    figure(2); hold on;
    plot(x0+x1+x2+x3, y0+y1+y2+y3, 'rx');
    xlim([-300 300]); ylim([-300 300]); zlim([0 600]);
    grid on; grid minor;
end
