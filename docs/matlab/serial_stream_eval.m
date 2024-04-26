clc, clear all
%%

% NUCLEO_H743ZI2 | NUCLEO_F446RE | NUCLEO_L432KC
% 'COM12'        | 'COM6'        | 'COM10'
port = 'COM19';
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

% parameters
R2 = 4.7e3;  % Ohm
R1 = R2 + 12e3;
C1 = 470e-9; % F
C2 = C1;

% rcrc
a = R1*R2*C1*C2
b = R1*C1 + R1*C2 + R2*C2

% transfer function
s = tf('s');
Grcrc_mod = 1 / (a*s^2 + b*s + 1);


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

% for i = 1:2
%     Nest     = round(2.0 / Ts);
%     koverlap = 0.5;
%     Noverlap = round(koverlap * Nest);
%     window   = hann(Nest);
%     Nest_min = round(0.1 / Ts);
% 
%     [~, ~, f, Pavg] = estimate_frequency_response(data.values(:,1), ...
%         data.values(:,i + 1), window, Noverlap, Nest, Ts);
%     while (true)
%         Nest = floor(Nest / 2.0);
%         Noverlap = round(koverlap * Nest);
%         window   = hann(Nest);
%         if (Nest < Nest_min)
%             break;
%         end
%         [~, ~, f_, Pavg_] = estimate_frequency_response(data.values(:,1), ...
%             data.values(:,i + 1), window, Noverlap, Nest, Ts);
%         f_min = 10^(log10(min(f_(f_ > 0))) + 1.2);
%         ind_avg = f >= f_min & f <= 1/2/Ts - f_min;
%         Pavg_ = interp1(f_, Pavg_, f(ind_avg), 'linear');
%         Pavg(ind_avg,:) = 0.5 * (Pavg(ind_avg,:) + Pavg_);
%     end
% 
%     if i == 1
%         G1 = frd(Pavg(:,2) ./ Pavg(:,1), f, Ts, 'Units', 'Hz');
%         C1 = frd(abs(Pavg(:,2)).^2 ./ (Pavg(:,1) .* Pavg(:,3)), f, Ts, 'Units', 'Hz');
%     else
%         G2 = frd(Pavg(:,2) ./ Pavg(:,1), f, Ts, 'Units', 'Hz');
%         C2 = frd(abs(Pavg(:,2)).^2 ./ (Pavg(:,1) .* Pavg(:,3)), f, Ts, 'Units', 'Hz');
%     end
% end

figure(2)
plot(data.time, data.values), grid on

figure(3)
bode(G1, G2, Grcrc_mod, 2*pi*G1.Frequency(G1.Frequency < 1/2/Ts)), grid on
legend('G1','G2', 'Grcrc mod')

opt = bodeoptions('cstprefs');
opt.MagUnits = 'abs';
opt.MagScale = 'linear';

figure(4)
bodemag(C1, C2, 2*pi*G1.Frequency(G1.Frequency < 1/2/Ts), opt), grid on
set(gca, 'YScale', 'linear')

