import asyncio

from fastapi import FastAPI

import settings
import uvicorn
import uvloop

from src.server.amqp_processors import yolo_model_processor
from common.rabbitmq.amqp import Server as AMQPServer

from common.rabbitmq.connection_pool import ConnectionPool as AmqpConnectionPool
from common.rabbitmq.consumer import Consumer, Subscription
from common.rabbitmq.publisher import Publisher

from src.server.object_detection_processor import ObjectDetectionProcessor
# from src.server.object_detection_processor_async import ObjectDetectionProcessor


async def main(loop: asyncio.AbstractEventLoop) -> None:
    amqp_connection_pool = AmqpConnectionPool(
        login=settings.RABBIT_LOGIN,
        password=settings.RABBIT_PASSWORD,
        host=settings.RABBIT_HOST,
        port=settings.RABBIT_PORT,
        ssl=settings.RABBIT_SSL,
        # no_verify_ssl=True if settings.LOCAL_RUN else False,
        no_verify_ssl=True,
        # prefetch_count=settings.RABBIT_PREFETCH_COUNT,
    )
    #

    publisher = Publisher(
        connection_pool=amqp_connection_pool,
        # app_id=settings.SERVICE_NAME,
    )

    detector = ObjectDetectionProcessor(
        ckpt_path=settings.MODEL_CHECKPOINT_PATH / settings.MODEL_NAME,
        input_dir=settings.MODEL_INPUT_DATA_PATH,
        output_dir=settings.MODEL_OUTPUT_DATA_PATH,
        device=settings.MODEL_DEVICE,  # 'cuda',  # или 'cpu'
        confidence_thresholds=settings.MODEL_CONFIDENCE_THRESHOLDS,
    )

    amqp_server = AMQPServer(
        publisher=publisher,
        message_processors={"to_yolo_model": yolo_model_processor},
        detector=detector,
        asyncronous=False
    )

    subscriptions = [
        Subscription(
            queue_name="to_yolo_model",
            callback=amqp_server.process_incoming_message,
            routing_key="to_yolo_model",
            exchange_name="ToModels",
        ),
    ]

    consumer = Consumer(
        connection_pool=amqp_connection_pool,
        subscriptions=subscriptions,
    )

    app = FastAPI()
    app.add_event_handler("startup", consumer.start)

    config = uvicorn.Config(app, host="0.0.0.0", port=8345)

    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        app = loop.run_until_complete(main(loop))
    finally:
        loop.close()
