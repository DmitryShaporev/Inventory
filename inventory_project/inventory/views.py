
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string

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
          'spis':'Списание ТМЦ'}
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
