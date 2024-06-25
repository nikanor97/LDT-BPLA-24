import asyncio
from collections import defaultdict

import uvicorn
import uvloop
from fastapi import FastAPI

from common.rabbitmq.consumer import Consumer, Subscription
from common.rabbitmq.publisher import Publisher
from src.db.base_manager import run_migrations
from src.db.main_db_manager import MainDbManager
from common.rabbitmq.connection_pool import ConnectionPool as AmqpConnectionPool

import settings
from src.db.projects.models import VerificationTagBase
from src.server.amqp_processors import yolo_markup_processor
from src.server.constants import verification_tags
from src.server.projects.endpoints import ProjectsEndpoints
from src.server.server import make_server_app

from common.rabbitmq.amqp import Server as AMQPServer


def main() -> FastAPI:

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

    publisher = Publisher(
        connection_pool=amqp_connection_pool,
        # app_id=settings.SERVICE_NAME,
    )

    tags_base = []
    pe = ProjectsEndpoints(main_db_manager, publisher)
    for groupname, tagnames in verification_tags.items():
        for tagname in tagnames:
            tag_base = VerificationTagBase(
                tagname=tagname[0],
                groupname=groupname
            )
            tags_base.append(tag_base)
    # tags = await pe.create_verification_tags(tags_base)

    content_frames_counter: defaultdict = defaultdict(int)

    amqp_server = AMQPServer(
        publisher=publisher,
        main_db_manager=main_db_manager,
        message_processors={
            "from_yolo_model": yolo_markup_processor,
        },
        asyncronous_consumer=True,
        content_frames_counter=content_frames_counter
    )

    subscriptions = [
        Subscription(
            queue_name="from_yolo_model",
            callback=amqp_server.process_incoming_message,
            routing_key="from_yolo_model",
            exchange_name="FromModels",
        )
    ]

    consumer = Consumer(
        connection_pool=amqp_connection_pool,
        subscriptions=subscriptions,
    )

    server_app = make_server_app(
        main_db_manager=main_db_manager,
        startup_events=[consumer.start],
        shutdown_events=[
            amqp_connection_pool.close,
            main_db_manager.close,
        ],
        publisher=publisher
    )

    return server_app


app = main()
