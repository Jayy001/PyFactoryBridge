from requests.adapters import HTTPAdapter
from ssl import create_default_context
from urllib3 import Retry


class FactoryGameSSLAdapter(HTTPAdapter):
    def __init__(
        self,
        verify_ssl_chain_path: str,
        pool_connections: int = 10,
        pool_maxsize: int = 10,
        max_retries: Retry | int | None = 0,
        pool_block: bool = False,
    ) -> None:
        self.verify_ssl_chain_path = verify_ssl_chain_path
        super().__init__(pool_connections, pool_maxsize, max_retries, pool_block)

    def init_poolmanager(self, *args, **kwargs):
        context = create_default_context(cafile=self.verify_ssl_chain_path)
        context.check_hostname = False
        kwargs["ssl_context"] = context
        return super().init_poolmanager(*args, **kwargs, assert_hostname=False)
