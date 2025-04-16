# Тестирующая система

Веб-приложение для создания и прохождения тестов с системой статистики и управления пользователями.

## Требования

- Python 3.8+
- Docker и Docker Compose (опционально)

## Установка

1. Создайте виртуальное окружение:
```bash
python -m venv venv
```

2. Активируйте виртуальное окружение:
- Windows:
```bash
.\venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Запуск

### Локальный запуск

1. Запустите приложение:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. Откройте в браузере:
- Главная страница: http://localhost:8000
- Документация API: http://localhost:8000/docs

### Запуск через Docker

1. Соберите и запустите контейнеры:
```bash
docker-compose up --build
```

2. Приложение будет доступно по тем же адресам.

## Основные функции

- Создание и редактирование тестов
- Прохождение тестов
- Просмотр результатов
- Управление пользователями
- Статистика и аналитика

## Структура проекта

```
Praktika/
├── api/           # API endpoints
├── core/          # Основная логика
├── static/        # Статические файлы
├── templates/     # HTML шаблоны
├── main.py        # Точка входа
└── requirements.txt
```

## Основные маршруты

- `/` - главная страница
- `/login` - страница входа
- `/register` - страница регистрации
- `/dashboard` - панель управления тестами
- `/create_test` - создание нового теста
- `/edit_test/{test_id}` - редактирование теста
- `/view_test/{test_id}` - просмотр теста
- `/add_question/{test_id}` - добавление вопроса к тесту
- `/edit_question/{question_id}` - редактирование вопроса
- `/delete_test/{test_id}` - удаление теста
- `/delete_question/{question_id}` - удаление вопроса

## Переход с Flask на FastAPI

Основные изменения при переходе с Flask на FastAPI:

1. Замена декораторов маршрутов Flask на FastAPI
2. Использование Pydantic для валидации данных
3. Использование зависимостей FastAPI для внедрения сессий БД
4. Замена Flask-Login на собственную систему аутентификации с JWT
5. Использование async/await для асинхронных операций
6. Типизация параметров функций
