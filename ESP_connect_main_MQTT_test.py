from ESP_connect_package_converter import *
import paho.mqtt.client as mqtt

# HOST = '192.168.1.72'  # The server's hostname or IP address
# PORT = 3333  # 65432        # The port used by the server
HOST = 'localhost'  # The server's hostname or IP address
PORT = 1883  # 65432        # The port used by the server


# Формирование данных из полученного пакета (в виде массива
#     байт и в виде строки на основе массива)
def from_packet_to_data(packet: bytearray):
    receive_data = {
        'int': [int(byte) for byte in packet],
        'str': str(packet)[2:-1]
    }
    return receive_data


# Условная реакция на топик регистрации (вывод int и str
#     форматов входящих данных, сообщения в терминал и
#     сообщения в топик '/down/registration'.
def up_id(receive_data):
    receive_data = receive_data['int']
    print('data[\'int\'] = ', end='')
    print(receive_data)
    receive_object = receive_esp_report(receive_data)
    if isinstance(receive_object, str):
        # Error
        print(receive_object)
    else:
        # Принят объект
        if isinstance(receive_object, Module):  # report = device or sensor
            module = receive_object
            print(module)
            print("module_id  = " + str(module.id))
            print("module_num = " + str(module.data))
            print("time = " + str(module.time))
            print()
        elif isinstance(receive_object, SystemRegistration):  # report = registration
            registration_data = receive_object
            print(registration_data)
            print("module_id   = " + str(registration_data.mainId))
            print("attached_id = " + str(registration_data.attachedId))
            print()
        else:  # report = None
            pass


# Набор топиков и соответствующие им функции.
# Т.е. topics['name'](data) - будет вызывать функцию, например
#     topics['/up/registration'](data) == up_registration(data)
topics = {'/up/5FDCBDCB5F2597308617089B': up_id}


# Обратный вызов, когда клиент получает ответ CONNACK от сервера.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Подписка в on_connect() означает, что если мы потеряем соединение
    # и переподключимся, то подписки будут возобновлены.

    # Подпись на топики
    # client.subscribe('/up/registration', 0)
    # client.subscribe('/up/registration_confirm', 0)

    # Альтернативный вид подписи (по сути своей тоже самое, но автоматом заполняет
    #     по ключам словаря, т.е. в первой итерации name = '/up/registration')
    for name in topics:
        client.subscribe(name, 0)


# Обратный вызов для получения сообщения PUBLISH от сервера.
def on_message(client, userdata, msg):
    print('\n----- on_message -----')
    # Вывод пришедшего сообщения в формате "топик : сообщение"
    print(msg.topic + " : " + str(msg.payload))
    # Преобразование пришедших данных (формата как удобнее)
    data = from_packet_to_data(msg.payload)
    # Передача данных в функции иммитирующие топики
    if str(msg.topic) in topics:
        topics[str(msg.topic)](data)
    print('----- ----- -----')


if __name__ == '__main__':
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    # 'localhost' - твой адрес, меняется на IP для связи с внешним миром.
    # Этот же адрес будет вводиться на ESP32 (IP естественно).
    client.connect(HOST, PORT, 60)

    # Блокирующий вызов, который обрабатывает сетевой трафик, отправляет обратные вызовы и
    # обрабатывает повторное подключение.
    # Доступны и другие функции loop*(), которые предоставляют многопоточный интерфейс и
    # ручной интерфейс.
    client.loop_forever()


# # HOST = '192.254.168.148'  # '127.0.0.1' - the default address of the loopback interface (localhost)
# # HOST = '192.168.1.70'  # '127.0.0.1' - the default address of the loopback interface (localhost)
# HOST = '192.168.1.37'  # '127.0.0.1' - the default address of the loopback interface (localhost)
# # HOST = '192.168.1.72'  # '127.0.0.1' - the default address of the loopback interface (localhost)
# # HOST = '127.0.0.1'  # '127.0.0.1' - the default address of the loopback interface (localhost)
# PORT = 3334  # Listening port (unprivileged ports > 1023)
# # PORT = 6543  # Listening port (unprivileged ports > 1023)
#
# # Array for device management
# #   for filling with objects of type "Module", example and
# #   content types see in "ESP_connect_classes.py"
# devices_command = []
# num_send_mode = 10
# modules_data_mode = Module(module_id='030712220c0dc2d24c01c402',
#                            module_data=[
#                              {'component': 'Signal_digital',
#                               'number': 0,
#                               'value': True  # False - STOP, True - WORK
#                               }
#                            ],
#                            time='')
# num_send_value = 10
# value_send_value = 4095
# modules_data_value = Module(module_id='030712220c0dc2d24c01c402',
#                             module_data=[
#                               {'component': 'Signal_PWM',
#                                'number': 0,
#                                'value': 4095  # Set value in {0, ..., 4095}
#                                }
#                             ],
#                             time='')
# send = False
#
# if __name__ == '__main__':
#     socket = init_esp_connect(host=HOST, port=PORT)  # init
#     print(socket.getsockname())
#     while True:
#         report = receive_esp_report(socket, devices_command)  # receive module
#         if isinstance(report, Module):  # report = device or sensor
#             module = report
#             print(module)
#             print("module_id  = " + str(module.id))
#             print("module_num = " + str(module.data))
#             print("time = " + str(module.time))
#             print()
#         elif isinstance(report, SystemRegistration):  # report = registration
#             registration_data = report
#             print(registration_data)
#             print("module_id   = " + str(registration_data.mainId))
#             print("attached_id = " + str(registration_data.attachedId))
#             print()
#         else:  # report = None
#             if not send:
#                 continue
#             print('.', end='')
#             send_packet = [
#                 # 'send_mode_packet',
#                 'send_value_packet',
#             ]
#             if 'send_mode_packet' in send_packet:
#                 num_send_mode -= 1
#                 if num_send_mode == 0:
#                     if modules_data_mode.data[0]['value']:
#                         modules_data_mode.data[0]['value'] = False  # False
#                     else:
#                         modules_data_mode.data[0]['value'] = True  # True
#                     devices_command.append(modules_data_mode)
#                     print('|S|')
#                     num_send_mode = 30
#             if 'send_value_packet' in send_packet:
#                 num_send_value -= 1
#                 if num_send_value == 0:
#                     if modules_data_value.data[0]['value'] == 4095:    # { 100% }
#                         modules_data_value.data[0]['value'] = 3071
#                     elif modules_data_value.data[0]['value'] == 3071:  # {  75% }
#                         modules_data_value.data[0]['value'] = 2047
#                     elif modules_data_value.data[0]['value'] == 2047:  # {  50% }
#                         modules_data_value.data[0]['value'] = 1023
#                     elif modules_data_value.data[0]['value'] == 1023:  # {  25% }
#                         modules_data_value.data[0]['value'] = 0
#                     else:                                              # {   0% }
#                         modules_data_value.data[0]['value'] = 4095
#                     devices_command.append(modules_data_value)
#                     print('|V|')
#                     num_send_value = 45
