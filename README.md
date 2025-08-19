# Описание
Домашнее задание по FastAPI в рамках курса "Прикладной Python"
# API для сервиса сокращения ссылок – shortist


## Описание API

Этот сервис предоставляет REST API для:
- Аутентификации пользователей (регистрация, вход, выход)
- Создания, управления и отслеживания сокращенных ссылок
- Получения статистики по ссылкам

API разделен на две основные группы эндпоинтов:
- `/auth` - для работы с пользователями
- `/links` - для работы со ссылками

## Примеры запросов

### Аутентификация

#### Регистрация нового пользователя
```http
POST /auth/register

{
  "email": "user@example.com",
  "password": "string",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false
}
```

#### Вход пользователя
```http
POST /auth/jwt/login
grant_type=password&username=username@example.com&password=password
```

#### Выход пользователя
```http
POST /auth/jwt/logout
```

### Работа со ссылками
#### Создание сокращенной ссылки
```http
POST /links/shorten

{
"original_url": "https://example.com",
"custom_alias": "my-link",
"expire_at": "2025-04-30T22:30+00:00"
}
```
#### Получение оригинальной ссылки (редирект)
```http
GET /links/{short_id}
```

#### Получение статистики по ссылке
```http
GET /links/{short_id}/stats
```

#### Обновление ссылки
```http
PUT /links/{short_id}

{
"original_url": "https://new-example.com",
"expire_at": "2025-05-30T22:30+00:00"
}
```


#### Удаление ссылки
```http
DELETE /links/{short_id}
```

#### Поиск ссылок
```http
GET /links/search/?original_url=http://example.com
```


### Инструкция по запуску

- Создайте и наполните .env файл под вашу конфигурацию
- Запустите сборку контейнеров: `docker-compose up -d --build`
- Выполните миграцию с инициализацией БД по схеме проекта: `docker-compose exec web alembic upgrade head`

Сервис готов к использованию 🎉

## Тесты и покрытие

### Установка зависимостей
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-test.txt
```

#### Запуск функциональных и юнит тестов
```bash
pytest tests/
```

#### Генерация HTML-отчёта (сгенерированный лежит в htmlcov\index.html)
```bash
pytest --cov=src --cov-report=html tests/
```

##### Актуальный отчёт о тестировании доступен по ссылке:
[Посмотреть HTML-отчёт](file:///C:/Users/%D0%90%D1%80%D1%82%D1%91%D0%BC%20%D0%93%D1%83%D0%BC%D0%B5%D0%BD%D1%8E%D0%BA/Documents/GitHub/shortist/htmlcov/index.html)

#### Запуск нагрузочных тестов

##### Не доделаны (не работают)