from asyncio import AbstractEventLoop, get_event_loop
from typing import Optional

from aio_pika import connect_robust
from aio_pika.abc import AbstractChannel, AbstractRobustConnection
from aio_pika.pool import Pool


class ConnectionPool:
    def __init__(
        self,
        login: str,
        password: str,
        host: str,
        port: int,
        ssl: bool = True,
        no_verify_ssl: bool = False,
        prefetch_count: int = 1,
        connection_pool_size: int = 3,
        channel_pool_size: int = 10,
        loop: Optional[AbstractEventLoop] = None,
    ) -> None:
        self._login = login
        self._password = password
        self._host = host
        self._port = port
        self._ssl = ssl
        self._prefetch_count = prefetch_count

        loop = loop or get_event_loop()

        async def get_connection() -> AbstractRobustConnection:
            return await connect_robust(
                login=self._login,
                password=self._password,
                host=self._host,
                port=self._port,
                ssl=self._ssl,
                ssl_options={"no_verify_ssl": 1} if no_verify_ssl else None,
            )

        self._connection_pool: Pool[AbstractRobustConnection] = Pool(
            constructor=get_connection,
            max_size=connection_pool_size,
            loop=loop,
        )

        async def get_channel() -> AbstractChannel:
            async with self._connection_pool.acquire() as connection:
                channel = await connection.channel()
                await channel.set_qos(prefetch_count=self._prefetch_count)
                return channel

        self._channel_pool: Pool[AbstractChannel] = Pool(
            constructor=get_channel,
            max_size=channel_pool_size,
            loop=loop,
        )

    @property
    def channel_pool(self) -> Pool[AbstractChannel]:
        return self._channel_pool

    @property
    def connection_pool(self) -> Pool[AbstractRobustConnection]:
        return self._connection_pool

    async def close(self) -> None:
        await self._channel_pool.close()
        await self._connection_pool.close()
