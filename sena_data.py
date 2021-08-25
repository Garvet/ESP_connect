class Module(object):
    def __init__(self, module_id, component, module_data, time):
        self.id = module_id
        self.type = component
        self.data = module_data
        self.time = time


devices_type = {0x00: {'name': 'Signal_PWM',        'num_bite': 12, 'type': int},   # value = 0...4095
                0x01: {'name': 'Signal_digital',    'num_bite':  1, 'type': bool},  # value = 0, 1
                0x02: {'name': 'Fan_PWM',           'num_bite': 12, 'type': int},   # value = 0...4095
                0x03: {'name': 'Pumping_system',    'num_bite':  1, 'type': bool},  # value = 0, 1
                0x04: {'name': 'Phytolamp_digital', 'num_bite':  1, 'type': bool},  # value = 0, 1
                0x05: {'name': 'Phytolamp_PWM',     'num_bite': 12, 'type': int}}   # value = 0...4095


def set_bytes(data, byte):
    data.append(byte)


def set_id(data, str_id):
    for num_byte in range(0, len(str_id), 2):
        set_bytes(data, int(str_id[num_byte:num_byte + 2], 16))


def send_esp_command(data, module):
    # Добавление ID
    set_id(data, module.id)
    # Добавление типа компонента
    set_bytes(data, 0x02)  # set type (only devices)
    # Добавление количества компонентов
    set_bytes(data, len(module.data))  # amt_component
    # Добавление данных о компонентах
    for i in range(len(module.data)):
        # Поиск номера типа компонента
        num_device = None
        for num, device in devices_type.items():
            if device['name'] == module.data[i]['component']:
                num_device = num
                break
        if num_device is None:
            return 'argh!!!'
        # Добавление номера типа компонента
        set_bytes(data, num_device)  # set component
        # Добавление номера компонента указанного типа
        set_bytes(data, module.data[i]['number'])  # set number

        # Добавление значения компонента
        if devices_type[num_device]['num_bite'] == 12:
            set_bytes(data, module.data[i]['value'] >> 8)
            set_bytes(data, module.data[i]['value'] & 0xFF)
        else:
            if module.data[i]['value']:
                set_bytes(data, 1)
            else:
                set_bytes(data, 0)


command = [Module('010203040506070809101112', 'Devices', [{'component': 'Signal_PWM', 'number': 1, 'value': 123}],
                  '12-04-1961 09:07:00')]
send_data = []
send_esp_command(data=send_data, module=command[0])
send_data = [1, (len(send_data) >> 8) & 0xFF, len(send_data) & 0xFF] + send_data
byt = bytearray(send_data)
print(send_data)
