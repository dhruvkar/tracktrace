
# Hamburg SUD Line

from bs4 import BeautifulSoup as bs
import copy
import datetime
import pendulum
import requests

from .base import ShippingContainer
from . import utils


class SUDUContainerBuilder(object):

    def __init__(self):
        self._instance = None


    def __call__(self, container, **_ignored):
        if not self._instance:
            self._instance = SUDUContainer(container)
        return self._instance


class SUDUContainer(ShippingContainer):

    def __init__(self, container_number):
        super().__init__(cn=container_number)
        self.shipping_line = "Hamburg SUD"
        
        self.url = "https://www.hamburgsud-line.com/linerportal/pages/hsdg/tnt.xhtml?lang=en"
        self.post_url = "https://www.hamburgsud-line.com/linerportal/pages/hsdg/tnt.xhtml"
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Host': 'www.hamburgsud-line.com',
            'TE': 'Trailers',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
            }
 
        self.session = requests.session()
        self.session.headers.update(headers)

        r1 = self.session.get(self.url)
        s1 = bs(r1.content, "lxml")
        self.s1 = s1
        
        ins = s1.find_all("input")
        jvs = None
        for i in ins:
            if i.attrs["name"] == "javax.faces.ViewState":
                jvs = i.attrs["value"]

        now = pendulum.now()

        startdate = now.subtract(weeks=8).format("DD-MMM-YYYY") 
        enddate = now.add(weeks=2).format("DD-MMM-YYYY")

        
        self.payload = {
            'javax.faces.partial.ajax': 'true',
            'javax.faces.source': 'j_idt6:searchForm:j_idt8:search-submit',
            'javax.faces.partial.execute': 'j_idt6:searchForm',
            'javax.faces.partial.render': 'j_idt6:searchForm',
            'j_idt6:searchForm:j_idt8:search-submit': 'j_idt6:searchForm:j_idt8:search-submit',
            'j_idt6:searchForm': 'j_idt6:searchForm',
            'j_idt6:searchForm:j_idt8:inputReferences': self.number,
            'j_idt6:searchForm:j_idt8:inputDateFrom_input': startdate,
            'j_idt6:searchForm:j_idt8:inputDateTo_input': enddate,
            'javax.faces.ViewState': jvs,
            }

        # update headers for posting
        self.session.headers['Faces-Request'] = "partial/ajax"
        self.session.headers['Content-Type'] = "application/x-www-form-urlencoded; charset=UTF-8"
        self.session.headers['Accept'] = 'application/xml, text/xml, */*; q=0.01'

        r = self.session.post(self.post_url, data=self.payload)
        self.soup = bs(r.content, "lxml")
        self.parse_updates(self.soup)
         
    def parse_updates(self, soup):
        self.updates = []
        twrap = soup.find("div", {"class": "ui-datatable-tablewrapper"})
        table = twrap.find("table")
        rows = table.find_all("tr") 
        for row in rows:
            cells = row.find_all("td")
            temp = copy.deepcopy(self._update_template)
            if cells:
                try:
                    temp["date"] = pendulum.from_format(cells[0].text, "DD-MMM-YYYY HH:mm")
                except ValueError:
                    temp["date"] = ""
 
                temp["location"] = self._handle_location(cells[1].text)
                temp["movement"] = cells[2].text
                try:
                    if len(cells[3].contents) == 2:
                        p1 = cells[3].contents[0].text.strip()
                        p2 = cells[3].contents[1].text.strip()
                        temp["vessel"] = p1
                        temp["voyage"] = p2
                        temp["mode"] = "VE"
                    else:
                        temp["vessel"] = cells[3].text
                        if "truck" in cells[3].text.lower():
                            temp["mode"] = "TR"
                        elif "railway" in cells[3].text.lower():
                            temp["mode"] = "RA"
                        
                except Exception as e:
                    print (e)

                self.updates.append(temp)

    def _handle_location(self, raw_loc):
        splitlocs = raw_loc.split(" ")
        if len(splitlocs[-1].strip()) == 5:
            loc = splitlocs[-1].strip()
        else:
            loc = ""
        return loc


"""
class SUDUContainer(ShippingContainer):
        
    def __init__(self, container_number):
        super().__init__(cn=container_number)
        self.shipping_line = "Hamburg SUD"
        
        self.url = "https://www.hamburgsud-line.com/linerportal/pages/hsdg/tnt.xhtml?lang=en"
        self.tracking_url = "https://www.hamburgsud-line.com/linerportal/pages/hsdg/tnt.xhtml?lang=en"
        #self.post_url = "https://www.hamburgsud-line.com/linerportal/pages/hsdg/tnt.xhtml;jsessionid={0}"
        self.post_url = "https://www.hamburgsud-line.com/linerportal/pages/hsdg/tnt.xhtml"
      
        
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Host": "www.hamburgsud-line.com",
            "TE": "Trailers",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"
            }

        self.session = requests.session()
        self.session.headers.update(headers)
        r = self.session.get(self.url)
        self.soup = bs(r.content, "lxml")
    
        for cookie in self.session.cookies:
            if cookie.name == "JSESSIONID":
                self.post_url = self.post_url.format(cookie.value)
        if self.number:
            #self.search_container() 
            pass

    def search_container(self): 
        _today = datetime.datetime.combine(datetime.date.today(), datetime.time())
        today = pendulum.instance(_today)
        begin = today.subtract(days=60).format("DD-MMM-YYYY")
        end = today.add(days=12).format("DD-MMM-YYYY")
        
        inputs = self.soup.find_all("input")
        
        jvs = None

        for i in inputs:
            if i.attrs["name"] == "javax.faces.ViewState":
                jvs = i.attrs["value"]
        payload = {
            "javax.faces.partial.ajax": "true",
            "javax.faces.source":"j_idt7:searchForm:j_idt9:search-submit",
            "javax.faces.partial.execute":"j_idt7:searchForm",
            "javax.faces.partial.render":"j_idt7:searchForm",
            "j_idt7:searchForm:j_idt9:search-submit":"j_idt7:searchForm:j_idt9:search-submit",
            "j_idt7:searchForm":"j_idt7:searchForm",
            "j_idt7:searchForm:j_idt9:inputReferences": self.number,
            "j_idt7:searchForm:j_idt9:inputDateFrom_input": begin,
            "j_idt7:searchForm:j_idt9:inputDateTo_input": end,
            "javax.faces.ViewState": jvs
        }

        payload = {
            'javax.faces.partial.ajax': 'true',
            'javax.faces.source': 'j_idt6:searchForm:j_idt8:search-submit',
            'javax.faces.partial.execute': 'j_idt6:searchForm',
            'javax.faces.partial.render': 'j_idt6:searchForm',
            'j_idt6:searchForm:j_idt8:search-submit': 'j_idt6:searchForm:j_idt8:search-submit',
            'j_idt6:searchForm': 'j_idt6:searchForm',
            'j_idt6:searchForm:j_idt8:inputReferences': self.number,
            'j_idt6:searchForm:j_idt8:inputDateFrom_input': '24-Sep-2020',
            'j_idt6:searchForm:j_idt8:inputDateTo_input': '04-Dec-2020',
            'javax.faces.ViewState': jvs,
            }
        
        self.r = self.session.post(self.post_url, data=payload)
        self.soup = bs(self.r.content, "lxml")
        #self.parse_updates(self.soup)
        #self.df = utils.create_df(self.updates)
        
    
    def parse_updates(self, soup):
        self.updates = []
        twrap = soup.find("div", {"class": "ui-datatable-tablewrapper"})
        table = twrap.find("table")
        rows = table.find_all("tr") 
        for row in rows:
            cells = row.find_all("td")
            temp = copy.deepcopy(self._update_template)
            if cells:
                try:
                    temp["date"] = pendulum.from_format(cells[0].text, "DD-MMM-YYYY HH:mm")
                except ValueError:
                    temp["date"] = ""
 
                temp["location"] = self._handle_location(cells[1].text)
                temp["movement"] = cells[2].text
                try:
                    if len(cells[3].contents) == 2:
                        p1 = cells[3].contents[0].text.strip()
                        p2 = cells[3].contents[1].text.strip()
                        temp["vessel"] = p1
                        temp["voyage"] = p2
                        temp["mode"] = "VE"
                    else:
                        temp["vessel"] = cells[3].text
                        if "truck" in cells[3].text.lower():
                            temp["mode"] = "TR"
                        elif "railway" in cells[3].text.lower():
                            temp["mode"] = "RA"
                        
                except Exception as e:
                    print (e)

                self.updates.append(temp)

    def _handle_location(self, raw_loc):
        splitlocs = raw_loc.split(" ")
        if len(splitlocs[-1].strip()) == 5:
            loc = splitlocs[-1].strip()
        else:
            loc = ""
        return loc

"""
