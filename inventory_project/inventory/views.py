
import pandas as pd
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from datetime import datetime
from django.template.loader import render_to_string
from django.db.models import Q
from .models import Izm, Podraz, Fio, Category, Postav, Spis, Obct, Nom


# Create your views here.

def index(request):
    """
    Главная страница
    """
    context = {
        'title': 'Главная страница',
        'message': 'Добро пожаловать на сайт!'
    }
    return render(request, 'inventory/index.html', context)


def get_data(request):
    """
    Пример представления для htmx запроса
    """

    data = {
        'items': [
            {'id': 1, 'name': 'Ноутбук'},
            {'id': 2, 'name': 'Монитор'},
            {'id': 3, 'name': 'Клавиатура'},
            {'id': 4, 'name': 'Мышь'},
        ]
    }

    if request.headers.get('HX-Request') == 'true':
        # Это htmx запрос
        html = render_to_string('inventory/data_partial.html', data)
        return HttpResponse(html)
    else:
        # Обычный запрос
        return JsonResponse(data)

def about(request):
    """
    Страница "О нас"
    """
    return render(request, 'inventory/about.html', {'title': 'О нас'})

def menu(request,section):
    """
    Страница "Справочники"
    """
    spr={'nom':'Номенклатура',
          'izm':'Единицы измерения',
          'kat':'Категории ТМЦ',
          'postav':'Поставщики',
          'podraz':'Подразделения',
          'obkt':'Объекты',
          'fio':'Подотчетные лица',
         'spis':'Списание'
          }
    docs={'incom':'Поступление ТМЦ',
          'move':'Передача ТМЦ',
          'ret':'Возврат ТМЦ',
          'spis':'Списание ТМЦ',
          }
    reports={'incom':'Поступление ТМЦ',
             'move':'Передача ТМЦ',
             'nal':'Наличие ТМЦ',
             'spis':'Списание ТМЦ',
             'obkt':'По объектам',
             'podraz':'По подразделениям',
             'kat':'По категориям',
             'fio':'По подотчету',
             'postav':'По поставщикам'}

    if section == 'spr':
        context = {
            'data': spr,
            'title': 'Справочники'
        }
    elif section == 'docs':
        context = {
            'data': docs,
            'title': 'Документы'
        }
    elif section == 'reports':
        context = {
            'data': reports,
            'title': 'Отчеты'
        }
    else:
        context = {
            'data': {},
            'title': 'Раздел не найден'
        }

    return render(request, 'inventory/menu.html', context)


def spr(request,section):
    tables={
        'izm':[Izm,'Единицы измерения'],
        'fio':[Fio,"Подотчетные лица"],
        'podraz':[Podraz,"Подразделения"],
        'postav':[Postav,"Поставщики"],
        'spis':[Spis,"Списание"],
        'kat':[Category,"Категории ТМЦ"],
        'obkt':[Obct,"Объекты"],
        'nom':[Nom,"Номенклатура"],
    }

    if section in tables:
        model, title = tables[section]  # распаковываем список в две переменные
        if section == 'nom':
            data = model.objects.select_related('category', 'izm').all().order_by('title')
        elif section == 'obkt':
            data = model.objects.select_related('idpodraz').all().order_by('title')
        else:
            data = model.objects.all().order_by('title')


    else:
        data = []
        title = 'Раздел не найден'

    context = {
       'data': data,
       'title': title,
        'section': section,
        }

    return render(request,'inventory/comon_spr.html',context)


def search_spr(request, section):
    """Поиск по справочнику"""
    search_query = request.GET.get('search', '')

    # Словарь моделей
    tables = {
        'izm': [Izm, 'Единицы измерения'],
        'fio': [Fio, "Подотчетные лица"],
        'podraz': [Podraz, "Подразделения"],
        'postav': [Postav, "Поставщики"],
        'spis': [Spis, "Списание"],
        'kat': [Category, "Категории ТМЦ"],
        'obkt': [Obct, "Объекты"],
        'nom': [Nom, "Номенклатура"],
    }

    if section in tables:
        model, title = tables[section]

        # Базовый запрос
        if section == 'nom':
            queryset = model.objects.select_related('category', 'izm').all()
        elif section == 'obkt':
            queryset = model.objects.select_related('idpodraz').all()
        else:
            queryset = model.objects.all()

        # Фильтрация по полю title (или name - зависит от модели)
        if search_query:
            if hasattr(model, 'title'):
                data = queryset.filter(title__icontains=search_query)
            else:
                data = queryset.filter(name__icontains=search_query)
        else:
            data = queryset

        # Сортируем
        data = data.order_by('title' if hasattr(model, 'title') else 'name')
    else:
        data = []

    html = render_to_string('inventory/partials/spr_table.html', {
        'data': data,
        'section': section
    })
    return HttpResponse(html)


def export_to_excel(request, section):
    """Простой экспорт справочника в Excel"""

    # Словарь моделей (как и везде)
    tables = {
        'izm': [Izm, 'Единицы измерения', ['id', 'title']],
        'fio': [Fio, "Подотчетные лица", ['id', 'title']],
        'podraz': [Podraz, "Подразделения", ['id', 'title']],
        'postav': [Postav, "Поставщики", ['id', 'title']],
        'spis': [Spis, "Списание", ['id', 'title']],
        'kat': [Category, "Категории ТМЦ", ['id', 'title']],
        'obkt': [Obct, "Объекты", ['id', 'title', 'idpodraz']],
        'nom': [Nom, "Номенклатура", ['id', 'title', 'category', 'izm']],
    }

    if section not in tables:
        return HttpResponse("Раздел не найден", status=404)

    model, title, fields = tables[section]

    # Получаем данные с оптимизацией
    if section == 'nom':
        data = model.objects.select_related('category', 'izm').all().order_by('title')
    elif section == 'obkt':
        data = model.objects.select_related('idpodraz').all().order_by('title')
    else:
        data = model.objects.all().order_by('title')

    # Преобразуем в список словарей
    rows = []
    for item in data:
        row = {'Наименование': item.title}

        # Добавляем связанные поля
        if section == 'nom':
            row['Категория'] = item.category.title if item.category else ''
            row['Ед. измерения'] = item.izm.title if item.izm else ''
        elif section == 'obkt':
            row['Подразделение'] = item.idpodraz.title if item.idpodraz else ''

        rows.append(row)

    # Создаем DataFrame
    df = pd.DataFrame(rows)

    # Создаем HTTP-ответ с Excel-файлом
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="Inventory_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx"'

    # Записываем DataFrame в Excel
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=title, index=False)

    return response
