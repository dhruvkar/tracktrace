# ONE Line

from bs4 import BeautifulSoup as bs
import pendulum
import requests

from .base import ShippingContainer
from . import utils


class ONEYContainerBuilder(object):
    
    def __init__(self):
        self.instance = None


    def __call__(self, container, **ignored):
        self._instance = ONEYContainer(container)
        return self._instance



class ONEYContainer(ShippingContainer):

    def __init__(self, container_number):

        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'DEFAULT:!DH'

        super().__init__(cn=container_number)
        self.shipping_line = "ONE"

        self.url =  "https://ecomm.one-line.com/ecom/CUP_HOM_3301GS.do"
        self.last_updated = pendulum.now(tz=("US/Central"))
        self.session = requests.session()
        headers = {
            'Host': 'ecomm.one-line.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }

        
        self.session.headers.update(headers)


        

    def get_update(self):
        r = self.session.get(self.url)
        data1 =  {'f_cmd': '122', 'cust_cd': '', 'cntr_no': self.number, 'search_type': 'C'}
        r = self.session.post(self.url, data=data1)
        
        try:
            j = r.json()
            copNo = j['list'][0]['copNo']
            bkgNo = j['list'][0]['bkgNo']
            data2 = {'f_cmd': '125', 'cntr_no': self.number, 'bkg_no': bkgNo, 'cop_no': copNo,}
            r = self.session.post(self.url, data=data2)
            return r
        except Exception as e:
            print (e)


    def parse_update(self,update):
        # date, movement, location, vessel, voyage, 
        pass
