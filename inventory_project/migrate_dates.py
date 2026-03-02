import os
import django
from datetime import datetime
import re

# Настройка Django окружения
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_project.settings')
django.setup()

from inventory.models import Doc


def parse_date(date_string):
    """
    Парсит дату из строки формата ДД.ММ.ГГГГ в объект date
    """
    if not date_string or not isinstance(date_string, str):
        return None

    # Убираем лишние пробелы
    date_string = date_string.strip()

    # Проверяем формат регулярным выражением
    pattern = r'^(\d{1,2})\.(\d{1,2})\.(\d{4})$'
    match = re.match(pattern, date_string)

    if match:
        day, month, year = map(int, match.groups())
        try:
            return datetime(year, month, day).date()
        except ValueError as e:
            print(f"  ❌ Некорректная дата: {date_string} - {e}")
            return None
    else:
        print(f"  ❌ Неверный формат: {date_string}")
        return None


def migrate_dates():
    """
    Переносит данные из datadoc в datadoc_temp
    """
    print("=" * 60)
    print("Начинаем перенос дат...")
    print("=" * 60)

    # Получаем все документы
    docs = Doc.objects.all()
    total = docs.count()

    print(f"Всего документов: {total}")
    print("-" * 60)

    # Счетчики
    success = 0
    skipped = 0
    error = 0
    already_filled = 0

    for doc in docs:
        # Пропускаем, если уже заполнено
        if doc.datadoc_temp:
            already_filled += 1
            print(f"⏭️  [{doc.id}] Документ №{doc.nomer}: уже заполнен ({doc.datadoc_temp})")
            continue

        # Парсим дату
        date_obj = parse_date(doc.datadoc)

        if date_obj:
            # Сохраняем преобразованную дату
            doc.datadoc_temp = date_obj
            doc.save()
            success += 1
            print(f"✅ [{doc.id}] Документ №{doc.nomer}: {doc.datadoc} -> {date_obj}")
        else:
            error += 1
            print(f"❌ [{doc.id}] Документ №{doc.nomer}: не удалось преобразовать '{doc.datadoc}'")

    print("=" * 60)
    print(f"Итоги переноса:")
    print(f"  ✅ Успешно преобразовано: {success}")
    print(f"  ⏭️  Уже было заполнено: {already_filled}")
    print(f"  ❌ Ошибок преобразования: {error}")
    print(f"  ⏸️  Пропущено (без данных): {skipped}")
    print(f"  📊 Всего обработано: {total}")
    print("=" * 60)


def check_results():
    """
    Проверяет результаты переноса
    """
    print("\n" + "=" * 60)
    print("Проверка результатов:")
    print("=" * 60)

    # Проверяем заполненные поля
    filled = Doc.objects.exclude(datadoc_temp__isnull=True).count()
    empty = Doc.objects.filter(datadoc_temp__isnull=True).count()
    total = Doc.objects.count()

    print(f"📊 Статистика:")
    print(f"  ✅ Заполнено datadoc_temp: {filled}")
    print(f"  ❌ Пустых datadoc_temp: {empty}")
    print(f"  📈 Процент заполнения: {filled / total * 100:.1f}%" if total > 0 else "  📈 Нет документов")

    # Показываем примеры
    print("\n📝 Примеры первых 5 записей:")
    for doc in Doc.objects.all()[:5]:
        print(f"  [{doc.id}] №{doc.nomer}: '{doc.datadoc}' -> {doc.datadoc_temp}")


def show_problem_dates():
    """
    Показывает проблемные даты, которые не удалось преобразовать
    """
    print("\n" + "=" * 60)
    print("Проблемные даты (не удалось преобразовать):")
    print("=" * 60)

    # Ищем записи, где datadoc_temp пустой, но datadoc не пустой
    problems = Doc.objects.filter(
        datadoc_temp__isnull=True
    ).exclude(
        datadoc__isnull=True
    ).exclude(
        datadoc=''
    )

    if problems.exists():
        for doc in problems[:20]:  # Показываем первые 20
            print(f"  [{doc.id}] №{doc.nomer}: '{doc.datadoc}'")

        if problems.count() > 20:
            print(f"  ... и ещё {problems.count() - 20} записей")
    else:
        print("  ✅ Проблемных дат нет!")


if __name__ == '__main__':
    try:
        # Выполняем миграцию
        migrate_dates()

        # Проверяем результаты
        check_results()

        # Показываем проблемные даты
        show_problem_dates()

        print("\n✨ Перенос данных завершен!")

    except Exception as e:
        print(f"\n❌ Ошибка при выполнении: {e}")
        import traceback

        traceback.print_exc()