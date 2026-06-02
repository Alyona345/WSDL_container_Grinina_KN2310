#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os # Нужен для работы с переменными окружения
import sys # Нужен для чтения аргументов командной строки (sys.argv)

# БЛОК 1: ГЛАВНАЯ ФУНКЦИЯ
def main():
    # Устанавливает переменную окружения, указывающую Django, где искать файл настроек — django_project/settings.py, setdefault — не перезаписывает, если переменная уже задана снаружи
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc  # Понятная ошибка вместо стандартного "ModuleNotFoundError"
        # Подсказывает: проверь установку Django и виртуальное окружение
    execute_from_command_line(sys.argv)  # Передаёт аргументы командной строки в Django
    # sys.argv[0] — имя файла (manage.py)
    # sys.argv[1] — команда, например: runserver, migrate, createsuperuser
    # sys.argv[2+] — дополнительные параметры, например: 0.0.0.0:8000

# БЛОК 2: ТОЧКА ВХОДА
if __name__ == '__main__':
    main() # Стандартная защита от случайного импорта:
    # main() вызывается только при прямом запуске файла, но не когда manage.py импортируется как модуль
