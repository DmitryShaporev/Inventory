from django.shortcuts import render


def index(request):
    """
    Главная страница
    """
    context = {
        'title': 'Главная страница',
        'message': 'Добро пожаловать на сайт!'
    }
    return render(request, 'inventory/index.html', context)


def menu(request, section):
    """
    Страница меню (справочники, документы, отчеты)
    """
    spr = {
        'nom': 'Номенклатура',
        'izm': 'Единицы измерения',
        'kat': 'Категории ТМЦ',
        'postav': 'Поставщики',
        'podraz': 'Подразделения',
        'obkt': 'Объекты',
        'fio': 'Подотчетные лица',
        'spis': 'Списание'
    }

    docs = {
        'incom': 'Поступление ТМЦ',
        'move': 'Передача ТМЦ',
        'ret': 'Возврат ТМЦ',
        'spis': 'Списание ТМЦ',
    }

    reports = {
        'incom': 'Поступление ТМЦ',
        'move': 'Передача ТМЦ',
        'nal': 'Наличие ТМЦ',
        'spis': 'Списание ТМЦ',
        'obkt': 'По объектам',
        'podraz': 'По подразделениям',
        'kat': 'По категориям',
        'fio': 'По подотчету',
        'postav': 'По поставщикам'
    }

    # Выбираем нужный словарь по section
    if section == 'spr':
        data = spr
        title = 'Справочники'
    elif section == 'docs':
        data = docs
        title = 'Документы'
    elif section == 'reports':
        data = reports
        title = 'Отчеты'
    else:
        data = {}
        title = 'Раздел не найден'

    context = {
        'data': data,
        'title': title,
        'section': section,
        'kind': section

    }
    return render(request, 'inventory/menu.html', context)
