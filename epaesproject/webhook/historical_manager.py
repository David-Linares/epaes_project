import logging
import redis
from django.conf import settings
# from .api_connection import ApiConnection
from .db_connection import DbConnection
# from .util import Util


class HistoricalManager:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # self.util = Util()
        self.db_conn = DbConnection()
        # self.api_conn = ApiConnection()
        self.rdb = redis.StrictRedis(host='localhost', port=6379)

