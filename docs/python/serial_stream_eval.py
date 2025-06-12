# conda create --name rcrc-env python=3.11.4 numpy scipy matplotlib pyserial control ipykernel

import time
import numpy as np
import matplotlib.pyplot as plt
import control as ct
import scipy as sp
from SerialStream import SerialStream


def tfestimate(x, y, fs, window, nperseg, noverlap):
    f, Pxy = sp.signal.csd(x, y, fs=fs, window=window, nperseg=nperseg, noverlap=noverlap)
    f, Pxx = sp.signal.csd(x, x, fs=fs, window=window, nperseg=nperseg, noverlap=noverlap)
    G = Pxy / Pxx
    return f, G


def get_step_resp_from_frd(G_frd, Ts, f_max=None):
    if f_max is None:
        f_max = np.max(G_frd.frequency) / (2 * np.pi)  # in Hz

    g = G_frd.magnitude.flatten() * np.exp(1j * G_frd.phase.flatten())  # complex response

    if np.isnan(np.abs(g[0])):
        g[0] = g[1]  # Todo: interpolate based on point 2 and 3

    freq_hz = G_frd.frequency / (2 * np.pi)  # rad/s -> Hz
    g[freq_hz >= f_max] = 0

    step_resp = 2 * np.cumsum(np.real(np.fft.ifft(g)))
    # Use double the sampling time because of 'symmetric' option
    time_vec = np.arange(len(step_resp)) * 2 * Ts
    return time_vec, step_resp


port = "/dev/ttyUSB0"
baudrate = int(2e6)

# Initialize the SerialStream object
try:
    serialStream.reset()
    print("Resetting existing serialStream object.")
except Exception as e:
    serialStream = SerialStream(port, baudrate)
    print("Creating new serialStream object.")

# Starting the stream
serialStream.start()
while serialStream.is_busy_flag():
    time.sleep(0.1)

# Accessing the data
try:
    data = serialStream.get_data()
except Exception as e:
    print("Data Stream not triggered.")
    exit()

# Evaluating the data

Ts = np.mean(np.diff(data["time"]))

plt.figure(1)
plt.plot(data["time"][:-1], np.diff(data["time"]) * 1e6)
plt.grid(True)
plt.title(f"Mean {np.mean(np.diff(data['time']) * 1e6):.0f} mus, " f"Std. {np.std(np.diff(data['time']) * 1e6):.0f} mus, " f"Med. dT = {np.median(np.diff(data['time']) * 1e6):.0f} mus")
plt.xlabel("Time (sec)")
plt.ylabel("dTime (mus)")
plt.xlim([0, data["time"][-2]])
plt.ylim([0, 1.2 * np.max(np.diff(data["time"]) * 1e6)])

# Defining the indices for the data columns
ind = {}
ind["u_e"] = 0
ind["u_c1"] = 1
ind["u_c2"] = 2
ind["sinarg"] = 3

# Parameters
R1 = 4.7e3  # Ohm
R2 = R1
C1 = 470e-9  # F
C2 = C1

a = R1 * R2 * C1 * C2
b = R1 * C1 + R1 * C2 + R2 * C2

# Transfer function
s = ct.tf([1, 0], 1)
G_rcrc_mod = 1 / (a * s**2 + b * s + 1)

# Frequency response estimation
N_est = round(0.5 / Ts)
k_overlap = 0.5
N_overlap = round(k_overlap * N_est)
window = sp.signal.windows.hann(N_est)

inp = np.diff(data["values"][:, ind["u_e"]])
out = np.diff(data["values"][:, ind["u_c1"]])
freq, g = tfestimate(inp, out, fs=1 / Ts, window=window, nperseg=N_est, noverlap=N_overlap)
_, c = sp.signal.coherence(inp, out, fs=1 / Ts, window=window, nperseg=N_est, noverlap=N_overlap)
G1 = ct.frd(g, 2 * np.pi * freq)
C1 = ct.frd(c, 2 * np.pi * freq)

inp = np.diff(data["values"][:, ind["u_e"]])
out = np.diff(data["values"][:, ind["u_c2"]])
freq, g = tfestimate(inp, out, fs=1 / Ts, window=window, nperseg=N_est, noverlap=N_overlap)
_, c = sp.signal.coherence(inp, out, fs=1 / Ts, window=window, nperseg=N_est, noverlap=N_overlap)
G2 = ct.frd(g, 2 * np.pi * freq)
C2 = ct.frd(c, 2 * np.pi * freq)

mag_G1, phase_G1, _ = ct.frequency_response(G1, 2 * np.pi * freq)
mag_G2, phase_G2, _ = ct.frequency_response(G2, 2 * np.pi * freq)
mag_Grcrc, phase_Grcrc, _ = ct.frequency_response(G_rcrc_mod, 2 * np.pi * freq)

plt.figure(2)
plt.subplot(2, 1, 1)
plt.semilogx(freq, 20 * np.log10(mag_G1.flatten()), label="G1")
plt.semilogx(freq, 20 * np.log10(mag_G2.flatten()), label="G2")
plt.semilogx(freq, 20 * np.log10(mag_Grcrc.flatten()), label="Grcrc mod")
plt.grid(True, which="both", axis="both")
plt.legend(loc="best")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude (dB)")
plt.subplot(2, 1, 2)
plt.semilogx(freq, 180 / np.pi * np.arctan2(np.sin(phase_G1.flatten()), np.cos(phase_G1.flatten())), label="G1")
plt.semilogx(freq, 180 / np.pi * np.arctan2(np.sin(phase_G2.flatten()), np.cos(phase_G2.flatten())), label="G2")
plt.semilogx(freq, 180 / np.pi * np.arctan2(np.sin(phase_Grcrc.flatten()), np.cos(phase_Grcrc.flatten())), label="Grcrc mod")
plt.grid(True, which="both", axis="both")
plt.legend(loc="best")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Phase (deg)")

plt.figure(3)
plt.semilogx(freq, C1.magnitude.flatten(), label="C1")
plt.semilogx(freq, C2.magnitude.flatten(), label="C2")
plt.grid(True, which="both", axis="both")
plt.legend(loc="best")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")

# Step responses
f_max = 800

step_time, step_resp_1 = get_step_resp_from_frd(G1, Ts, f_max)
_, step_resp_2 = get_step_resp_from_frd(G2, Ts, f_max)

_, step_resp_mod = ct.step_response(G_rcrc_mod, step_time)

plt.figure(4)
plt.plot(step_time, step_resp_1, label="G1")
plt.plot(step_time, step_resp_2, label="G2")
plt.plot(step_time, step_resp_mod, label="Grcrc mod")
plt.grid(True)
plt.xlabel("Time (sec)")
plt.ylabel("Voltage (V)")
plt.legend()
plt.xlim([0, 0.05])

# Show all plots
plt.show()
