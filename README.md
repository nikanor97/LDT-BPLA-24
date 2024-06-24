Репо для конкурса "Лидеры Цифровой Трансформации 2024".
Трек от компании Автономные технологии.

Структура репозитория:
1) backend - папка с сервисом бекенда (API) + скрипт запуска телеграм бота
2) frontend - папка с сервисом фронтенда (веб-интерфейс)
3) common - папка с утилитами для работы с очередями (RabbitMQ)
4) notebooks - папка с ноутбуками для экспериментов с моделями и данными
5) yolo-model - папка с модельным сервисом. В целевом виде этих сервисов запускается множество и они обрабатывают данные от сервиса backend в параллель.

Важно: телеграм бот уже запущен на стороннем сервере и он будет работать только с развернутым сервисом на нашей стороне.
http://autonomous-tech.dev-stand.com

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

Самая последняя модель - best-3.pt