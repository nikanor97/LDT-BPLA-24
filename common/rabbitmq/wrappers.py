from typing import Any, Awaitable, Callable, TypeVar

import ujson
from aio_pika.abc import AbstractIncomingMessage
from loguru import logger
from pydantic import parse_obj_as

T = TypeVar("T")


def amqp_callback_wrapper(
    message_parser: Callable[[AbstractIncomingMessage], T]
) -> Callable[[Callable[[Any, T], Awaitable[None]],], Callable[[Any, AbstractIncomingMessage], Awaitable[None]]]:
    def outer_wrapper(
        func: Callable[[Any, T], Awaitable[None]],
    ) -> Callable[[Any, AbstractIncomingMessage], Awaitable[None]]:
        async def inner_wrapper(self: Any, message: AbstractIncomingMessage) -> None:
            logger.info(f"start proceeding {func.__name__}")
            try:
                parsed_message = message_parser(message)
                await func(self, parsed_message)
            except:
                logger.exception(f"while proceeding {func.__name__} an exception occurred")
            logger.info(f"{func.__name__} proceeded successfully")

        return inner_wrapper

    return outer_wrapper


def parse_amqp_msg_to_pydantic(
    model: type[T],
) -> Callable[[AbstractIncomingMessage], T]:
    def wrapper(message: AbstractIncomingMessage) -> T:
        body = message.body.decode("utf-8")
        message_data = ujson.loads(body)
        return parse_obj_as(model, message_data)

    return wrapper
