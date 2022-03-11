import ESP_connect_packet_objects as ESP_objects

Direction_type = {'Exit': 0, 'Entry': 1}


class Object_ACS(ESP_objects.Packet_object):
    def __init__(self, acs_id):
        super().__init__()
        self.acs_id = acs_id

    def get_acs_id(self):
        return self.acs_id


class Pass_request(Object_ACS):
    def __init__(self, acs_id, card_id, direction):
        super().__init__(acs_id=acs_id)
        self.card_id = card_id
        self.direction = None
        if isinstance(direction, int):
            for key, value in Direction_type.items():
                if value == direction:
                    self.direction = key
        elif isinstance(direction, str):
            self.direction = direction

    def get_card_id(self):
        return self.card_id

    def get_direction(self):
        return self.direction

    def get_direction_num(self):
        return Direction_type[self.direction]


class Passage_permission(Object_ACS):
    def __init__(self, acs_id, card_id, direction):
        super().__init__(acs_id=acs_id)
        self.card_id = card_id
        self.direction = None
        if isinstance(direction, int):
            for key, value in Direction_type.items():
                if value == direction:
                    self.direction = key
        elif isinstance(direction, str):
            self.direction = direction

    def get_card_id(self):
        return self.card_id

    def get_direction(self):
        return self.direction

    def get_direction_num(self):
        return Direction_type[self.direction]


class Passage_prohibition(Object_ACS):
    def __init__(self, acs_id, card_id):
        super().__init__(acs_id=acs_id)
        self.card_id = card_id

    def get_card_id(self):
        return self.card_id


class Add_ID(Object_ACS):
    def __init__(self, acs_id, card_id):
        super().__init__(acs_id=acs_id)
        self.card_id = card_id

    def get_card_id(self):
        return self.card_id


class Delete_ID(Object_ACS):
    def __init__(self, acs_id, card_id):
        super().__init__(acs_id=acs_id)
        self.card_id = card_id

    def get_card_id(self):
        return self.card_id
