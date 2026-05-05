from typing import Optional


def validate_dimensions(width: float, height: float) -> tuple[bool, str]:
    if width <= 0:
        return False, "Ширина должна быть больше 0"
    if height <= 0:
        return False, "Высота должна быть больше 0"
    if width > 10000:
        return False, "Ширина слишком большая (макс. 10000 мм)"
    if height > 10000:
        return False, "Высота слишком большая (макс. 10000 мм)"
    return True, ""


def validate_quantity(quantity: int) -> tuple[bool, str]:
    if quantity <= 0:
        return False, "Количество должно быть больше 0"
    if quantity > 10000:
        return False, "Количество слишком большое"
    return True, ""


def validate_price(price: float) -> tuple[bool, str]:
    if price < 0:
        return False, "Цена не может быть отрицательной"
    if price > 1000000:
        return False, "Цена слишком большая"
    return True, ""


def validate_order_number(order_number: str) -> tuple[bool, str]:
    if not order_number or len(order_number.strip()) == 0:
        return False, "Номер заказа не может быть пустым"
    if len(order_number) > 50:
        return False, "Номер заказа слишком длинный (макс. 50 символов)"
    return True, ""


def validate_cut_params(cut_width: float, edge_offset: float, sheet_width: float, sheet_height: float) -> tuple[bool, str]:
    if cut_width < 0:
        return False, "Ширина реза не может быть отрицательной"
    if edge_offset < 0:
        return False, "Отступ от края не может быть отрицательным"
    if cut_width > min(sheet_width, sheet_height) / 2:
        return False, "Ширина реза слишком большая для данного листа"
    return True, ""