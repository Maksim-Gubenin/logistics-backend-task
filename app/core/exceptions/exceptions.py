class InsufficientStockError(Exception):
    def __init__(self, nomenclature_id: int, available_quantity: int, requested_quantity: int):
        self.nomenclature_id = nomenclature_id
        self.available_quantity = available_quantity
        self.requested_quantity = requested_quantity
        super().__init__(
            f"Недостаточное количество товара ID {nomenclature_id}. "
            f"Запрошено: {requested_quantity}, "
            f"в наличии: {available_quantity}."
        )

class OrderNotFoundError(Exception):
    def __init__(self, order_id: int):
        self.order_id = order_id
        super().__init__(f"Заказ с ID {order_id} не найден.")

class NomenclatureNotFoundError(Exception):
    def __init__(self, nomenclature_id: int):
        self.nomenclature_id = nomenclature_id
        super().__init__(f"Номенклатура с ID {nomenclature_id} не найдена.")
