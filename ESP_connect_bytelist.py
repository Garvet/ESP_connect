def hex_to_byte(data: str):
    if not isinstance(data, str):
        return None
    if len(data) % 2 == 1:
        data = '0' + data
    return [int(data[i:i+2], 16) for i in range(0, len(data), 2)]


def uint_to_byte(data: int, amt_bit: int = 12):
    if not isinstance(data, int) or not isinstance(amt_bit, int) or amt_bit < 0:
        return None
    mas = []
    for i in range(amt_bit//8):
        mas.insert(0, data >> (i * 8) & 0xFF)
    if amt_bit % 8 != 0:
        # bit_mask = sum([1 << i for i in range(amt_bit % 8)])
        # mas.insert(0, data >> (amt_bit//8 * 8) & bit_mask)
        mas.insert(0, data >> (amt_bit//8 * 8) & sum([1 << i for i in range(amt_bit % 8)]))
    return mas


def CRC_counter(data):
    if isinstance(data, int):
        data = [data]
    if not isinstance(data, list):
        return None
    crc = 0
    for byte in data:
        crc += byte * 211
        crc = (crc & 0xFF) ^ ((crc >> 8) & 0xFF)
    return crc


class ByteList(object):
    def __init__(self, data: list = None):
        """ Конструктор ByteList

        @param data : C{list} - массив байт типа int.
        """
        if data is None:
            data = []
        self.data = data
        self.num = 0
        self.crc_sum = 0

    def __len__(self):
        """ Длинна

        @return: Возвращает длинну массива
        """
        return len(self.data)

    def index(self):
        """ Индекс

        @return: Возвращает текущий индекс считывания
        """
        return self.num

    def remainder(self):
        """ Остаток

        @return: Возвращает количесвто оставшихся байт от текущего индекса
        """
        return len(self) - self.num

    def empty(self):
        """ Очистка полей класса
        """
        self.__init__([])

    def get_bytes(self, amt: int = 1):
        """ Получение байт из конца массива

        @param amt : Параметр указывающий количество следующих изымаемых байт, увеличивая
        счётчик (при отрицательных значениях, счётчик уменьшается, как и индексы, но порядок
        остаётся таким же, каким был в массиве).
        @return: Возвращает числовое значение байта, или массив байтов
        """
        if len(self.data) < self.num:
            print('Error')
        if amt > 0:
            byte = self.data[self.num:self.num + amt]
        else:
            byte = self.data[self.num + amt:self.num]
        self.num += amt
        if len(byte) == 1:
            return byte[0]
        return byte

    def get_hex(self, amt: int = 12) -> str:
        """ Получение шестнадцатеричного значения из конца массива

        @param amt : Параметр указывающий количество байт, изымаемых из конца массива
        @return: Возвращает строку байт в HEX формате из конца массива (длиной amt*2)
        """
        mas_id = self.get_bytes(amt=amt)
        id_str = ''
        if isinstance(mas_id, int):
            mas_id = [mas_id]
        for num in mas_id:
            if num < 16:
                id_str = id_str + '0'
            id_str = id_str + format(num, 'x')
        return id_str

    def add_bytes(self, data):
        """ Добавление байт в конец массива

        @param data : значение или массив добавляемых байт.
        @return: Возвращает C{None} или ошибку, если значения не int или вне диапазона 0-255.
        """
        if isinstance(data, int):
            data = [data]
        if isinstance(data, list):
            for i in data:
                if (not isinstance(i, int)) or i < 0 or i > 255:
                    return 'Error: array element does not belong to values int[0-255].'
            self.data = self.data + data
            return None
        else:
            return 'Error: Invalid parameters type.'

    @staticmethod
    def formation_receive_packet(byte_data: bytearray):
        """ Изъятие данных из принятого пакета

        @param byte_data : С{bytearray} массив принятых байт.
        @return: Возвращает ByteList сформированный на основе данных пакета.
        """
        # Изменяет поле data следующим образом:
        # - преобразовавает bytearray в list[int]
        receive_data = [int(byte) for byte in byte_data]
        # - забирает последний байт (CRC_sum)
        crc_sum = receive_data.pop(-1)
        # - проверяет кратность 9
        if len(receive_data) % 9 != 0:
            return
        # - разбивает на 9-ки вида 8:1
        amt_byte = 9
        mas = [(receive_data[num:num + amt_byte - 1], receive_data[num + amt_byte - 1])
               for num in range(0, len(receive_data), amt_byte)]
        # - считает CRC в каждой восьмёрке с проверкой ссоответствия CRC-пакета
        for string, crc in mas:
            if CRC_counter(string) != crc:
                return
        # - считает CRC всех CRC с проверкой соответствия
        if CRC_counter([crc for string, crc in mas]) != crc_sum:
            return
        # - складывает все восьмёрки
        l_data = ByteList([elem for string, crc in mas for elem in string])
        return l_data

    def formation_send_packet(self):
        """ Формирование пакета отправки

        @return: Возвращает bytearray сформированный на основе данных класса.
        """
        # Изменяет поле data следующим образом:
        # - разбивает на восьмёрки
        amt_byte = 8
        mas = [self.data[num:num+amt_byte] + ([0] * (amt_byte - len(self.data[num:num+amt_byte])))
               for num in range(0, len(self.data), amt_byte)]
        # - считает CRC на каждую из них
        # - добавляет посчитанные CRC в конец каждой, получая девятки
        for string in mas:
            string.append(CRC_counter(string))
        # - считает CRC всех CRC
        self.crc_sum = CRC_counter([string[-1] for string in mas])
        # - соединяет все девятки друг с другом и с CRC
        byte_data = [elem for string in mas for elem in string] + [self.crc_sum]
        # - переводит их в byte
        return byte_data
        # return bytearray(byte_data)


# b_list = ByteList([127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140])
#
# print(b_list.get_bytes(1))
# print(b_list.get_bytes(2))
# print(b_list.get_bytes(3))
# print(b_list.get_bytes(-1))
# print(b_list.get_bytes(-2))
# print(b_list.get_bytes(-3))
# print(b_list.get_hex(1))
# print(b_list.get_hex(2))
# print(b_list.get_hex(3))
# print(b_list.get_hex(-1))
# print(b_list.get_hex(-2))
# print(b_list.get_hex(-3))
# hstr = '012FF3456'
# print(hex_to_byte(hstr))
# for ir in hex_to_byte(hstr):
#     print(hex(ir))
# print(uint_to_byte(0xFFFF, 14))
# print(uint_to_byte(0xFFFF, 0))
# print([mas*8 for mas in range(5)]+[mas*4 for mas in range(10)]+[mas*2 for mas in range(5)])
# print(set([mas*8 for mas in range(5)]+[mas*4 for mas in range(10)]+[mas*2 for mas in range(5)]))
# print([ir for ir in set([mas*8 for mas in range(5)]+[mas*4 for mas in range(10)]+[mas*2 for mas in range(5)])])
# print('-')
# print([q + s for q in range(5) for s in range(2)])
# a = list(range(6))
# b = list(range(4))
# print([q + s for q, s in zip(a, b)])
# print([x+y for x, y in zip(a, b)] + (a if len(a) >= len(b) else b)[min(len(a), len(b)):])
#
#
# def sym_two(ai: int, bi: int):
#     return ai + bi
#
#
# print(list(map(sym_two, a, b)))  # [q + s for q, s in zip(a, b)]
# print(list(map((lambda ai, bi: ai + bi), a, b)))  # [q + s for q, s in zip(a, b)]
