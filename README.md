# Репо для конкурса "Лидеры Цифровой Трансформации 2024".
Трек от компании Автономные Технологии.

## Структура репозитория:
1) backend - директория с сервисом бекенда (API) + скрипт запуска телеграм бота
2) frontend - директория с сервисом фронтенда (веб-интерфейс)
3) common - директория с утилитами для работы с очередями (RabbitMQ)
4) notebooks - директория с ноутбуками для экспериментов с моделями и данными
5) yolo-model - директория с модельным сервисом. В целевом виде этих сервисов запускается множество и они обрабатывают данные от сервиса backend в параллель.

### Подробно о структуре директорий:
<details>
<summary>backend</summary>

- alembic - миграции для базы данных
- main - код для запуска сервиса бекенда
- notebooks - Jupyter ноутбуки для экспериментов
- scripts - скрипты для наполнения базы тестовыми данными
- src - исходники сервиса
  - db - слой для работы с базой данных
    - projects - работа с проектами
      - db_manager.py - менеджер для работы с базой данных проектов
      - models.py - модели в БД проектов
    - users - работа с пользователями
      - db_manager.py - менеджер для работы с базой данных пользователей
      - models.py - модели в БД пользователей
    - base_manager.py - обвязка для работы с БД
    - common_sql_manager.py - общие методы для работы с БД
    - exceptions.py - исключения
    - main_db_manager.py - основной менеджер для работы с БД
    - mixins.py - миксины для моделей
  - server - слой для работы с веб-сервером
    - projects
      - endpoints.py - эндпоинты для работы с проектами
      - models.py - серверные модели (requests and responses)
      - router.py - роутер для проектов
      - video_utils.py - утилиты для работы с видео
    - users
      - endpoints.py - эндпоинты для работы с пользователями
      - models.py - серверные модели (requests and responses)
      - router.py - роутер для пользователей
    - amqp_processor.py - обработчики сообщений из очереди
    - auth.py - аутентификация
    - auth_utils.py - утилиты для аутентификации
    - common.py - обертки для ответов сервера
    - constants.py - константы
    - server.py - класс с сервером FastAPI
    - telegram_bot.py - имплементация бота для телеграмма
- .pre-commit-config.yaml - конфиг для pre-commit
- alembic.ini - конфиг для alembic
- Dockerfile - Dockerfile для сервиса бекенда
- poetry.lock - лок файл для poetry
- pyproject.toml - пакеты для poetry
- settings.py - настройки сервиса
</details>

<details>
<summary>common</summary>

- rabbitmq - обертка для работы с RabbitMQ
  - amqp.py - обертка для процессора входящих сообщений
  - client.py - обертка для клиента RabbitMQ
  - connection_pool.py - обертка для пула соединений с RabbitMQ
  - consumer.py - обертка для консьюмера RabbitMQ
  - publisher.py - асинхронная обертка для продюсера RabbitMQ
  - sync_publisher.py - синхронная обертка для продюсера RabbitMQ
  - wrappers.py - прочие обертки для работы с RabbitMQ

</details>

<details>
<summary>yolo-model</summary>

- main - код для запуска модельного сервиса
- models - модели
  - best-1.pt - наша первая попытка
  - best_2.pt - наша вторая попытка
  - best-3.pt - наша третья попытка (лучшая модель)
- src - исходники сервиса
  - server - код модельного сервиса
    - amqp_processor.py - обработчики сообщений из очереди
    - object_detection_processor.py - синхронный детектор объектов
    - object_detection_processor_async.py - асинхронный детектор объектов
- Dockerfile - Dockerfile для запуска модельного сервиса на GPU
- Dockerfile-cpu - Dockerfile для запуска модельного сервиса на CPU
- poetry.lock - лок файл для poetry
- pyproject.toml - пакеты для poetry
- settings.py - настройки сервиса

</details>

## Телеграм бот
Важно: телеграм бот уже запущен на стороннем сервере и он будет работать только с развернутым сервисом на нашей стороне.
http://autonomous-tech.dev-stand.com

## Deployment
Для запуска сервиса у себя локально, нужно воспользоваться docker-compose файлом, который находится в корне репозитория.

Также, важно не забыть перед запуском сервиса подложить .env файл примерно следующего содержания

```bash
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="superpassword"
POSTGRES_HOST="db"
POSTGRES_PORT="5432"
POSTGRES_PORT_ON_HOST="5422"
DB_NAME_PREFIX="ldt_bpla_dev_"

BACKEND_HOST="backend"
BACKEND_PORT="8000"
BACKEND_PORT_ON_HOST="6035"

FRONTEND_PORT="80"
FRONTEND_PORT_ON_HOST="7035"

RABBIT_HOST="rabbit"
RABBIT_PORT="5672"
RABBIT_PORT_ON_HOST="5679"
RABBIT_UI_PORT="15672"
RABBIT_UI_PORT_ON_HOST="15679"
RABBIT_LOGIN="rmuser"
RABBIT_PASSWORD="superpassword"
RABBIT_SSL="false"

COMPOSE_PROJECT_NAME=ldt_bpla_local_dev

CONTAINER_RUN="true"

GUNICORN_WORKERS=4

MODEL_NAME="best-3.pt"
MODEL_DEVICE="cuda"

VIDEO_FRAMING_WORKERS=8
FRAME_STEP=1
```

## Модели
Самая последняя модель - best-3.pt (находится в директории yolo-model/models)