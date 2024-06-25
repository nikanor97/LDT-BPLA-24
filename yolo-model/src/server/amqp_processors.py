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

    detector: ObjectDetectionProcessor = kwargs["detector"]

    markup = detector.process_image(  # TODO убрать AWAIT если синхронный запуск
        image_path=str(settings.MEDIA_DIR / data["image_path"]),
        filename=str(settings.MEDIA_DIR / data["image_path"]),
    )

    data_to_send = {
        "data": {
            "markup": str(markup) if markup is not None else {},
            "frame_id": data["frame_id"],
            "project_id": data["project_id"],
            "frames_in_content": data["frames_in_content"],
            "image_path": data["image_path"],
            "type": data["type"]
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
        # Настройка соединения с RabbitMQ
        credentials = pika.PlainCredentials('rmuser', 'rmpassword')
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbit', 5672, '/', credentials))
        channel = connection.channel()

        # Включаем подтверждение доставки сообщений
        channel.confirm_delivery()

        # Объявляем очередь
        channel.queue_declare(queue='to_yolo_model', durable=True)

        # Объявляем обменник
        exchange_name = "FromModels"
        channel.exchange_declare(exchange=exchange_name, exchange_type='direct', durable=True)

        sync_publisher = SyncPublisher(channel, exchange_name)

        sync_publisher.publish(
            routing_key="from_yolo_model",
            exchange_name="FromModels",
            data=data_to_send,
            mandatory=True  # Включаем mandatory для гарантии доставки
        )

    logger.info("Message sent")
