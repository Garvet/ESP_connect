# coding=utf-8
"""ESP connect interface classes
Классы для контроля общения между модулем управления группой и сервером.

В данном модуле описаны следующие классы пакетов:
(+) 0xFF - C{Packet} : Общий класс пакетов;
(-) 0x00 - C{SystemRegistration} : Класс пакета завершения регистрации;
(-) 0x01 - C{Module} : Класс пакета отчётов компонентов;
(+) 0x02 - C{SystemControl} : Класс пакета состояний модуля;
(+) 0x03 - C{TimeControl} : Класс пакета контроля времени;
(+) 0x04 - C{Error} : Класс пакета ошибок;
(-) 0x05 - C{Check} : Класс пакета проверки наличия команд;
(-) 0x06 - C{SystemSetting} : Класс пакета настройки системы;
(+) 0x07 - C{ACS} : Класс пакетов связанных с системой контроля доступа;
 (+) 0x00 - C{DetectRFID} : Класс покета сообщения сигнала со СКУДов;
 (+) 0x01 - C{TurnstileControl} : Класс покета управления турникетом;
 (+) 0x02 - C{RFIDListControl} : Класс пакета управления RFID-списка на СКУДе;
 (+) 0x03 - C{} : Класс пакета реакции изменения RFID-списка на СКУДе.
"""
# В файле есть (-) -----
import ESP_connect_interface_data as PEnum
import ESP_connect_bytelist as PByte

import datetime

# Create send packet (ByteList->header|data|CRC) (-) ----- (+/-) data -> CRC in ESP_connect_bytelist
# Read receive packet (header|data|CRC->ByteList) (-) ----- (+/-) del CRC in ESP_connect_bytelist

# Во всех классах добавить: (-) -----
#     ByteList->Packet
#     Packet->ByteList
# - Packet             ( - - )
# - SystemRegistration ( - - )
# - Module             ( - - )
# - SystemControl      ( - - )
# - Error              ( - - )
# - Check              ( - - )
# - SystemSetting      ( - - )


def check_id(string_id: str):
    """ Проверка параметра на ID

    @param string_id : С{str} проверяемая строка.
    """
    if isinstance(string_id, str) and len(string_id) == 16:
        try:
            int(string_id, 16)  # проверка на то, является ли строка шестнадцатеричной 'HEX'
            int(string_id[0], 16)  # проверка на то, является ли первый символ шестнадцатеричным ' HEX'
            int(string_id[-1], 16)  # проверка на то, является ли последний символ шестнадцатеричным 'HEX '
            return True
        except ValueError:
            pass
    return False


def get_PT_num(search_value, search_area='Packet'):
    """ Получение номера типа пакета

    @param search_value : С{str} название типа пакета.
                          С{type(Packet)} тип пакета.
    @param search_area : C{Dict} область поиска типа
    @return : C{int} номер типа пакета.
              C{None} ошибка поиска.
    """
    if search_value in [value for key, values in packet_type[search_area].items() for value in values.values()]:
        if isinstance(search_value, str):
            return [key for key, value in packet_type[search_area].items() if value['name'] == search_value][0]
        elif issubclass(search_value, Packet):
            return [key for key, value in packet_type[search_area].items() if value['class'] == search_value][0]
    return None


def get_PT_name(search_value, search_area='Packet'):
    """ Получение названия типа пакета

    @param search_value : С{int} номер типа пакета.
                          С{type(Packet)} тип пакета.
    @param search_area : C{Dict} область поиска типа
    @return : C{str} название типа пакета.
              C{None} ошибка поиска.
    """
    if isinstance(search_value, int):
        if search_value not in packet_type[search_area]:
            return None
        return packet_type[search_area][search_value]['name']
    elif issubclass(search_value, Packet):
        if search_value in [value for key, values in packet_type[search_area].items() for value in values.values()]:
            return packet_type[search_area][get_PT_num(search_value)]['name']
    return None


def get_PT(search_value, search_area='Packet'):
    """ Получение типа пакета

    @param search_value : С{int} номер типа пакета.
                          С{str} название типа пакета.
    @param search_area : C{Dict} область поиска типа
    @return : C{type(Packet)} тип пакета.
              C{None} ошибка поиска.
    """
    if isinstance(search_value, int):
        if search_value not in packet_type[search_area]:
            return None
        return packet_type[search_area][search_value]['class']
    elif isinstance(search_value, str):
        if search_value in [value for key, values in packet_type[search_area].items() for value in values.values()]:
            return packet_type[search_area][get_PT_num(search_value)]['class']
    return None


class Packet(object):
    """Общий класс пакетов

    Содержит методы являющиеся общими для пакетов
    всех видов учавствующих в общении между модулем
    управления группой (МУГом) и сервером. Содержит
    поле ID МУГа и время отправки пакета.
    """
    type_name = 'Packet'

    def __init__(self, packet=None, group_id: str = None, time: str = None):
        """Конструктор основного класса

        Имеется два варианта конструирования:
        1. Через передачу ID МУГа и времени генерации пакета (в текстовом виде);
        2. При помощи другого пакета, из которого будут получены данные параметры.
        3. При помощи словаря пакета, из которого будут получены данные параметры.

        @param packet : C{Packet} - пакет, из которого будут получены данные параметры.
                        C{dict} - словарь полей класса.
        @param group_id : C{str} - строка ID МУГа, состоит из 12 символов в шестнадцатиричном виде.
        @param time : C{str} - строка времени в следующем формате 'DD-MM-YYYY hh:mm:ss'.
        """
        self.class_error = {Packet.type_name: []}
        self.type = get_PT_num(Packet.type_name)
        self.group_id = ''
        self.time = ''
        # Конструктор по значению
        if isinstance(group_id, str) and isinstance(time, str):
            self.group_id = group_id
            self.time = time
        # Конструктор копирования
        elif isinstance(packet, Packet):
            self.class_error = packet.class_error
            self.group_id = packet.group_id
            self.time = packet.time
        # Конструктор из словаря
        elif isinstance(packet, dict) and packet.keys() >= {'class_error', 'group_id', 'time'}:
            self.class_error = packet['class_error']
            self.group_id = packet['group_id']
            self.time = packet['time']
        # Ошибка конструирования
        else:
            self.class_error[Packet.type_name].append('__init__: Invalid parameters type.')

    def get_class_error(self, one_mas: bool = False):
        """Возврат ошибок класса

        @param one_mas : C{bool} - параметр указывающий на то, является ли возврат единым массивом
        (если True) или является словарём, где ключём является имя класса, на уровне которого
        возникли ошибки.
        @return: Возвращает ошибки, возникшие во время существования данного объекта, в зависимости
        от входного значения one_mas.
        """
        if isinstance(one_mas, bool):
            if one_mas:
                return self.class_error[Packet.type_name]
            else:
                return self.class_error
        else:
            self.class_error[Packet.type_name].append('get_class_error: Invalid parameters type.')
            return

    def get_packet_len(self):
        return 24
    # ByteList->Packet (-) -----
    # Packet->ByteList (-) -----

    @staticmethod
    def convert_from_ByteList(byte_array):
        """Конвертация байтовой строки в пакет

        @return: пакет
        """
        # чтение полей (-) -----

    def convert_to_ByteList(self, index: int = 0):
        """Конвертация пакета в байтовую строку

        @return: bytearray()
        """
        byte_list = PByte.ByteList()
        byte_list.add_bytes(0b10100101)  # Преамбула
        byte_list.add_bytes(PByte.hex_to_byte(self.group_id))
        byte_list.add_bytes(self.type)
        byte_list.add_bytes([0, 0])  # self.get_len_packet() рассчитывающаяся, будет вызывать ф.наследников (-) -----
        byte_list.add_bytes(index)
        # ДД-ММ-ГГГГ чч:мм:сс (-) -----
        print(byte_list.data)

        # заполнение поля data (-) -----
        return byte_list.formation_send_packet()

    #

    #

    #
    @staticmethod
    def object_creator(byte):
        """Генератор объекта

        @return: созданный объект
        """
        p_group_id = byte['group_id']
        p_time = byte['time']
        if byte['num'] != 0xFF:
            p_type = get_PT(byte['num'])
            return p_type.object_creator(byte)
        else:
            return Packet(group_id=p_group_id, time=p_time)

    def obt_to_byte(self):
        """

        @return:
        """

    """ @var class_error

    C{dict} - Переменная списка ошибок, произошедших при работе класса. Является
    словарём. Ключ - класс C{str} 'Packet', значение - C{List} ошибок. Разделение
    произведено для удобства поиска ошибок при наследовании (у наследников другие
    ключи). 
    """
    """ @var group_id

    C{str} - ID МУГа, состоит из 12 символов в шестнадцатиричном виде.
    """
    """ @var time

    C{str} - строка содержащая время отправки пакета в следующем формате 'DD-MM-YYYY hh:mm:ss'.
    """


# ByteList->Packet (-) -----
# Packet->ByteList (-) -----
class SystemControl(Packet):
    """Пакет состояний модуля

    Пакет управления состоянием компонентов системы отвечает за смену режима модуля
    по ID, содержит в себе поля с самим ID и новым состоянием. Если в поле находится
    ID не компонента группы а МУГа, то будет реакция на всю группу в целом, а не
    на отдельный компонент.
    """
    type_name = 'SystemControl'

    def __init__(self, module_id: str, state: str,
                 packet=None, group_id: str = None, time: str = None):
        """Конструктор пакета состояний модуля

        @param module_id : C{str} - ID компонента, состоящее из 12 символов в шестнадцатиричном виде.
        @param state : C{str} - Состояние компонента [см. state_system].
        @param packet : C{SystemControl}/C{dict} - см. Packet.
        @param group_id : C{str} - см. Packet.
        @param time : C{str} - см. Packet.
        """
        if isinstance(packet, SystemControl) or isinstance(packet, dict):
            super().__init__(packet=packet)
        else:
            super().__init__(group_id=group_id, time=time)
        self.class_error[SystemControl.type_name] = []
        self.type = get_PT_num(SystemControl.type_name)
        self.module_id = ''
        self.state = ''
        # Конструктор по значению
        if isinstance(module_id, str) and isinstance(state, str):
            if state in PEnum.state_system.values():
                self.module_id = module_id
                self.state = state
            else:
                self.class_error[SystemControl.type_name].append('__init__: Invalid state system.')
        # Конструктор копирования
        elif isinstance(packet, SystemControl):
            self.module_id = packet.module_id
            self.state = packet.state
        # Конструктор из словаря
        elif isinstance(packet, dict) and packet.keys() >= {'module_id', 'state'}:
            self.module_id = packet['module_id']
            self.state = packet['state']
        # Ошибка конструирования
        else:
            self.class_error[SystemControl.type_name].append('__init__: Invalid parameters type.')

    def get_class_error(self, one_mas: bool = False):
        """Возврат ошибок класса

        @param one_mas : C{bool} - см. Packet.
        @return: см. Packet.
        """
        if isinstance(one_mas, bool):
            if one_mas:
                return super().get_class_error(one_mas) + self.class_error[SystemControl.type_name]
            else:
                return self.class_error
        else:
            self.class_error[SystemControl.type_name].append('get_class_error: Invalid parameters type.')
            return

    def get_packet_len(self):
        return super().get_packet_len() + 13

    # ByteList->Packet (-) -----
    # Packet->ByteList (-) -----


# ByteList->Packet (-) -----
# Packet->ByteList (-) -----
class TimeControl(Packet):
    """Пакет управления временем модуля

    Пакет управления временем в системе узлов. Содержит в себе поле с самим ID
    и поля даты и времени.
    """
    type_name = 'TimeControl'

    def __init__(self, module_id: str, state: datetime.datetime,
                 packet=None, group_id: str = None, time: str = None):
        """Конструктор пакета состояний модуля

        @param module_id : C{str} - ID компонента, состоящее из 12 символов в шестнадцатиричном виде.
        @param state : C{str} - Состояние компонента [см. state_system].
        @param packet : C{SystemControl}/C{dict} - см. Packet.
        @param group_id : C{str} - см. Packet.
        @param time : C{str} - см. Packet.
        """
        if isinstance(packet, SystemControl) or isinstance(packet, dict):
            super().__init__(packet=packet)
        else:
            super().__init__(group_id=group_id, time=time)
        self.class_error[SystemControl.type_name] = []
        self.type = get_PT_num(SystemControl.type_name)
        self.module_id = ''
        self.state = ''
        # Конструктор по значению
        if isinstance(module_id, str) and isinstance(state, str):
            if state in PEnum.state_system.values():
                self.module_id = module_id
                self.state = state
            else:
                self.class_error[SystemControl.type_name].append('__init__: Invalid state system.')
        # Конструктор копирования
        elif isinstance(packet, SystemControl):
            self.module_id = packet.module_id
            self.state = packet.state
        # Конструктор из словаря
        elif isinstance(packet, dict) and packet.keys() >= {'module_id', 'state'}:
            self.module_id = packet['module_id']
            self.state = packet['state']
        # Ошибка конструирования
        else:
            self.class_error[SystemControl.type_name].append('__init__: Invalid parameters type.')

    def get_class_error(self, one_mas: bool = False):
        """Возврат ошибок класса

        @param one_mas : C{bool} - см. Packet.
        @return: см. Packet.
        """
        if isinstance(one_mas, bool):
            if one_mas:
                return super().get_class_error(one_mas) + self.class_error[SystemControl.type_name]
            else:
                return self.class_error
        else:
            self.class_error[SystemControl.type_name].append('get_class_error: Invalid parameters type.')
            return

    def get_packet_len(self):
        return super().get_packet_len() + 13

    # ByteList->Packet (-) -----
    # Packet->ByteList (-) -----


# get_packet_len (-) -----
# ByteList->Packet (-) -----
# Packet->ByteList (-) -----
class Error(Packet):
    """Пакет ошибок

    Пакет содержит в себе данные об ошибках, которые возникают в тех или иных
    ситуациях. В параметре module_ID содержится информация о компоненте, с
    которым произошла ошибка (МУГа — если в рамках всей группы).
    """
    type_name = 'Error'

    def __init__(self, module_id: str, error: str, data=None,
                 packet=None, group_id: str = None, time: str = None):
        """Конструктор пакета состояний модуля

        @param module_id : C{str} - ID компонента, состоящее из 12 символов в шестнадцатиричном виде.
        @param error : C{str} - Имя ошибки [см. error_type].
        @param packet : C{Error}/C{dict} - см. Packet.
        @param group_id : C{str} - см. Packet.
        @param time : C{str} - см. Packet.
        """
        if isinstance(packet, Error) or isinstance(packet, dict):
            super().__init__(packet=packet)
        else:
            super().__init__(group_id=group_id, time=time)
        self.class_error[Error.type_name] = []
        self.type = get_PT_num(Error.type_name)
        self.module_id = ''
        self.error = ''
        self.data = None
        # Конструктор по значению
        if isinstance(module_id, str) and isinstance(error, str):
            if error in PEnum.error_type.values():
                self.module_id = module_id
                self.error = error
                self.data = data
            else:
                self.class_error[Error.type_name].append('__init__: Invalid error type.')
        # Конструктор копирования
        elif isinstance(packet, Error):
            self.module_id = packet.module_id
            self.error = packet.error
            self.data = packet.data
        # Конструктор из словаря
        elif isinstance(packet, dict) and packet.keys() >= {'module_id', 'error', 'data'}:
            self.module_id = packet['module_id']
            self.error = packet['error']
            self.data = packet['data']
        # Ошибка конструирования
        else:
            self.class_error[Error.type_name].append('__init__: Invalid parameters type.')

    def get_class_error(self, one_mas: bool = False):
        """Возврат ошибок класса

        @param one_mas : C{bool} - см. Packet.
        @return: см. Packet.
        """
        if isinstance(one_mas, bool):
            if one_mas:
                return super().get_class_error(one_mas) + self.class_error[Error.type_name]
            else:
                return self.class_error
        else:
            self.class_error[Error.type_name].append('get_class_error: Invalid parameters type.')
            return

    # get_packet_len (-) -----
    def get_packet_len(self):
        return 24

    # ByteList->Packet (-) -----
    # Packet->ByteList (-) -----


# ByteList->Packet (-) -----
# Packet->ByteList (-) -----
class Check(Packet):
    """Пакет проверки наличия команд

    Пустой пакет, приходящий раз в N секунд, чтобы проверить не подготовил
    ли сервер команды управления для него. Может служить для детектирования
    ошибок наличия связи (если они перестали поступать в указанное время,
    значит отсутствует связь), но в этом случае следует учесть возможные
    задержки.
    """
    type_name = 'Check'

    def __init__(self, subtype: int, data: list, packet=None, group_id: str = None, time: str = None):
        """Конструктор проверки наличия команд

        @param subtype : C{int} - номер подтипа пакета.
        @param data : C{list} - массив данных подтипа.
        @param packet : C{Check}/C{dict} - см. Packet.
        @param group_id : C{str} - см. Packet.
        @param time : C{str} - см. Packet.
        """
        if isinstance(packet, Check) or isinstance(packet, dict):
            super().__init__(packet=packet)
        else:
            super().__init__(group_id=group_id, time=time)
        self.class_error[Check.type_name] = []
        self.type = get_PT_num(Check.type_name)
        self.subtype = -1
        self.data = []

        # Конструктор по значению
        if isinstance(subtype, int) and isinstance(data, list):
            self.subtype = subtype
            self.data = data
        # Конструктор копирования
        elif isinstance(packet, Check):
            self.subtype = packet.subtype
            self.data = packet.data
        # Конструктор из словаря
        elif isinstance(packet, dict) and packet.keys() >= {'subtype', 'data'}:
            self.subtype = packet['subtype']
            self.data = packet['data']
        # Ошибка конструирования
        else:
            self.class_error[Check.type_name].append('__init__: Invalid parameters type.')

    def get_class_error(self, one_mas: bool = False):
        """Возврат ошибок класса

        @param one_mas : C{bool} - см. Packet.
        @return: см. Packet.
        """
        if isinstance(one_mas, bool):
            if one_mas:
                return super().get_class_error(one_mas) + self.class_error[Check.type_name]
            else:
                return self.class_error
        else:
            self.class_error[Check.type_name].append('get_class_error: Invalid parameters type.')
            return

    def get_packet_len(self):
        return super().get_packet_len() + 3

    # ByteList->Packet (-) -----
    # Packet->ByteList (-) -----


# get_packet_len (-) -----
# ByteList->Packet (-) -----
# Packet->ByteList (-) -----
class SystemSetting(Packet):
    """Пакеты настройки системы

    Класс подготовленный для будущего. В нём будут дочерние пакеты (или
    определённые поля), позволяющие осуществлять контроль над настройками
    группы, т.е. производить регистрацию и замену модулей, передавать
    данные о контейнере и технологии выращивания (конфигурацию).
    """
    type_name = 'SystemSetting'

    def __init__(self, packet=None, group_id: str = None, time: str = None):
        """Конструктор пакета настройки системы

        @param packet : C{SystemSetting}/C{dict} - см. Packet.
        @param group_id : C{str} - см. Packet.
        @param time : C{str} - см. Packet.
        """
        if isinstance(packet, SystemSetting) or isinstance(packet, dict):
            super().__init__(packet=packet)
        else:
            super().__init__(group_id=group_id, time=time)
        self.class_error[SystemSetting.type_name] = []
        self.type = get_PT_num(SystemSetting.type_name)

        # Конструктор по значению
        if isinstance(None, str):
            pass
        # Конструктор копирования
        elif isinstance(packet, SystemSetting):
            pass
        # Конструктор из словаря
        elif isinstance(packet, dict) and packet.keys() >= {''}:
            pass
        # Ошибка конструирования
        else:
            pass
            # self.class_error[SystemSetting.type_name].append('__init__: Invalid parameters type.')

    def get_class_error(self, one_mas: bool = False):
        """Возврат ошибок класса

        @param one_mas : C{bool} - см. Packet.
        @return: см. Packet.
        """
        if isinstance(one_mas, bool):
            if one_mas:
                return super().get_class_error(one_mas) + self.class_error[SystemSetting.type_name]
            else:
                return self.class_error
        else:
            self.class_error[SystemSetting.type_name].append('get_class_error: Invalid parameters type.')
            return

    # get_packet_len (-) -----
    def get_packet_len(self):
        return 24

    # ByteList->Packet (-) -----
    # Packet->ByteList (-) -----


# get_packet_len (-) -----
# ByteList->Packet (-) -----
# Packet->ByteList (-) -----
class ACS(Packet):
    """Пакеты настройки системы

    Класс подготовленный для будущего. В нём будут дочерние пакеты (или
    определённые поля), позволяющие осуществлять контроль над настройками
    группы, т.е. производить регистрацию и замену модулей, передавать
    данные о контейнере и технологии выращивания (конфигурацию).
    """
    type_name = 'SystemSetting'

    def __init__(self, packet=None, group_id: str = None, time: str = None):
        """Конструктор пакета настройки системы

        @param packet : C{SystemSetting}/C{dict} - см. Packet.
        @param group_id : C{str} - см. Packet.
        @param time : C{str} - см. Packet.
        """
        if isinstance(packet, SystemSetting) or isinstance(packet, dict):
            super().__init__(packet=packet)
        else:
            super().__init__(group_id=group_id, time=time)
        self.class_error[SystemSetting.type_name] = []
        self.type = get_PT_num(SystemSetting.type_name)

        # Конструктор по значению
        if isinstance(None, str):
            pass
        # Конструктор копирования
        elif isinstance(packet, SystemSetting):
            pass
        # Конструктор из словаря
        elif isinstance(packet, dict) and packet.keys() >= {''}:
            pass
        # Ошибка конструирования
        else:
            pass
            # self.class_error[SystemSetting.type_name].append('__init__: Invalid parameters type.')

    def get_class_error(self, one_mas: bool = False):
        """Возврат ошибок класса

        @param one_mas : C{bool} - см. Packet.
        @return: см. Packet.
        """
        if isinstance(one_mas, bool):
            if one_mas:
                return super().get_class_error(one_mas) + self.class_error[SystemSetting.type_name]
            else:
                return self.class_error
        else:
            self.class_error[SystemSetting.type_name].append('get_class_error: Invalid parameters type.')
            return

    # get_packet_len (-) -----
    def get_packet_len(self):
        return 24

    # ByteList->Packet (-) -----
    # Packet->ByteList (-) -----


# packet_type = {0xFF: {'name': Packet.type_name,             'class': Packet},
#                0x00: {'name': SystemRegistration.type_name, 'class': SystemRegistration},
#                0x01: {'name': Module.type_name,             'class': Module},
#                0x02: {'name': SystemControl.type_name,      'class': SystemControl},
#                0x03: {'name': Error.type_name,              'class': Error},
#                0x04: {'name': Check.type_name,              'class': Check},
#                0x05: {'name': SystemSetting.type_name,      'class': SystemSetting}}

packet_type = dict()
packet_type['Packet'] = {0xFF: {'name': Packet.type_name,             'class': Packet},
                         # 0x00: {'name': SystemRegistration.type_name, 'class': SystemRegistration},
                         # 0x01: {'name': Module.type_name,             'class': Module},
                         0x02: {'name': SystemControl.type_name,      'class': SystemControl},
                         0x03: {'name': TimeControl.type_name,        'class': TimeControl},
                         0x04: {'name': Error.type_name,              'class': Error},
                         # 0x05: {'name': Check.type_name,              'class': Check},
                         # 0x06: {'name': SystemSetting.type_name,      'class': SystemSetting}
                         0x07: {'name': ACS.type_name,                'class': ACS}
                         }

packet_type['ACS'] = {0x00: {'name': Packet.type_name,             'class': Packet},  # DetectRFID
                      0x01: {'name': Packet.type_name,             'class': Packet},  # TurnstileControl
                      0x02: {'name': Packet.type_name,             'class': Packet},  # RFIDListControl
                      0x03: {'name': Packet.type_name,             'class': Packet}   # (-) -----
                      }


#
# /-------------- Example of filled objects --------------\
# |                                                       |
# |--- SystemRegistration --------------------------------|
# |                                                       |
# | mainId = '010510200a0bc0d04affc200'                   |
# | attached_id = ['020611210b0cc1d14b00c301',            |
# |                '030712220c0dc2d24c01c402',            |
# |                '040813230d0ec3d34d02c503']            |
# |                                                       |
# | * type: mainId - str                                  |
# |         attached_id - dict: amount id modules         |
# |             id modules - str                          |
# |                                                       |
# |--- Module - Sensor -----------------------------------|
# |                                                       |
# | module_id  = '020611210b0cc1d14b00c301'               |
# | module_data = [                                       |
# |                 { 'component': 'Air_humidity',        |
# |                   'number': 1,                        |
# |                   'value': 36.5999                    |
# |                 },                                    |
# |                 { 'component': 'Illumination_level',  |
# |                   'number': 0,                        |
# |                   'value': 230.0                      |
# |                 }                                     |
# |               ]                                       |
# | time = '15-6-2020 12:30:30'                           |
# |                                                       |
# | * type: module_id - str                               |
# |         module_data - dict: 3                         |
# |             'component' - str                         |
# |             'number' - int                            |
# |             'value' - look in variable 'sensors_type' |
# |         time  - str                                   |
# |                                                       |
# |--- Module - Device -----------------------------------|
# |                                                       |
# | module_id  = '030712220c0dc2d24c01c402'               |
# | module_data = [                                       |
# |                 { 'component': 'Fan_PWM',             |
# |                   'number': 0,                        |
# |                   'value': 2063                       |
# |                 },                                    |
# |                 { 'component': 'Pumping_system',      |
# |                   'number': 0,                        |
# |                   'value': True                       |
# |                 }                                     |
# |               ]                                       |
# | time = '31-12-2020 23:59:59'                          |
# |                                                       |
# | * type: module_id - str                               |
# |         module_data - dict: 3                         |
# |             'component' - str                         |
# |             'number' - int                            |
# |             'value' - look in variable 'devices_type' |
# |         time  - str                                   |
# |                                                       |
# \-------------------------------------------------------/
#
