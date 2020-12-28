# CMA CGM line

from bs4 import BeautifulSoup as bs
import pandas as pd
import pendulum
import requests


from .base import ShippingContainer
from . import utils


class CMDUContainerBuilder(object):

    def __init__(self):
        self._instance = None


    def __call__(self, container, **_ignored):
        if not self._instance:
            self._instance = CMDUContainer(container)
        return self._instance


class CMDUContainer(ShippingContainer):
    
    def __init__(self, container_number):
        super().__init__(cn=container_number)
        self.shipping_line = "CMA CGM"
        
        self.url = "https://www.cma-cgm.com/ebusiness/tracking/search?SearchBy=Container&Reference={0}&search=Search".format(self.number)
        self.tracking_url = "https://www.cma-cgm.com/ebusiness/tracking/search?SearchBy=Container&Reference={0}&search=Search".format(self.number)

        
        self.updates = []
        self.df = pd.DataFrame()
        
        if self.number:
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.5",
                "Connection": "keep-alive",
                "Host": "www.cma-cgm.com",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
            }

            r = requests.get(self.url, headers=headers)
            self.soup = bs(r.content, "lxml")
            table = self.soup.find("table")
            rlocs = self.soup.find_all("span", {"class":"o-trackingnomap--place"})
            self._raw_locs = [rl.text for rl in rlocs]

            df = pd.read_html(str(table))[0]
            df = df.drop(["Unnamed: 1"], 1)

            self.updates = df.to_dict(orient="records")
            self.updates.reverse()
            self.format_updates()


    def format_updates(self):
        updates = []
        for u in self.updates:
            temp = {"location":"","vessel":"", "voyage":"", "movement": "", "mode": "","date":""}
            #temp = copy.deepcopy(self._update_template)
            for k,v in u.items():
                if k.lower() == "date":
                    temp_date  = v
                elif k.lower() == "moves":
                    temp["movement"] = v
                elif k.lower() == "vessel":
                    temp["vessel"] = v
                elif k.lower() == "location":
                    v = v.split("Accessible")[0].strip()
                    try:
                        full_loc = [l for l in self._raw_locs if v in l][0]
                    except IndexError:
                        full_loc = v
                    print (full_loc)
                    city, state, country = self.parse_location(full_loc)
                    temp["location"] = Place(city=city, subdivision=state, country=country)
                elif k.lower() == "voyage":
                    temp["voyage"] = v
            if temp["voyage"]:
                temp["mode"] = "VE"
            try: 
                temp["date"] = pendulum.from_format(temp_date, "ddd DD MMM YYYY HH:mm", tz=temp["location"].timezone).in_tz("UTC")
            except Exception as e:
                print (e)
            updates.append(temp)
        self.updates = updates
        self.df = utils.create_df(self.updates)


    def parse_location(self, raw_loc):
        city, state, country = None, None, None

        # it varies - 'COLOMBO', 'ST LOUIS, MO, US', 'LOUISVILLE, KY'

        pat_csc = re.compile("(.+),\s+(\D{2})\s*\((\D{2})\)")
        pat_cs = re.compile("(.+),\s+(\D{2})")
        pat_cc = re.compile("(.+)\s*\((\D{2})\)")
        
        
        if "," not in raw_loc:
            f = pat_cc.match(raw_loc)
            if not f:
                city = raw_loc
            else:
                city = f.group(1).strip()
                country = f.group(2).strip()
        else:
            f = pat_csc.match(raw_loc)
            if not f:
                f = pat_cs.match(raw_loc)
                if not f:
                   print ("unknown error - couldn't parse")
                else:
                    city = f.group(1).strip()
                    state = f.group(2).strip()
            else:
                city = f.group(1).strip()
                state = f.group(2).strip()
                country = f.group(3).strip()
        return city, state, country
 
