import json
from typing import Any

from loguru import logger

import settings
from common.rabbitmq.publisher import Publisher
from common.rabbitmq.sync_publisher import SyncPublisher
import pika


async def yolo_model_processor(data: dict, publisher: Publisher, main_db_manager: Any, **kwargs) -> None:
    """Обработчик данных из очереди to_yolo_model."""
    logger.info(f"RECEIVED: {data}")
    logger.info(f"kwargs keys: {kwargs.keys()}")

    # detector = ObjectDetectionProcessor(
    #     ckpt_path=settings.MODEL_CHECKPOINT_PATH / settings.MODEL_NAME,
    #     input_dir=settings.MODEL_INPUT_DATA_PATH,
    #     output_dir=settings.MODEL_OUTPUT_DATA_PATH,
    #     device=settings.MODEL_DEVICE,  #'cuda',  # или 'cpu'
    #     confidence_thresholds=settings.MODEL_CONFIDENCE_THRESHOLDS,
    # )
    detector: ObjectDetectionProcessor = kwargs["detector"]

    markup = detector.process_image(  # TODO убрать AWAIT если синхронный запуск
        image_path=str(settings.MEDIA_DIR / data["image_path"]),
        filename=str(settings.MEDIA_DIR / data["image_path"]),
        # model, str(settings.MEDIA_DIR / data["video_url"])
    )

    data_to_send = {
        "data": {
            "markup": str(markup) if markup is not None else {},
            "frame_id": data["frame_id"],
            "project_id": data["project_id"],
            # "frame_markup_id": data["frame_markup_id"],
        },
    }

    logger.info(f"SENDING data: {data_to_send}")

    if kwargs['asyncronous_publisher']:
        await publisher.publish(
            routing_key="from_yolo_model",
            exchange_name="FromModels",
            data=data_to_send,
            ensure=False,
        )
    else:
        kwargs['sync_publisher'].publish(
            routing_key="from_yolo_model",
            exchange_name="FromModels",
            data=data_to_send,
            mandatory=True  # Включаем mandatory для гарантии доставки
        )
    logger.info("Message sent")
    # logger.info(f"SENT message info: {message}")