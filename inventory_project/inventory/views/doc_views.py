from datetime import datetime, date

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.db.models import Q

from django.db.models.deletion import ProtectedError
from django.http import HttpResponse
from ..models import Izm, Podraz, Fio, Category, Postav, Spis, Obct, Nom,Doc

def docs(request, section):

    if section == 'incom':
        title = 'Входящие документы'
        data = Doc.objects.filter(oper=2).select_related('postav').order_by('-datadoc')

    elif section == 'move':
        title = 'Документы по передаче ТМЦ'
        data = Doc.objects.filter(oper=3).select_related('fio', 'obct', 'obct__idpodraz', 'postav').order_by('-datadoc')
    elif section == 'ret':
        title = 'Документы на возврат ТМЦ'
        data = Doc.objects.filter(oper=4).select_related('fio', 'obct', 'obct__idpodraz', 'postav').order_by('-datadoc')
    else:
        title ='Документы по списанию ТМЦ'
        data = Doc.objects.filter(oper=4).select_related('fio', 'obct', 'obct__idpodraz', 'postav').order_by('-datadoc')

    context={'title':title,
             'data': data,
             'section': section}
    return render(request, 'inventory/doc_journal.html',context)


def search_doc(request):
    """Поиск по документам"""
    search_query = request.GET.get('search', '')
    section = request.GET.get('section', 'incom')  # Получаем тип документа

    # Соответствие разделов и операций
    doc_types = {
        'incom': 2,  # Приход
        'move': 3,  # Перемещение
        'ret': 4,  # Возврат
        'spis': 5,  # Списание
    }

    # Базовый запрос с фильтрацией по типу
    oper = doc_types.get(section)
    if oper:
        queryset = Doc.objects.filter(oper=oper).select_related('postav', 'obct', 'fio')
    else:
        queryset = Doc.objects.select_related('postav', 'obct', 'fio')

    # Поиск по тексту
    if search_query:
        # Создаем Q объект для поиска
        q_filter = Q(nomer__icontains=search_query)

        # Добавляем поиск по связанным полям
        q_filter |= Q(postav__title__icontains=search_query)
        q_filter |= Q(obct__title__icontains=search_query)
        q_filter |= Q(fio__title__icontains=search_query)

        # Попробуем поискать по дате
        try:
            # Парсим дату в формате ДД.ММ.ГГГГ
            day, month, year = search_query.split('.')
            date_obj = date(int(year), int(month), int(day))
            q_filter |= Q(datadoc=date_obj)
        except (ValueError, AttributeError):
            pass

        # Пробуем как год
        try:
            if search_query.isdigit() and len(search_query) == 4:
                q_filter |= Q(datadoc__year=search_query)
        except:
            pass

        queryset = queryset.filter(q_filter)

    # Сортировка и ограничение
    data = queryset.order_by('-datadoc')[:100]  # Максимум 100 результатов

    html = render_to_string('inventory/partials/doc_table.html', {
        'data': data,
        'section': section
    })
    return HttpResponse(html)


def create_doc_inc(request):
    postav_list=Postav.objects.all()
    content={
        'postav_list':postav_list
    }
    return render(request,'inventory/create_doc_inc.html',context=content)