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


from dotenv import load_dotenv
load_dotenv('.env')



class CSX(object):

    def __init__(self):
        self.session = requests.session()
        self.post_url = 'https://api.csx.com/shipcsx-ship/v1//shipments/search'
        self.terminals_url = 'https://api.csx.com/shipcsx-main/v1//terminals'
        headers = {
                'Accept': 'application/json, text/plain, */*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Content-Type':'application/json',
                'Host':'api.csx.com',
                'Origin':'https://next.shipcsx.com',
                'Referer': 'https://next.shipcsx.com/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
                'X-APIKey': 'XBhZFoja3TM9BBFMVSFKIPbwtPuxJ7q5',
                }
        self.session.headers.update(headers)

   
    def get_terminals(self):
        r = self.session.get(self.terminals_url)
        if r.ok:
            return r.json()
        else:
            return None

    def search_container(self, terminal, container, reference_number=None):
        self.container = utils.validate_container_number(container, separate='true')
        self.reference_number = reference_number

        """
            'terminal':{
                'city':'EAST ST LOUIS',
                'fsac':'40570',
                'liftFlag':'true',
                'name':'East St Louis',
                'scac':'CSXT',
                'state':'IL',
                'timezoneID': 'America/Chicago',
            },
        """
        json_data = [{
            'terminal': terminal,
            'shipmentData':[{
                'equipmentID':{'equipmentInitial':'{0}'.format(self.container[0]),'equipmentNumber':'{0}'.format(self.container[1][:-1])},
                'referenceNumber':'{0}'.format(self.reference_number)
                }]
        }]

        

        r = self.session.post(self.post_url, json=json_data)
        res = self.parse_response(r.json()) 
        return res

    def parse_response(self, json):
        d = {
            'found': False,
            'last_event_code': '',
            'last_event_desc': '',
            'last_event_time': '',
            'last_event_location': '',
            'current_status': '',
            'etg': '',
            'grounded': False,
            'ground_date': '',
            }
      
        try:
            if json['shipments']:
                d['found'] = 'true'
                print (json)
               
                try:
                    status = json['shipments'][0]['shipmentStatus'].lower()
                    d['current_status'] = status
                    if status.lower() == 'notified':
                        d['grounded'] = 'true'
                        try:
                            # only available if grounded
                            gd = json['shipments'][0]['premise']['notifiedDate']
                            d['ground_date'] = pendulum.from_format(gd, 'YYYY-MM-DD')
                            
                            lfd = json['shipments'][0]['premise']['lastFreeDate']
                            d['last_free_date'] = pendulum.from_format(lfd, 'YYYY-MM-DD')
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
                    retg = json['shipments'][0]['tripPlan']['updatedEtn'].replace('Z', '')
                    d['etg'] = pendulum.from_format(retg, 'YYYY-MM-DDTHH:mm:ss')
                except IndexError:
                    pass
                except KeyError as e:
                    print (e)
                    pass
                
                try:
                    lastevent = json['shipments'][0]['lastReportedEvent']
                    rd = lastevent['actualDateTime'].replace('Z', '')
                    d['last_event_code'] = lastevent['eventCode']
                    d['last_event_desc'] = lastevent['eventTypeDescription']
                    d['last_event_time'] = pendulum.from_format(rd, 'YYYY-MM-DDTHH:mm:ss')
                    d['last_event_location'] = lastevent['city'] + ', ' + lastevent['state']

                except KeyError as e:
                    print (e)
                    pass
        except KeyError as e:
            print (e)
            return (json)
                
        return d



TERMINALS = {
    'atlanta':{'city':'ATLANTA HULSEY',
            'fsac':'23488',
            'liftFlag':'true',
            'name':'Atlanta Hulsey',
            'scac':'CSXT',
            'state':'GA',
            'timezoneID':'America/New_York'},
    'saint_louis':{'city':'EAST ST LOUIS',
            'fsac':'40570',
            'liftFlag':'true',
            'name':'East St Louis',
            'scac':'CSXT',
            'state':'IL',
            'timezoneID':'America/Chicago'},
    'baltimore':{'city':'BALTIMORE',
            'fsac':'70121',
            'liftFlag':'true',
            'name':'Baltimore',
            'scac':'CSXT',
            'state':'MD',
            'timezoneID':'America/New_York'},
    'bedford_park':{'city':'BEDFORD PARK',
            'fsac':'71732','liftFlag':'true',
            'name':'Bedford Park',
            'scac':'CSXT',
            'state':'IL',
            'timezoneID':'America/Chicago'},
    'buffalo': {'city':'BUFFALO',
            'fsac':'89241',
            'liftFlag':'true',
            'name':'Buffalo',
            'scac':'CSXT',
            'state':'NY',
            'timezoneID':'America/New_York'},
    'caictf': {'city':'CAICTF',
            'fsac':'15983',
            'liftFlag':'true',
            'name':'CAICTF',
            'scac':'CSXT',
            'state':'AL',
            'timezoneID':'America/Chicago'},
    'central_florirda_ilc': {'city':'CENTRAL FLORIDA ILC',
            'fsac':'15133',
            'liftFlag':'true',
            'name':'Central Florida ILC',
            'scac':'CSXT',
            'state':'FL',
            'timezoneID':'America/New_York'},
    'chambersburg': {'city':'CHAMBERSBURG',
            'fsac':'76131',
            'liftFlag':'true',
            'name':'Chambersburg',
            'scac':'CSXT',
            'state':'PA',
            'timezoneID':'America/New_York'},
    'charleston': {'city':'CHARLESTON',
            'fsac':'12097',
            'liftFlag':'true',
            'name':'Charleston',
            'scac':'CSXT',
            'state':'SC',
            'timezoneID':'America/New_York'},
    'charlotte': {'city':'CHARLOTTE',
            'fsac':'22240',
            'liftFlag':'true',
            'name':'Charlotte',
            'scac':'CSXT',
            'state':'NC',
            'timezoneID':'America/New_York'},
    'chicago_59th_st': {'city':'CHICAGO 59TH ST',
            'fsac':'89455',
            'liftFlag':'true',
            'name':'Chicago 59th St',
            'scac':'CSXT',
            'state':'IL',
            'timezoneID':'America/Chicago'},
    'cincinnati': {'city':'CINCINNATI',
            'fsac':'49500',
            'liftFlag':'true',
            'name':'Cincinnati',
            'scac':'CSXT',
            'state':'OH',
            'timezoneID':'America/New_York'},
    'cleveland': {'city':'CLEVELAND',
            'fsac':'72168',
            'liftFlag':'true',
            'name':'Cleveland',
            'scac':'CSXT',
            'state':'OH',
            'timezoneID':'America/New_York'},
    'columbus': {'city':'COLUMBUS',
            'fsac':'86090',
            'liftFlag':'true',
            'name':'Columbus',
            'scac':'CSXT',
            'state':'OH',
            'timezoneID':'America/New_York'},
    'detroit': {'city':'DETROIT',
            'fsac':'87598',
            'liftFlag':'true',
            'name':'Detroit',
            'scac':'CSXT',
            'state':'MI',
            'timezoneID':'America/New_York'},
    'east_st_louis': {'city':'EAST ST LOUIS','fsac':'40570','liftFlag':'true','name':'East St Louis','scac':'CSXT','state':'IL','timezoneID':'America/Chicago'},
    'fairburn': {'city': 'FAIRBURN',
            'fsac': '52023',
            'liftFlag': 'true',
            'name': 'Fairburn',
            'scac': 'CSXT',
            'state': 'GA',
            'timezoneID': 'America/New_York'},
    'indianapolis': {'city': 'INDIANAPOLIS',
            'fsac': '75128',
            'liftFlag': 'true',
            'name': 'Indianapolis',
            'scac': 'CSXT',
            'state': 'IN',
            'timezoneID': 'America/New_York'},
    'jacksonville': {'city': 'JACKSONVILLE',
            'fsac': '14023',
            'liftFlag': 'true',
            'name': 'Jacksonville',
            'scac': 'CSXT',
            'state': 'FL',
            'timezoneID': 'America/New_York'},
    'louisville': {'city': 'LOUISVILLE',
            'fsac': '41000',
            'liftFlag': 'true',
            'name': 'Louisville',
            'scac': 'CSXT',
            'state': 'KY',
            'timezoneID': 'America/New_York'},
    'memphis': {'city': 'MEMPHIS',
          'fsac': '46380',
          'liftFlag': 'true',
          'name': 'Memphis',
          'scac': 'CSXT',
          'state': 'TN',
          'timezoneID': 'America/Chicago'},
    'nashville': {'city': 'NASHVILLE',
          'fsac': '45050',
          'liftFlag': 'true',
          'name': 'Nashville',
          'scac': 'CSXT',
          'state': 'TN',
          'timezoneID': 'America/Chicago'},
    'north_bergen': {'city': 'NORTH BERGEN',
          'fsac': '17915',
          'liftFlag': 'true',
          'name': 'North Bergen',
          'scac': 'CSXT',
          'state': 'NJ',
          'timezoneID': 'America/New_York'},
    'northwest_ohio_ictf': {'city': 'NORTHWEST OHIO ICTF',
          'fsac': '71663',
          'liftFlag': 'true',
          'name': 'Northwest Ohio ICTF',
          'scac': 'CSXT',
          'state': 'OH',
          'timezoneID': 'America/New_York'},
    'philadelphia': {'city': 'PHILADELPHIA',
          'fsac': '70005',
          'liftFlag': 'true',
          'name': 'Philadelphia',
          'scac': 'CSXT',
          'state': 'PA',
          'timezoneID': 'America/New_York'},
    'pittsburgh': {'city': 'PITTSBURGH',
          'fsac': '71053',
          'liftFlag': 'true',
          'name': 'Pittsburgh',
          'scac': 'CSXT',
          'state': 'PA',
          'timezoneID': 'America/New_York'},
    'portsmouth': {'city': 'PORTSMOUTH',
          'fsac': '10188',
          'liftFlag': 'true',
          'name': 'Portsmouth',
          'scac': 'CSXT',
          'state': 'VA',
          'timezoneID': 'America/New_York'},
    'savannah': {'city': 'SAVANNAH',
          'fsac': '13015',
          'liftFlag': 'true',
          'name': 'Savannah',
          'scac': 'CSXT',
          'state': 'GA',
          'timezoneID': 'America/New_York'},
    'south_kearny': {'city': 'SOUTH KEARNY',
          'fsac': '39137',
          'liftFlag': 'true',
          'name': 'South Kearny',
          'scac': 'CSXT',
          'state': 'NJ',
          'timezoneID': 'America/New_York'},
    'springfield': {'city': 'SPRINGFIELD',
          'fsac': '16530',
          'liftFlag': 'true',
          'name': 'Springfield',
          'scac': 'CSXT',
          'state': 'MA',
          'timezoneID': 'America/New_York'},
    'syracuse': {'city': 'SYRACUSE',
          'fsac': '17440',
          'liftFlag': 'true',
          'name': 'Syracuse',
          'scac': 'CSXT',
          'state': 'NY',
          'timezoneID': 'America/New_York'},
    'tampa': {'city': 'TAMPA',
          'fsac': '14209',
          'liftFlag': 'true',
          'name': 'Tampa',
          'scac': 'CSXT',
          'state': 'FL',
          'timezoneID': 'America/New_York'},
    'valleyfield': {'city': 'VALLEYFIELD',
          'fsac': '16005',
          'liftFlag': 'true',
          'name': 'Valleyfield',
          'scac': 'CSXT',
          'state': 'PQ',
          'timezoneID': 'America/New_York'},
    'worcester': {'city': 'WORCESTER',
          'fsac': '16430',
          'liftFlag': 'true',
          'name': 'Worcester',
          'scac': 'CSXT',
          'state': 'MA',
          'timezoneID': 'America/New_York'},
          }
