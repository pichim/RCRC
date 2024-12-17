clc, clear all
%% openlager

% % TODO: Test this, not used in a while
% file_id = fopen('LOG278.TXT');
% 
% num_of_floats = fread(file_id, 1, 'uint8')
% data_raw = fread(file_id, 'single');
% length(data_raw)
% fclose(file_id);
% 
% data_raw = data_raw(1:floor( length(data_raw)/num_of_floats ) * num_of_floats);
% data.values = reshape(data_raw, [num_of_floats, length(data_raw)/num_of_floats]).';         
% data.time = cumsum(data.values(:,1)) * 1e-6;
% data.time = data.time - data.time(1);
% data.values = data.values(:,2:end);


%% streaming to matlab

port = 'COM6';
baudrate = 2e6;

if (~exist('serialStream', 'var'))
    serialStream = SerialStream(port, baudrate);
else
    serialStream.reset();
end

serialStream.start()
while (serialStream.isBusy())
    pause(0.1);
end

% access the data
data = serialStream.getData();

return

%%

Ts = mean(diff(data.time));

figure(1)
plot(data.time(1:end-1), diff(data.time * 1e6)), grid on
title( sprintf(['Mean %0.0f mus, ', ...
                'Std. %0.0f mus, ', ...
                'Med. dT = %0.0f mus'], ...
                mean(diff(data.time * 1e6)), ...
                std(diff(data.time * 1e6)), ...
                median(diff(data.time * 1e6))) )
xlabel('Time (sec)'), ylabel('dTime (mus)')
xlim([0 data.time(end-1)])
ylim([0 1.2*max(diff(data.time * 1e6))])


% parameters
R1 = 4.7e3;  % Ohm
R2 = R1;
C1 = 470e-9; % F
C2 = C1;

% rcrc
a = R1*R2*C1*C2
b = R1*C1 + R1*C2 + R2*C2

% transfer function
s = tf('s');
Grcrc = 1 / (a*s^2 + b*s + 1);

% rotating filter
Dlp = sqrt(3) / 2;
wlp = 2 * pi * 10;
Glp = c2d(tf(wlp^2, [1 2*Dlp*wlp wlp^2]), Ts, 'tustin');

% frequency response estimation
Nest     = round(2.0 / Ts);
koverlap = 0.9;
Noverlap = round(koverlap * Nest);
window   = hann(Nest);


inp = apply_rotfiltfilt(Glp, data.values(:,4), data.values(:,1));
out = apply_rotfiltfilt(Glp, data.values(:,4), data.values(:,2));
[G1, C1] = estimate_frequency_response(inp, out, window, Noverlap, Nest, Ts);

inp = apply_rotfiltfilt(Glp, data.values(:,4), data.values(:,1));
out = apply_rotfiltfilt(Glp, data.values(:,4), data.values(:,3));
[G2, C2] = estimate_frequency_response(inp, out, window, Noverlap, Nest, Ts);

figure(2)
plot(data.time, data.values), grid on


figure(3)
bode(G1, G2, Grcrc, 2*pi*G1.Frequency(G1.Frequency < 1/2/Ts)), grid on
legend('G1', 'G2', 'Grcrc mod', 'Location', 'best')

opt = bodeoptions('cstprefs');
opt.MagUnits = 'abs';
opt.MagScale = 'linear';

figure(4)
bodemag(C1, C2, 2*pi*G1.Frequency(G1.Frequency < 1/2/Ts), opt), grid on
