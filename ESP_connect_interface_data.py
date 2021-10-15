# coding=utf-8
"""ESP connect interface data
Словари содержащие информацию о вариации данных в пакетах.

В данном модуле нходятся следующие переменные:
- C{module_type} : Типы модулей системы;
- C{sensors_type} : Компоненты датчиков и их параметры;
- C{devices_type} : Компоненты устройств и их параметры;
- C{component_type} : Типы узлов и их компонентов;
- C{state_system} : Состояния узлов системы;
- C{error_type} : Типы ошибок.
"""
# Есть (-) -----
import ESP_connect_classes as Pcls

module_type = {0x00: 'Group control module',
               0x01: 'Sensor',
               0x02: 'Device',
               0x03: 'Access control system'}
""" @var module_type

C{dict} - словарь типов узлов системы. Номер и соответствующее ему название.
• 0x00: 'Group control module' - Модуль управления группой (МУГ)
• 0x01: 'Sensor' - Датчик
• 0x02: 'Device' - Устройство
• 0x03: 'Access control system' - Система контроля управления доступом (СКУД)
"""


# Описать (-) -----
# packet_type = Pcls.packet_type
# packet_type = {0xFF: ['Packet',             Pcls.Packet],
#                0x00: ['SystemRegistration', Pcls.SystemRegistration],
#                0x01: ['Module',             Pcls.Module],
#                0x02: ['SystemControl',      Pcls.SystemControl],
#                0x03: ['Error',              Pcls.Error],
#                0x04: ['Check',              Pcls.Check],
#                0x05: ['SystemSetting',      Pcls.SystemSetting]}

# Описать (-) -----
sensors_type = {0x00: {'name': 'Analog_signal',      'num_byte': 2, 'type': int},  # value = 0...4095
                0x01: {'name': 'Discrete_signal',    'num_byte': 1, 'type': bool},
                0x02: {'name': 'Battery_charge',     'num_byte': 4, 'type': float},
                0x03: {'name': 'Air_humidity',       'num_byte': 4, 'type': float},
                0x04: {'name': 'Air_temperature',    'num_byte': 4, 'type': float},
                0x05: {'name': 'Water_temperature',  'num_byte': 4, 'type': float},
                0x06: {'name': 'Illumination_level', 'num_byte': 4, 'type': float},
                0x07: {'name': 'Lamp_power',         'num_byte': 4, 'type': float},
                0x08: {'name': 'Pump_power',         'num_byte': 4, 'type': float},
                0x09: {'name': 'Indicator_pH',       'num_byte': 4, 'type': float},
                0x0A: {'name': 'Indicator_EC',       'num_byte': 4, 'type': float},
                0x0B: {'name': 'Indicator_eCO2',     'num_byte': 4, 'type': float},
                0x0C: {'name': 'Indicator_nYVOC',    'num_byte': 4, 'type': float}}

# Описать (-) -----
devices_type = {0x00: {'name': 'Signal_PWM',        'num_byte': 2, 'type': int},  # value = 0...4095
                0x01: {'name': 'Signal_digital',    'num_byte': 1, 'type': bool},
                0x02: {'name': 'Fan_PWM',           'num_byte': 2, 'type': int},  # value = 0...4095
                0x03: {'name': 'Pumping_system',    'num_byte': 1, 'type': bool},
                0x04: {'name': 'Phytolamp_digital', 'num_byte': 1, 'type': bool},
                0x05: {'name': 'Phytolamp_PWM',     'num_byte': 2, 'type': int}}  # value = 0...4095

# Описать (-) -----
component_type = {module_type[0x00]: None,
                  module_type[0x01]: sensors_type,
                  module_type[0x02]: devices_type}

# Описать (-) -----
state_system = {0x00: 'Work',
                0x01: 'Sleep',
                0x02: 'Setting'}

# Описать (-) -----
error_type = {0x00: 'Ok',
              0x01: 'No connection server',
              0x02: 'No ID control',
              0x03: 'No connection',
              0x04: 'Interruption communication',
              0x05: 'Pump: overpressure',
              0x06: 'Pump: pressure drop'}
