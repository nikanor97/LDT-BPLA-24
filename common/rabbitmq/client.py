from typing import Callable, Any, Awaitable, Coroutine, Optional

import aio_pika
import asyncio
from loguru import logger

import aiormq
from aio_pika.abc import AbstractConnection, AbstractChannel, AbstractQueue


class RabbitClient:
    connection: AbstractConnection
    channel: AbstractChannel
    callback_queue: AbstractQueue
    loop: asyncio.AbstractEventLoop

    def __init__(self):
        pass

    async def connect(self) -> 'ModelRpcClient':
        while True:
            try:
                self.connection = await aio_pika.connect(
                    host='rabbit',
                    port=5672,
                    login='rmuser',
                    password='rmpassword'
                )
                break
            except aiormq.exceptions.AMQPConnectionError:
                logger.info("Rabbit is not accessible yet. Waiting for 2 seconds")
                await asyncio.sleep(2)
        self.channel = await self.connection.channel()
        # self.callback_queue = await self.channel.declare_queue(exclusive=True)
        # await self.callback_queue.consume(self.on_response, no_ack=True)
        # return self

    async def publish(self, routing_key: str, body: bytes):
        # routing_key = "test_queue"

        # channel = await connection.channel()

        await self.channel.default_exchange.publish(
            aio_pika.Message(body=body), routing_key=routing_key,
        )

    async def consume(
        self,
        queue_name: str,
        callback: Callable,
        callback_args: Optional[list[Any]] = None,
        callback_kwargs: Optional[dict[str, Any]] = None
    ):
        # Will take no more than 10 messages in advance
        await self.channel.set_qos(prefetch_count=10)

        # Declaring queue
        queue = await self.channel.declare_queue(queue_name, auto_delete=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                await callback(await message, *callback_args, **callback_kwargs)
                # async with message.process():
                #     print(message.body)

                    # if queue.name in message.body.decode():
                    #     break
