import ESP_connect_objects_ASC as ASC_objects

PACKET_TYPE = {"Pass_request":
                   {"num": 1, "class": ASC_objects.Pass_request, "len": 5, "field": ["card_id", "direction"]},
               "Passage_permission":
                   {"num": 2, "class": ASC_objects.Passage_permission, "len": 5, "field": ["card_id", "direction"]},
               "Passage_prohibition":
                   {"num": 3, "class": ASC_objects.Passage_prohibition, "len": 4, "field": ["card_id"]},
               "Add_ID":
                   {"num": 4, "class": ASC_objects.Add_ID, "len": 4, "field": ["card_id"]},
               "Delete_ID":
                   {"num": 5, "class": ASC_objects.Delete_ID, "len": 4, "field": ["card_id"]}
               }

ACS_ID = '0D0E0F101112131415161718'


def _create_hex(byte):
    result = ''
    if len(hex(byte)[2:]) == 1:
        result += '0'
    return result + hex(byte)[2:].upper()


def _hex_to_byte(data: str):
    if not isinstance(data, str):
        return None
    if len(data) % 2 == 1:
        data = '0' + data
    return [int(data[i:i+2], 16) for i in range(0, len(data), 2)]


def _uint_to_byte(data: int, amt_bit: int = 32):
    if not isinstance(data, int) or not isinstance(amt_bit, int) or amt_bit < 0:
        return None
    mas = []
    for i in range(amt_bit // 8):
        mas.insert(0, data >> (i * 8) & 0xFF)
    if amt_bit % 8 != 0:
        # bit_mask = sum([1 << i for i in range(amt_bit % 8)])
        # mas.insert(0, data >> (amt_bit//8 * 8) & bit_mask)
        mas.insert(0, data >> (amt_bit // 8 * 8) & sum([1 << i for i in range(amt_bit % 8)]))
    return mas


def _CRC_counter(data):
    if isinstance(data, int):
        data = [data]
    if not isinstance(data, list):
        return None
    crc = 0
    for byte in data:
        crc += byte
        crc = (crc & 0xFF)
    return crc
    # if isinstance(data, int):
    #     data = [data]
    # if not isinstance(data, list):
    #     return None
    # crc = 0
    # for byte in data:
    #     crc += byte * 211
    #     crc = (crc & 0xFF) ^ ((crc >> 8) & 0xFF)
    # return crc


def convert_to_packet(data: ASC_objects.Object_ACS):
    packet = []
    for obj in PACKET_TYPE.values():
        if isinstance(data, obj["class"]):
            packet.append(obj["num"])
            packet.append(obj["len"])
            if "card_id" in obj["field"]:
                card_id = data.get_card_id()
                # packet = packet + _uint_to_byte(card_id)
                packet = packet + _hex_to_byte(card_id)
                # creat.set_data({(uint8_t)(card_id >> 24 & 0xFF),
                #                 (uint8_t)(card_id >> 16 & 0xFF),
                #                 (uint8_t)(card_id >> 8 & 0xFF),
                #                 (uint8_t)(card_id >> 0 & 0xFF),
            if "direction" in obj["field"]:
                direction = data.get_direction_num()
                packet.append(direction)
            packet.append(_CRC_counter(packet))
            break
    return packet


def convert_to_object(data: list):
    if data[1] == len(data) - 3:
        if data[-1] == _CRC_counter(data[:-1]):
            for obj in PACKET_TYPE.values():
                if data[0] == obj["num"]:
                    obj_class = obj["class"]
                    card_id = None
                    direction = None
                    index = 2
                    if "card_id" in obj["field"]:
                        card_id = _create_hex(data[index])
                        index += 1
                        card_id = card_id + _create_hex(data[index])
                        index += 1
                        card_id = card_id + _create_hex(data[index])
                        index += 1
                        card_id = card_id + _create_hex(data[index])
                        index += 1
                    if "direction" in obj["field"]:
                        direction = data[index]
                        index += 1

                    if direction is not None:
                        result_obj = obj_class(ACS_ID, card_id, direction)
                    else:
                        result_obj = obj_class(ACS_ID, card_id)
                    return result_obj
        else:
            print('Error, CRC')
    else:
        print('Error, size')
    return None


#

#
#
# my_packet1 = [1, 5, 0x11, 0x12, 0x13, 0x14, 0]
# my_packet2 = [2, 5, 0x21, 0x22, 0x23, 0x24, 1]
# my_packet3 = [3, 4, 0x31, 0x32, 0x33, 0x34]
# my_packet4 = [4, 4, 0x41, 0x42, 0x43, 0x44]
# my_packet5 = [5, 4, 0x51, 0x52, 0x53, 0x54]
# my_packet = [my_packet1, my_packet2, my_packet3, my_packet4, my_packet5]
# for packet in my_packet:
#     packet.append(_CRC_counter(packet))
#     print(packet, ' \tCRC = 0x'+_create_hex(packet[-1]))
#
# my_obj = []
# for packet in my_packet:
#     my_obj.append(convert_to_object(packet))
#
# for num in range(len(my_obj)):
#     acs_obj = my_obj[num]
#     print('- acs_obj №', num, '-')
#     print(' Type =', type(acs_obj))
#     print(' ACS_id =', ACS_ID)
#     # print(' Card_id = 0x', _create_hex(acs_obj.get_card_id() >> 24 & 0xFF),
#     #       _create_hex(acs_obj.get_card_id() >> 16 & 0xFF),
#     #       _create_hex(acs_obj.get_card_id() >> 8 & 0xFF),
#     #       _create_hex(acs_obj.get_card_id() & 0xFF), ' \t(',
#     #       acs_obj.get_card_id(), ')', sep='')
#     byte_mas = _hex_to_byte(acs_obj.get_card_id())
#     number = 0
#     for el in byte_mas:
#         number = (number << 8) + el
#
#     print(' Card_id = 0x', acs_obj.get_card_id(), ' \t(', number, ')', sep='')
#
#     if isinstance(acs_obj, (ASC_objects.Pass_request, ASC_objects.Passage_permission)):
#         print(' Direction =', acs_obj.get_direction())
#
# my_packet2 = []
# for acs_obj in my_obj:
#     my_packet2.append(convert_to_packet(acs_obj))
#
# for packet in my_packet2:
#     print(packet)


# # coding=utf-8
# """ESP connect interface
# Модуль содержащий в себе методы интерфейса для общения с МУГом.
#
# - C{Название} : описание ;
# - C{Название} : описание .
#
# В данном модуле описаны следующие переменные:
# - C{packet_buf} : словарь содержащий буфер общения с каждым МУГом.
# В данном модуле описаны следующие методы:
# - C{} : .
# В данном модуле описаны следующие классы:
# - C{PacketBuf} : буфер общения с МУГом.
# """
# # В файле есть (-) -----
# import ESP_connect_classes as PCl
# # import ESP_connect_bytelist as PByte
#
#
# #
# packet_buf = dict()  # dict {GCM_id: PacketBuf} - для простоты поиска
#
#
# # буффер пакетов
# class PacketBuf(object):
#     def __init__(self, GCM_id):
#         """ Конструктор буфера пакетов
#
#         @param GCM_id : С{str} строка ID из 16 байт.
#         """
#         self.ID = 'XXXXXXXXXXXXXXXX'
#         self.send_buffer = dict()  # dict {индекс: Packet}
#         self.receive_buffer = dict()  # dict {индекс: Packet}
#         self.sent_packet = {'ID': None, 'Packet': None}  # {"ID": индекс, "Packet": bytearray(Packet)}
#         if PCl.check_id(GCM_id):
#             self.ID = GCM_id
#
#     def get_id(self):
#         return self.ID
#
#
# # функции оперирования с буфферами (-) -----
# # - socket = Инициализация порта для приёма/отправки                         // запуск работы
# # - (индекс пакета, ошибка) = Добавление пакета в буфер отправки (ID, пакет) // отправка пакета
# # - ? = Прослушивание порта ()                                               // запуск приёма пакета
# # - пакет = Получение пакета по ID (ID)                                      // приём пакета
# # - {ID: amt} = Получение размеров буферов по ID ()                          // проверка приёма пакета
# # - bool = Подтверждение получения пакета (ID, индекс пакета)                // проверка отправки пакета
#
#
# def U_init_connect():
#     """ Инициализация порта для приёма/отправки
#
#     @return : socket
#     """
#     pass
#
#
# def U_send_packet(packet):
#     """ Добавление пакета в буфер отправки
#     Отправка данных происходит не сразу при добавлении.
#     Только после того, как МУГ установит кондакт с вопросом о наличии пакетов.
#     Также после отправки пакета он попадёт в специальный резерв, где будет
#     находится до тех пор, пока МУГ не подтвердит приём по индексу. Если
#     подтверждения не будет, то он будет отправляться вновь и вновь.
#
#     @param packet : С{Packet} - заполненный пакет.
#     @return : (индекс пакета, ошибка)
#         индекс пакета - индекс присвоеный пакету перед заносом в буфер;
#         ошибка - если при занесении в буфер возникла ошибка, то значение не 0.
#     """
#     pass
#
#
# # - ? = запуск приёма пакета ()
# def U_start_receive(gcm_socket):
#     """ Прослушивание порта
#     .
#
#     @param gcm_socket : С{socket} - .
#     @return : .
#     """
#     pass
#
#
# # - пакет = приём пакета (ID)
# def U_receive_packet(gcm_id: str = None, all_packet: bool = False):
#     """ Получение пакета по ID
#     Возвращает (удаляя) пакет(ы) из очереди приёма.
#
#     @param gcm_id : С{None} - получение пакетов из первой не пустой очереди.
#                     С{str} - получение пакета по определённому ID.
#     @param all_packet : С{bool} - выбор получения всех пакетов или только первого принятого.
#     @return : принятый пакет С{Packet} (при all_packet=False), массив пакетов [С{Packet},...]
#               (при all_packet=True, gcm_id=str_id) или список массивов пакетов
#               {id: [С{Packet},...],...} (при all_packet=True, gcm_id=None) из очереди.
#     """
#     pass
#
#
# # - {ID: amt} = проверка приёма пакета ()
# def U_5(gcm_id: str = None):
#     """ Получение размеров буферов по ID
#     .
#
#     @param gcm_id : С{None} - получение пакетов всех непустых МУГов.
#                     С{str} - получение пакета по определённому ID.
#     @return : список принятых пакетов формата {'id': len()}, если в параметре gcm_id передан
#               нужный id, то возвращает число для этого МУГа (если его нет во внутреннем списке,
#               то возвращает -1, т.е. общение не происходило ни в одну из сторон).
#     """
#     pass
#
#
# # - bool = проверка отправки пакета (ID, индекс пакета)
# def U_6(gcm_id: str, index: int):
#     """ Подтверждение получения пакета
#     .
#
#     @param gcm_id : С{str} - ID устройства у каторого проверяется передача.
#     @param index : С{int} - индекс отправленного пакета.
#     @return : С{bool} - False, если пакет в буфере, True - если пакета нет в буфере (отправлен или не появлялся).
#     """
#     pass
#
#
# #
#
# #
#
# #
#
# #
#
# #
#
# test_byte_data = {'num': 0x00,
#                   'time': '19-07-2021 15:19:51',
#                   'group_id': '0102030405060708',
#                   'attached_id': [{'01020304050607AA': 'component1', '01020304050607BB': 'component2'}],
#                   'name': 'Container name'}
# print('{')
# for k, v in test_byte_data.items():
#     print('  "' + k + '":', v)
# print('}')
#
# result = PCl.Packet.object_creator(test_byte_data)
# print(type(result))
# res = result.__dict__
# print('{')
# for k, v in res.items():
#     print('  "' + k + '":', v)
# print('}')
#
# result.convert_to_ByteList(4)
