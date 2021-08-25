
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

devices_type = {0x00: {'name': 'Signal_PWM',        'num_byte': 2, 'type': int},  # value = 0...4095
                0x01: {'name': 'Signal_digital',    'num_byte': 1, 'type': bool},
                0x02: {'name': 'Fan_PWM',           'num_byte': 2, 'type': int},  # value = 0...4095
                0x03: {'name': 'Pumping_system',    'num_byte': 1, 'type': bool},
                0x04: {'name': 'Phytolamp_digital', 'num_byte': 1, 'type': bool},
                0x05: {'name': 'Phytolamp_PWM',     'num_byte': 2, 'type': int}}  # value = 0...4095


class Module(object):
    def __init__(self, module_id, module_data, time):
        self.id = module_id
        self.data = module_data
        self.time = time


class SystemRegistration(object):
    def __init__(self, module_id, module_data):
        self.mainId = module_id
        self.attachedId = module_data

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
