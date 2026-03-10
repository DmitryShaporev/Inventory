from django.urls import path
from . import views



urlpatterns = [
    path('', views.index, name='index'), # Главная страница с картинкой:)
    path('api/data/', views.get_data, name='get_data'),
    path('menu/<str:section>/', views.menu, name='menu'), #Страница меню
    path('menu/spr/<str:section>/', views.spr, name='spr'), #Страница простых справочников
    path('search/<str:section>/', views.search_spr, name='search_spr'),
    path('spr/<str:section>/<int:pk>/edit/', views.edit_spr_row, name='edit_spr_row'),
    path('spr/<str:section>/<int:pk>/delete/', views.delete_spr_row, name='delete_spr_row'),


]