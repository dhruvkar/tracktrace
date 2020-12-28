# =======
# Imports
# =======

#from .models import Activity, Address, Shipment, Scac, SteamshipLine, Railroad, RailTerminal, EquipmentDepot, LocodeMain, LocodeStatus, LocodeFunction


from bs4 import BeautifulSoup as bs
import copy
import datetime
import feedparser
import os
import pandas as pd
import pendulum
import re
import requests
from timezonefinder import TimezoneFinder
import uuid

from xml.etree import cElementTree as ctree

from . import utils

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)



# countries and states as per ISO 3166 - https://www.iso.org/obp/ui/#search/code/
# cities as per UN LOCODES - https://www.unece.org/cefact/locode/service/location


## TEST DATA

# Hapag Lloyd - timezone given UTC
locode_test = ["BRPEC", "USNYC", "USSTL"]   #DONE

# MSC - timezone given
citystatecountry_test = ["HYDERABAD, TG, IN", "NHAVA SHEVA, MH, IN", "NEW YORK, NY, US", "EAST SAINT LOUIS, IL, US", "ST LOUIS, MO, US"] #DONE

# APL & CMACGM - times are local to the place
citycountry_test = ['NORFOLK, VA (US)', 'NHAVA SHEVA (IN)', 'HYDERABAD (IN)', 'JAIPUR (IN)', 'MUNDRA (IN)']

# Alianca & Hamburg SUD - times are local to the place
citylocode_test = ["St Louis USSTL", "Louisville USLUI", "Norfolk USORF", "Santos BRSSZ", "Vitoria BRVIX"]




container_factory = ContainerFactory()
container_factory.register_builder("MSCU", MSCUContainerBuilder())
container_factory.register_builder("HLCU", HLCUContainerBuilder())


##
# Need to add correct timezone parsing for updates
##


        
##
# NEED TO REVAMP
##
"""
class ShipmentLink(object):

    def __init__(self):
        self.home_url = "https://www.shipmentlink.com/"
        self.signin_url = "https://www.shipmentlink.com/tam1/jsp/TAM1_Login.jsp"
        self.captcha_url = "https://www.shipmentlink.com/servlet/TUF1_CaptchaUtils"
        self.post_url = "https://www.shipmentlink.com/servlet/TAM1_LoginController.do?action=TAM1_LoginController&lang=en"
        self.track_url = "https://www.shipmentlink.com/servlet/TDB1_CargoTracking.do"
        
        self.last_updated = pendulum.now(tz=("US/Central"))
        timezone = self.last_updated.tz.tzname(self.last_updated)
        self.last_updated_string = self.last_updated.format("DD-MMM-YYYY hh:MM A") + " " + timezone
        
        headers = {
            "Host": "www.shipmentlink.com",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cookie": ""
            }

        self.session = requests.session()
        self.session.headers.update(headers)
        self.r = self.session.get(self.home_url)
        for c in self.session.cookies:
            if c.name == "JSESSIONID":
                headers["Cookie"] = "JSESSIONID={}".format(c.value)

        self.session.headers.update(headers)
        self.soup = bs(self.r.content, "lxml")
        self.signed_in = False
        self.sign_in()
        self.r = self.session.get(self.track_url)


    def sign_in(self):
        while not self.is_signed_in(self.soup):
            self.sign_in_once()

    def sign_in_once(self):
        r = self.session.get(self.signin_url)
        self.soup = bs(r.content, "lxml")
        raw_sid = self.soup.find("input", {"name": "sID"})
        sid = raw_sid.attrs["value"]
        text = self.captcha()
        form_data = {
            "sID": sid,
            "id": "me@dkar.org",
            "password": "Grnite001",
            "captcha_input": text,
            "chkRmId": "on"
            }
        self.r = self.session.post(self.post_url, data=form_data)
        #r = self.session.get(self.home_url)
        self.soup = bs(self.r.content, "lxml")
        

    
    def is_signed_in(self, soup):

        divs = soup.find_all("div")
        for d in divs:
            if "Welcome" in d.text and "Kar" in d.text:
                self.signed_in = True
        return self.signed_in



    def captcha(self):
        r = self.session.get(self.captcha_url, stream=True)
        path = "captcha.jpg"
        temp = "temp.png"
        if r.status_code == 200:
            with open(path, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
        im = cv2.imread(path)
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 3)
        cv2.imwrite(temp, gray)
        image = Image.open(temp).convert("L")
        text = pytesseract.image_to_string(image, config='--psm 7')
        os.remove(path)
        os.remove(temp)
        return text.replace(" ", "")

    def track(self):
        pass
"""
