function [joints, message] = ikinematics(radius, theta, height, attack, claw)
    % constants (mm)
    bicep_length = 170.384;
    forearm_length = 136.307;
    wrist_length = 85;
    shoulder_radial_offset = 30.309;
    shoulder_z_offset = 53;
    message = '';
    
    [t, r] = cart2pol(shoulder_radial_offset, shoulder_z_offset);
    [x0, y0, z0] = sph2cart(deg2rad(theta), t, r);
    
    % tool point in cylindrical coordinates
    tool_point = [radius, theta, height];

    % find vector from tool_point to wrist origin along angle of attack
    [x, y] = pol2cart(deg2rad(attack - 180), wrist_length);
    wrist_point = [tool_point(1) + x, tool_point(3) + y];

    % find length of vector from shoulder origin to wrist_point
    [theta, c] = cart2pol(wrist_point(1) - shoulder_radial_offset, wrist_point(2) - z0);

    % use cosine rule to solve shoulder and elbow joint angles
    a = forearm_length;
    b = bicep_length;

    % check if pose can be achieved (threshold of 5mm)
    if c >= (a + b - 5)
        message = 'forearm and bicep over extended';
    end
    
    % cosine rule continued
    A =  acosd((b^2 + c^2 - a^2) / (2*b*c));
    C =  acosd((a^2 + b^2 - c^2) / (2*a*b));
    B = 180 - A - C;
    
    % find joint angles relative to each joint
    joints(1) = wrapTo360(tool_point(2)); % base
    joints(2) = A + rad2deg(theta); % shoulder
    joints(3) = C; % elbow
    joints(4) = wrapTo360(attack + B + (180 - rad2deg(theta))); % wrist
    joints(5) = claw; % claw
    
    % check that angles are in range
    if any(joints < 0) || any(joints > 360)
        message = 'joint angles out of range';
    end
    
    % check that claw is in range
    if joints(4) < 20 || joints(4) > 360
        message = 'claw out of range';
    end
    
    % graphing
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
    
    figure(2); hold on;
    plot(x0+x1+x2+x3, y0+y1+y2+y3, 'rx');
    xlim([-300 300]); ylim([-300 300]); zlim([0 600]);
    grid on; grid minor;
    
    joints(2) = wrapTo360(joints(2) * 2.857);
end