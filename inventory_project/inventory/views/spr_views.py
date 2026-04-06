from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string



from django.db.models.deletion import ProtectedError
from django.http import HttpResponse


from ..models import Izm, Podraz, Fio, Category, Postav, Spis, Obct, Nom

# Create your views here.
def my_view(request):
    if request.user.username != 'operator':
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Доступ только для операторов")


def spr(request, section):
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
    if section == 'obkt':
        # Для объектов передаем список подразделений в модальное окно
        data = Obct.objects.select_related('idpodraz').all().order_by('title')
        podraz_list = Podraz.objects.all().order_by('title')  # Получаем все подразделения

        return render(request, 'inventory/comon_spr.html', {
            'data': data,
            'title': 'Объекты',
            'section': section,
            'podraz_list': podraz_list,  # Передаем в шаблон
        })
    if section == 'nom':
        # Для номенклатуры передаем список категорий и единиц в модальное окно
        data = Nom.objects.select_related('category','izm').all().order_by('title')
        category_list = Category.objects.all().order_by('title')  # Получаем все категории
        izm_list = Izm.objects.all().order_by('title')  # Получаем все единицы измерения
        return render(request, 'inventory/comon_spr.html', {
            'data': data,
            'title': 'Номенклатура',
            'section': section,
            'category_list': category_list,
            'izm_list': izm_list
        })
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

    return render(request, 'inventory/comon_spr.html', context)












def delete_spr_row(request, section, pk):
    '''Удаление записи из справочника'''
    models = {
        'izm': Izm,
        'fio': Fio,
        'podraz': Podraz,
        'postav': Postav,
        'spis': Spis,
        'kat': Category,
        'obkt': Obct,
        'nom': Nom,
    }

    if section not in models:
        return HttpResponse(status=404)

    if request.method == 'DELETE':
        model = models[section]
        try:
            item = model.objects.get(pk=pk)
            item.delete()
            return HttpResponse(status=200)  # Успешно удалено

        except ProtectedError:
            html = f'''
                <tr id="row-{section}-{pk}" style="background-color: #fff3f3;">
                    <td colspan="2" class="text-center py-3">
                        <span class="text-danger">❌ Нельзя удалить - есть связанные записи</span>
                        <button class="btn btn-sm btn-outline-secondary ms-3" 
                                onclick="location.reload()"
                                style="border-radius: 0;">
                            ⟲ Обновить
                        </button>
                    </td>
                </tr>
            '''
            return HttpResponse(html, status=200)
        except model.DoesNotExist:
            return HttpResponse(status=404)

    return HttpResponse(status=405)

def add_spr_row(request, section):
    '''Добавление новой записи в простые справочники'''
    # Словарь моделей и соответствующих им параметров (section)
    models = {
        'izm': Izm,
        'fio': Fio,
        'podraz': Podraz,
        'postav': Postav,
        'spis': Spis,
        'kat': Category
    }
    if section not in models:
        return HttpResponse(status=404)
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if title:
            model = models[section]
            if model.objects.filter(title=title).exists():
                return HttpResponse("⚠️ Такая строка уже есть...", status=400)


            new_item = model.objects.create(title=title)
            html = render_to_string('inventory/partials/spr_row.html', {
                'item': new_item,
                'section': section
            })
            return HttpResponse(html)
        return HttpResponse(status=400)


def edit_spr_row(request, section, pk):
    """Загружает форму с данными для редактирования"""
    models = {
        'izm': Izm,
        'fio': Fio,
        'podraz': Podraz,
        'postav': Postav,
        'spis': Spis,
        'kat': Category,
    }

    model = models.get(section)
    if not model:
        return HttpResponse(status=404)

    item = get_object_or_404(model, pk=pk)

    return render(request, 'inventory/modals/edit_form.html', {
        'item': item,
        'section': section
    })


def update_spr_row(request, section, pk):
    '''Обновление записи в справочнике'''
    models = {
        'izm': Izm,
        'fio': Fio,
        'podraz': Podraz,
        'postav': Postav,
        'spis': Spis,
        'kat': Category,
    }

    if section not in models:
        return HttpResponse(status=404)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if title:
            model = models[section]
            if model.objects.filter(title=title).exists():
                return HttpResponse("⚠️ Такая строка уже есть...", status=400)

            item = get_object_or_404(model, pk=pk)
            item.title = title
            item.save()

            # Возвращаем обновленную строку
            html = render_to_string('inventory/partials/spr_row.html', {
                'item': item,
                'section': section
            })
            return HttpResponse(html)

    return HttpResponse(status=400)


from ..models import Obct, Podraz  # Добавляем Podraz


def add_obkt_row(request):
    '''Добавление нового объекта'''
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        podraz_id = request.POST.get('podraz_id')

        # Валидация
        if not title:
            return HttpResponse("❌ Название объекта не может быть пустым", status=400)

        if not podraz_id:
            return HttpResponse("❌ Выберите подразделение", status=400)

        try:
            podraz = Podraz.objects.get(id=podraz_id)

            # Проверка на дубликат (объект с таким названием уже есть?)
            if Obct.objects.filter(title=title).exists():
                return HttpResponse("❌ Объект с таким названием уже существует", status=400)

            # Создаем новый объект
            new_obct = Obct.objects.create(
                title=title,
                idpodraz=podraz
            )

            # Возвращаем строку таблицы
            html = render_to_string('inventory/partials/spr_row.html', {
                'item': new_obct,
                'section': 'obkt'
            })
            return HttpResponse(html)

        except Podraz.DoesNotExist:
            return HttpResponse("❌ Выбранное подразделение не существует", status=400)
        except Exception as e:
            return HttpResponse(f"❌ Ошибка при сохранении: {str(e)}", status=400)

    return HttpResponse(status=405)


def edit_obkt_row(request, pk):
    '''Загрузка формы редактирования объекта с данными'''
    obkt = get_object_or_404(Obct, pk=pk)
    podraz_list = Podraz.objects.all().order_by('title')

    return render(request, 'inventory/modals/edit_obkt_content.html', {
        'item': obkt,
        'podraz_list': podraz_list
    })


def update_obkt_row(request):
    '''Обновление объекта'''
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        title = request.POST.get('title', '').strip()
        podraz_id = request.POST.get('podraz_id')

        if not title:
            return HttpResponse("❌ Название объекта не может быть пустым", status=400)

        if not podraz_id:
            return HttpResponse("❌ Выберите подразделение", status=400)

        try:
            obct = Obct.objects.get(id=item_id)
            podraz = Podraz.objects.get(id=podraz_id)

            # Проверка на дубликат (исключая текущую запись)
            if Obct.objects.filter(title=title).exclude(id=item_id).exists():
                return HttpResponse("❌ Объект с таким названием уже существует", status=400)

            obct.title = title
            obct.idpodraz = podraz
            obct.save()

            html = render_to_string('inventory/partials/spr_row.html', {
                'item': obct,
                'section': 'obkt'
            })
            return HttpResponse(html)

        except Obct.DoesNotExist:
            return HttpResponse("❌ Объект не найден", status=404)
        except Podraz.DoesNotExist:
            return HttpResponse("❌ Подразделение не найдено", status=400)
        except Exception as e:
            return HttpResponse(f"❌ Ошибка: {str(e)}", status=400)

    return HttpResponse(status=405)


def add_nom_row(request):
    '''Добавление новой номенклатуры'''
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        category_id = request.POST.get('category_id')
        izm_id = request.POST.get('izm_id')

        # Валидация
        if not title:
            return HttpResponse("❌ Название номенклатуры не может быть пустым", status=400)

        if not category_id:
            return HttpResponse("❌ Выберите категорию", status=400)

        if not izm_id:
            return HttpResponse("❌ Выберите единицу измерения", status=400)

        try:
            category = Category.objects.get(id=category_id)
            izm = Izm.objects.get(id=izm_id)  # ← БЫЛО: category_id, ИСПРАВЛЕНО: izm_id

            # Проверка на дубликат
            if Nom.objects.filter(title=title).exists():
                return HttpResponse("❌ Номенклатура с таким названием уже существует", status=400)

            # Создаем новую номенклатуру
            new_nom = Nom.objects.create(  # ← БЫЛО: Obct.objects, ИСПРАВЛЕНО: Nom.objects
                title=title,
                izm=izm,
                category=category
            )

            html = render_to_string('inventory/partials/spr_row.html', {
                'item': new_nom,
                'section': 'nom'
            })

            return HttpResponse(html)

        except Category.DoesNotExist:
            return HttpResponse("❌ Выбранная категория не существует", status=400)
        except Izm.DoesNotExist:
            return HttpResponse("❌ Выбранная единица измерения не существует", status=400)
        except Exception as e:
            return HttpResponse(f"❌ Ошибка при сохранении: {str(e)}", status=400)

    return HttpResponse(status=405)



def edit_nom_row(request, pk):
    '''Загрузка формы редактирования номенклатуры с данными'''
    nom = get_object_or_404(Nom, pk=pk)
    category_list = Category.objects.all().order_by('title')
    izm_list = Izm.objects.all().order_by('title')


    return render(request, 'inventory/modals/edit_nom_content.html', {
        'item': nom,
        'category_list': category_list,
        'izm_list': izm_list
    })


def update_nom_row(request):
    '''Обновление номенклатуры'''
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        title = request.POST.get('title', '').strip()
        izm_id = request.POST.get('izm_id')
        category_id = request.POST.get('category_id')

        if not title:
            return HttpResponse("❌ Название объекта не может быть пустым", status=400)

        if not izm_id:
            return HttpResponse("❌ Выберите единицу измерения", status=400)
        if not category_id:
            return HttpResponse("❌ Выберите категорию", status=400)

        try:
            nom = Nom.objects.get(id=item_id)
            izm = Izm.objects.get(id=izm_id)
            category=Category.objects.get(id=category_id)

            # Проверка на дубликат (исключая текущую запись)
            if Nom.objects.filter(title=title).exclude(id=item_id).exists():
                return HttpResponse("❌ Номенклатура с таким названием уже существует", status=400)

            nom.title = title
            nom.izm = izm
            nom.category=category
            nom.save()

            html = render_to_string('inventory/partials/spr_row.html', {
                'item': nom,
                'section': 'nom'
            })
            return HttpResponse(html)

        except Nom.DoesNotExist:
            return HttpResponse("❌ Номенклатура не найдена", status=404)
        except Izm.DoesNotExist:
            return HttpResponse("❌ Единица измерения не найдено", status=400)
        except Exception as e:
            return HttpResponse(f"❌ Ошибка: {str(e)}", status=400)

    return HttpResponse(status=405)


from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json


@csrf_exempt
@require_POST
def add_nom_ajax(request):
    """Добавление новой номенклатуры через AJAX"""
    print("=== add_nom_ajax вызван ===")

    try:
        # Пробуем получить данные из POST
        title = request.POST.get('title', '').strip()
        izm_id = request.POST.get('izm_id')
        category_id = request.POST.get('category_id')

        print(f"title: {title}, izm_id: {izm_id}, category_id: {category_id}")

        # Валидация
        if not title:
            return JsonResponse({'error': 'Введите наименование'}, status=400)
        if not izm_id:
            return JsonResponse({'error': 'Выберите единицу измерения'}, status=400)
        if not category_id:
            return JsonResponse({'error': 'Выберите категорию'}, status=400)

        # Проверяем существование
        if Nom.objects.filter(title=title).exists():
            return JsonResponse({'error': 'Товар с таким названием уже существует'}, status=400)

        # Создаем
        izm = Izm.objects.get(id=izm_id)
        category = Category.objects.get(id=category_id)

        new_nom = Nom.objects.create(
            title=title,
            izm=izm,
            category=category
        )

        print(f"Создан: {new_nom.id} - {new_nom.title}")

        return JsonResponse({
            'status': 'ok',
            'id': new_nom.id,
            'title': new_nom.title,
            'izm': new_nom.izm.title
        })

    except Izm.DoesNotExist:
        return JsonResponse({'error': 'Единица измерения не найдена'}, status=400)
    except Category.DoesNotExist:
        return JsonResponse({'error': 'Категория не найдена'}, status=400)
    except Exception as e:
        print(f"Ошибка: {e}")
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def add_postav_ajax(request):
    """Добавление нового поставщика через AJAX"""
    print("=== add_postav_ajax вызван ===")

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()

        if not title:
            return JsonResponse({'error': 'Введите наименование поставщика'}, status=400)

        # Проверка на дубликат
        if Postav.objects.filter(title=title).exists():
            return JsonResponse({'error': 'Поставщик с таким названием уже существует'}, status=400)

        try:
            new_postav = Postav.objects.create(title=title)
            return JsonResponse({
                'status': 'ok',
                'id': new_postav.id,
                'title': new_postav.title
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)




def get_nom_by_id(request, nom_id):
    """Получить товар по ID для сканера"""
    try:
        nom = Nom.objects.select_related('izm').get(id=nom_id)
        return JsonResponse({
            'status': 'ok',
            'data': {
                'id': nom.id,
                'title': nom.title,
                'izm': nom.izm.title if nom.izm else 'шт'
            }
        })
    except Nom.DoesNotExist:
        return JsonResponse({'status': 'error', 'error': 'Товар не найден'}, status=404)