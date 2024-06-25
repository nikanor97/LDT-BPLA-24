import asyncio

import uvloop

import settings
from common.rabbitmq.connection_pool import ConnectionPool as AmqpConnectionPool
from common.rabbitmq.publisher import Publisher
from src.db.main_db_manager import MainDbManager
from src.db.projects.models import VerificationTagBase
from src.server.constants import verification_tags
from src.server.users.endpoints import UsersEndpoints
from src.server.projects.endpoints import ProjectsEndpoints


async def init_db():
    main_db_manager = MainDbManager(db_name_prefix=settings.DB_NAME_PREFIX)

    amqp_connection_pool = AmqpConnectionPool(
        login=settings.RABBIT_LOGIN,
        password=settings.RABBIT_PASSWORD,
        host=settings.RABBIT_HOST,
        port=settings.RABBIT_PORT,
        ssl=settings.RABBIT_SSL,
        no_verify_ssl=True,
    )

    publisher = Publisher(
        connection_pool=amqp_connection_pool,
    )

    ue = UsersEndpoints(main_db_manager)
    pe = ProjectsEndpoints(main_db_manager, publisher)

    tags_base = []
    for groupname, tagnames in verification_tags.items():
        for tagname in tagnames:
            tag_base = VerificationTagBase(
                tagname=tagname[0],
                groupname=groupname
            )
            tags_base.append(tag_base)
    tags = await pe.create_verification_tags(tags_base)


if __name__ == "__main__":
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        app = loop.run_until_complete(init_db())
    finally:
        loop.close()
