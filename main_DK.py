# coding=utf-8
import ESP_connect_UART_controller as Utr
import ESP_connect_objects_ASC as ASC_objects
import ESP_connect_interface as ESP_intr
from _special_data import acs_id, acs_password

# класс для взаимодействия с сервером
from communicator import DatabaseCommunicator

buffer_object_send = []
correct_id = ['11223344', '01020304']

USB_port = '/dev/ttyUSB0'
# USB_port = ['/dev/ttyUSB1', '/dev/ttyUSB2']

if __name__ == '__main__':
    # подключаемся, указываем адрес API, ID устройства и пароль
    dc = DatabaseCommunicator()
    dc.init('https://lk.spiiras.nw.ru/api.php', acs_id, acs_password)

    Utr.begin(USB_port)
    # Utr.log_print['Print transmitted bytes'] = True
    # Utr.log_print['Print transfer result'] = True
    # Utr.log_print['Print sent package'] = True
    # Utr.log_print['Print received package'] = True
    while True:
        Utr.loop()
        # Если с ESP был принят пакет
        if Utr.size_receive_buffer() != 0:
            obj = ESP_intr.convert_to_object(Utr.receive_data(0))
            # Обработка принятого пакета, если он "запрос на проход"
            print(obj)
            if isinstance(obj, ASC_objects.Pass_request):
                print('Пришёл запрос от ' + obj.get_acs_id())
                print('    на проход ' + obj.get_card_id())
                print('    в направлении ' + obj.get_direction())
                # Разрешение, если есть в массиве correct_id, или запрет, если нет
                #if obj.get_card_id() in correct_id:
                # проверяем теперь через сервер
                if dc.checkPermission(obj.get_card_id()):
                    dc.writeLog('ALLOW %s %s' % (obj.get_card_id(), obj.get_direction()))
                    #print(' + Проход разрешён')
                    buffer_object_send.append(ASC_objects.Passage_permission(
                        acs_id=obj.get_acs_id(), card_id=obj.get_card_id(), direction=obj.get_direction()))
                else:
                    dc.writeLog('DENY %s %s' % (obj.get_card_id(), obj.get_direction()))
                    #print(' - Проход запрещён')
                    buffer_object_send.append(ASC_objects.Passage_prohibition(
                        acs_id=obj.get_acs_id(), card_id=obj.get_card_id()))
            elif isinstance(obj, ASC_objects.Send_error):
                print(' - Отправка пакета произошла с ошибкой')
            elif isinstance(obj, ASC_objects.Send_correct):
                print(' + Пакет успешно отправлен')
        # Отправка пакета на ESP
        if len(buffer_object_send) != 0:
            Utr.send_data(ESP_intr.convert_to_packet(buffer_object_send.pop(0)))

        # проверяем команды от сервера
        dc.checkCommands()

# - - - Для работы необходимо
# [10] Указать порт соединения - USB_port
# [13] Для инициализации передать в Utr.begin(USB_port)
# [19] Переодически вызывать Utr.loop() для обработки сигналов
# [20] Utr.size_receive_buffer() - возвращает количество принятых пакетов
# [21] Возвращает объект на основе принятого пакета ESP_intr.convert_to_object(Utr.receive_data(0))
# [47] Utr.send_data(ESP_intr.convert_to_packet(<object>) конвертирует и отправляет объект


