class Payment:
    def __init__(self, amount):
        self.amount = amount

    def process_payment(self):
        raise NotImplementedError("Метод должен быть переопределен в дочернем классе")


class CardPayment(Payment):
    def __init__(self, amount, card_number):
        super().__init__(amount)
        self.__card_number = card_number  # Приватный атрибут

    def process_payment(self):
        # Маскируем номер карты для безопасности
        masked_card = "**** " + self.__card_number[-4:]
        return "Оплата картой " + masked_card + ": " + str(self.amount) + " руб."


class PayPalPayment(Payment):
    def __init__(self, amount, email):
        super().__init__(amount)
        self.email = email

    def process_payment(self):
        return "Оплата PayPal (" + self.email + "): " + str(self.amount) + " руб."
