import json
from typing import Any

from aio_pika.abc import AbstractIncomingMessage
from loguru import logger
from common.rabbitmq.publisher import Publisher

# from src.db.main_db_manager import MainDbManager


class Server:
    def __init__(
        self,
        publisher: Publisher = None,  # For responses
        main_db_manager: Any = None,
        message_processors: dict = None,
        **kwargs,
    ) -> None:
        self._publisher = publisher
        self._message_processors = message_processors
        self._main_db_manager = main_db_manager
        self._kwargs = kwargs

    async def process_incoming_message(self, message: AbstractIncomingMessage) -> None:
        local_logger = logger.bind(
            headers=message.headers,
            routing_key=message.routing_key,
            exchane=message.exchange,
        )
        try:
            if message.routing_key is None:
                raise ValueError("routing key somehow is empty")

            local_logger.debug(f"Received message from {message.routing_key}")

            body = message.body.decode("utf-8")
            data = json.loads(body)["data"]

            local_logger.debug(
                f"Exchange: {message.exchange}, "
                f"Type: {message.routing_key}, "
            )

            if message.routing_key in self._message_processors:
                processor = self._message_processors[str(message.routing_key)]
                if self._kwargs['asyncronous_consumer']:
                    await processor(
                        data,
                        publisher=self._publisher,
                        main_db_manager=self._main_db_manager,
                        **self._kwargs,
                    )
                else:
                    processor(
                        data,
                        publisher=self._publisher,
                        main_db_manager=self._main_db_manager,
                        **self._kwargs,
                    )

        except:
            local_logger.exception("While proceeding message an exception occurred")
