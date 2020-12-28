# MSC Line

import feedparser
import pendulum
import requests


from .base import ShippingContainer
from . import utils



class MSCUContainerBuilder(object):

    def __init__(self):
        self._instance = None


    def __call__(self, container, **_ignored):
        self._instance = MSCUContainer(container)
        return self._instance




class MSCUContainer(ShippingContainer):
    # using RSS feeds 
    def __init__(self, container_number):
        super().__init__(cn=container_number)
        self.shipping_line = "MSC"
        
        
        self.url = "http://wcf.mscgva.ch/publicasmx/Tracking.asmx/GetRSSTrackingByContainerNumber?ContainerNumber={0}".format(self.number)
        self.tracking_url = "https://www.msc.com/track-a-shipment"
        self.xml = feedparser.parse(self.url)["entries"]
        
        self.last_updated = pendulum.now(tz=("US/Central"))
        timezone = self.last_updated.tz.tzname(self.last_updated)
        self.last_updated_string = self.last_updated.format("DD-MMM-YYYY hh:MM A") + " " + timezone
        
        self.updates = []
        self.get_update()

        if self.updates:
            #self.to_json(self.updates)
            self.df = utils.create_df(self.updates)
    
        

    def get_update(self, tz="UTC"):

        for x in self.xml:
            df = pd.read_html(str(x["summary"]))
            df = df[0].drop(1,1)
            data = dict(df.to_dict(orient="split")["data"])
            
            self.dat = data #temp var
            
            pb_date = pendulum.from_format(x["published"], "ddd, DD MMM YYYY HH:mm:ss ZZ")
            up_date = pendulum.from_format(x["updated"], "YYYY-MM-DD[T]HH:mm:ssZ")
            
            temp = copy.deepcopy(self._update_template)
            if pb_date == up_date:
                temp["date"] = up_date.in_tz(tz)
            else:
                temp["date"] = max(up_date, pb_date)

            try:
                temp["movement"] = data["Description"]
            except KeyError:
                temp["movement"] = ""
            
            rawlocs = data["Location"].split(",")

            if len(rawlocs) == 3:
                try:
                    city, subdivision, country = list(map(str.strip, data["Location"].split(",")))
                    
                    temp["location"] = (city, subdivision, country)
                except KeyError:
                    temp["location"] = "" 
            elif len(rawlocs) == 2:
                try:
                    city, country = list(map(str.strip, data["Location"].split(",")))
                    
                    temp["location"] = (city, country)
                except KeyError:
                    temp["location"] = ""
                
            try:
                temp["vessel"] = data["Vessel"]
            except KeyError:
                temp["vessel"] = ""

            try:
                temp["voyage"] = data["Voyage"]
            except KeyError:
                temp["voyage"] = ""

            if temp["voyage"]:
                temp["mode"] = "VE"

           

            self.updates.append(temp)

        return self.updates


"""
class MSCContainer(ShippingContainer):
    # scraping the site
    def __init__(self, container_number):
        
        super().__init__(cn=container_number)
        self.shipping_line = "MSC"
        self.updates = []
        self.session = requests.session()
        self.track_container(self.number)

    
    
    def login_mobile(self):
        # mobile app
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
            "Host": "www.mymsc.com",
            "User-Agent": ""
            }
        json = {
            "UserName": os.getenv("msc_username"),
            "Password": os.getenv("msc_password"),
            #"DeviceId": str(uuid.uuid1())
            "DeviceId":"340bf228-7f26-11ea-9dac-58a02321962f",
            "Device":"Device Maunfacturer: ONEPLUS, Device Model: ONEPLUS A3000, Device Name:  OnePlus3T"
            }
        url = "https://mymsc.com/mymsc.mobile.service/V3.6/authentication/Verifyuser/"
        self.session.headers.update(headers)
        self.r = self.session.post(url, json=json)
        try:
            self.r.json()
            self.logged_in = True
        except JSONDecodeError:
            pass

    def track_container(self, container):
        url = "https://www.msc.com/track-a-shipment?agencyPath=usa"
        #url = "https://www.msc.com/track-a-shipment?link={0}".format(str(uuid.uuid1()))
        form_data = {
            "__EVENTTARGET": "ctl00$ctl00$plcMain$plcMain$TrackSearch$hlkSearch",
            "__EVENTARGUMENT":"",
            "__LASTFOCUS":"",
            "lng": "en-GB",
            "__VIEWSTATEGENERATOR": "",
            "__EVENTVALIDATION": "",
            "ctl00$ctl00$Header$LanguageSelectionDropDown$ddlSelectLanguage": "en-GB",
            "ctl00$ctl00$Header$TrackSearch$txtBolSearch$TextField":"",
            "ctl00$ctl00$Header$ScheduleSearch$txtorigin$TextField": "",
            "ctl00$ctl00$Header$ScheduleSearch$hdnorigin":"",
            "ctl00$ctl00$Header$ScheduleSearch$txtdestination$TextField":"",
            "ctl00$ctl00$Header$ScheduleSearch$hdndestination":"",
            "ctl00$ctl00$Header$ScheduleSearch$txtDate": "{0}".format(pendulum.now().format("YYYY-MM-DD")),  # today's date in format 2020-04-15
            "ctl00$ctl00$Header$ScheduleSearch$ddlWeeksOut$DropDownField": "8",                             # how many weeks out, usually 8 is good
            "ctl00$ctl00$Header$SearchBox2$fldSearchText$TextField": "",
            "ctl00$ctl00$plcMain$plcMain$TrackSearch$txtBolSearch$TextField": "{0}".format(container),      #container number
            "ctl00$ctl00$plcMain$plcMain$hdnEmailAlertsId":"",
            "ctl00$ctl00$plcMain$plcMain$txtEmail$TextField":"",
            "ctl00$ctl00$plcMain$plcMain$hdnDetailsTrackingType":"",
            "ctl00$ctl00$plcMain$plcMain$hdnDetailsTrackingKey":"",
            "ctl00$ctl00$plcMain$plcMain$TrackingSendForm$fldRecipientName$TextField":"",
            "ctl00$ctl00$plcMain$plcMain$TrackingSendForm$fldRecipientEmail$TextField":"",
            "ctl00$ctl00$plcMain$plcMain$TrackingSendForm$fldSenderName$TextField":"",
            "ctl00$ctl00$plcMain$plcMain$TrackingSendForm$fldSenderEmail$TextField":"",
            "ctl00$ctl00$ucUpdateEmailPreferencesModal$txtEmail$TextField":"",
            "__VIEWSTATE": "",
            }
        
        headers =  {
            "Host": "www.msc.com",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
            "Sec-Fetch-Dest": "document",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Referer": "https://www.msc.com/track-a-shipment?agencyPath=usa",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
        }

        s = requests.session()
        r = s.get(url)

        soup = bs(r.content, "lxml")
        to_find = ["__EVENTARGUMENT", "__LASTFOCUS", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION", "__VIEWSTATE"]

        for tf in to_find:
            try:
                form_data[tf] = soup.find(id=tf).attrs["value"]
            except AttributeError as e:
                print (e)
                pass
        
        r = s.post(url, data=form_data)

        self._parse_response(r)

    
    def _parse_response(self, rr):
        soup = bs(rr.content,"lxml")

        tbs = soup.find_all("table")
        if len(tbs) == 2:
            df = pd.read_html(str(tbs[1]))
            datas = df[0].fillna("").to_dict("records")
            
            self.dat = datas

            for data in datas:
                temp = copy.deepcopy(self._update_template)
                try:
                    temp["movement"] = data["Description"]
                except KeyError:
                    temp["movement"] = ""
                
                rawlocs = data["Location"].split(",")

                if len(rawlocs) == 3:
                    try:
                        city, subdivision, country = list(map(str.strip, data["Location"].split(",")))
                        loc = Place(city=city, subdivision=subdivision, country=country)
                        temp["location"] = loc
                    except KeyError:
                        temp["location"] = "" 
                elif len(rawlocs) == 2:
                    try:
                        city, country = list(map(str.strip, data["Location"].split(",")))
                        loc = Place(city=city, country=country)
                        temp["location"] = loc
                    except KeyError:
                        temp["location"] = ""
                
                try:
                    temp["date"] = pendulum.from_format(data["Date"], "DD/MM/YYYY")
                except KeyError:
                    temp["date"] = ""

                try:
                    temp["vessel"] = data["Vessel"]
                except KeyError:
                    temp["vessel"] = ""

                try:
                    temp["voyage"] = data["Voyage"]
                except KeyError:
                    temp["voyage"] = ""

                if temp["voyage"]:
                    temp["mode"] = "VE"

                self.updates.append(temp)
"""
