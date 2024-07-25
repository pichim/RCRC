import SerialStream as stream
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, filtfilt, freqz, csd
from control import tf, c2d
import control
from control.matlab import bode

# Example usage:
port = 'COM19'  # Adjust port accordingly
baudrate = 2000000  # Adjust baudrate accordingly
stream = stream.SerialStream(port, baudrate)
stream.start()

data = stream.get_data()

# Calculate differences
time_diff = np.diff(data[:,0]) * 1e6
zero = np.array([0])


# Plotting
plt.figure(1)
plt.plot(data[:-1,0], time_diff, marker='o', linestyle='-')
plt.grid(True)
plt.title(f"Mean {np.mean(time_diff):.0f} mus, Std. {np.std(time_diff):.0f} mus, Med. dT = {np.median(time_diff):.0f} mus")
plt.xlabel('Time (sec)')
plt.ylabel('dTime (mus)')
plt.ylim([0, 1.2 * np.max(time_diff)])


# R2 = 4.7e3
# R1 = R2 + 12e3
# C1 = 470e-9
# C2 = C1

# a = R1*R2*C1*C2
# b = R1*C1 + R1*C2 + R2*C2

# s = tf('s')
# # Grcrc_mod = 1 / (a*s^2 + b*s + 1)

# Ts = np.mean(np.diff(data[:, 0]))

# # Define system parameters
# Dlp = np.sqrt(3) / 2
# wlp = 2 * np.pi * 10
# Glp = c2d(tf([wlp**2], [1, 2*Dlp*wlp, wlp**2]), Ts, 'tustin')

# # Define frequency response estimation parameters
# Nest = round(2.0 / Ts)
# koverlap = 0.9
# Noverlap = round(koverlap * Nest)
# window = np.hanning(Nest)

# # Apply rotating filter and estimate frequency response
# # inp = filtfilt(*butter(N, Wn, btype='low', analog=False), data[:, 3])
# # out = filtfilt(*butter(N, Wn, btype='low', analog=False), data[:, 1])
# G1, C1 = csd(data[:, 1], data[:, 3], fs=Ts, nperseg=Nest, noverlap=Noverlap, window=window, scaling='density')
# # G1 = tfest(data[:, 1], data[:, 3], window=window, noverlap=Noverlap, nperseg=Nest, Ts=Ts)
# # inp = filtfilt(*butter(N, Wn, btype='low', analog=False), data[:, 3])
# # out = filtfilt(*butter(N, Wn, btype='low', analog=False), data[:, 2])
# G2, C2 = csd(data[:, 2], data[:, 3], fs=Ts, nperseg=Nest, noverlap=Noverlap, window=window, scaling='density')
# # G2 = tfest(data[:, 2], data[:, 3], window=window, noverlap=Noverlap, nperseg=Nest, Ts=Ts)

# # Assuming G1_coeffs contains the numerator and denominator coefficients of the transfer function G1
# numerator = G1[0]  # Numerator coefficients
# denominator = G1[1]  # Denominator coefficients

# # Create a transfer function object
# G1_tf = control.TransferFunction(numerator, denominator, Ts)

# # # Plotting
# # plt.figure(1)
# # plt.plot(data[:, 0], data[:, 1:], marker='o', linestyle='-')
# # plt.grid(True)

# plt.figure(2)
# control.bode(G1_tf, omega_limits=[0, 0.5 / Ts])
# plt.grid(True)
# plt.legend(['G1'])

# # plt.figure(3)
# # bodemag(C1, C2, omega_limits=[0, 0.5 / Ts])
# # plt.grid(True)
# # plt.gca().set_yscale('linear')

plt.show()

