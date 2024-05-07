import serial
import time
import math
import numpy as np

class SerialStream:
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        self.serial_port = serial.Serial(self.port, self.baudrate)
        self.data = np.zeros(int(1e8))  # preallocate big data array
        self.reset()

    def reset(self):
        self.data = np.zeros_like(self.data)
        self.timeout = 3.0
        self.is_waiting_for_first_measurement = True
        self.ind_end = 0
        self.num_of_floats = 0
        self.is_busy = True
        self.max_trigger_attempts = 5
        self.trigger_attempts = 0

    # def start(self):
    #     self.send_start_byte()

    #     while True:
    #         bytes_readable = self.serial_port.in_waiting

    #         if self.is_waiting_for_first_measurement and bytes_readable > 0:
    #             self.is_waiting_for_first_measurement = False
    #             self.num_of_floats = int.from_bytes(self.serial_port.read(1), 'little')

    #             bytes_readable -= 1

    #             print(f"SerialStream started, logging {self.num_of_floats} signals")
    #             self.timeout = 0.3

    #         if bytes_readable >= 4:
    #             num_of_floats_readable = (bytes_readable // 4) * 4
    #             # np.ceil(bytes_readable / 4)
    #             print(num_of_floats_readable)
    #             data_raw = self.serial_port.read(int(num_of_floats_readable))
    #             buffer_size = len(data_raw)
    #             print(buffer_size)
    #             print(data_raw)
    #             # ind_start = self.ind_end + 1
    #             # self.ind_end = ind_start + num_of_floats_readable - 1
    #             self.data[0:num_of_floats_readable] = np.frombuffer(data_raw, dtype='float32')

    #             self.timer = time.time()

    def start(self):
        self.send_start_byte()

        while True:
            bytes_readable = self.serial_port.in_waiting

            if self.is_waiting_for_first_measurement and bytes_readable > 0:
                self.is_waiting_for_first_measurement = False
                self.num_of_floats = int.from_bytes(self.serial_port.read(1), 'little')
                print(self.num_of_floats)
                bytes_readable -= 1

                print(f"SerialStream started, logging {self.num_of_floats} signals")
                self.timeout = 0.3

            if bytes_readable >= 4:
                num_of_floats_readable = math.floor(bytes_readable / 4)
                data_raw = self.serial_port.read(int(num_of_floats_readable * 4))

                ind_start = self.ind_end + 1
                self.ind_end = ind_start + num_of_floats_readable - 1
                # Convert bytes to floats and store in data array
                self.data[ind_start:self.ind_end+1] = np.frombuffer(data_raw, dtype=np.float32)
                # self.data[ind_start:self.ind_end+1] = np.frombuffer(data_raw[:num_bytes_to_read], dtype=np.float32)
                # print(data_float)
                # self.data[:num_of_floats_to_store] = data_float
                # print(f"self data: {self.data}")

                self.timer = time.time()

            if time.time() - self.timer > self.timeout:
                if self.is_waiting_for_first_measurement and self.trigger_attempts < self.max_trigger_attempts:
                    self.send_start_byte()
                else:
                    if self.is_waiting_for_first_measurement:
                        print(f"SerialStream timeout, logging not triggered after {self.max_trigger_attempts} attempts of waiting {self.timeout:.2f} seconds")
                    else:
                        print(f"SerialStream ended with {self.timeout:.2f} seconds timeout")
                        print(f"             measured {self.ind_end} datapoints")
                    self.is_busy = False
                    break

    def is_busy(self):
        return self.is_busy

    def get_data(self):
        data = np.zeros((self.ind_end, self.num_of_floats))
        data = self.data[0:self.ind_end].reshape((self.num_of_floats, int(self.ind_end/self.num_of_floats))).T
        data[:,0] = np.cumsum(data[:, 0]) * 1e-6
        return data

        # data = {}
        # data['values'] = self.data[0:self.ind_end].reshape((self.num_of_floats, int(self.ind_end/self.num_of_floats))).T
        # data['time'] = np.cumsum(data['values'][:, 0]) * 1e-6
        # data['time'] = data['time'] - data['time'][0]
        # data['values'] = data['values'][:, 1:]
        # return data

    def send_start_byte(self, start_byte=255):
        self.serial_port.reset_input_buffer()
        self.timer = time.time()
        self.serial_port.write(bytes([start_byte]))
        self.trigger_attempts += 1
        print(f"SerialStream waiting for {self.timeout:.2f} seconds...")

# Example usage:
# port = 'COM1'  # Adjust port accordingly
# baudrate = 9600  # Adjust baudrate accordingly
# stream = SerialStream(port, baudrate)
# stream.start()
# data = stream.get_data()
# print(data)