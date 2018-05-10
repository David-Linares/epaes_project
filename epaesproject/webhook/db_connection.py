# -*- coding: utf-8 -*-
import logging
import redis
from django.conf import settings
from django.db import connection
# from .api_connection import ApiConnection
from .session import Session
# from .util import Util


class DbConnection:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # self.util = Util()
        # self.api_conn = ApiConnection()
        self.rdb = redis.StrictRedis(host='localhost', port=6379)
        self.session = Session()

