from ESP_connect_TCP_exchange import *

# HOST = '192.254.168.148'  # '127.0.0.1' - the default address of the loopback interface (localhost)
# HOST = '192.168.1.70'  # '127.0.0.1' - the default address of the loopback interface (localhost)
HOST = '192.168.1.37'  # '127.0.0.1' - the default address of the loopback interface (localhost)
# HOST = '192.168.1.72'  # '127.0.0.1' - the default address of the loopback interface (localhost)
# HOST = '127.0.0.1'  # '127.0.0.1' - the default address of the loopback interface (localhost)
PORT = 3334  # Listening port (unprivileged ports > 1023)
# PORT = 6543  # Listening port (unprivileged ports > 1023)

# Array for device management
#   for filling with objects of type "Module", example and
#   content types see in "ESP_connect_classes.py"
devices_command = []
num_send = 10
modules_data = Module(module_id='030712220c0dc2d24c01c402',
                      module_data=[
                          {'component': 'Signal_digital',
                           'number': 0,
                           'value': True
                           }
                      ],
                      time='')

if __name__ == '__main__':
    socket = init_esp_connect(host=HOST, port=PORT)  # init
    print(socket.getsockname())
    while True:
        report = receive_esp_report(socket, devices_command)  # receive module
        if isinstance(report, Module):  # report = device or sensor
            module = report
            print(module)
            print("module_id  = " + str(module.id))
            print("module_num = " + str(module.data))
            print("time = " + str(module.time))
            print()
        elif isinstance(report, SystemRegistration):  # report = registration
            registration_data = report
            print(registration_data)
            print("module_id   = " + str(registration_data.mainId))
            print("attached_id = " + str(registration_data.attachedId))
            print()
        else:  # report = None
            print('.', end='')
            num_send -= 1
            if num_send == 0:
                if modules_data.data[0]['value']:
                    modules_data.data[0]['value'] = False  # False
                else:
                    modules_data.data[0]['value'] = True  # True
                devices_command.append(modules_data)
                print('|')
                num_send = 30
