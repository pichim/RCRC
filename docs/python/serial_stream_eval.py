import time
import numpy as np
import matplotlib.pyplot as plt

from SerialStream import SerialStream

port = '/dev/ttyUSB0'
baudrate = int(2e6)

serialStream = SerialStream(port, baudrate)
serialStream.start()

while serialStream.is_busy_flag():
    time.sleep(0.1)

#  access the data
data = serialStream.get_data()

length_time = len(data['time'])
Ndata, Nsignals = data['values'].shape
print(length_time)
print(Ndata)
print(Nsignals)

time_diff = np.diff(data['time']) * 1e6
values = data['values']
print(time_diff[0:10])
print(values[0:10, :].T)
print(values.shape)

# --- Plotting the data

Ts = np.mean(np.diff(data['time']))

plt.figure(1)
plt.plot(data['time'][:-1], np.diff(data['time']) * 1e6)
plt.grid(True)
plt.title(f"Mean {np.mean(np.diff(data['time']) * 1e6):.0f} mus, "
          f"Std. {np.std(np.diff(data['time']) * 1e6):.0f} mus, "
          f"Med. dT = {np.median(np.diff(data['time']) * 1e6):.0f} mus")
plt.xlabel('Time (sec)')
plt.ylabel('dTime (mus)')
plt.xlim([0, data['time'][-2]])
plt.ylim([0, 1.2 * np.max(np.diff(data['time']) * 1e6)])

for i in range(Nsignals):
    plt.figure(i + 2)
    plt.plot(data['time'], data['values'][:, i])
    plt.grid(True)

plt.show()
