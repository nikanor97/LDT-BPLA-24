from os import getenv
from pathlib import Path

from dotenv import load_dotenv


# Env possible paths in order that they should be called
env_paths = [Path(__file__).parent.parent / ".env", Path(__file__).parent / ".env"]
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)

DB_NAME_PREFIX = getenv("DB_NAME_PREFIX", "ldt_samolet_local_dev_")

# LOCAL_RUN = getenv("LOCAL_RUN", "False").lower() in ("true", "1", "t")
CONTAINER_RUN = getenv("CONTAINER_RUN", "False").lower() in ("true", "1", "t")

if CONTAINER_RUN:
    POSTGRES_HOST = getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = int(getenv("POSTGRES_PORT", 5432))
    RABBIT_HOST = getenv("RABBIT_HOST", "localhost")
    RABBIT_PORT = int(getenv("RABBIT_PORT", 5672))
    # BASE_DIR = Path(__file__).parent
else:
    POSTGRES_HOST = "localhost"
    POSTGRES_PORT = int(getenv("POSTGRES_PORT_ON_HOST", 5432))
    RABBIT_HOST = "localhost"
    RABBIT_PORT = int(getenv("RABBIT_PORT_ON_HOST", 5672))
    # BASE_DIR = Path(__file__).parent.parent
POSTGRES_USER = getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_MAX_CONNECTIONS = int(getenv("POSTGRES_MAX_CONNECTIONS", 5))

API_PREFIX = getenv("API_PREFIX", "/api/v1")
APP_PORT = int(getenv("BACKEND_PORT", 8090))

BASE_DIR = Path(__file__).parent
MEDIA_DIR = BASE_DIR / "media"
MEDIA_DIR.mkdir(exist_ok=True)
# Директория - вольюм для медиафайлов
(BASE_DIR.parent / "media").mkdir(exist_ok=True)

SECRET_KEY = getenv(
    "SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
)
HASHING_ALGORITHM = getenv("HASHING_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7))
REFRESH_TOKEN_EXPIRE_MINUTES = int(
    getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7 * 4)
)

CLIP_FRAME_STEP = int(getenv("CLIP_FRAME_STEP", 10))
CLIP_PORT = int(getenv("CLIP_PORT", 8080))
CLIP_HOST = getenv("CLIP_HOST", "clip")

CLASSIFIER_PORT = int(getenv("CLASSIFIER_PORT", 8080))
CLASSIFIER_HOST = getenv("CLASSIFIER_HOST", "classifier")


RABBIT_LOGIN = getenv("RABBIT_LOGIN", "login")
RABBIT_PASSWORD = getenv("RABBIT_PASSWORD", "password")
RABBIT_SSL = getenv("RABBIT_SSL", "False").lower() in ("true", "1", "t")

FRAME_STEP = int(getenv("FRAME_STEP", "5"))
VIDEO_FRAMING_WORKERS = int(getenv("VIDEO_FRAMING_WORKERS", 4))

TELEGRAM_TOKEN = getenv("TELEGRAM_TOKEN")
