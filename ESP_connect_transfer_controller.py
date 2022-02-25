import array
from enum import Enum

# Максимальный размер пакета (по умолчанию)
BUFFER_SIZE = 250


# Состояние обмена информацией
class Stage(Enum):
    No_transmission = 0  # Нет передачи
    # Принимающий модуль
    Received_initialization_byte = 1  # Принят инициализирующий байт
    Received_length_byte = 2  # Принят байт длины
    Receive_bytes = 3  # Приём байт
    Expect_trailing_byte = 4  # Ожидается завершающий байт
    # Отправляющий модуль
    Sent_initialization_byte = 5  # Отправлен инициализирующий байт
    Sent_length_byte = 6  # Отправлен байт длины
    Sending_bytes = 7  # Отправка байт
    Sent_trailing_byte = 8  # Отправлен завершающий байт
    # Количество компонентов
    AMT_COMPONENTS = 9


# Статус завершения передачи/приёма
class Status(Enum):
    Ok = 0  # Передача или приём завершены и обработаны
    Exit = 1  # Передача или приём завершены и не обработаны
    Error = 2  # Передача или приём завершены с ошибкой
    # --- Это не сделано, реакция на одновременную отправку 2-х
    # --- модулей друг другу. В этом случае менее приоритетный
    # --- модуль должен будет перейти в состояние Postponed.
    Postponed = 3  # (-) ----- Передача ожидает завершения приёма
    # Количество компонентов
    AMT_COMPONENTS = 4


class WireTransferController(object):
    """Класс контроля проводного обмена

    Данный класс осуществляет контроль простейшего
    обмена между двумя узлами. Позволяет осуществлять
    передачу при дуплексном, быстром обмене.

    Attributes
    ----------
    send_buffer : array.array
        Массив буфера отправки, длиной BUFFER_SIZE.
    send_len : int
        Отправляемая длина
    send_cnt : int
        Отправленная количество
    last_send_byte : int
        Последний отправленный байт
    send_status : Status
        Статус отправки
    receive_buffer : array.array
        Массив буфера приёма, длиной BUFFER_SIZE.
    receive_len : int
        Ожидаемая длина
    receive_cnt : int
        Принятое количество
    last_receive_byte : list(int)
        Последний принятый байт
    receive_status : Status
        Статус приёма
    stage : Status
        Текущая стадия
    send : function(uint8_t)
        Функция отправки байта информации
    receive : function(uint8_t&)
        Функция приёма байта информации (по адресу, т.е. массиву единичной длины)
    ----------
    """

    def __init__(self, send, receive):
        self.send_buffer = array.array('i', [0]) * BUFFER_SIZE  # буфер отправки
        self.send_len = 0  # отправляемая длина
        self.send_cnt = 0  # отправленная количество
        self.last_send_byte = 0  # последний отправленный байт
        self.send_status = Status.Ok  # статус отправки
        self.receive_buffer = array.array('i', [0]) * BUFFER_SIZE  # буфер приёма
        self.receive_len = 0  # ожидаемая длина
        self.receive_cnt = 0  # принятое количество
        self.amt_error = 0  # количество произошедших ошибок
        self.max_amt_error = 5  # максимальное количество произошедших ошибок
        self.last_receive_byte = [0]  # последний принятый байт
        self.receive_status = Status.Ok  # статус приёма
        self.stage = Stage.No_transmission  # текущая стадия
        self.send = send  # функция отправки байта информации
        self.receive = receive  # функция приёма байта информации

    def begin(self) -> None:
        """ Сброс всех полей и старт приёма """
        self.erase()
        self.receive(self.last_receive_byte)

    def get_send_status(self) -> Status:
        """ Получение статуса отправки """
        return self.send_status

    def get_receive_status(self) -> Status:
        """ Получение статуса приёма """
        return self.receive_status

    def get_stage(self) -> Stage:
        """ Получение состояния передачи/приёма """
        return self.stage

    def send_data(self, buffer) -> bool:
        """ Начать отправку буфера данных """
        if isinstance(buffer, int):
            buffer = [buffer]
        if not isinstance(buffer, list):
            return True
        else:
            buffer = buffer[:]  # копирование буфера
        if (self.stage != Stage.No_transmission) or (BUFFER_SIZE < len(buffer)):
            return True
        self.send_cnt = 0
        self.send_len = len(buffer)
        self.send_status = Status.Ok
        self.stage = Stage.Sent_initialization_byte
        self.amt_error = 0

        for ind, num in enumerate(buffer):
            self.send_buffer[ind] = num
        self.last_send_byte = 0xA5
        self.send(self.last_send_byte)
        return False

    def receive_data(self):
        """ Получить принятые данные """
        if (self.stage != Stage.No_transmission) or (self.receive_status == Status.Ok):
            return None
        size = self.receive_len
        self.receive_status = Status.Ok
        self.receive_cnt = 0
        self.receive_len = 0
        buffer = []
        for ind in range(size):
            buffer.append(self.receive_buffer[ind])
        return buffer

    def end_send(self) -> None:
        """ Завершена отправка байта """
        if self.stage == Stage.No_transmission:
            # Такого быть не может
            pass
        elif self.stage == Stage.Received_initialization_byte:
            # отправили ответ на байт инициализации, ожидаем байт длины
            self.receive(self.last_receive_byte)
        elif self.stage == Stage.Received_length_byte:
            # отправили ответ на байт длины, ожидаем байт подтверждения длины
            self.receive(self.last_receive_byte)
        elif self.stage == Stage.Receive_bytes:
            # Такого быть не может
            pass
        elif self.stage == Stage.Expect_trailing_byte:
            # Отправили ответ на завершающий байт
            self.stage = Stage.No_transmission
            self.receive_status = Status.Exit
            # (-) ----- отправить инициализирующий пакет, если ожидаем?
        elif self.stage == Stage.Sent_initialization_byte:
            # Отправили байт инициализации, ожидаем реакцию; отправили 0, отправляем байт инициализации
            if self.last_send_byte == 0:
                self.last_send_byte = 0xA5
                self.send(self.last_send_byte)
            else:
                self.receive(self.last_receive_byte)
        elif self.stage == Stage.Sent_length_byte:
            # Отправили байт длины, ожидаем реакцию; отправили 0xFF, отправляем байт длины
            if self.last_send_byte == 0xFF:
                self.last_send_byte = self.send_len
                self.send(self.last_send_byte)
            else:
                self.receive(self.last_receive_byte)
        elif self.stage == Stage.Sending_bytes:
            # Отправили байт, отправляем следующий или отправляем конечный
            if self.send_cnt < self.send_len:
                # self.last_send_byte = self.send_buffer[self.send_cnt]
                # self.send_cnt += 1
                # self.send(self.last_send_byte)
                self.last_send_byte = self.send_buffer[:self.send_len]
                self.send_cnt += len(self.last_send_byte)
                self.send(self.last_send_byte)
            else:
                self.stage = Stage.Sent_trailing_byte
                self.last_send_byte = 0x5A
                self.send(self.last_send_byte)
        elif self.stage == Stage.Sent_trailing_byte:
            # Отправили конечный, ожидаем байт подтверждения
            self.receive(self.last_receive_byte)
        else:
            self.stage = Stage.No_transmission

    def end_receive(self) -> None:
        """ Завершён приём байта """
        if self.stage == Stage.No_transmission:
            # начало отправки с другой стороны, отправить реакцию игнор
            if self.last_receive_byte[0] == 0xA5:
                self.stage = Stage.Received_initialization_byte
                self.last_send_byte = 0xDB
                self.send(self.last_send_byte)
                self.amt_error = 0
            else:
                self.last_receive_byte[0] = 0
                self.receive(self.last_receive_byte)
        elif self.stage == Stage.Received_initialization_byte:
            # проверяю на 0, если есть длина, отправляю инверсию, если 0 ожидаю начало инициализации
            if self.last_receive_byte[0] == 0:
                self.stage = Stage.No_transmission
                self.receive(self.last_receive_byte)
            elif self.last_receive_byte[0] == 0xFF:
                self.receive(self.last_receive_byte)
            else:
                self.stage = Stage.Received_length_byte
                self.receive_len = self.last_receive_byte[0]
                self.last_send_byte = ((~self.receive_len) & 0xFF)
                self.send(self.last_send_byte)
        elif self.stage == Stage.Received_length_byte:
            # проверяю на 0xFF, если есть инверсия длины, принимаю серию байт, если 0 ожидаю байт длины
            check_byte = (((~self.receive_len) & 0xFF) << 4 & 0xF0) | (((~self.receive_len) & 0xFF) >> 4 & 0x0F)
            if self.last_receive_byte[0] == 0xFF:
                self.stage = Stage.Received_initialization_byte
            elif self.last_receive_byte[0] == check_byte:
                self.stage = Stage.Receive_bytes
            else:
                self.stage = Stage.No_transmission
                self.receive_status = Status.Error
            self.receive(self.last_receive_byte)
        elif self.stage == Stage.Receive_bytes:
            # принимаем байты, если все - то ожидаем последний байт
            self.receive_buffer[self.receive_cnt] = self.last_receive_byte[0]
            self.receive_cnt += 1
            self.receive(self.last_receive_byte)
            if self.receive_cnt == self.receive_len:
                self.receive_cnt = 0
                self.stage = Stage.Expect_trailing_byte
        elif self.stage == Stage.Expect_trailing_byte:
            # Принимаем завершающий байт
            if self.last_receive_byte[0] == 0x5A:
                self.last_send_byte = 0x24
                self.send(self.last_send_byte)
            else:
                self.stage = Stage.No_transmission
                self.receive_status = Status.Error
                # (-) ----- отправить инициализирующий пакет, если ожидаем?
        elif self.stage == Stage.Sent_initialization_byte:
            # Реакция на инициализирующий пакет
            if self.last_receive_byte[0] == 0xDB:
                # отправить длину
                self.stage = Stage.Sent_length_byte
                self.last_send_byte = self.send_len
                self.send(self.last_send_byte)

            elif self.last_receive_byte[0] == 0xA5:
                # (-) ----- проверка на приоритет, если я важнее, то реагируем как в
                #       Received_initialization_byte, если нет - то отправить 0xDB
                self.last_send_byte = 0xDB
                self.send(self.last_send_byte)
            else:
                self.last_send_byte = 0
                self.send(self.last_send_byte)
        elif self.stage == Stage.Sent_length_byte:
            # Принята инвертированная длина
            if self.last_receive_byte[0] == ((~self.send_len) & 0xFF):
                # отправить перемешанную длину
                self.stage = Stage.Sending_bytes
                self.last_send_byte = (self.last_receive_byte[0] << 4 & 0xF0) | (self.last_receive_byte[0] >> 4 & 0x0F)
                self.send(self.last_send_byte)
            else:
                # Ошибка, обнуляю
                self.last_send_byte = 0xFF
                self.send(self.last_send_byte)
        elif self.stage == Stage.Sending_bytes:
            # Такого быть не может
            pass
        elif self.stage == Stage.Sent_trailing_byte:
            # Принимаем реакцию на завершающий байт
            if self.last_receive_byte[0] == 0x24:
                self.stage = Stage.No_transmission
                self.send_status = Status.Exit
            else:
                self.stage = Stage.No_transmission
                self.send_status = Status.Error
            self.receive(self.last_receive_byte)
        else:
            self.stage = Stage.No_transmission

    def receive_timeout(self) -> None:
        """ Истекло время ожидания байта """
        self.last_receive_byte[0] = 0
        if self.stage == Stage.No_transmission:
            self.stage = Stage.No_transmission
            self.receive(self.last_receive_byte)
        elif self.stage in (Stage.Received_initialization_byte, Stage.Received_length_byte, Stage.Receive_bytes,
                            Stage.Expect_trailing_byte):
            self.stage = Stage.No_transmission
            self.receive_status = Status.Error
            self.receive(self.last_receive_byte)
        elif self.stage == Stage.Sent_initialization_byte:
            # (-) ----- зацикливание
            self.amt_error += 1
            if self.amt_error == self.max_amt_error:
                self.amt_error = 0
                self.stage = Stage.No_transmission
                self.send_status = Status.Error
                self.receive(self.last_receive_byte)
            else:
                self.last_send_byte = 0
                self.send(self.last_send_byte)
        elif self.stage == Stage.Sent_length_byte:
            # (-) ----- зацикливание
            self.amt_error += 1
            if self.amt_error == self.max_amt_error:
                self.amt_error = 0
                self.stage = Stage.No_transmission
                self.send_status = Status.Error
                self.receive(self.last_receive_byte)
            else:
                self.last_send_byte = 0xFF
                self.send(self.last_send_byte)
        elif self.stage == Stage.Sending_bytes:
            pass
        elif self.stage == Stage.Sent_trailing_byte:
            self.stage = Stage.No_transmission
            self.send_status = Status.Error
            self.receive(self.last_receive_byte)
        else:
            self.stage = Stage.No_transmission
            self.receive(self.last_receive_byte)

    def clear_send_status(self) -> Status:
        """ Сбросить состояние отправки """
        result = Status(self.send_status)
        self.send_status = Status.Ok
        return result

    def clear_receive_status(self) -> Status:
        """ Сбросить состояние приёма """
        result = Status(self.receive_status)
        self.receive_status = Status.Ok
        return result

    def erase(self) -> None:
        """ Сбросить состояние всех полей """
        self.stage = Stage.No_transmission
        self.send_status = Status.Ok
        self.receive_status = Status.Ok
