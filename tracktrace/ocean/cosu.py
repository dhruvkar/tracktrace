# COSCO Line

import decimal
import pendulum
import time

from bs4 import BeautifulSoup as bs
import requests

from .base import ShippingContainer
from . import utils


class COSUContainerBuilder(object):

    def __init__(self):
        self._instance = None


    def __call__(self, container, **_ignored):
        if not self._instance:
            self._instance = COSUContainer(container)
        return self._instance


class COSUContainer(ShippingContainer):

    def __init__(self, container_number):

        super().__init__(cn=container_number)
        self.shipping_line = "COSCO"

        separated = utils.validate_container_number(number=self.number, separate=True)

        self.searchable_number = separated[0] + "  " + separated[1]

        self.url = " https://elines.coscoshipping.com/ebtracking/public/containers/{0}?timestamp={1}".format(self.number, "{0}")
        self.tracking_url = "https://elines.coscoshipping.com/ebusiness/cargoTracking?trackingType=CONTAINER&number={0}".format(self.number)

        self.updates = []
        self.get_updates()


    def get_updates(self, tz="UTC"):
        s = requests.session()
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Host": "elines.coscoshipping.com",
            "language": "en_US",
            "Referer": self.tracking_url,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "sys": "eb",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            }

        s.headers.update(headers)
        ts = str(float(round(decimal.Decimal(time.time()),3))).replace(".","")
        r = s.get(self.url.format(ts))
        j = r.json()

        updates = j['data']["content"]["containers"][0]
    
        return updates


    def parse_updates(self, updates):
        pass
