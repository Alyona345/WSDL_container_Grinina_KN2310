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
from django.contrib import admin
from django.urls import path
from wsdl_security import views

urlpatterns = [
    # Админ-панель Django
    path('admin/', admin.site.urls),

    # ГЛАВНАЯ СТРАНИЦА - статистика и графики
    # URL: http://127.0.0.1:8000/
    path('', views.index, name='index'),

    # НОВАЯ СТРАНИЦА - просмотр фейковых WSDL-ответов
    # URL: http://127.0.0.1:8000/fake-wsdl/
    path('fake-wsdl/', views.fake_wsdl_viewer, name='fake_wsdl_viewer'),

    # НОВЫЙ МАРШРУТ - скачивание фейкового WSDL для конкретного IP
    # URL: http://127.0.0.1:8000/fake-wsdl/download/192.165.1.10/
    path('fake-wsdl/download/<str:ip_address>/', views.download_fake_wsdl, name='download_fake_wsdl'),
]