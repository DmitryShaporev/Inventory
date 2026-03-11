from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Главная страница с картинкой:)

    path('menu/<str:section>/', views.menu, name='menu'),  # Страница меню
    path('menu/spr/<str:section>/', views.spr, name='spr'),  # Открытие страницы справочника
    path('search/<str:section>/', views.search_spr, name='search_spr'),  # поиск по справочнику
    path('spr/<str:section>/edit/<int:pk>', views.edit_spr_row, name='edit_spr_row'), # Вызывает модальное окно для редактирования
    path('spr/<str:section>/<int:pk>/update/', views.update_spr_row, name='update_spr_row'), # Сохраняет изменения в строке справочника
    path('spr/<str:section>/<int:pk>/delete/', views.delete_spr_row, name='delete_spr_row'),
    path('spr/<str:section>/add/', views.add_spr_row, name='add_spr_row'),


]
