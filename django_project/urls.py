"""
URL configuration for django_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# БЛОК 1: ИМПОРТЫ
from django.contrib import admin # Встроенный модуль Django для административной панели
# Регистрирует маршрут /admin/ со всем интерфейсом управления
from django.urls import path # Функция path() — описывает один URL-маршрут
# Принимает: строку пути, view-функцию, необязательное имя маршрута
from wsdl_security import views # Импортируем модуль views целиком, а не отдельные функции

# БЛОК 2: ТАБЛИЦА МАРШРУТОВ
urlpatterns = [
    # Маршрут 1: Административная панель
    # URL: /admin/
    # Обработчик: встроенный Django Admin
    # Используется для управления пользователями и моделями через браузер
    path('admin/', admin.site.urls),

    # Маршрут 2: Главная страница
    # URL: / (корень сайта, пустая строка)
    # Обработчик: views.index
    # Строит 3 графика, таблицу IP и журнал атак 
    # name='index' позволяет ссылаться на маршрут по имени: {% url 'index' %}
    path('', views.index, name='index'),

    # Маршрут 3: Просмотр фейковых WSDL
    # URL: /fake-wsdl/
    # Обработчик: views.fake_wsdl_viewer
    # Двухколоночная страница: список IP-нарушителей + содержимое их WSDL
    # IP выбирается через GET-параметр: /fake-wsdl/?ip=192.165.1.10
    path('fake-wsdl/', views.fake_wsdl_viewer, name='fake_wsdl_viewer'),

    # Маршрут 4: Скачивание фейкового WSDL
    # URL: /fake-wsdl/download/192.165.1.10/
    # Обработчик: views.download_fake_wsdl
    # <str:ip_address> — динамический сегмент URL:
    # Django вырезает строку между /download/ и финальным и передаёт её в функцию как аргумент ip_address
    # Возвращает XML-файл с заголовком Content-Disposition: attachment
    path('fake-wsdl/download/<str:ip_address>/', views.download_fake_wsdl, name='download_fake_wsdl'),
]