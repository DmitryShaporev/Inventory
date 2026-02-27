# myapp/admin.py
from django.contrib import admin
from .models import (
    Izm, Category, Nom, Podraz, Obct, Postav,
    Fio, Doc, Detail,  Spis
)

# Простая регистрация (базовый вид)
admin.site.register(Izm)
admin.site.register(Category)
admin.site.register(Nom)
admin.site.register(Podraz)
admin.site.register(Obct)
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
    list_display = ['nomer', 'datadoc', 'postav', 'obct', 'fio', 'total']
    list_filter = ['postav', 'obct', 'fio', 'datadoc']
    search_fields = ['nomer']

    inlines = [DetailInline]  # Показываем детали документа внутри карточки документа

@admin.register(Detail)
class DetailAdmin(admin.ModelAdmin):
    list_display = ['id_doc', 'id_nom', 'kolvo', 'price', 'cost']
    list_filter = ['id_doc__postav', 'id_nom']  # Фильтр по поставщику документа и товару
    search_fields = ['id_doc__nomer', 'id_nom__title']