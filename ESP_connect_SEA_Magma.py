# Алгоритм шифрования Магма согласно
# ГОСТ 28147-89 «Системы обработки информации. Защита криптографическая.
# Алгоритм криптографического преобразования» и ГОСТ 34.12-2018
# «Криптографическая защита информации. Блочные шифры.»

import traceback

# Блоки сдвигов при шифровании
# blocks = (
#     (4, 10, 9, 2, 13, 8, 0, 14, 6, 11, 1, 12, 7, 15, 5, 3),
#     (14, 11, 4, 12, 6, 13, 15, 10, 2, 3, 8, 1, 0, 7, 5, 9),
#     (5, 8, 1, 13, 10, 3, 4, 2, 14, 15, 12, 7, 6, 0, 9, 11),
#     (7, 13, 10, 1, 0, 8, 9, 15, 14, 4, 6, 12, 11, 2, 5, 3),
#     (6, 12, 7, 1, 5, 15, 13, 8, 4, 10, 9, 14, 0, 3, 11, 2),
#     (4, 11, 10, 0, 7, 2, 1, 13, 3, 6, 8, 5, 9, 12, 15, 14),
#     (13, 11, 4, 1, 3, 15, 5, 9, 0, 10, 14, 7, 6, 8, 2, 12),
#     (1, 15, 13, 0, 5, 7, 10, 4, 9, 2, 3, 14, 6, 11, 8, 12),
# )

# Подстановки нелинейного биективного преобразования | Nonlinear Bijective Transform Substitutions
SUBSTITUTIONS = (
    (12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1),
    (6, 8, 2, 3, 9, 10, 5, 12, 1, 14, 4, 7, 11, 13, 0, 15),
    (11, 3, 5, 8, 2, 15, 10, 13, 14, 1, 7, 4, 12, 9, 6, 0),
    (12, 8, 2, 1, 13, 4, 15, 6, 7, 0, 10, 5, 3, 14, 9, 11),
    (7, 15, 5, 10, 8, 1, 6, 13, 0, 9, 3, 14, 11, 4, 2, 12),
    (5, 13, 15, 6, 9, 2, 12, 10, 11, 7, 8, 1, 4, 3, 14, 0),
    (8, 14, 2, 5, 6, 9, 1, 12, 15, 4, 11, 0, 13, 10, 3, 7),
    (1, 7, 14, 13, 0, 5, 8, 3, 4, 15, 10, 6, 9, 12, 11, 2)
)


class Magma(object):
    def __init__(self, key, substitutions=SUBSTITUTIONS):
        self._key = None
        self._subkeys = None
        self.key = key
        self.substitutions = tuple(substitutions)

    @property
    def key(self):
        """Доступ к значению ключа"""
        return list(self._key)

    @key.setter
    def key(self, key):
        """Формирование ключа и подключей"""
        if isinstance(key, int):
            self._key = self._int_to_key(key)
        elif isinstance(key, str):
            self._key = self._str_to_key(key)
        elif isinstance(key, list):
            self._key = self._list_to_key(key)
        else:
            self._write_log(f'Error: Function = {traceback.extract_stack()[-1][2]}; Text: key of unknown type',
                            True, ValueError)
        # Для генерации подключей исходный 256-битный ключ разбивается на восемь 32-битных блоков: K1…K8.
        self._subkeys = [int.from_bytes(self._key[i:i + 4], 'little') for i in range(0, len(self._key), 4)]
        self._subkeys.reverse()

    def encrypt(self, data: list):
        """Шифрование сообщения"""
        data = list(data)
        data.reverse()
        msg = 0
        for byte_val in data:
            msg = msg << 8 | byte_val

        assert self._bit_length(msg) <= 64
        # открытый текст сначала разбивается на две половины
        # (младшие биты — rigth_path, старшие биты — left_path)
        left_part = msg >> 32
        right_part = msg & 0xFFFFFFFF
        # Выполняем 32 раунда со своим подключом Ki
        # Ключи K1…K24 являются циклическим повторением ключей K1…K8 (нумеруются от младших битов к старшим).
        for i in range(24):
            left_part, right_part = self._round_transformation(left_part, right_part, self._subkeys[i % 8])
            # Ключи K25…K32 являются ключами K1…K8, идущими в обратном порядке.
        for i in range(8):
            left_part, right_part = self._round_transformation(left_part, right_part, self._subkeys[7 - i])
        # Возвращаем массив зашифрованных байт
        return [((left_part >> ind) & 0xFF) for ind in range(0, 32, 8)] + \
               [((right_part >> ind) & 0xFF) for ind in range(0, 32, 8)]  # сливаем половинки вместе

    def decrypt(self, data):
        """Дешифрование сообщения
        Расшифрование выполняется так же, как и шифрование, но инвертируется порядок подключей Ki."""
        data = list(data)
        data.reverse()
        crypted_msg = 0
        for byte_val in data:
            crypted_msg = crypted_msg << 8 | byte_val

        assert self._bit_length(crypted_msg) <= 64
        # открытый текст сначала разбивается на две половины
        # (младшие биты — rigth_path, старшие биты — left_path)
        left_part = crypted_msg >> 32
        right_part = crypted_msg & 0xFFFFFFFF
        # Выполняем 32 раунда со своим подключом Ki
        for i in range(8):
            left_part, right_part = self._round_transformation(left_part, right_part, self._subkeys[i])
        for i in range(24):
            left_part, right_part = self._round_transformation(left_part, right_part, self._subkeys[(7 - i) % 8])
        # Возвращаем массив дешифрованных байт
        return [((left_part >> ind) & 0xFF) for ind in range(0, 32, 8)] + \
               [((right_part >> ind) & 0xFF) for ind in range(0, 32, 8)]  # сливаем половинки вместе

    def _int_to_key(self, key: int):
        """Функция формирования ключа на основе числа"""
        if self._bit_length(key) > 256:
            self._write_log(f'Warning: Function = {traceback.extract_stack()[-1][2]}; Text: bitlen key > 256')
        return [(key >> (8 * i)) & 0xFF for i in reversed(range(32))]

    def _str_to_key(self, key: str):
        """Функция формирования ключа на основе hex-строки"""
        key = key.strip()
        if len(key) > 32:
            self._write_log(f'Warning: Function = {traceback.extract_stack()[-1][2]}; Text: bitlen key > 256')
        try:
            key = '0'[:len(key) % 2] + key
            key = [int(key[i:i+2], 16) for i in range(0, len(key), 2)]
            return key + [0] * (32 - len(key))
        except ValueError:
            self._write_log(f'Error: Function = {traceback.extract_stack()[-1][2]}; Text: key is not hex number',
                            True, ValueError)

    def _list_to_key(self, key: list):
        """Функция формирования ключа на основе списка"""
        # key.reverse()
        if len(key) > 32:
            self._write_log(f'Warning: Function = {traceback.extract_stack()[-1][2]}; Text: bitlen key > 256')
        for num in key:
            if num > 255:
                self._write_log(
                    f'Error: Function = {traceback.extract_stack()[-1][2]}; Text: Key elements greater than a byte',
                    True, ValueError)
        return key + [0] * (32 - len(key))

    def _byte_transformation(self, part, key):
        """Функция преобразования байтов по таблице (выполняется в раундах)"""
        # assert self._bit_length(part) <= 32
        temp = (part + key) & 0xFFFFFFFF  # сложение числа с ключом
        output = 0
        # разбиваем на блоки по 4 бита, каждый из которых смещается по
        # таблице подстановки нелинейного биективного преобразования, т.е. с
        # substitutions[i][j], где i-номер шага, j-значение 4 битного блока i шага
        # выходы всех восьми S-блоков объединяются в 32-битное слово
        for i in range(8):
            output |= ((self.substitutions[i][(temp >> (4 * i)) & 0b1111]) << (4 * i))
            # всё слово циклически сдвигается влево (к старшим разрядам) на 11 битов.
        return ((output << 11) | (output >> (32 - 11))) & 0xFFFFFFFF

    def _round_transformation(self, left_part, right_part, round_key):
        return right_part, left_part ^ self._byte_transformation(right_part, round_key)

    @staticmethod
    def _write_log(log_text, log_crit=False, type_except=Exception):
        if log_crit:
            raise type_except(log_text)
        else:
            print(log_text)

    @staticmethod
    def _bit_length(value):
        """Получить длину числа в битах"""
        return len(bin(value)[2:])  # удаляем '0b' в начале
