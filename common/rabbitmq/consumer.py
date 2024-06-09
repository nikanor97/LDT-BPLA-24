import asyncio
from asyncio import AbstractEventLoop
from dataclasses import dataclass
from typing import Awaitable, Callable, Optional

import aio_pika
from aio_pika.abc import AbstractIncomingMessage
from aio_pika.exchange import ExchangeType
from loguru import logger

from common.rabbitmq.connection_pool import ConnectionPool


@dataclass
class Subscription:
    queue_name: str
    callback: Callable[[AbstractIncomingMessage], Awaitable[None]]
    routing_key: str = ""
    exchange_name: str = ""
    exchange_type = ExchangeType.DIRECT

    def __post_init__(self) -> None:
        if self.exchange_name == "":
            self.routing_key = self.queue_name


class Consumer:
    def __init__(
        self,
        connection_pool: ConnectionPool,
        subscriptions: list[Subscription],
    ) -> None:
        self._connection = connection_pool
        self._subscriptions = subscriptions

    def start(self, loop: Optional[AbstractEventLoop] = None) -> None:
        loop = loop or asyncio.get_running_loop()
        loop.create_task(self._start())

    async def _start(self) -> None:
        while True:
            try:
                logger.info("starting consuming")
                async with self._connection.channel_pool.acquire() as channel:
                    for subscription in self._subscriptions:
                        queue = await channel.declare_queue(name=subscription.queue_name, durable=True)
                        if subscription.exchange_name != "":
                            # if exchange is not default
                            exchange = await channel.declare_exchange(
                                name=subscription.exchange_name,
                                type=subscription.exchange_type,
                                durable=True,
                            )
                            await queue.bind(exchange, routing_key=subscription.routing_key)
                        await queue.consume(subscription.callback, no_ack=True)
                    return
            except aio_pika.pool.PoolInvalidStateError:
                return
            except:
                logger.exception("while consuming messages an exception occurred")
                await asyncio.sleep(5)
