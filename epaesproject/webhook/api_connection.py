import logging
import requests
from django.conf import settings
from .util import Util


class ApiConnection:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.util = Util()

