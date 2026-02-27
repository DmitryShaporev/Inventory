# myapp/admin.py
from django.contrib import admin
from .models import (
    Izm, Category, Nom, Podraz, Obct, Postav,
    Fio, Doc, Detail,  Spis
)

# Простая регистрация (базовый вид)
admin.site.register(Izm)
admin.site.register(Category)
# admin.site.register(Nom)
admin.site.register(Podraz)
# admin.site.register(Obct)
admin.site.register(Postav)
admin.site.register(Fio)
admin.site.register(Spis)
# admin.site.register(Akt)

# Для Doc и Detail сделаем более красивое отображение
class DetailInline(admin.TabularInline):
    model = Detail
    extra = 0  # Не показывать пустые строки для новых деталей
    fields = ['id_nom', 'kolvo', 'price', 'cost', 'oper']
    readonly_fields = ['cost']  # Стоимость можно сделать только для чтения

@admin.register(Doc)
class DocAdmin(admin.ModelAdmin):
    list_display = ['nomer', 'datadoc', 'postav', 'obct', 'fio', 'total','oper']
    list_filter = ['postav', 'obct', 'fio', 'datadoc','oper']
    search_fields = ['nomer']

    def operation_name(self, obj):
        operations = {
            1: 'Остатки',
            2: 'Поступление',
            3: 'Перемещение',
            4: 'Списание',  # добавьте свои значения
        }
        return operations.get(obj.oper, f'Неизвестно ({obj.oper})')

    operation_name.short_description = 'Операция'

    inlines = [DetailInline]  # Показываем детали документа внутри карточки документа

@admin.register(Detail)
class DetailAdmin(admin.ModelAdmin):
    list_display = ['id_doc', 'id_nom', 'kolvo', 'price', 'cost']
    list_filter = ['id_doc__postav', 'id_nom']  # Фильтр по поставщику документа и товару
    search_fields = ['id_doc__nomer', 'id_nom__title']


@admin.register(Obct)
class ObctAdmin(admin.ModelAdmin):
    list_display = ['title', 'idpodraz']  # Просто указываем поле ForeignKey
    list_display_links = ['title']  # Делаем title ссылкой
    search_fields = ['title']  # Поиск по названию объекта
    list_filter = ['idpodraz']  # Фильтр по подразделению


@admin.register(Nom)
class NomAdmin(admin.ModelAdmin):
    list_display = ['title', 'category']  # Просто указываем поле ForeignKey
    list_display_links = ['title']  # Делаем title ссылкой
    search_fields = ['title','category']  # Поиск по названию объекта
    list_filter = ['category']  # Фильтр по подразделению