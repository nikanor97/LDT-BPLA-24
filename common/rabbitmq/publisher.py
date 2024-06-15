from datetime import datetime
from typing import Any, Optional, Union

import ujson
from aio_pika import Message

from common.rabbitmq.connection_pool import ConnectionPool


class Publisher:
    def __init__(
        self,
        connection_pool: ConnectionPool,
        app_id: Optional[str] = None,
    ) -> None:
        self._connection = connection_pool
        self._app_id = app_id

    async def publish(
        self, routing_key: str, exchange_name: str, data: Union[list[Any], dict[str, Any]], ensure: bool = True
    ) -> Message:  # TODO: tests
        async with self._connection.channel_pool.acquire() as channel:
            exchange = await channel.get_exchange(name=exchange_name, ensure=ensure)
            message = Message(
                body=ujson.dumps(data).encode(),
                content_type="application/json",
                timestamp=datetime.utcnow(),
                app_id=self._app_id,
            )
            await exchange.publish(message=message, routing_key=routing_key)
            return message
