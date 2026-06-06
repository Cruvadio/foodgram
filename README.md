# Foodgram — Продуктовый помощник

Foodgram — это сервис для публикации рецептов, добавления их в избранное и формирования списка покупок. Пользователи могут делиться своими рецептами, подписываться на других авторов и автоматически формировать список необходимых ингредиентов для приготовления выбранных блюд.

## Возможности

### Неавторизованные пользователи

* Просмотр рецептов
* Просмотр профилей авторов
* Поиск и фильтрация рецептов по тегам
* Регистрация аккаунта

### Авторизованные пользователи

* Создание, редактирование и удаление собственных рецептов
* Добавление рецептов в избранное
* Подписка на авторов
* Формирование списка покупок
* Скачивание списка ингредиентов в текстовом формате
* Изменение пароля и управление профилем

### Администратор

* Полный доступ к управлению пользователями
* Управление рецептами, ингредиентами и тегами
* Доступ к административной панели Django

---

## Технологии

### Backend

* Python 3.12+
* Django
* Django REST Framework
* Djoser
* PostgreSQL
* Gunicorn

### Frontend

* React

### Инфраструктура

* Docker
* Docker Compose
* Nginx
* GitHub Actions

---

## Запуск проекта через Docker

### Клонирование репозитория

```bash
git clone https://github.com/Cruvadio/foodgram.git
cd foodgram
```

### Создание файла .env

Создайте файл `.env` в корневой директории проекта:

```env
SECRET_KEY=your_secret_key

DEBUG=False

ALLOWED_HOSTS=localhost,127.0.0.1

DB_ENGINE=django.db.backends.postgresql

DB_NAME=foodgram

POSTGRES_USER=foodgram_user

POSTGRES_PASSWORD=foodgram_password

DB_HOST=db

DB_PORT=5432
```

### Запуск контейнеров

```bash
docker compose up -d
```

### Выполнение миграций

```bash
docker compose exec backend python manage.py migrate
```

### Сбор статических файлов

```bash
docker compose exec backend python manage.py collectstatic --noinput
```

### Создание администратора

```bash
docker compose exec backend python manage.py createsuperuser
```

---

## Загрузка ингредиентов

Если в проекте используется CSV-файл с ингредиентами:

```bash
docker compose exec backend python manage.py load_ingredients
```

или

```bash
docker compose exec backend python manage.py loaddata data/ingredients.json
```

---

## API

После запуска документация API доступна по адресу:

```text
http://localhost/api/docs/
```

или

```text
http://localhost/redoc/
```

---

## Примеры запросов

### Получение списка рецептов

```http
GET /api/recipes/
```

### Получение рецепта

```http
GET /api/recipes/{id}/
```

### Добавление рецепта в избранное

```http
POST /api/recipes/{id}/favorite/
```

### Подписка на автора

```http
POST /api/users/{id}/subscribe/
```

---

## CI/CD

Проект использует GitHub Actions для:

* Проверки кода (flake8)
* Запуска тестов
* Сборки Docker-образов
* Публикации образов в Docker Hub
* Автоматического деплоя на сервер

Для работы CI/CD необходимо настроить следующие Secrets:

```text
SECRET_KEY
DOCKER_USERNAME
DOCKER_PASSWORD
HOST
USER
SSH_KEY
SSH_PASSPHRASE
POSTGRES_USER
POSTGRES_PASSWORD
DB_NAME
```

---

## Локальная разработка

Создание виртуального окружения:

```bash
python -m venv venv
```

Linux/macOS:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

Установка зависимостей:

```bash
pip install -r requirements.txt
```

Применение миграций:

```bash
python manage.py migrate
```

Запуск сервера:

```bash
python manage.py runserver
```

---

## Автор

**Cruvadio**

GitHub: https://github.com/Cruvadio

---

## Лицензия

Проект распространяется под лицензией MIT.
