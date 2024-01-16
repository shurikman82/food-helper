# food-helper
Food-helper - это полнофункциональное веб-приложение, которое позволяет пользователям делиться своими предпочтениями в еде и интересами, а также находить новые рецепты и делится своими идеями в области кулинарии. Вы можете создать свой собственный уникальный рецепт и поделиться им с окружающими. Возможно, Вас заметят! Тогда многие любители кулинарного исскуства смогут подписаться на Вас как на любимого автора!

## Особенности:

– Аутентификация пользователя: происходит по имейлу и паролю, которые Вы указали при регистрации.

– Просмотр рецептов: Поиск рецептов по принадлежности к завтраку, обеду или ужину. Рецепты представлены с изображениями, списком ингредиентов и временем приготовления.

– Вы можете добавить понравившейся рецепт в избранное, чтобы не потерять его!

– Вы можете добавить понравившейся рецепт и не один в список покупок, а потом разом скачать ингредиенты, которые понадобятся Вам для приготовления любимого блюда или нескольких любимых блюд.

## Запуск проекта локально
Проект упакован в три контейнера: nginx, PostgreSQL и Django, запускаемые через docker-compose. Файлы для сборки фронтенда хранятся в репозитории food-helper в папке frontend.

Для запуска проекта выполните следующие шаги:
1. Склонируйте репозиторий foodgram-project-react на свой компьютер.
2. Создайте и активируйте виртуальное окружение:
   - для Windows
   ```bash
   python -m venv venv
   source venv/Scripts/activate
   ```
   - для Linux/macOS
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Обновите [pip](https://pip.pypa.io/en/stable/):
   - для Windows
   ```bash
   python -m pip install --upgrade pip
   ```
   - для Linux/macOS
   ```bash
   python3 -m pip install --upgrade pip
   ```
4. Установите зависимости из файла requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```
5. Создайте и заполните файл .env на примере:
   ```bash
   DEBUG=False
   SECRET_KEY='Your Django key'
   ALLOWED_HOSTS=127.0.0.1,localhost,etc,
   POSTGRES_DB=foodgram
   POSTGRES_USER=foodgram_user
   POSTGRES_PASSWORD=foodgram_password
   DB_HOST=localhost
   PORT=5432
   ```
7. Запустите проект в трёх контейнерах с помощью Docker Compose:
   ```bash
    docker compose up
   ```
8. Выполните миграции:
   ```bash
    docker compose exec backend python manage.py migrate
   ```
9. Соберите статические файлы:
    ```bash
    docker compose exec backend python manage.py collectstatic
    ```
    ```bash
    docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
    ```
10. Вам потребуется работа в панели администратора, создайте суперпользователя:
   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```
11. С помощью браузера зайдите в панель администратора сервиса. Сделайте импорт ингредиентов из JSON-файла.

## Автор: 
Александр Русанов, shurik.82rusanov@yandex.ru




