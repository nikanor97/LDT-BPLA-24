import re
from logging.config import fileConfig
from loguru import logger

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy_utils import database_exists, create_database

from src.db.projects.models import ProjectsDataSQLModel
from src.db.users.models import UsersSQLModel
import settings

USE_TWOPHASE = False

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None
target_metadata = {
    "projects": ProjectsDataSQLModel.metadata,
    "users": UsersSQLModel.metadata,
}

db_names = list(target_metadata.keys())

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def construct_engine_url(db_name: str) -> str:
    return f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@" \
           f"{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.DB_NAME_PREFIX}{db_name}"


def create_db_if_not_exists(engine: Engine) -> None:
    if not database_exists(engine.url):
        db_full_name = str(engine.url).split('/')[-1]
        logger.info(f"Database with name {db_full_name} does not exist. It will be created now")
        create_database(engine.url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # url = config.get_main_option("sqlalchemy.url")
    # context.configure(
    #     url=url,
    #     target_metadata=target_metadata,
    #     literal_binds=True,
    #     dialect_opts={"paramstyle": "named"},
    # )
    #
    # with context.begin_transaction():
    #     context.run_migrations()

    engines = {}
    for name in re.split(r",\s*", db_names):
        engines[name] = rec = {}
        rec["url"] = context.config.get_section_option(name, "sqlalchemy.url")

    for name, rec in engines.items():
        logger.info("Migrating database %s" % name)
        file_ = "%s.sql" % name
        logger.info("Writing output to %s" % file_)
        with open(file_, "w") as buffer:
            context.configure(
                url=rec["url"],
                output_buffer=buffer,
                target_metadata=target_metadata.get(name),
                literal_binds=True,
                dialect_opts={"paramstyle": "named"},
                compare_type=True,
            )
            with context.begin_transaction():
                context.run_migrations(engine_name=name)


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # connectable = engine_from_config(
    #     config.get_section(config.config_ini_section, {}),
    #     prefix="sqlalchemy.",
    #     poolclass=pool.NullPool,
    # )
    #
    # with connectable.connect() as connection:
    #     context.configure(
    #         connection=connection, target_metadata=target_metadata
    #     )
    #
    #     with context.begin_transaction():
    #         context.run_migrations()

    engines = {}
    for name in db_names:
        engines[name] = rec = {}
        engine = create_engine(construct_engine_url(name))
        create_db_if_not_exists(engine)
        rec["engine"] = engine

    for name, rec in engines.items():
        engine = rec["engine"]
        rec["connection"] = conn = engine.connect()

        if USE_TWOPHASE:
            rec["transaction"] = conn.begin_twophase()
        else:
            rec["transaction"] = conn.begin()

    try:
        for name, rec in engines.items():
            logger.info("Migrating database %s" % name)
            context.configure(
                connection=rec["connection"],
                upgrade_token="%s_upgrades" % name,
                downgrade_token="%s_downgrades" % name,
                target_metadata=target_metadata.get(name),
                compare_type=True,  # Enables type comparison with old ones in migrations
            )
            context.run_migrations(engine_name=name)

        if USE_TWOPHASE:
            for rec in engines.values():
                rec["transaction"].prepare()

        for rec in engines.values():
            rec["transaction"].commit()
    except:
        for rec in engines.values():
            rec["transaction"].rollback()
        raise
    finally:
        for rec in engines.values():
            rec["connection"].close()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
