import asyncio

import uvicorn
import uvloop

from common.rabbitmq.consumer import Consumer
from common.rabbitmq.publisher import Publisher
from src.db.base_manager import run_migrations
# from internal_common.logging.logging import get_uvicorn_log_file, loguru_json_serializer
# from internal_common.rabbitmq import ConnectionPool as AmqpConnectionPool, Consumer
# from internal_common.cron.scheduler import Scheduler, Task
from src.db.main_db_manager import MainDbManager
# from supply.ingestors.generator.balnamoon import retrieve_balnamoon_generation
from common.rabbitmq.connection_pool import ConnectionPool as AmqpConnectionPool

import settings
# from supply.external_clients import MainExternalClient
from src.server.server import make_server_app
from src.server.amqp import Server as AMQPServer


async def main(loop: asyncio.AbstractEventLoop) -> None:
    # if not settings.LOCAL_RUN:
    #     logging.config.fileConfig(get_uvicorn_log_file())
    #     logger.remove()
    #     logger.add(loguru_json_serializer, level=settings.LOG_LEVEL, serialize=True)

    run_migrations()

    main_db_manager = MainDbManager(db_name_prefix=settings.DB_NAME_PREFIX)

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

    # executor = ProcessPoolExecutor(
    #     max_workers=1,
    # )

    # scheduler = Scheduler(
    #     [
    #         Task(
    #             settings.BALNAMOON_DATA_RETRIEVAL_CRON,
    #             retrieve_balnamoon_generation,
    #             [loop, executor, main_db_manager],
    #         )
    #     ]
    # )

    publisher = Publisher(
        connection_pool=amqp_connection_pool,
        # app_id=settings.SERVICE_NAME,
    )

    amqp_server = AMQPServer(
        main_db_manager=main_db_manager,
        publisher=publisher
    )
    #
    consumer = Consumer(
        connection_pool=amqp_connection_pool,
        subscriptions=amqp_server.subscriptions,
    )

    server_app = make_server_app(
        main_db_manager=main_db_manager,
        # authorization=not settings.LOCAL_RUN,
        # startup_events=[consumer.start, scheduler.start],
        startup_events=[consumer.start],
        shutdown_events=[
            amqp_connection_pool.close,
            main_db_manager.close,
            # main_external_client.close,
            # scheduler.stop,
            # executor.shutdown,
        ],
        publisher=publisher
    )

    # if not settings.LOCAL_RUN:
    #     config = uvicorn.Config(
    #         server_app,
    #         host="0.0.0.0",
    #         port=settings.APP_PORT,
    #         log_config=get_uvicorn_log_file(),
    #         use_colors=False,
    #     )
    # else:
    #     config = uvicorn.Config(server_app, host="0.0.0.0", port=settings.APP_PORT)

    config = uvicorn.Config(server_app, host="0.0.0.0", port=settings.APP_PORT)

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
