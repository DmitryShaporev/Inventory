from datetime import datetime, date
import json

from django.db import transaction
from django.shortcuts import render, get_object_or_404
from ..models import Izm, Podraz, Fio, Category, Postav, Spis, Obct, Nom,Doc,Detail,Manage
from django.db.models.deletion import ProtectedError

from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce




def parse_decimal(value):
    """Преобразует строку с запятой в число с плавающей точкой"""
    if not value:
        return 0.0
    # Заменяем запятую на точку
    value = str(value).replace(',', '.')
    # Удаляем пробелы
    value = value.replace(' ', '')
    try:
        return float(value)
    except ValueError:
        return 0.0


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


def create_doc_inc(request):
    """Создание нового приходного документа"""
    from datetime import date

    context = {
        'today': date.today(),
        'postav_list': Postav.objects.all().order_by('title'),
        'nom_list': Nom.objects.select_related('izm').all().order_by('title'),
        'izm_list': Izm.objects.all().order_by('title'),
        'category_list': Category.objects.all().order_by('title'),
        'is_edit': False,  # ← флаг для нового документа
    }
    return render(request, 'inventory/incom_doc_form.html', context)

def save_incom_doc(request):
    """Сохранение приходного документа"""

    manage = Manage.objects.first()
    if not manage:
        return JsonResponse({'error': 'Не настроены параметры склада (Manage)'}, status=400)

    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

    try:
        data = json.loads(request.body)

        with transaction.atomic():
            doc = Doc.objects.create(
                nomer=data['doc']['nomer'],
                datadoc=data['doc']['datadoc'],
                postav_id=data['doc']['postav_id'],
                fio=manage.fio,
                obct=manage.obkt,
                oper=2,
                total=0
            )

            total = 0
            for item in data['items']:
                # Преобразуем значения с запятой в числа
                kolvo = parse_decimal(item['kolvo'])
                price = parse_decimal(item['price'])
                vat_rate = parse_decimal(item['vat_rate'])
                cost_without_vat = parse_decimal(item['cost_without_vat'])
                vat_amount = parse_decimal(item['vat_amount'])
                total_with_vat = parse_decimal(item['total_with_vat'])

                detail = Detail.objects.create(
                    id_doc=doc,
                    id_nom_id=item['nom_id'],
                    kolvo=kolvo,
                    price=price,
                    cost=cost_without_vat,
                    vat_rate=vat_rate,
                    vat_amount=vat_amount,
                    total_with_vat=total_with_vat,
                    oper=2
                )

                total += total_with_vat

            doc.total = total
            doc.save()

        return JsonResponse({'status': 'ok'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def edit_incom_doc(request, doc_id):
    """Редактирование приходного документа"""
    from datetime import date

    # Получаем документ
    doc = get_object_or_404(Doc, id=doc_id, oper=2)

    # Получаем строки документа
    details = Detail.objects.filter(id_doc=doc).select_related('id_nom', 'id_nom__izm')

    context = {
        'doc': doc,
        'details': details,
        'today': date.today(),
        'postav_list': Postav.objects.all().order_by('title'),
        'nom_list': Nom.objects.select_related('izm').all().order_by('title'),
        'izm_list': Izm.objects.all().order_by('title'),
        'category_list': Category.objects.all().order_by('title'),
        'is_edit': True,  # флаг для шаблона, что это редактирование
    }
    return render(request, 'inventory/incom_doc_form.html', context)


def update_incom_doc(request, pk):
    """Обновление приходного документа"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

    try:
        data = json.loads(request.body)

        with transaction.atomic():
            # Получаем существующий документ
            doc = Doc.objects.get(id=pk, oper=2)

            # Обновляем шапку
            doc.nomer = data['doc']['nomer']
            doc.datadoc = data['doc']['datadoc']
            doc.postav_id = data['doc']['postav_id']

            # Удаляем старые строки
            doc.details.all().delete()

            # Создаем новые строки
            total = 0
            for item in data['items']:
                kolvo = parse_decimal(item['kolvo'])
                price = parse_decimal(item['price'])
                vat_rate = parse_decimal(item['vat_rate'])
                cost_without_vat = parse_decimal(item['cost_without_vat'])
                vat_amount = parse_decimal(item['vat_amount'])
                total_with_vat = parse_decimal(item['total_with_vat'])

                Detail.objects.create(
                    id_doc=doc,
                    id_nom_id=item['nom_id'],
                    kolvo=kolvo,
                    price=price,
                    cost=cost_without_vat,
                    vat_rate=vat_rate,
                    vat_amount=vat_amount,
                    total_with_vat=total_with_vat,
                    oper=2
                )
                total += total_with_vat

            doc.total = total
            doc.save()

        return JsonResponse({'status': 'ok'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)





@require_POST
def delete_incom_doc(request, doc_id):
    """Удаление приходного документа"""
    try:
        doc = get_object_or_404(Doc, id=doc_id, oper=2)

        # Проверяем, есть ли строки
        if doc.details.exists():
            return JsonResponse({
                'error': f'❌ Нельзя удалить документ №{doc.nomer} — есть строки!'
            }, status=400)

        doc.delete()
        return JsonResponse({'status': 'ok'})

    except ProtectedError:
        return JsonResponse({
            'error': f'❌ Нельзя удалить документ — есть связанные записи!'
        }, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# inventory/views/doc_views.py




# inventory/views/doc_views.py

def create_move_doc(request):
    """Создание нового документа перемещения"""
    from datetime import date
    from ..models import Fio, Obct

    context = {
        'today': date.today(),
        'fio_list': Fio.objects.all().order_by('title'),
        'obct_list': Obct.objects.all().order_by('title'),
        'is_edit': False,
    }
    return render(request, 'inventory/move_doc_form.html', context)


def edit_move_doc(request, doc_id):
    """Редактирование документа перемещения"""
    from datetime import date
    from ..models import Doc, Detail, Fio, Obct

    doc = get_object_or_404(Doc, id=doc_id, oper=3)
    details = Detail.objects.filter(id_doc=doc).select_related('id_nom', 'id_nom__izm')

    context = {
        'doc': doc,
        'details': details,
        'today': date.today(),
        'fio_list': Fio.objects.all().order_by('title'),
        'obct_list': Obct.objects.all().order_by('title'),
        'is_edit': True,
    }
    return render(request, 'inventory/move_doc_form.html', context)


def save_move_doc(request):
    """Сохранение нового документа перемещения"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

    try:
        data = json.loads(request.body)

        with transaction.atomic():
            # Создаем документ перемещения (oper=3)
            doc = Doc.objects.create(
                nomer=data['doc']['nomer'],
                datadoc=data['doc']['datadoc'],
                fio_id=data['doc']['fio_id'],
                obct_id=data['doc']['obct_to_id'],  # склад-получатель
                oper=3,  # код перемещения
                total=0
            )

            total = 0
            for item in data['items']:
                kolvo = parse_decimal(item['kolvo'])
                price = parse_decimal(item['price'])
                cost = kolvo * price

                # Записываем строку с отрицательным количеством
                Detail.objects.create(
                    id_doc=doc,
                    id_nom_id=item['nom_id'],
                    kolvo=-kolvo,
                    price=price,
                    cost=-cost,
                    oper=3
                )
                total += cost

            doc.total = abs(total)
            doc.save()

        return JsonResponse({'status': 'ok'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def update_move_doc(request, doc_id):
    """Обновление документа перемещения"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

    try:
        data = json.loads(request.body)

        with transaction.atomic():
            # Получаем существующий документ
            doc = Doc.objects.get(id=doc_id, oper=3)

            # Обновляем шапку
            doc.nomer = data['doc']['nomer']
            doc.datadoc = data['doc']['datadoc']
            doc.fio_id = data['doc']['fio_id']
            doc.obct_id = data['doc']['obct_to_id']

            # Удаляем старые строки
            doc.details.all().delete()

            # Создаем новые строки
            total = 0
            for item in data['items']:
                kolvo = parse_decimal(item['kolvo'])
                price = parse_decimal(item['price'])
                cost = kolvo * price

                Detail.objects.create(
                    id_doc=doc,
                    id_nom_id=item['nom_id'],
                    kolvo=-kolvo,
                    price=price,
                    cost=-cost,
                    oper=3
                )
                total += cost

            doc.total = abs(total)
            doc.save()

        return JsonResponse({'status': 'ok'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

    # Добавь в doc_views.py или в отдельный файл


def get_fio_list(request):
    """Получить список подотчетных лиц для модалки"""
    fio_list = Fio.objects.all().order_by('title')
    return render(request, 'inventory/modals/fio_list_content.html', {'fio_list': fio_list})


def get_obct_list(request):
    """Получить список складов для модалки"""
    obct_list = Obct.objects.all().order_by('title')
    return render(request, 'inventory/modals/obct_list_content.html', {'obct_list': obct_list})


# def api_remains(request):
#     """API для получения остатков товаров с группировкой по цене"""
#     from django.db import connection
#
#     query = """
#         SELECT
#             n.id as nom_id,
#             n.title as title,
#             i.title as izm,
#             d.price,
#             SUM(d.kolvo) as quantity
#         FROM detail d
#         INNER JOIN nom n ON d.id_nom = n.id
#         LEFT JOIN izm i ON n.izm_id = i.id
#         INNER JOIN doc ON d.id_doc = doc.id
#         WHERE doc.oper IN (1, 2, 4, 3, 5)
#         GROUP BY n.id, d.price
#         HAVING SUM(d.kolvo) != 0
#         ORDER BY n.title, d.price
#     """
#
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute(query)
#             columns = [col[0] for col in cursor.description]
#             rows = cursor.fetchall()
#
#         remains = []
#         for row in rows:
#             data = dict(zip(columns, row))
#             remains.append({
#                 'nom_id': data['nom_id'],
#                 'title': data['title'] or 'Без названия',
#                 'izm': data['izm'] or 'шт',
#                 'price': float(data['price']),
#                 'quantity': float(data['quantity'])
#             })
#
#         print(f"Найдено остатков: {len(remains)}")
#         return JsonResponse({'status': 'ok', 'data': remains})
#
#     except Exception as e:
#         print(f"Ошибка в api_remains: {e}")
#         import traceback
#         traceback.print_exc()
#         return JsonResponse({'status': 'error', 'error': str(e)}, status=500)

def api_remains(request):
    """API для получения остатков товаров (по средней цене)"""
    from django.db import connection

    query = """
        SELECT 
            n.id as nom_id,
            n.title as title,
            i.title as izm,
            SUM(d.kolvo) as quantity,
            CASE 
                WHEN SUM(d.kolvo) != 0 
                THEN SUM(d.kolvo * d.price) / SUM(d.kolvo)
                ELSE 0
            END as avg_price
        FROM detail d
        INNER JOIN nom n ON d.id_nom = n.id
        LEFT JOIN izm i ON n.izm_id = i.id
        INNER JOIN doc ON d.id_doc = doc.id
        WHERE doc.oper IN (1, 2, 4, 3, 5)
        GROUP BY n.id, n.title, i.title
        HAVING SUM(d.kolvo) > 0  -- Только положительные остатки
        ORDER BY n.title
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

        remains = []
        for row in rows:
            data = dict(zip(columns, row))
            quantity = float(data['quantity'])
            avg_price = float(data['avg_price']) if data['avg_price'] else 0

            # Дополнительная проверка на положительность
            if quantity <= 0:
                continue

            remains.append({
                'nom_id': data['nom_id'],
                'title': data['title'] or 'Без названия',
                'izm': data['izm'] or 'шт',
                'price': round(avg_price, 2),
                'quantity': round(quantity, 0)
            })

        print(f"Найдено остатков: {len(remains)}")
        return JsonResponse({'status': 'ok', 'data': remains, 'total_count': len(remains)})

    except Exception as e:
        print(f"Ошибка в api_remains: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'error': str(e)}, status=500)




@require_POST
def delete_move_doc(request, doc_id):
    """Удаление документа перемещения"""
    try:
        doc = get_object_or_404(Doc, id=doc_id, oper=3)

        # Проверяем, есть ли строки
        if doc.details.exists():
            return JsonResponse({
                'error': f'❌ Нельзя удалить документ №{doc.nomer} — есть строки!'
            }, status=400)

        doc.delete()
        return JsonResponse({'status': 'ok'})

    except ProtectedError:
        return JsonResponse({
            'error': f'❌ Нельзя удалить документ — есть связанные записи!'
        }, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)