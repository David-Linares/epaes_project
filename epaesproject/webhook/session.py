# -*- coding: utf-8 -*-
import datetime
import logging
import redis
from django.conf import settings
from django.db import connection
# from .api_connection import ApiConnection
# from .db_connection import DbConnection
# from .util import Util
# from .util import Util
logger = logging.getLogger(__name__)


class Session:

    def __init__(self):
        # self.util = Util()
        # self.db_conn = DbConnection()
        # self.api_conn = ApiConnection()
        self.rdb = redis.StrictRedis(host='localhost', port=6379)


