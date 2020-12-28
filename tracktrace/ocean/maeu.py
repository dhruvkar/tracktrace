# Maersk Line

from bs4 import BeautifulSoup as bs
import pendulum
import requests


from .base import ShippingContainer
from . import utils



class MAEUContainerBuilder(object):

    def __init__(self):
        self._instance = None


    def __call__(self, container, **_ignored):
        if not self._instance:
            self._instance = MAEUContainer(container)
        return self._instance


class MAEUContainer(object):

    def __init__(self, container_number):
        super().__init__(cn=container_number)
        self.shipping_line = "Maersk"

        self.url = "https://api.maerskline.com/track/{0}?operator=maeu"
