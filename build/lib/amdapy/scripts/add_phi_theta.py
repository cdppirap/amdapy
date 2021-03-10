"""
Tools for managing spase resources

SpaseManager and ParameterManager implementation test.

Objectiv : - connect to the SPASE repository and list all NumericalData files
           - find those that contain a parameter named "b_rtn"
           - if the NumericalData file does not contain two parameters named "phi" and "theta" then create them
           - save the new NumericalData file to the repository
           - save the new Parameter files to the parameter repository
"""
import os
import sys
import subprocess

from spase.manager import SpaseManager, make_parameter_element_from_dict
from parameters.manager import ParameterManager
from parameters.parameter_xml import ParameterXML
from xml.etree.ElementTree import fromstring,tostring,register_namespace

"""
Phi and theta parameter definition strings
"""
phi_param_def_xml="""<?xml version="1.0"?>
  <param xml:id='psp_b_1min_phi'>
    <get>
      <amdaParam name='psp_b_1min'/>
    </get>
    <process>180+RAD2DEG*atan2(-$psp_b_1min[1],-$psp_b_1min[0])</process>
    <output/>
  </param>"""
theta_param_def_xml="""<?xml version="1.0"?>
  <param xml:id='psp_b_1min_theta'>
    <get>
      <amdaParam name='psp_b_1min'/>
    </get>
    <process>asin($psp_b_1min[2] / magnitude($psp_b_1min))*RAD2DEG</process>
    <output/>
  </param>"""


if __name__=="__main__":
  print("Testing SPASE resource manager")
  path="/usr/share/tomcat/webapps/amda-registry/metadata/CNES"
  spase_user="amda_admin"
  spase_host="apus"
  manager=SpaseManager(path=path, user=spase_user, host=spase_host)
  param_manager=ParameterManager(path="/home/myriam/AMDA_20170601/AMDA_INTERNAL_METADATA", user="amda_admin", host="pc1177")
  
  for nd in manager.iter_numdata():
    if nd.has_parameter_name("b_rtn"):
      if nd.has_parameter_name("phi") and nd.has_parameter_name("theta"):
        print("skipping {}".format(nd.get_id()))
        #print("correcting the parameter files, only run this once")
        #param=nd.get_parameter_by_name("b_rtn")

        #new_phi_xml=phi_param_def_xml.replace("psp_b_1min", param.get_parameter_key())
        #new_theta_xml=theta_param_def_xml.replace("psp_b_1min", param.get_parameter_key())
        #phi_param=ParameterXML.from_string(new_phi_xml)
        #theta_param=ParameterXML.from_string(new_theta_xml)

        #param_manager.save(phi_param)
        #param_manager.save(theta_param)

        continue
      print("Adding parameters phi and theta to {}".format(nd.get_id()))
      param=nd.get_parameter_by_name("b_rtn")
      phi_param_key="{}_phi".format(param.get_parameter_key())
      theta_param_key="{}_theta".format(param.get_parameter_key())
      print("key of the original parameter : {}".format(param.get_id()))
      print("key of the phi parameter : {}".format(phi_param_key))
      print("key of the theta parameter : {}".format(theta_param_key))
      print("")
      # set new id for phi and theta parameters
      new_phi_xml=phi_param_def_xml.replace("psp_b_1min", param.get_parameter_key())
      new_theta_xml=theta_param_def_xml.replace("psp_b_1min", param.get_parameter_key())
      # add two parameters to the numerical data file
      # create two NDParameter objects
      phi_el=make_parameter_element_from_dict({"Name": "phi", "ParameterKey": phi_param_key, "Description": "Magnetic field phi angle" , "Ucd": "phys.magField", "Units": "degrees", "UnitsConversion": "1e-9&gt;T", "RenderingHints": {"DisplayType":"TimeSeries"} , "Structure":{"Size":"1"} })
      theta_el=make_parameter_element_from_dict({"Name": "theta", "ParameterKey": theta_param_key, "Description": "Magnetic field theta angle" , "Ucd": "phys.magField", "Units": "degrees", "UnitsConversion": "1e-9&gt;T", "RenderingHints": {"DisplayType":"TimeSeries"} , "Structure":{"Size":"1"} })
      nd.add_parameter(phi_el)
      nd.add_parameter(theta_el)
      # save the newly created NumericalData file
      manager.save(nd)
      # save the newly created Parameter files
      phi_param=ParameterXML.from_string(new_phi_xml)
      theta_param=ParameterXML.from_string(new_theta_xml)

      param_manager.save(phi_param)
      param_manager.save(theta_param)
      # create the two parameter definition files and send them to the parameter repository
      # pause for checking
      #input("check")
    else:
      print("Resource file {} does not cont#ain a b_rtn parameter".format(nd.get_id()))
