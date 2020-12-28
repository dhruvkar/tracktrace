import pendulum
from . import utils
 

class ContainerFactory(object):

    def __init__(self):
        self._builders = {}


    def register_builder(self, key, builder):
        self._builders[key] = builder


    def create(self, scac, **kwargs):
        builder = self._builders.get(scac)
        if not builder:
            raise ValueError(key)

        return builder(**kwargs)



class ShippingContainer(object):

    def __init__(self, cn):

        self.number = utils.validate_container_number(cn)
        self.last_updated = pendulum.now(tz=("US/Central"))
        timezone = self.last_updated.tz.tzname(self.last_updated)
        self.last_updated_string = self.last_updated.format("DD-MMM-YYYY hh:MM A") + " " + timezone
        self._update_template = {
            "location":"","vessel":"", "voyage":"", "movement": "", "mode": "","date":""}
        self.json = None
        self.df = None
    
    def __repr__(self):
        return "<ShippingContainer {0} - [{1} LINE]>".format(self.number, self.shipping_line)

    
    def handle_saints(self, city_name):
        cn = city_name.lower()
        
        if cn.startswith("st. ") :
            cn = cn.replace("st. ", "saint ")
        elif cn.startswith("st "):
            cn = cn.replace("st ", "saint ")
        
        return cn.title()


    def to_json(self, dupdates):
        j = copy.copy(dupdates)
        """list of dictionaries to json for API"""
        for x in j:
            x["location"].__dict__.pop("cursor")
            x["location"].__dict__.pop("df")
            x["date"] = x["date"].isoformat()
        self.json = j 
        

