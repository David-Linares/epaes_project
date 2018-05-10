import logging
import redis
import subprocess

from django.conf import settings
# from .api_connection import ApiConnection
from .db_connection import DbConnection
# from .util import Util


class AudioManager:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # self.util = Util()
        # self.api_conn = ApiConnection()
        self.db_conn = DbConnection()
        self.rdb = redis.StrictRedis(host='localhost', port=6379)

