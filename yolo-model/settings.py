from os import getenv
from pathlib import Path

from dotenv import load_dotenv

# Env possible paths in order that they should be called
env_paths = [Path(__file__).parent.parent / ".env", Path(__file__).parent / ".env"]
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)

# LOCAL_RUN = getenv("LOCAL_RUN", "False").lower() in ("true", "1", "t")
CONTAINER_RUN = getenv("CONTAINER_RUN", "False").lower() in ("true", "1", "t")

if CONTAINER_RUN:
    RABBIT_HOST = getenv("RABBIT_HOST", "localhost")
    RABBIT_PORT = int(getenv("RABBIT_PORT", 5672))
    APP_PORT = int(getenv("BACKEND_PORT", 8090))
    BASE_DIR = Path(__file__).parent
else:
    RABBIT_HOST = "localhost"
    RABBIT_PORT = int(getenv("RABBIT_PORT_ON_HOST", 5672))
    APP_PORT = int(getenv("BACKEND_PORT_ON_HOST", 8090))
    BASE_DIR = Path(__file__).parent.parent

API_PREFIX = getenv("API_PREFIX", "/api/v1")

MEDIA_DIR = BASE_DIR / "media"

RABBIT_LOGIN = getenv("RABBIT_LOGIN", "login")
RABBIT_PASSWORD = getenv("RABBIT_PASSWORD", "password")
RABBIT_SSL = getenv("RABBIT_SSL", "False").lower() in ("true", "1", "t")

FRAME_STEP = int(getenv("FRAME_STEP", "5"))

MODEL_CHECKPOINT_PATH = BASE_DIR / "models"
MODEL_NAME = getenv("MODEL_NAME")
MODEL_INPUT_DATA_PATH = BASE_DIR / "data" / "input"
MODEL_OUTPUT_DATA_PATH = BASE_DIR / "data" / "output"
MODEL_DEVICE = getenv("MODEL_DEVICE")
MODEL_CONFIDENCE_THRESHOLDS = {
    0: 0.5,
    1: 0.3,
    2: 0.3,
    3: 0.3,
    4: 0.3,
}