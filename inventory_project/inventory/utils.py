from .models import Akt

def get_next_move_doc_number():
    """Возвращает следующий номер для документа перемещения"""
    last_akt = Akt.objects.last()  # Берём последнюю запись
    if last_akt and last_akt.nomer is not None:
        return last_akt.nomer + 1
    return 1  # Если записей нет, начинаем с 1

def update_move_doc_number(used_number):
    """Обновляет номер в Akt после использования"""
    Akt.objects.create(nomer=used_number)