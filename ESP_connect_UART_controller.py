import ESP_connect_transfer_controller as Utc
import serial

log_print = {
    'Print transmitted bytes': False,
    'Print transfer result': False,
    'Print sent package': False,
    'Print received package': False,
}
_adr_receive = []  # = &uart_data.last_receive_byte;
_end_send = False
_end_receive = False
_start_receive = False
global _uart
global _uart_controller
_receive_buffer = []
_send_packet = []
# global uart: serial.Serial
# uart = None


def _create_hex(byte):
    result = ''
    if len(hex(byte)[2:]) == 1:
        result += '0'
    return result + hex(byte)[2:].upper()


def _print_hex(byte, end=''):
    print(_create_hex(byte), end=end)
    # if len(hex(byte)[2:]) == 1:
    #     print('0', end='')
    # print(hex(byte)[2:].upper(), end=end)


def _uart_print(print_uart):
    mas_stage = ['No_transmission (Нет передачи)',
                 'Received_initialization_byte (Принят инициализирующий байт)',
                 'Received_length_byte (Принят байт длины)',
                 'Receive_bytes (Приём байт)',
                 'Expect_trailing_byte (Ожидается завершающий байт)',
                 'Sent_initialization_byte (Отправлен инициализирующий байт)',
                 'Sent_length_byte (Отправлен байт длины)',
                 'Sending_bytes (Отправка байт)',
                 'Sent_trailing_byte (Отправлен завершающий байт)']
    mas_status_s = ['Ok (Передача завершена и обработана)',
                    'Exit (Передача завершена и не обработана)',
                    'Error (Передача завершена с ошибкой)',
                    'Postponed (Передача ожидает завершения приёма)']
    mas_status_r = ['Ok (Приём завершён и обработан)',
                    'Exit (Приём завершён и не обработан)',
                    'Error (Приём завершён с ошибкой)']
    print('Stage = ' + mas_stage[print_uart.get_stage().value])
    print('S_status = ' + mas_status_s[print_uart.get_send_status().value])
    print('R_status = ' + mas_status_r[print_uart.get_receive_status().value])
    print()


def uart_print():
    _uart_print(_uart_controller)


def _uart_send(data):
    # Осуществляет отправку данных
    global _end_send
    global _uart
    if isinstance(data, int):
        data = [data]
    # _uart.write(bytearray([data]))
    _uart.write(bytearray([byte & 0xFF for byte in data]))
    _end_send = True
    # LOG
    if log_print['Print transmitted bytes']:
        for num in data:
            print('!', end='')
            _print_hex(int(num))
            print('! >>')
    # if log_print['Print transmitted bytes']:
    #     print('!', end='')
    #     _print_hex(int(data))
    #     print('! >>')


def _uart_start_receive(data):
    # Поднимает флаг готовности принимать данные
    global _adr_receive
    global _start_receive
    _adr_receive = data
    _start_receive = True


def _uart_receive():
    # Осуществляет приём байта данных
    global _adr_receive
    global _end_receive
    global _start_receive
    global _uart
    # data = [int(byte) for byte in bytearray(uart.read(1))]
    if _start_receive:
        receive = bytearray(_uart.read(1))
        if len(receive) > 0:
            _adr_receive[0] = int(receive[0])
            _start_receive = False
            _end_receive = True
            # LOG
            if log_print['Print transmitted bytes']:
                print('     << !', end='')
                _print_hex(int(receive[0]))  #
                print('!')


# Обработчик успешной отправки
def _handler_correct_dispatch():
    global _uart_controller
    # Опустить флаг отправки
    _uart_controller.begin()
    # LOG
    if log_print['Print sent package']:
        print('Correct send: [' + ''.join([_create_hex(num) + ', ' for num in _send_packet])[:-2] + ']')


# Обработчик ошибочной отправки
def _handler_error_dispatch():
    global _uart_controller
    # (-) ----- повторно начать отправку
    # Опустить флаг отправки
    _uart_controller.begin()
    # LOG
    if log_print['Print sent package']:
        print('Error send: [' + ''.join([_create_hex(num) + ', ' for num in _send_packet])[:-2] + ']')


# Обработчик успешного приёма
def _handler_correct_reception():
    global _uart_controller
    # (-) ----- принять пакет в массив
    _receive_buffer.append(_uart_controller.receive_data())
    # Опустить флаг приёма
    _uart_controller.begin()
    # LOG
    if log_print['Print received package']:
        print('Receive: [' + ''.join([_create_hex(num) + ', ' for num in _receive_buffer[-1]])[:-2] + ']')


# Обработчик ошибочного приёма
def _handler_error_reception():
    global _uart_controller
    # (-) ----- сообщить об этом
    # Опустить флаг приёма
    _uart_controller.begin()


def begin(port: str = "/dev/ttyUSB0"):
    global _uart
    global _uart_controller
    _uart = serial.Serial(port, baudrate=115200, timeout=0)
    _uart_controller = Utc.WireTransferController(_uart_send, _uart_start_receive)
    _uart_controller.begin()
    _uart.write([0])
    #


def loop():
    global _end_send
    global _end_receive
    global _uart_controller
    _uart_receive()
    if _end_send:
        _end_send = False
        _uart_controller.end_send()
    if _end_receive:
        _end_receive = False
        _uart_controller.end_receive()

    # Обработка результатов
    if _uart_controller.get_send_status() == Utc.Status.Exit:
        # LOG
        if log_print['Print transfer result']:
            print('\\/ S + \\/')
            uart_print()
            print('/\\ /\\ /\\')
        # Обработка
        _handler_correct_dispatch()
    if _uart_controller.get_send_status() == Utc.Status.Error:
        # LOG
        if log_print['Print transfer result']:
            print('\\/ S - \\/')
            uart_print()
            print('/\\ /\\ /\\')
        # Обработка
        _handler_error_dispatch()
    if _uart_controller.get_receive_status() == Utc.Status.Exit:
        # LOG
        if log_print['Print transfer result']:
            print('\\/ R + \\/')
            uart_print()
            print('/\\ /\\ /\\')
        # Обработка
        _handler_correct_reception()
    if _uart_controller.get_receive_status() == Utc.Status.Error:
        # LOG
        if log_print['Print transfer result']:
            print('\\/ R - \\/')
            uart_print()
            print('/\\ /\\ /\\')
        # Обработка
        _handler_error_reception()


def send_data(data):
    global _uart_controller
    global _send_packet
    # Отправить пакет
    if isinstance(data, int):
        data = [data]
    if not isinstance(data, list):
        return 'Error: type(data) is not list or int.'
    elif Utc.BUFFER_SIZE < len(data):
        return 'Error: max_len < length packet (' + str(Utc.BUFFER_SIZE) + ' < ' + str(len(data)) + ').'
    else:
        data = data[:]  # копирование буфера
        _send_packet = data[:]
    _uart_controller.send_data(data)
    # LOG
    if log_print['Print sent package']:
        print('Send: [' + ''.join([_create_hex(num) + ', ' for num in data])[:-2] + ']')
    return 'Correct'


def size_receive_buffer():
    # Размер буфера, с принятыми пакетами
    return len(_receive_buffer)


def receive_data(number: int = None):
    global _receive_buffer
    # Получить пакет под номером X (при -1 возвращает массив из всех пакетов)
    if number is None:
        data = _receive_buffer
        _receive_buffer = []
    else:
        data = _receive_buffer.pop(number)
    return data

