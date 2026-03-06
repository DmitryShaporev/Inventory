

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


