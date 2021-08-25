from ESP_connect_TCP_exchange import *

HOST = '95.181.230.220'  # '192.168.1.70'    # '127.0.0.1' - the default address of the loopback interface (localhost)
PORT = 3334  # Listening port (unprivileged ports > 1023)

# Array for device management
#   for filling with objects of type "Module", example and
#   content types see in "ESP_connect_classes.py"
devices_command = []

if __name__ == '__main__':
    socket = init_esp_connect(host=HOST, port=PORT)  # init
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
            # add a device control command to send to the ESP
            #    devices_command.append(modules_data) <- type(modules_data) = Module
            pass
