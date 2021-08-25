#!/usr/bin/env python3

import socket

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 3334  # 65432        # The port used by the server

# packet_type
#     0x00 - send registration report
#     0x01 - send sensor report
#     0x02 - send device report
#     0xFF - checking for commands

send_packet_type = [0xFF]
data = []

for send_packet in send_packet_type:
    if send_packet == 0x00:  # send registration report
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            mas = [0x01, 0x05, 0x10, 0x20, 0x0a, 0x0b, 0xc0, 0xd0, 0x4a, 0xff, 0xc2, 0x00,  # ID
                   0,  # type report (0 - registration, 1 - sensor, 2 - device)
                   3,  # amt
                   0x02, 0x06, 0x11, 0x21, 0x0b, 0x0c, 0xc1, 0xd1, 0x4b, 0x00, 0xc3, 0x01,  # module 1
                   0x03, 0x07, 0x12, 0x22, 0x0c, 0x0d, 0xc2, 0xd2, 0x4c, 0x01, 0xc4, 0x02,  # module 2
                   0x04, 0x08, 0x13, 0x23, 0x0d, 0x0e, 0xc3, 0xd3, 0x4d, 0x02, 0xc5, 0x03,  # module 3
                   15, 6, 2020 >> 8, 2020 & 0xFF,  # date
                   12, 45, 20]  # time
            byt = bytearray(mas)
            s.sendall(byt)
            data.append(s.recv(1024))

    elif send_packet == 0x01:  # send sensor report
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            mas = [0x02, 0x06, 0x11, 0x21, 0x0b, 0x0c, 0xc1, 0xd1, 0x4b, 0x00, 0xc3, 0x01,  # ID
                   1,  # type report (0 - registration, 1 - sensor, 2 - device)
                   2,  # amt
                   # 0, 0, 10, 20,          # sensor 1
                   # 1, 0, 1,               # sensor 2
                   3, 1, 0x42, 0x12, 0x66, 0x66,  # sensor 3
                   6, 0, 0x43, 0x66, 0x00, 0x00,  # sensor 4
                   15, 6, 2020 >> 8, 2020 & 0xFF,  # date
                   12, 30, 30]  # time
            byt = bytearray(mas)
            s.sendall(byt)
            data.append(s.recv(1024))

    elif send_packet == 0x02:  # send device report
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            mas = [0x03, 0x07, 0x12, 0x22, 0x0c, 0x0d, 0xc2, 0xd2, 0x4c, 0x01, 0xc4, 0x02,  # ID
                   #  3,    7,   18,   34,   12,   13,  194,  210,   76,    1,  196,    2,  # ID
                   2,            # type report (0 - registration, 1 - sensor, 2 - device)
                   2,            # amt
                   2, 0, 8, 15,  # device 1
                   3, 0, 1,      # device 2
                   31, 12, 2020 >> 8, 2020 & 0xFF,  # date
                   23, 59, 59]    # time
            byt = bytearray(mas)
            s.sendall(byt)
            data.append(s.recv(1024))

    elif send_packet == 0xFF:  # checking for commands
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            mas = [0x01, 0x05, 0x10, 0x20, 0x0a, 0x0b, 0xc0, 0xd0, 0x4a, 0xff, 0xc2, 0x00,  # ID
                   0xFF]  # type report (0 - registration, 1 - sensor, 2 - device, 255 - checking for commands)
            byt = bytearray(mas)
            s.sendall(byt)
            data.append(s.recv(1024))

    else:
        data.append('~')


for receive in data:
    print('Received\n', repr(receive), end='\n\n')

# print('Received', repr(data0))
# print('Received', repr(data1))
# print('Received', repr(data2))
# print('Received', repr(data3))
