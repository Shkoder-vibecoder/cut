TEXTURE_LABELS = {
    "none": "Без направления",
    "horizontal": "Горизонтальная",
    "vertical": "Вертикальная",
}

ORDER_STATUS_LABELS = {
    "draft": "Черновик",
    "in_progress": "В работе",
    "completed": "Завершен",
    "archived": "В архиве",
}

TASK_STATUS_LABELS = {
    "pending": "Ожидание",
    "running": "Выполняется",
    "done": "Готово",
    "failed": "Ошибка",
}

ALGORITHM_LABELS = {
    "greedy": "Жадный",
    "genetic": "Генетический",
    "annealing": "Отжиг",
}

CUT_TYPE_LABELS = {
    "free": "Свободный",
    "guillotine": "Гильотинный",
}

FIBERS_LABELS = {
    "any": "Любое",
    "horizontal": "Горизонтальное",
    "vertical": "Вертикальное",
}

MOVEMENT_REASON_LABELS = {
    "arrival": "Поступление",
    "cutting": "Раскрой",
    "manual": "Ручное изменение",
    "return": "Возврат",
}


def label_for(mapping: dict[str, str], code: str | None) -> str:
    if code is None:
        return ""
    return mapping.get(code, code)
