# import socket
# import sys
# import time
import struct
from ESP_connect_interface_classes import *


def get_bytes(data, num, amt=1):
    byte = data[num[0]:num[0]+amt]
    num[0] += amt
    if len(byte) == 1:
        return byte[0]
    return byte


def get_id(data, num, amt=12):
    mas_id = get_bytes(data=data, num=num, amt=amt)
    id_str = ''
    for num in mas_id:
        if num < 16:
            id_str = id_str + '0'
        id_str = id_str + format(num, 'x')
    return id_str

# def init_esp_connect(host='127.0.0.1', port=1234):
#     try:
#         esp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     except socket.error as error:
#         print('Failed to create socket. Error: ' + str(error))
#         sys.exit()
#     try:
#         esp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         # esp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE,
#         #                       str("wlxd03745b6d153" + '\0').encode('utf-8'))
#         while True:
#             try:
#                 # esp_socket.bind((HOST, PORT))
#                 esp_socket.bind((host, port))
#             except OSError:
#                 time.sleep(0.5)
#             else:
#                 break
#         esp_socket.settimeout(1.0)
#         esp_socket.listen()
#     except socket.error as error:
#         print('Bind failed. Error: ' + str(error))
#         sys.exit()
#     print('Server listening')
#     return esp_socket


def read_module_report(module_id, module_type, data, num_byte):
    if module_type == 1:
        component_type = sensors_type
    elif module_type == 2:
        component_type = devices_type
    else:
        return None
    amt_component = get_bytes(data, num_byte)
    components = []
    for i in range(amt_component):
        component = get_bytes(data, num_byte)
        number = get_bytes(data, num_byte)
        if component_type[component]['num_byte'] == 4:
            reg_float = get_bytes(data, num_byte, 4)
            reg_float.reverse()
            byt = bytearray(reg_float)
            value = struct.unpack('<f', byt)[0]
        elif component_type[component]['num_byte'] == 2:
            value = (get_bytes(data, num_byte) << 8) + get_bytes(data, num_byte)
        else:
            value = get_bytes(data, num_byte, component_type[component]['num_byte'])
        value = component_type[component]['type'](value)
        components.append({'component': component_type[component]['name'], 'number': number, 'value': value})
    data_time = get_bytes(data, num_byte, 7)
    year = ((0xFF & data_time[2]) << 8) | (0xFF & data_time[3])
    date_time = f'{data_time[0]}-{data_time[1]}-{year} {data_time[4]}:{data_time[5]}:{data_time[6]}'
    return Module(module_id,
                  components,
                  date_time
                  )


def read_registration_report(module_id, data, num_byte):
    amt_component = get_bytes(data, num_byte)
    modules = []
    for i in range(amt_component):
        modules.append(get_id(data, num_byte))
    return SystemRegistration(module_id, modules)


# def receive_esp_report(esp_socket, command=None):
def receive_esp_report(packet: (bytearray, list)):
    data = [int(byte) for byte in packet]
    # if isinstance(packet, bytearray):
    #     data = [int(byte) for byte in packet]
    # elif isinstance(packet, list):
    #     for i in range(len(packet)):
    #         if isinstance(packet[i], int):
    #             data.append(packet[i])
    #         else:
    #             return 'Error: when passing an list, all components must be int.'
    # else:
    #     return 'Error: Only components of type bytearray or list[int] are processed.'

    num_byte = [0]
    module_id = get_id(data, num_byte)
    module_type = get_bytes(data, num_byte)
    if module_type == 0xFF:
        return None
    elif module_type == 0:
        return read_registration_report(module_id, data, num_byte)
    else:
        return read_module_report(module_id, module_type, data, num_byte)

    # while True:
    #     try:
    #         conn, address = esp_socket.accept()
    #     except socket.timeout:
    #         return None
    #     with conn:
    #         print('Connected by', address, '.')
    #         report_data = None
    #         conn.settimeout(5.0)
    #         try:
    #             report_data = conn.recv(1024)
    #         except socket.timeout:
    #             print('Connect error.')
    #         else:
    #             if isinstance(command, list) and \
    #                     len(command) > 0 and \
    #                     isinstance(command[0], Module):
    #                 send_data = []
    #                 send_esp_command(data=send_data, module=command[0])
    #                 send_data = [1, (len(send_data) >> 8) & 0xFF, len(send_data) & 0xFF] + send_data
    #                 byt = bytearray(send_data)
    #                 conn.sendall(byt)
    #                 command.pop(0)
    #             else:
    #                 conn.sendall(b'Receive correct.\r\n')
    #                 if isinstance(command, list) and len(command) > 0:
    #                     command.pop(0)
    #
    #         finally:
    #             conn.settimeout(None)
    #             conn.close()
    #
    #     if not report_data:
    #         continue
    #     else:
    #         # data = [int(byte) for byte in report_data]
    #         # data = [int(report_data[i]) for i in range(len(report_data))]
    #         for i in range(len(report_data)):
    #             data.append(int(report_data[i]))
    #         break


# function write data


# 'set_bytes' used for further encryption or quality control functions
def set_bytes(data, byte):
    data.append(byte)


def set_id(data, str_id):
    for num_byte in range(0, len(str_id), 2):
        set_bytes(data, int(str_id[num_byte:num_byte+2], 16))


# def send_esp_command(data, module):
#     set_id(data, module.id)
#     set_bytes(data, 0x02)  # set type (only devices)
#     set_bytes(data, len(module.data))  # amt_component
#     for i in range(len(module.data)):
#
#         num_device = None
#         for num, device in devices_type.items():
#             if device['name'] == module.data[i]['component']:
#                 num_device = num
#                 break
#         set_bytes(data, num_device)  # set component
#         set_bytes(data, module.data[i]['number'])  # set number
#
#         if devices_type[num_device]['num_byte'] == 2:
#             set_bytes(data, module.data[i]['value'] >> 8)
#             set_bytes(data, module.data[i]['value'] & 0xFF)
#         else:
#             if module.data[i]['value']:
#                 set_bytes(data, 1)
#             else:
#                 set_bytes(data, 0)

