"""
Parameter representation
"""

class DerivedParameter:
    def __init__(self, userid, paramid, name, timestep, buildchain, attrib={}):
        self.userid=userid
        self.paramid=paramid
        self.name=name
        self.timestep=timestep
        self.buildchain=buildchain
        self.attrib=attrib
    def __str__(self):
        return "DerivedParameter (user={}, id={}, name={})".format(self.userid, self.parameter_id(), self.name)
    def parameter_id(self):
        return "ws_{}".format(self.name)
    @staticmethod
    def from_tree_element(el, userid):
        did=""
        name=el.attrib["name"]
        buildchain=el.attrib["buildchain"]
        timestep=float(el.attrib["timestep"])

        for k in el.attrib:
            if k.endswith("}id"):
                did=el.attrib[k]
        return DerivedParameter(userid, did, name, timestep, buildchain, el.attrib)
   
