import json
from typing import Any

from loguru import logger

import settings
from common.rabbitmq.publisher import Publisher
import pika


class SyncPublisher:
    def __init__(self, channel, exchange):
        self.channel = channel
        self.exchange = exchange

    def publish(self, routing_key, exchange_name, data, mandatory=False):
        self.channel.basic_publish(
            exchange=exchange_name,
            routing_key=routing_key,
            body=json.dumps(data),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
            ),
            mandatory=mandatory
        )


def yolo_model_processor(data: dict, publisher: Publisher, main_db_manager: Any, **kwargs) -> None:
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

    # message = await publisher.publish(
    #     routing_key="from_yolo_model",
    #     exchange_name="FromModels",
    #     data=data_to_send,
    #     ensure=False,
    # )

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

    publisher = SyncPublisher(channel, exchange_name)

    publisher.publish(
        routing_key="from_yolo_model",
        exchange_name="FromModels",
        data=data_to_send,
        mandatory=True  # Включаем mandatory для гарантии доставки
    )
    logger.info("Message sent")
    # logger.info(f"SENT message info: {message}")