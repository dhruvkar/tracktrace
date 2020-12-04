#!/usr/bin/env python

import json
from json import JSONDecodeError
import os
import pendulum
import random
import requests
import time
import uuid
from bs4 import BeautifulSoup as bs


from . import utils
from . import misc
from .places import Place


from dotenv import load_dotenv
load_dotenv(".env")


class CSX(object):

    def __init__(self, terminal=None):
        self.session = requests.session()
        self.post_url = "https://api.csx.com/shipcsx-ship/v1//shipments/search"
        self.terminals_url = "https://api.csx.com/shipcsx-main/v1//terminals"
        headers = {
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.5",
                "Connection": "keep-alive",
                "Content-Type":"application/json",
                "Host":"api.csx.com",
                "Origin":"https://next.shipcsx.com",
                "Referer": "https://next.shipcsx.com/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
                "X-APIKey": "XBhZFoja3TM9BBFMVSFKIPbwtPuxJ7q5",
                }
        self.session.headers.update(headers)

   
    def get_terminals(self):
        r = self.session.get(self.terminals_url)
        if r.ok:
            return r.json()
        else:
            return None

    def search_container(self, container, reference_number=None):
        self.container = utils.validate_container_number(container, separate=True)
        self.reference_number = reference_number
        
        json_data = [{
            "terminal":{
                "city":"EAST ST LOUIS",
                "fsac":"40570",
                "liftFlag":"true",
                "name":"East St Louis",
                "scac":"CSXT",
                "state":"IL",
                "timezoneID": "America/Chicago",
            },
            "shipmentData":[{
                "equipmentID":{"equipmentInitial":"{0}".format(self.container[0]),"equipmentNumber":"{0}".format(self.container[1][:-1])},
                "referenceNumber":"{0}".format(self.reference_number)
                }]
        }]

        r = self.session.post(self.post_url, json=json_data)
        res = self.parse_response(r.json()) 
        return res

    def parse_response(self, json):
        d = {
            "found": False,
            "last_event_code": "",
            "last_event_desc": "",
            "last_event_time": "",
            "last_event_location": "",
            "current_status": "",
            "etg": "",
            "grounded": False,
            "ground_date": "",
            }
      
        if json["shipments"]:
            d["found"] = True
           
            try:
                status = json["shipments"][0]["shipmentStatus"].lower()
                d["current_status"] = status
                if status.lower() == "notified":
                    d["grounded"] = True
                    try:
                        # only available if grounded
                        gd = json["shipments"][0]["premise"]["notifiedDate"]
                        d["ground_date"] = pendulum.from_format(gd, "YYYY-MM-DD")
                        
                        lfd = json["shipments"][0]["premise"]["lastFreeDate"]
                        d["last_free_date"] = pendulum.from_format(lfd, "YYYY-MM-DD")
                    except IndexError as e:
                        print (e)
                        pass
                    except KeyError as e:
                        print (e)
                        pass
            except IndexError as e:
                print (e)
                pass
            except KeyError as e:
                print (e)
                pass

            try:
                retg = json["shipments"][0]["tripPlan"]["updatedEtn"].replace("Z", "")
                d["etg"] = pendulum.from_format(retg, "YYYY-MM-DDTHH:mm:ss")
            except IndexError:
                pass
            except KeyError as e:
                print (e)
                pass
            
            try:
                lastevent = json["shipments"][0]["lastReportedEvent"]
                rd = lastevent["actualDateTime"].replace("Z", "")
                d["last_event_code"] = lastevent["eventCode"]
                d["last_event_desc"] = lastevent["eventTypeDescription"]
                d["last_event_time"] = pendulum.from_format(rd, "YYYY-MM-DDTHH:mm:ss")
                d["last_event_location"] = lastevent["city"] + ", " + lastevent["state"]

            except KeyError as e:
                print (e)
                pass
            
        return d

    

class NorfolkSouthern(object):
    
    def __init__(self):
        self.session = requests.session()
        self.username = os.getenv("norfolksouthern_username")
        self.password = os.getenv("norfolksouthern_password")
        self.event_codes = misc.NORFOLK_SOUTHERN_EVENT_CODES
        loggedin = self.login()
        
        
        
    def login(self):
        url1 = "https://accessns.nscorp.com/"                                   # sets cookies
        url2 = "https://accessns.nscorp.com/accessNS/rest/version?_dc={0}"      # format with set_timestamp(). Sets JSESSIONID cookie
        url3 = "https://accessns.nscorp.com/accessNS/rest/auth/v3/login"        # post creds to login
        headers1 = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.5",
                "Connection": "keep-alive",
                "DNT": "1",
                "Host": "accessns.nscorp.com",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
                }
        headers2 = {
            "Accept": "*/*",
            "requestUUID": self.set_uuid(),
            "Referer": "https://accessns.nscorp.com/accessNS/nextgen/",
            }

        headers3 = { 
            "requestUUID": self.set_uuid(),
            "Content-Type": "application/json",
            "Origin": "https://accessns.nscorp.com",
            }

        self.session.headers.update(headers1)
        r1 = self.session.get(url1)
        
        self.session.headers.update(headers2)
        r2  = self.session.get(url2.format(self.set_timestamp))
        
        self.session.headers.update(headers3)
        r3 = self.session.post(url3, json={"id":"{0}".format(self.username),"pwd":"{0}".format(self.password)})
        if r3.json()["message"] == "Success":
            self.session.headers.update({"CSRFTOKEN": r3.json()["result"]["token"]})
            return True
        else:
            return False


    def search_container(self, cont):
        container = utils.validate_container_number(cont)
        self.last_searched = container
        url = "https://accessns.nscorp.com/accessNS/rest/backend-v2/Services/services/quicksearch/v3/carUnitsInfoSearch"
        initial = container[:4]
        number = container[4:][:-1]

        data = {
            "applicationName": "QS",
            "createTimestamp": "{0}".format(self.set_timestamp()),
            "createUserId": "{0}".format(self.username.upper()),
            "extnSchema": "ACCESSNS",
            "favouriteData": "{0}".format(container),
            "favouriteHistoryFlag": "H",
            "favouriteName": "Type: Quick Dray{0} {1}".format(container, pendulum.now().format("M/D/YYYY")),
            "searchType": "Track and Trace",
            "updateTimestamp": "{0}".format(self.set_timestamp()),
            "updateUserId": "{0}".format(self.username.upper()),
            }
    
        self.session.headers.update({"requestUUID":self.set_uuid()})
        r = self.session.post(url, json=data)
        if r.ok:
            d = self.parse_response(r.json())
            return d
            
           
    def parse_response(self, json):
        d = {
            "found": False,
            "last_event_code": "",
            "last_event_desc": "",
            "last_event_time": "",
            "last_event_location": "",
            "etg": "",
            }

        if json["result"]["drayUnits"]: # or if r.json()["result"]["notFound"]
            res = json["result"]["drayUnits"][0]
            
            d["found"] = True
            
            try:
                d["last_event_code"] = res["lastEvent"]
            except KeyError:
                pass

            try:
                d["last_event_desc"] = self.event_codes[res["lastEvent"]]
            except KeyError:
                pass

            try:
                d["last_event_time"] = pendulum.from_format(res["eventTime"], "M/D/YYYY hh:mm A", tz="America/New_York")
            except KeyError:
                pass
            except ValueError:
                pass

            try:
                d["last_event_location"] = res["location"]
            except KeyError:
                pass

            try:
                d["etg"] = pendulum.from_format(res["etg"], "M/D/YYYY hh:mm A", tz="America/New_York")
            except KeyError:
                pass
            except ValueError:
                pass

        return d


    def set_timestamp(self):
        return str(round(time.time(), 3)).replace(".","")

    def set_uuid(self):
        return str(uuid.uuid4())




class UnionPacific(object):

    def __init__(self):
         #to account for weak security on Union Pacific's website
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'DEFAULT:!DH'
        
        self.session = requests.session()
        self.username = os.getenv("unionpacific_username")
        self.password = os.getenv("unionpacific_password")
        self.login()


    def login(self):
        headers0 = {
            "Host": "www.up.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            }

        self.session.headers.update(headers0)

        r = self.session.get("https://www.up.com/index.htm")
        
        headers1 = {
                "Host": "c02.my.uprr.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "https://www.up.com",
                "Connection": "keep-alive",
                "Referer": "https://www.up.com/index.htm",
                }
        
        self.session.headers.update(headers1)

        url1 = "https://c02.my.uprr.com/admin/login.fcc"

        form_data1 = {
                "target": "https://c02.my.uprr.com/myuprr/ptl/secure/",
                "SMAUTHREASON": "0",
                "TYPE": "33554433",
                "USER": os.getenv("unionpacific_username"),
                "PASSWORD": os.getenv("unionpacific_password"),
                }

        r = self.session.post(url1, data=form_data1)

    """
    def search_container(self, container_number):
        
        #Using Equipment Track and Trace. EOL August 3, 2020
        

        if type(container_number) == list:
            cn = ""
            for x in container_number:
                nc =  utils.validate_container_number(x)
                cn += nc[:-1]+"\n"
        elif type(container_number) == str:
            cn = utils.validate_container_number(container_number)
            cn = cn[:-1]
        else:
            print ("invalid container number")

        r = self.session.get("https://c02.my.uprr.com/wet_jboss/secure/jas/index")
        
        post_url = "https://c02.my.uprr.com/wet_jboss/secure/jas/index?wicket:interface=:0:indexPageForm:indexPanel:indexForm:traceGroupBox:traceButton::IActivePageBehaviorListener:1:&wicket:ignoreIfNotActive=true&random={0}".format(random.random())
        form_data = {
          "id6_hf_0":"",
          "indexPanel:indexForm:traceGroupBox:tracePanel:traceForm:traceTabSet:newTraceTab:newTracePanel:frmNewTraceTab:equipIdsTextArea":"{0}".format(cn),
          "indexPanel:indexForm:traceGroupBox:tracePanel:traceForm:traceTabSet:commonTab:commonTabContent:traceDropDown":"default",
          "indexPanel:indexForm:traceGroupBox:traceButton":"1"
        }

        r = self.session.post(post_url, data=form_data)
        self.soup = bs(r.content, "lxml")
        result = self.soup.find(id="defaultTraceResultsGrid")

        bodies = result.find_all("tbody")
        if bodies:
            tbody = bodies[0]
        res = self._parse_tbody(tbody)
        return res
    """


    def search_container(self, container_number):
        """
        using the new Track Shipments
        """
        now = pendulum.now()

        u = "https://c02.my.uprr.com/services/customer-integration/shipping/track-shipments/1.1"
        j = json.dumps({"equipmentIds":["{0}".format(container_number[:-1])]})

        h = {
            "Accept": "application/json, text/plain, */*", 
            "web-tracking-date": "{0}".format(now.format("ddd MMM DD YYYY")),
            "web-tracking-id": "{0}".format(os.getenv("unionpacific_tracking_id")),
            "Content-Type": "application/json"
            }
        self.session.headers.update(h)
        
        r = self.session.post(u,j)
        self.r_ = r
        if r.ok:
            try:
                d = self.parse_response(r.json())
                return d
            except JSONDecodeError:
                return r
        else:
            return r


    def parse_response(self, json):
        d = {
            "found": False,
            "last_event_code": "",
            "last_event_desc": "",
            "last_event_time": "",
            "last_event_location": "",
            "etg": "",
            }

        if isinstance(json, list):
            r = json[0]
        else:
            r = json

        events_found = False

        if r["equipment"]["isIntermodal"]:
        
            try:
                x = r["events"]
                events_found = True
            except KeyError:
                pass

            d["found"] = True
            
            if events_found:
                for e in r['events']:
                    try:
                        if e["isCurrentEvent"] and e["eventDescription"].lower() != "estimated time of grounding":
                            d["last_event_desc"] = e["eventDescription"]
                            ts, tz = e["eventTime"], e["timezone"]
                            d["last_event_time"] = pendulum.from_format(ts, "YYYY-MM-DD HH:mm:ss", tz=tz)
                            d["last_event_location"] = e["locationDetails"]["address"]["city"] + ", " + e["locationDetails"]["address"]["state"] + ", US"
                    except KeyError as e:
                        pass
                for e in r["events"]:
                    try:
                        if e["eventDescription"].lower() == "estimated time of grounding":
                            ts_etg, tz_etg = e["eventTime"], e["timezone"]
                            d["etg"] = pendulum.from_format(ts_etg, "YYYY-MM-DD HH:mm:ss", tz=tz_etg)
                    except KeyError:
                        pass
            
        return d

                

    def _parse_tbody(self, tbody):
        d = {
            "found": False,
            "last_event_code": "",
            "last_event_desc": "",
            "last_event_time": "",
            "last_event_location": "",
            "etg": "",
            }
        
        spans = tbody.find_all("span")
        
        check_found = []
        for span in spans:
            try:
                if "invalidMessage" in span.attrs["class"]:
                    check_found.append(False)
                else:
                    check_found.append(True)
            except KeyError:
                pass

        if all(check_found):
            tds = tbody.find_all("td")
            d["found"] = True
            try:
                retg = tbody.find(id="etaDateTime").text
                d["etg"] = pendulum.from_format(retg, "M/D/YY HH:mm", tz="America/Chicago")
            except ValueError:
                pass
            except AttributeError:
                pass

            try:
                d["last_event_desc"] = tds[1].text.replace("\n", "").strip()
            except AttributeError as ae:
                print (ae)
                pass
            except IndexError as ie:
                print (ie)

            try:
                d["last_event_location"] = tds[2].text.replace("\n", "").strip()
            except AttributeError as ae:
                print (ae)
                pass
            except IndexError as ie:
                print (ie)
                pass
            
            try:
                ledt = tds[3].text.replace("\n", "").strip()
                d["last_event_time"] = pendulum.from_format(ledt, "M/D/YY HH:mm", tz="America/Chicago")
            except ValueError as ve:
                print (ve)
                pass
            except IndexError as e:
                print (e)
                pass

        return d
