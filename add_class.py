class OrderClass:
    def __init__(self):
        self.number_of_rooms = 0
        self.number_of_bathrooms = 0
        self.additional_services = []
        self.year = ''
        self.month = ''
        self.day = ''
        self.time = ''
        self.the_date = ''
        self.regularity_of_cleaning = []
        self.address = ''
        self.full_name = ''
        self.telephone = ''
        self.email = ''
        self.promo_code = []
        self.total = ''
        self.cleaning_time = 0
        self.price = 0
        self.username = ''


class UserRequest:
    def __init__(self):
        self.window = 'Нет'
        self.furniture = 'Нет'
        self.telephone = ''
        self.username = ''