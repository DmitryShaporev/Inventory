from django.http import HttpResponse


def reports(request, section):
    """Временная заглушка для отчетов"""
    return HttpResponse(f"Страница отчетов: {section} (в разработке)")


from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.db.models import Sum
from ..models import Doc, Detail, Nom
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side
from io import BytesIO
from datetime import datetime, timedelta


def incom_report(request):
    """Отчет о поступлении ТМЦ"""
    date_start = request.GET.get('date_start')
    date_end = request.GET.get('date_end')
    date_type = request.GET.get('date_type', 'doc')  # 'doc' или 'created'

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_incom_report_table(request, date_start, date_end, date_type)

    context = {
        'date_start': date_start,
        'date_end': date_end,
        'date_type': date_type,
    }
    return render(request, 'inventory/reports/incom_report.html', context)


def render_incom_report_table(request, date_start, date_end, date_type='doc'):
    """Рендеринг таблицы отчета"""

    # Базовый запрос
    docs = Doc.objects.filter(oper=2).select_related('postav').prefetch_related('details', 'details__id_nom',
                                                                                'details__id_nom__izm')

    # Фильтрация по дате в зависимости от выбранного типа
    if date_start:
        if date_type == 'doc':
            docs = docs.filter(datadoc__gte=date_start)
        else:  # 'created'
            # Преобразуем дату в начало дня
            start_datetime = datetime.strptime(date_start, '%Y-%m-%d')
            docs = docs.filter(update_date__gte=start_datetime)

    if date_end:
        if date_type == 'doc':
            docs = docs.filter(datadoc__lte=date_end)
        else:  # 'created'
            # Преобразуем дату в конец дня
            end_datetime = datetime.strptime(date_end, '%Y-%m-%d') + timedelta(days=1)
            docs = docs.filter(update_date__lt=end_datetime)

    docs = docs.order_by('-datadoc')

    # Добавляем агрегированные суммы для каждого документа
    docs_with_totals = []
    grand_total = 0
    grand_total_vat = 0
    grand_total_without_vat = 0

    for doc in docs:
        details = list(doc.details.all())
        total_without_vat = sum(d.cost for d in details)
        total_vat = sum(d.vat_amount for d in details)
        total = sum(d.total_with_vat for d in details)

        grand_total_without_vat += total_without_vat
        grand_total_vat += total_vat
        grand_total += total

        # Форматируем даты для отображения
        date_start_display = ''
        date_end_display = ''

        if date_start:
            try:
                date_start_display = datetime.strptime(date_start, '%Y-%m-%d').strftime('%d.%m.%Y')
            except:
                date_start_display = date_start

        if date_end:
            try:
                date_end_display = datetime.strptime(date_end, '%Y-%m-%d').strftime('%d.%m.%Y')
            except:
                date_end_display = date_end

        docs_with_totals.append({
            'id': doc.id,
            'nomer': doc.nomer,
            'datadoc': doc.datadoc,
            'postav': doc.postav,
            'details': details,
            'total': total,
            'total_without_vat': total_without_vat,
            'total_vat': total_vat,
            'created_at': doc.update_date,  # добавляем дату создания
        })

    html = render_to_string('inventory/reports/incom_report_table.html', {
        'docs': docs_with_totals,
        'date_start': date_start_display if 'date_start_display' in locals() else '',
        'date_end': date_end_display if 'date_end_display' in locals() else '',
        'date_type': date_type,
        'grand_total': grand_total,
        'grand_total_vat': grand_total_vat,
        'grand_total_without_vat': grand_total_without_vat
    })
    return HttpResponse(html)


def incom_report_excel(request):
    """Экспорт отчета в Excel"""
    date_start = request.GET.get('date_start')
    date_end = request.GET.get('date_end')
    date_type = request.GET.get('date_type', 'doc')

    docs = Doc.objects.filter(oper=2).select_related('postav').prefetch_related('details', 'details__id_nom',
                                                                                'details__id_nom__izm')

    if date_start:
        if date_type == 'doc':
            docs = docs.filter(datadoc__gte=date_start)
        else:
            start_datetime = datetime.strptime(date_start, '%Y-%m-%d')
            docs = docs.filter(update_date__gte=start_datetime)

    if date_end:
        if date_type == 'doc':
            docs = docs.filter(datadoc__lte=date_end)
        else:
            end_datetime = datetime.strptime(date_end, '%Y-%m-%d') + timedelta(days=1)
            docs = docs.filter(update_date__lt=end_datetime)

    docs = docs.order_by('-datadoc')

    # Создаем Excel файл
    import openpyxl
    from openpyxl.styles import Font, Alignment
    from io import BytesIO

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Отчет по поступлению"

    # Заголовки
    headers = ['№ п/п', 'Документ', 'Дата', 'Поставщик', 'Наименование', 'Ед.изм.', 'Кол-во', 'Цена',
               'Стоимость без НДС', 'НДС %', 'Сумма НДС', 'Стоимость с НДС']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')

    row_num = 2
    for doc in docs:
        for detail in doc.details.all():
            ws.cell(row=row_num, column=1, value=row_num - 1)
            ws.cell(row=row_num, column=2, value=doc.nomer)
            ws.cell(row=row_num, column=3, value=doc.datadoc.strftime('%d.%m.%Y'))
            ws.cell(row=row_num, column=4, value=doc.postav.title if doc.postav else '')
            ws.cell(row=row_num, column=5, value=detail.id_nom.title if detail.id_nom else '')
            ws.cell(row=row_num, column=6, value=detail.id_nom.izm.title if detail.id_nom and detail.id_nom.izm else '')
            ws.cell(row=row_num, column=7, value=float(detail.kolvo))
            ws.cell(row=row_num, column=8, value=float(detail.price))
            ws.cell(row=row_num, column=9, value=float(detail.cost))
            ws.cell(row=row_num, column=10, value=float(detail.vat_rate))
            ws.cell(row=row_num, column=11, value=float(detail.vat_amount))
            ws.cell(row=row_num, column=12, value=float(detail.total_with_vat))
            row_num += 1
        row_num += 1  # пустая строка после документа

    # Настраиваем ширину колонок
    for col in range(1, 13):
        ws.column_dimensions[chr(64 + col)].width = 15

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    response = HttpResponse(output.getvalue(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=incom_report_{datetime.now().strftime("%Y%m%d")}.xlsx'
    return response


def reports_menu(request, section):
    """Страница меню отчетов"""
    # Просто показываем меню, независимо от section
    reports = {
        'incom': 'Поступление ТМЦ',
        'move': 'Перемещение ТМЦ',
        'remain': 'Наличие ТМЦ',
        'postav':'По поставщикам',
        'obct': 'По объектам',
        'podraz':'По подразделениям',
        'fio': 'По подотчетным лицам',
        'category':'По категориям'

    }

    context = {
        'data': reports,
        'title': 'Отчеты',
        'section': section,
        'kind': 'reports',
    }
    return render(request, 'inventory/menu.html', context)


def move_report(request):
    """Отчет о перемещении ТМЦ"""
    date_start = request.GET.get('date_start')
    date_end = request.GET.get('date_end')
    date_type = request.GET.get('date_type', 'created')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_move_report_table(request, date_start, date_end, date_type)

    context = {
        'date_start': date_start,
        'date_end': date_end,
        'date_type': date_type,
    }
    return render(request, 'inventory/reports/move_report.html', context)


def render_move_report_table(request, date_start, date_end, date_type='created'):
    """Рендеринг таблицы отчета по перемещению"""
    from datetime import datetime, timedelta

    # Объявляем переменные ДО условий
    date_start_display = ''
    date_end_display = ''

    docs = Doc.objects.filter(oper=3).select_related('fio', 'obct', 'obct__idpodraz').prefetch_related('details',
                                                                                                       'details__id_nom',
                                                                                                       'details__id_nom__izm')

    if date_start:
        if date_type == 'doc':
            docs = docs.filter(datadoc__gte=date_start)
        else:
            start_datetime = datetime.strptime(date_start, '%Y-%m-%d')
            docs = docs.filter(update_date__gte=start_datetime)

        # Форматируем дату для отображения
        try:
            date_start_display = datetime.strptime(date_start, '%Y-%m-%d').strftime('%d.%m.%Y')
        except:
            date_start_display = date_start

    if date_end:
        if date_type == 'doc':
            docs = docs.filter(datadoc__lte=date_end)
        else:
            end_datetime = datetime.strptime(date_end, '%Y-%m-%d') + timedelta(days=1)
            docs = docs.filter(update_date__lt=end_datetime)

        # Форматируем дату для отображения
        try:
            date_end_display = datetime.strptime(date_end, '%Y-%m-%d').strftime('%d.%m.%Y')
        except:
            date_end_display = date_end

    docs = docs.order_by('-datadoc')

    docs_with_totals = []
    grand_total = 0
    grand_total_vat = 0
    grand_total_without_vat = 0

    for doc in docs:
        details = list(doc.details.all())
        total_without_vat = sum(d.cost for d in details)
        total_vat = sum(d.vat_amount for d in details)
        total = sum(d.total_with_vat for d in details)

        grand_total_without_vat += total_without_vat
        grand_total_vat += total_vat
        grand_total += total

        docs_with_totals.append({
            'id': doc.id,
            'nomer': doc.nomer,
            'datadoc': doc.datadoc,
            'fio': doc.fio.title if doc.fio else '—',
            'obct': doc.obct.title if doc.obct else '—',
            'podraz': doc.obct.idpodraz.title if doc.obct and doc.obct.idpodraz else '—',
            'details': details,
            'total': total,
            'total_without_vat': total_without_vat,
            'total_vat': total_vat,
        })

    html = render_to_string('inventory/reports/move_report_table.html', {
        'docs': docs_with_totals,
        'date_start': date_start_display,
        'date_end': date_end_display,
        'date_type': date_type,
        'grand_total': grand_total,
        'grand_total_vat': grand_total_vat,
        'grand_total_without_vat': grand_total_without_vat,
    })
    return HttpResponse(html)

def move_report_excel(request):
    """Экспорт отчета по перемещению в Excel"""
    from datetime import datetime, timedelta
    import openpyxl
    from openpyxl.styles import Font, Alignment
    from io import BytesIO

    date_start = request.GET.get('date_start')
    date_end = request.GET.get('date_end')
    date_type = request.GET.get('date_type', 'created')

    docs = Doc.objects.filter(oper=3).select_related('fio', 'obct', 'obct__idpodraz').prefetch_related('details', 'details__id_nom', 'details__id_nom__izm')

    if date_start:
        if date_type == 'doc':
            docs = docs.filter(datadoc__gte=date_start)
        else:
            start_datetime = datetime.strptime(date_start, '%Y-%m-%d')
            docs = docs.filter(update_date__gte=start_datetime)

    if date_end:
        if date_type == 'doc':
            docs = docs.filter(datadoc__lte=date_end)
        else:
            end_datetime = datetime.strptime(date_end, '%Y-%m-%d') + timedelta(days=1)
            docs = docs.filter(update_date__lt=end_datetime)

    docs = docs.order_by('-datadoc')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Отчет по перемещению"

    headers = ['№ п/п', 'Документ', 'Дата', 'Подразделение', 'Объект', 'Подотчет',
               'Наименование', 'Ед.изм.', 'Кол-во', 'Цена', 'Стоимость без НДС', 'НДС %', 'Сумма НДС', 'Стоимость с НДС']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')

    row_num = 2
    for doc in docs:
        for detail in doc.details.all():
            ws.cell(row=row_num, column=1, value=row_num - 1)
            ws.cell(row=row_num, column=2, value=doc.nomer)
            ws.cell(row=row_num, column=3, value=doc.datadoc.strftime('%d.%m.%Y'))
            ws.cell(row=row_num, column=4, value=doc.obct.idpodraz.title if doc.obct and doc.obct.idpodraz else '')
            ws.cell(row=row_num, column=5, value=doc.obct.title if doc.obct else '')
            ws.cell(row=row_num, column=6, value=doc.fio.title if doc.fio else '')
            ws.cell(row=row_num, column=7, value=detail.id_nom.title if detail.id_nom else '')
            ws.cell(row=row_num, column=8, value=detail.id_nom.izm.title if detail.id_nom and detail.id_nom.izm else '')
            ws.cell(row=row_num, column=9, value=abs(float(detail.kolvo)))
            ws.cell(row=row_num, column=10, value=abs(float(detail.price)))
            ws.cell(row=row_num, column=11, value=abs(float(detail.cost)))
            ws.cell(row=row_num, column=12, value=abs(float(detail.vat_rate)))
            ws.cell(row=row_num, column=13, value=abs(float(detail.vat_amount)))
            ws.cell(row=row_num, column=14, value=abs(float(detail.total_with_vat)))
            row_num += 1
        row_num += 1

    for col in range(1, 15):
        ws.column_dimensions[chr(64 + col)].width = 15

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=move_report_{datetime.now().strftime("%Y%m%d")}.xlsx'
    return response


def remain_report(request):
    """Отчет об остатках ТМЦ на текущую дату"""
    show_zero = request.GET.get('show_zero', 'all')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_remain_report_table(request, show_zero)

    return render(request, 'inventory/reports/remain_report.html')


def render_remain_report_table(request, show_zero='all'):
    """Рендеринг таблицы отчета об остатках (группировка по товару+цена с объединением)"""
    from django.db import connection

    # Убираем HAVING — получаем ВСЕ товары, включая нулевые остатки
    query = """
        SELECT 
            n.id as nom_id,
            n.title as title,
            COALESCE(i.title, 'шт') as izm,
            d.price,
            SUM(d.kolvo) as quantity
        FROM detail d
        INNER JOIN nom n ON d.id_nom = n.id
        LEFT JOIN izm i ON n.izm_id = i.id
        INNER JOIN doc ON d.id_doc = doc.id
        WHERE doc.oper IN (1, 2, 4, 3, 5)
        GROUP BY n.id, n.title, i.title, d.price
        ORDER BY n.title, d.price
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

        # Временный словарь для объединения одинаковых товаров с одинаковой ценой
        temp_dict = {}

        for row in rows:
            data = dict(zip(columns, row))
            quantity = float(data['quantity'])

            # Ключ: товар + цена
            key = f"{data['nom_id']}_{data['price']}"

            if key in temp_dict:
                # Если уже есть — суммируем количество
                temp_dict[key]['quantity'] += quantity
            else:
                # Если нет — добавляем новую запись
                temp_dict[key] = {
                    'nom_id': data['nom_id'],
                    'title': data['title'] or 'Без названия',
                    'izm': data['izm'] or 'шт',
                    'price': float(data['price']),
                    'quantity': quantity
                }

        # Формируем итоговый список с фильтрацией
        remains = []
        total_quantity = 0
        total_sum = 0

        for key, item in temp_dict.items():
            quantity = round(item['quantity'], 0)

            # Фильтрация по show_zero (уже на уровне Python)
            if show_zero == 'positive' and quantity <= 0:
                continue

            remains.append({
                'nom_id': item['nom_id'],
                'title': item['title'],
                'izm': item['izm'],
                'price': item['price'],
                'quantity': quantity
            })
            total_quantity += quantity if quantity > 0 else 0
            total_sum += quantity * item['price'] if quantity > 0 else 0

        # Сортируем по наименованию, затем по цене
        remains.sort(key=lambda x: (x['title'], x['price']))

        html = render_to_string('inventory/reports/remain_report_table.html', {
            'remains': remains,
            'total_quantity': total_quantity,
            'total_sum': total_sum,
        })
        return HttpResponse(html)

    except Exception as e:
        print(f"Ошибка в remain_report: {e}")
        import traceback
        traceback.print_exc()
        return HttpResponse('<div class="alert alert-danger">Ошибка формирования отчета</div>')

def remain_report_excel(request):
    """Экспорт отчета об остатках в Excel"""
    from django.db import connection
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill
    from io import BytesIO
    from datetime import datetime

    show_zero = request.GET.get('show_zero', 'all')

    query = """
        SELECT 
            n.id as nom_id,
            n.title as title,
            COALESCE(i.title, 'шт') as izm,
            d.price,
            SUM(d.kolvo) as quantity
        FROM detail d
        INNER JOIN nom n ON d.id_nom = n.id
        LEFT JOIN izm i ON n.izm_id = i.id
        INNER JOIN doc ON d.id_doc = doc.id
        WHERE doc.oper IN (1, 2, 4, 3, 5)
        GROUP BY n.id, n.title, i.title, d.price
        HAVING SUM(d.kolvo) != 0
        ORDER BY n.title, d.price
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    # Объединяем одинаковые товары с одинаковой ценой
    temp_dict = {}
    for row in rows:
        nom_id = row[0]
        title = row[1] or 'Без названия'
        izm = row[2] or 'шт'
        price = float(row[3])
        quantity = float(row[4])

        key = f"{nom_id}_{price}"
        if key in temp_dict:
            temp_dict[key]['quantity'] += quantity
        else:
            temp_dict[key] = {
                'nom_id': nom_id,
                'title': title,
                'izm': izm,
                'price': price,
                'quantity': quantity
            }

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Остатки ТМЦ"

    # Заголовки
    headers = ['№ п/п', 'Наименование', 'Ед.изм.', 'Цена', 'Количество']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')

    row_num = 2
    total_quantity = 0
    total_sum = 0
    yellow_fill = PatternFill(start_color="FFF3CD", end_color="FFF3CD", fill_type="solid")

    i = 1
    for key, item in temp_dict.items():
        quantity = round(item['quantity'], 0)

        if show_zero == 'positive' and quantity <= 0:
            continue

        ws.cell(row=row_num, column=1, value=i)
        ws.cell(row=row_num, column=2, value=item['title'])
        ws.cell(row=row_num, column=3, value=item['izm'])
        ws.cell(row=row_num, column=4, value=item['price'])
        ws.cell(row=row_num, column=5, value=quantity)

        # Подсветка нулевых
        if quantity == 0:
            for col in range(1, 6):
                ws.cell(row=row_num, column=col).fill = yellow_fill

        total_quantity += quantity if quantity > 0 else 0
        total_sum += quantity * item['price'] if quantity > 0 else 0
        row_num += 1
        i += 1

    # Итоговая строка
    ws.cell(row=row_num, column=4, value='ИТОГО:')
    ws.cell(row=row_num, column=5, value=total_quantity)
    ws.cell(row=row_num, column=4).font = Font(bold=True)
    ws.cell(row=row_num, column=5).font = Font(bold=True)

    for col in range(1, 6):
        ws.column_dimensions[chr(64 + col)].width = 20

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    response = HttpResponse(output.getvalue(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=remain_report_{datetime.now().strftime("%Y%m%d")}.xlsx'
    return response


def nom_card(request, nom_id):
    """Карточка товара — история всех движений"""
    from decimal import Decimal

    nom = get_object_or_404(Nom, id=nom_id)

    # Получаем все движения по товару в хронологическом порядке
    movements = Detail.objects.filter(
        id_nom_id=nom_id
    ).select_related('id_doc', 'id_doc__postav', 'id_doc__fio', 'id_doc__obct').order_by('id_doc__datadoc', 'id')

    movement_list = []
    balance = Decimal('0')
    total_income = Decimal('0')
    total_outcome = Decimal('0')
    total_sum_without_vat = Decimal('0')
    total_vat = Decimal('0')
    total_sum = Decimal('0')

    for detail in movements:
        doc = detail.id_doc
        if not doc:
            continue

        kolvo = detail.kolvo

        # Обновляем остаток
        balance += kolvo

        # Определяем "от кого получено / кому отпущено"
        from_party = ''
        to_party = ''

        if doc.oper == 2:  # Приход
            from_party = doc.postav.title if doc.postav else '—'
            to_party = ''
        elif doc.oper == 3:  # Перемещение
            from_party = ''
            to_party = f"{doc.fio.title if doc.fio else '—'} на {doc.obct.title if doc.obct else '—'}"
        elif doc.oper == 4:  # Возврат
            from_party = doc.postav.title if doc.postav else '—'
            to_party = ''
        elif doc.oper == 5:  # Списание
            from_party = ''
            to_party = f"Списание: {doc.fio.title if doc.fio else '—'}"
        else:
            from_party = '—'
            to_party = '—'

        # Используем правильные поля для отображения
        cost_without_vat = abs(detail.cost) if detail.cost else Decimal('0')
        vat_amount = abs(detail.vat_amount) if detail.vat_amount else Decimal('0')
        total_with_vat = abs(detail.total_with_vat) if detail.total_with_vat else cost_without_vat + vat_amount

        movement_list.append({
            'doc_id': doc.id,
            'nomer': doc.nomer,
            'datadoc': doc.datadoc,
            'oper': doc.oper,
            'kolvo': kolvo,
            'from_party': from_party,
            'to_party': to_party,
            'price': abs(detail.price) if detail.price else Decimal('0'),
            'cost': cost_without_vat,
            'vat_rate': detail.vat_rate if detail.vat_rate else Decimal('0'),
            'vat_amount': vat_amount,
            'total_with_vat': total_with_vat,
            'balance_after': balance
        })

        if kolvo > 0:
            total_income += abs(kolvo)
        else:
            total_outcome += abs(kolvo)

        total_sum_without_vat += cost_without_vat
        total_vat += vat_amount
        total_sum += total_with_vat

    context = {
        'nom': nom,
        'movements': movement_list,
        'current_balance': balance,
        'total_income': total_income,
        'total_outcome': total_outcome,
        'total_sum_without_vat': total_sum_without_vat,
        'total_vat': total_vat,
        'total_sum': total_sum,
    }
    return render(request, 'inventory/reports/nom_card.html', context)