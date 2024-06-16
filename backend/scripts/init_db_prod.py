import asyncio
import random
import uuid

import uvloop
from fastapi import UploadFile

import settings
from common.rabbitmq.connection_pool import ConnectionPool as AmqpConnectionPool
from common.rabbitmq.publisher import Publisher
from src.db.main_db_manager import MainDbManager
from src.db.projects.models import ProjectBase, UserRoleBase, VerificationTagBase, LabelBase
from src.server.constants import verification_tags
from src.server.projects.models import ProjectCreate, ContentMarkupCreate, FramesWithMarkupCreate, MarkupListCreate
from src.server.users.endpoints import UsersEndpoints
from src.server.projects.endpoints import ProjectsEndpoints
from src.server.users.models import UserCreate, UserLogin


lorem_ipsum = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed elit ligula, gravida sed hendrerit sed, congue ut justo. Pellentesque vel volutpat dolor. Vivamus vestibulum, arcu mattis sollicitudin luctus, nunc ante convallis elit, vel fringilla orci est at sapien. Etiam a ultricies turpis. Duis ac libero eget urna tincidunt scelerisque. Maecenas in elementum ipsum. In vitae lacus in ligula molestie porta nec id lectus. Proin ac purus feugiat, suscipit felis sed, convallis mi. Suspendisse potenti. Sed imperdiet bibendum mattis. Sed id elementum lectus, id suscipit libero. In hac habitasse platea dictumst. Proin eget tellus lobortis elit euismod tempus sit amet sed enim. Integer a euismod nunc. Vivamus consectetur sollicitudin lacus, et tristique metus semper in. Donec rhoncus aliquet quam ut semper. Proin congue, nibh quis suscipit placerat, est tellus egestas augue, non fermentum risus neque sit amet purus. Maecenas ultricies interdum sagittis. Suspendisse et neque erat. Vestibulum maximus, ante et cursus commodo, ipsum est mattis diam, vitae dignissim tellus ipsum molestie nibh. Sed vel odio consequat, rutrum massa non, tristique erat. Sed in pulvinar tortor. Aliquam et sodales ex. Vivamus urna leo, aliquam at felis eu, luctus pretium est. Fusce vitae ultrices diam, nec egestas elit. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Duis at volutpat magna. Duis vel blandit ex, et cursus odio. Nunc dictum porta accumsan. Aenean at sapien elit. Sed felis massa, molestie eu vehicula tincidunt, sodales at dolor. Nullam ut vulputate magna, sed consectetur leo. Vivamus vitae augue et erat tempus suscipit quis pellentesque augue. Quisque malesuada scelerisque mi, at sollicitudin ipsum condimentum eu. Duis fermentum tempor sollicitudin. Cras lacinia et erat in egestas. Aenean vitae neque nec odio accumsan porttitor. In hac habitasse platea dictumst. Nam vestibulum lobortis erat quis dignissim. Cras congue justo mi, id efficitur neque rutrum vitae. Nullam non eleifend magna, sed placerat purus. Donec bibendum purus malesuada risus tempor, vitae pellentesque purus faucibus. Donec nec nunc neque. Cras quis hendrerit tellus, posuere volutpat turpis. Sed et dolor sem. Praesent non dapibus est. Suspendisse et sagittis nisl. Duis posuere luctus consequat. Proin dignissim tempus felis ut semper. Vivamus mauris metus, efficitur dapibus interdum vitae, tempor vel velit. In tempus libero massa, sit amet porttitor nisi congue imperdiet. Vivamus in diam sed massa efficitur fermentum. Sed turpis justo, sagittis non volutpat eget, posuere quis lectus. Aliquam eget magna magna. Aenean nec nulla lacus."""
colors = ['#00C12B', '#510FAE', '#FF7400']
houses = [
    'Верейская 41',
    "Квартал Строгино",
    "Квартал Ивакино",
    "Польские Кварталы",
    "Квартал Марьино",
    "Новое Видное",
    "Пятницкие Луга",
    "Пригород Лесное",
    "Квартал Западный",
    "Рублевский Квартал",
]

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
