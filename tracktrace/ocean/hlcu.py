# Hapag Lloyd Line

import pendulum
import requests
from xml.etree import cElementTree as ctree


from .base import ShippingContainer
from . import utils

class HLCUContainerBuilder(object):

    def __init__(self):
        self._instance = None


    def __call__(self, container, **_ignored):
        if not self._instance:
            self._instance = HLCUContainer(container)
        return self._instance


class HLCUContainer(ShippingContainer):
 
    def __init__(self, container_number):
        super().__init__(cn=container_number)
        self.shipping_line = "HAPAG LLOYD"
        
        separated = utils.validate_container_number(number=self.number, separate=True)

        self.searchable_number = separated[0] + "  " + separated[1]

        self.url = "https://194.9.149.83/com/hlag/esb/services/mobile/MobileService"
        self.tracking_url = "https://www.hapag-lloyd.com/en/online-business/tracing/tracing-by-container.html?container={0}".format(self.number)
        
        self.updates = []
        self.get_updates()
        
        if self.updates:
            self.df = utils.create_df(self.updates)
            #self.to_json(self.updates)
            
            
 
    def get_updates(self):
        
        headers = {
            'Connection': 'Keep-Alive',
            'Content-Type': 'text/xml;charset=UTF-8',
            'Host': 'svc01.hlag.com',
            'SOAPAction': 'urn:traceByContainer',
            'User-Agent': '',
            }

        body = """
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:hls="http://esb.hlag.com/services/mobile/MobileService">
            <soapenv:Header/>
            <soapenv:Body>
                <hls:traceByContainerRequest>
                    <hls:language>en</hls:language>
                    <hls:deviceId>A;en_US;201905040328148420833643;</hls:deviceId>
                    <hls:appVersion>7.2.3</hls:appVersion>
                    <hls:frameworkVersion>a1.7.4</hls:frameworkVersion>
                    <hls:Container>
                        <hls:containerNumber>{0}</hls:containerNumber>
                    </hls:Container>
                </hls:traceByContainerRequest>
            </soapenv:Body>
            </soapenv:Envelope>""".format(self.searchable_number)

        self.r = requests.post(self.url, data=body, headers=headers, verify=False)
        self.root = ctree.fromstring(self.r.content)
        self.parse_updates()
        self.updates.reverse()
  

    def parse_updates(self, locate=True):
        if self.root:
            base = '{{http://esb.hlag.com/services/mobile/MobileService}}{0}' 
            
            # check if anything was returned
            found = [e for e in self.root.iter(tag=base.format("eGrpTracingData"))]
            
            if found:
                for e in self.root.iter(tag=base.format("eGrpTracingData")):

                    temp = {"location":"","vessel":"", "voyage":"", "movement": "", "mode": "","date":""}
                    _date = "0000-00-00"
                    _time = "00:00:00"
                    
                    for i in e.iter():
                       
                        if i.tag.endswith("businessLocode"):
                            temp["location"] = (i.text,)
                        elif i.tag.endswith("eLineVessel"):
                            temp["vessel"] = i[0].text
                        elif i.tag.endswith("eLineOperation"):
                            temp["movement"] = i[0].text
                        elif i.tag.endswith("plannedArrDate"):
                            _date = i.text
                        elif i.tag.endswith("plannedArrTime"):
                            _time = i.text.split(".")[0]
                        elif i.tag.endswith("eLineMot"):
                            temp["mode"] = i[0].text
                        elif i.tag.endswith("scheduleVoyageNo"):
                            temp["voyage"] = i.text

                    try:
                        pt = _date + " " + _time
                        # date/times are local to each place of activty. 
                        try:
                            rd = pendulum.from_format(pt, "YYYY-MM-DD HH:mm:ss", tz=temp["location"].timezone)
                        except AttributeError:
                            rd = pendulum.from_format(pt, "YYYY-MM-DD HH:mm:ss", tz="UTC")

                        # convert each time to UTC
                        utc = pendulum.timezone("UTC")
                        nrd = utc.convert(rd)
                        temp["date"] = nrd
                    except ValueError as ve:
                        pass

                    self.updates.append(temp)

        else:
            pass
