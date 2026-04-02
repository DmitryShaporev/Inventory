from django.http import HttpResponse


def reports(request, section):
    """Временная заглушка для отчетов"""
    return HttpResponse(f"Страница отчетов: {section} (в разработке)")


from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.db.models import Sum
from ..models import Doc, Detail
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
        'remain': 'Остатки ТМЦ',
    }

    context = {
        'data': reports,
        'title': 'Отчеты',
        'section': section,
        'kind': 'reports',
    }
    return render(request, 'inventory/menu.html', context)