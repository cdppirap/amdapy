# -*- coding: utf-8 -*-

from enum import Enum
from xml.etree.ElementTree import fromstring, ParseError
import requests
import re
import time

from urllib.parse import urlparse
import urllib.request
import pandas as pd
import os
import datetime
from lxml import etree
import io

# observatory tree
from .obstree import ObsTree

class AMDAOutputFormat(Enum):
    """
    Enum : Available output file formats
    """
    ASCII = 'ASCII'
    VOTABLE = 'VOTable'
    CDF = 'CDF'
    # File format netCDF not implemented in AMDA
    # NETCDF = 'netCDF'


class AMDATimeFormat(Enum):
    """
    Enum : Available output time formats
    """
    ISO = 'ISO8601'
    TIMESTAMP = 'unixtime'


class AMDAOutputCompression(Enum):
    """
    Enum : Available compression mode
    """
    NONE = 0
    GZIP = 1


class AMDASpaceCraft(Enum):
    """
    Enum : Available missions
    """
    CASSINI = "Cassini"
    GALILEO = "Galileo"
    VOYAGER1 = "Voyager_1"
    VOYAGER2 = "Voyager_2"
    PIONEER10 = "Pioneer_10"
    PIONEER11 = "Pioneer_11"
    PVO = "PVO"
    ACE = "ACE"
    VEX = "VEX"
    MEX = "MEX"
    MGS = "MGS"
    MAVEN = "MAVEN"
    MESSENGER = "MESSENGER"
    ULYSSES = "ULYSSES"
    STEREOA = "Stereo-A"
    STEREOB = "Stereo-B"
    WIND = "WIND"
    THEMISA = "THEMIS-A"
    THEMISB = "THEMIS-B"
    THEMISC = "THEMIS-C"
    THEMISD = "THEMIS-D"
    THEMISE = "THEMIS-E"
    CLUSTER1 = "CLUSTER1"
    CLUSTER2 = "CLUSTER2"
    CLUSTER3 = "CLUSTER3"
    CLUSTER4 = "CLUSTER4"
    DOUBLESTAR1 = "DoubleStar1"
    IMP8 = "IMP-8"
    GEOTAIL = "GEOTAIL"
    POLAR = "POLAR"
    INTERBALLTAIL = "INTERBALL-Tail"
    ISEE1 = "ISEE-1"
    ISEE2 = "ISEE-2"


class AMDACoordinatesSystem(Enum):
    """
    Enum : Available Coordinates systems
    """
    CPHIO = "CPHIO"
    GPHIO = "GPHIO"
    IPHIO = "IPHIO"
    EPHIO = "EPHIO"
    EQUATORIAL = "Equatorial"
    CGM = "CGM"
    CARRINGTON = "Carrington"
    DM = "DM"
    GEI = "GEI"
    GEO = "GEO"
    GSE = "GSE"
    GSEQ = "GSEQ"
    GSM = "GSM"
    HAE = "HAE"
    HCC = "HCC"
    HCI = "HCI"
    HCR = "HCR"
    HEE = "HEE"
    HEEQ = "HEEQ"
    HG = "HG"
    HGI = "HGI"
    HPC = "HPC"
    HPR = "HPR"
    J2000 = "J2000"
    LGM = "LGM"
    MAG = "MAG"
    MFA = "MFA"
    RTN = "RTN"
    SC = "SC"
    SE = "SE"
    SM = "SM"
    SR = "SR"
    SR2 = "SR2"
    SSE = "SSE"
    SSE_L = "SSE_L"
    SPACECRAFTORBPLANE = "SpacecraftOrbitPlane"
    WGS84 = "WGS84"
    MSO = "MSO"
    VSO = "VSO"


class AMDAOrbitUnit(Enum):
    """
    Enum : Available units for orbits
    """
    KM = "km"
    RS = "Rs"
    RJ = "Rj"
    RCA = "Rca"
    RGA = "Rga"
    RIO = "Rio"
    REU = "Reu"
    RV = "Rv"
    RM = "Rm"
    RE = "Re"
    AU = "AU"


class AMDARESTClient:
    """
    AMDA REST WS client implementation
    API description: http://amda.irap.omp.eu/help/apidoc/

    Attributes
    ----------
    proxy :
        To use only if you are behind a proxy (default None)
    entry_point : str
        Define AMDA REST WS entry point (default http://amda.irap.omp.eu/php/rest/)

    """

    __proxies = None
    __entry_point = 'http://amda.irap.omp.eu/php/rest/'

    def __init__(self, entry_point=None, proxies=None):
        if entry_point:
            self.__entry_point = entry_point
        self.__proxies = proxies

    def is_alive(self):
        """
        Used to check whether AMDA services are available or not.
        http://amda.irap.omp.eu/help/apidoc/#api-webservices-isAlive
        :return: True if service is alive, False else
        """
        result = self.__get_request('isAlive.php')
        if not result:
            return False
        result_json = result.json()
        return result_json and ('alive' in result_json) and result_json['alive']

    def auth(self):
        """
        Returns a token to use as an API parameter for get_dataset, get_orbites and get_parameter.
        http://amda.irap.omp.eu/help/apidoc/#api-webservices-auth
        :return: Token string or None if failed
        """
        result = self.__get_request('auth.php')
        if not result or (result.text == ''):
            return None
        return result.text

    def get_obs_data_tree(self):
        """
        Provides the hierarchy of public access data in AMDA.
        http://amda.irap.omp.eu/help/apidoc/#api-webservices-getObsDataTree
        :return: Url string or None if failed
        """
        result = self.__get_request('getObsDataTree.php')
        if not result:
            return None

        try:
            result_xml = fromstring(result.text)
        except ParseError:
            return None
        if result_xml.tag != 'LocalDataBaseParameters':
            return None

        return result_xml.text

    def get_dataset(self, token, starttime, stoptime, datasetid,
                    sampling=None, userid=None, password=None, fileformat=None, timeformat=None, compression=None):
        """
        Provides data corresponding to a dataset chosen by the user among those available in AMDA
        http://amda.irap.omp.eu/help/apidoc/#api-webservices-getDataset
        :param token: Token string obtained with auth method
        :param starttime: Start time in ISO format (ex.: 2008-01-01T00:00:00)
        :param stoptime: Stop time in ISO format (ex.: 2008-01-01T00:00:00)
        :param datasetid: Dataset Id. Can be obtained thanks the use of get_obs_data_tree method
        :param sampling: Optional. Define a sampling to apply to data
        :param userid: Optional. User identifier. Usefull to access to non-public dataset
        :param password: Optional. User password. Usefull to access to non-public dataset
        :param fileformat: Optional. Output file format.
        Available file formats are defined in AMDAOutputFormat class (default ASCII).
        :param timeformat: Optional. Output time format.
        Available time formats are defined in AMDATimeFormat class (default ISO8601).
        :param compression: Optional. Compression mode to apply to the output file.
        Available compression modes are defined in AMDAOutputCompression (default 0)
        :return: Url string or None if failed
        """
        params = {
            'token': token,
            'startTime': starttime,
            'stopTime': stoptime,
            'datasetID': datasetid
        }

        optional_params = {
            'sampling': sampling,
            'userID': userid,
            'password': password,
            'outputFormat': fileformat,
            'timeFormat': timeformat,
            'gzip': compression
        }
        result = self.__get_request('getDataset.php', params=self.__merge_params(params, optional_params))
        if not result:
            print("Error retrieving data, try a smaller time period")
            return None

        result_json = result.json()
        if not result_json or ('success' not in result_json) or (not result_json['success']) \
                or ('dataFileURLs' not in result_json) or (result_json['dataFileURLs'] == ''):
            print("Error retrieving data, try a smaller time period")
            return None

        return result_json['dataFileURLs']

    def get_orbites(self, token, starttime, stoptime, spacecraft, coordsys,
                    sampling=None, units=None, userid=None, password=None, fileformat=None, timeformat=None, compression=None):
        """
        Provides the trajectory of a spacecraft during a period of time.
        http://amda.irap.omp.eu/help/apidoc/#api-webservices-getOrbites
        :param token: Token string obtained with auth method
        :param starttime: Start time in ISO format (ex.: 2008-01-01T00:00:00)
        :param stoptime: Stop time in ISO format (ex.: 2008-01-01T00:00:00)
        :param spacecraft: Spacecraft name.
        Available scacecrafts are defined in AMDASpaceCraft class
        :param coordsys: Ouptut coordinates system
        Available coordinates systems are defined in AMDACoordinatesSystem class
        :param sampling: Optional. Define a sampling to apply to data
        :param units: Units for output data
        Available units are defined in AMDAOrbitUnit class. Default: km
        :param userid: Optional. User identifier. Usefull to access to non-public dataset
        :param password: Optional. User password. Usefull to access to non-public dataset
        :param fileformat: Optional. Output file format.
        Available file formats are defined in AMDAOutputFormat class (default ASCII).
        :param timeformat: Optional. Output time format.
        Available time formats are defined in AMDATimeFormat class (default ISO8601).
        :param compression: Optional. Compression mode to apply to the output file.
        Available compression modes are defined in AMDAOutputCompression (default 0)
        :return: Url string or None if failed
        """
        params = {
            'token': token,
            'startTime': starttime,
            'stopTime': stoptime,
            'spacecraft': spacecraft,
            'CoordinateSystem': coordsys
        }

        optional_params = {
            'sampling': sampling,
            'units': units,
            'userID': userid,
            'password': password,
            'outputFormat': fileformat,
            'timeFormat': timeformat,
            'gzip': compression
        }

        result = self.__get_request(method='getOrbites.php', params=self.__merge_params(params, optional_params))

        if not result:
            return None

        result_json = result.json()
        if not result_json or ('success' not in result_json) or (not result_json['success']) \
                or ('dataFileURLs' not in result_json) or (result_json['dataFileURLs'] == ''):
            return None

        return result_json['dataFileURLs']

    def get_parameter_list(self, userid=None, password=None, local=True):
        """
        Provides the hierarchy of derived parameters belonging to a user and parameters in AMDA.
        http://amda.irap.omp.eu/help/apidoc/#api-webservices-getParameterList
        :param userid: Optional. User identifier. Usefull to access to non-public dataset
        :param password: Optional. User password. Usefull to access to non-public dataset
        :param local: True to retrieve the local database parameters or False to retrieve derived parameters of 'userid'
        :return: Url string or None if failed
        """
        optional_params = {
            'userID': userid,
            'password': password
        }

        result = self.__get_request(method='getParameterList.php', params=self.__merge_params({}, optional_params))

        if not result:
            return None

        if local:
            res = re.findall("<LocalDataBaseParameters>(.*?)</LocalDataBaseParameters>", result.text)

        else:
            res = re.findall("<UserDefinedParameters>(.*?)</UserDefinedParameters>", result.text)

        if not res:
            return None

        return res[0]

    def get_parameter(self, token, starttime, stoptime, paramid,
                      sampling=None, userid=None, password=None, fileformat=None, timeformat=None, compression=None):
        """
        Provides data corresponding to a parameter chosen by the user among those available in AMDA
        (common or user defined parameters).
        http://amda.irap.omp.eu/help/apidoc/#api-webservices-getParameter
        :param token: Token string obtained with auth method
        :param starttime: Start time in ISO format (ex.: 2008-01-01T00:00:00)
        :param stoptime: Stop time in ISO format (ex.: 2008-01-01T00:00:00)
        :param paramid: Identifier of the parameter. Can be retrieve thanks the use of get_parameter_list method
        :param sampling: Optional. Define a sampling to apply to data
        :param userid: Optional. User identifier. Usefull to access to non-public dataset
        :param password: Optional. User password. Usefull to access to non-public dataset
        :param fileformat: Optional. Output file format.
        Available file formats are defined in AMDAOutputFormat class (default ASCII).
        :param timeformat: Optional. Output time format.
        Available time formats are defined in AMDATimeFormat class (default ISO8601).
        :param compression: Optional. Compression mode to apply to the output file.
        Available compression modes are defined in AMDAOutputCompression (default 0)
        :return: Url string or None if failed
        """
        params = {
            'token': token,
            'startTime': starttime,
            'stopTime': stoptime,
            'parameterID': paramid
        }

        optional_params = {
            'sampling': sampling,
            'userID': userid,
            'password': password,
            'outputFormat': fileformat,
            'timeFormat': timeformat,
            'gzip': compression
        }

        result = self.__get_request(method='getParameter.php', params=self.__merge_params(params, optional_params))

        if not result:
            print("Error getting parameter data, try a smaller time period")
            return None

        result_json = result.json()

        if not result_json or ('success' not in result_json) or (not result_json['success']):
            print("Error getting parameter data, try a smaller time period")
            return None

        if ('status' in result_json) and (result_json['status'] == 'in progress'):
            #In batch mode
            while True:
                #Wait for 30 seconds
                print("Download in progress, please do not interrupt")
                time.sleep(30)
                result = self.get_status(result_json['id'])
                if not result:
                    return None
                elif result == 'in progress':
                    continue
                return result

        if ('dataFileURLs' not in result_json) or (result_json['dataFileURLs'] == ''):
            return None

        return result_json['dataFileURLs']

    def get_status(self, processid):
        """
        Get the current status of the request according to a process ID.
        http://amda.irap.omp.eu/help/apidoc/#api-webservices-getStatus
        :param processid: Process identifier
        :return: URL of result file if done. 'in progress' if not finished. None in case of error
        """
        params = {
            'id': processid
        }

        result = self.__get_request(method='getStatus.php', params=params)

        if not result:
            return None

        result_json = result.json()

        if not result_json or ('success' not in result_json) or (not result_json['success']):
            return None

        if ('status' in result_json) and (result_json['status'] == 'in progress'):
            return 'in progress'

        if ('dataFileURLs' not in result_json) or (result_json['dataFileURLs'] == ''):
            return None

        return result_json['dataFileURLs']

    def get_timetable_list(self, userid=None, password=None):
        """
        Provides the private list of Time Tables (Time Table or TT) owned by a user.
        When called without userid, this web-service returns the list of shared Time Tables.
        http://amda.irap.omp.eu/help/apidoc/#api-webservices-getTimeTablesList
        :param userid: Optional. User identifier. Usefull to access to non-public dataset
        :param password: Optional. User password. Usefull to access to non-public dataset
        :return: Url string or None if failed
        """
        optional_params = {
            'userID': userid,
            'password': password
        }

        result = self.__get_request(method='getTimeTablesList.php', params=self.__merge_params({}, optional_params))

        if not result or (result.text == ''):
            return None

        return result.text

    def get_timetable(self, ttid, userid=None, password=None):
        """
        Provides the contents of a Time Table (TT).
        http://amda.irap.omp.eu/help/apidoc/#api-webservices-getTimeTable
        :param ttid: TT or catalog identifier. Can be retrieve thanks the use of get_timetable_list method
        http://amda.irap.omp.eu/help/apidoc/#api-webservices-getTimeTable
        :param userid: Optional. User identifier. Usefull to access to non-public dataset
        :param password: Optional. User password. Usefull to access to non-public dataset
        :return: Url string or None if failed
        """
        params = {
            'ttID': ttid
        }

        optional_params = {
            'userID': userid,
            'password': password
        }

        result = self.__get_request(method='getTimeTable.php', params=self.__merge_params(params, optional_params))

        if not result or (result.text == ''):
            return None

        return result.text

    @staticmethod
    def __merge_params(params, optional_params):
        return {**params, **{k: v for k, v in optional_params.items() if v is not None}}

    def __get_request(self, method, params=None):
        session = requests.Session()
        if self.__proxies:
            session.proxies = self.__proxies
        else:
            session.trust_env = False
        result = session.get(url=self.__entry_point + '/' + method, params=params, verify=True)
        if result.ok:
            return result
        else:
            return None
DATE_FORMAT="%Y-%m-%dT%H:%M:%S"
DATE_FORMATZ="%Y-%m-%dT%H:%M:%S.%f"
def get_column_names(in_str):
    for line in in_str.split("\n"):
        if line.startswith("# DATA_COLUMNS : "):
            l=line.replace("# DATA_COLUMNS : ","")
            l=l.replace("AMDA_TIME","Time")
            return l.split(", ")

from amdapy.core.parameter import DerivedParameter
def list_derived(userid, password):
    """List user defined parameters
    :param userid: username
    :type userid: str
    :param password: password
    :type password: str
    :return: list of derived parameters
    :rtype: list
    """
    client=AMDARESTClient()
    t=client.auth()
    if t is None:
      print("Error getting authentification token")
      return []
    # get list of derived parameters for user
    up=client.get_parameter_list(userid, password, local=False)
    r=requests.get(up).text
    tree=etree.fromstring(r)
    a=[]
    for e in tree.iter():
        if not isinstance(e, etree._Comment):
            if e.tag=="param":
                a.append(DerivedParameter.from_tree_element(e, userid))
    return a
    

def get_derived(userid, password, param_id, start_date, stop_date, col_names, date_parser=None, sampling=None):
    """Get parameters from user space.
    :param userid: username
    :type userid: str
    :param password: password
    :type password: str
    :param param_id: parameter id with format `ws_<name>`
    :type param_id: str
    :param start_date: start date
    :type start_date: str
    :param stop_date: stop date
    :type stop_date: str
    :param col_names: column names
    :type col_names: list
    :param date_parser: date parser
    :type date_parser: date parser
    :param sampling: sampling time in seconds
    :type sampling: float
    :return: derived parameter data
    :rtype: pandas.DataFrame
    """
    start,stop=start_date,stop_date
    if isinstance(start,datetime.datetime):
        start=start.strftime(DATE_FORMAT)
    if isinstance(stop,datetime.datetime):
        stop=stop.strftime(DATE_FORMAT)
    client=AMDARESTClient()
    t=client.auth()
    if t is None:
      return
    # get list of derived parameters for user
    pfu=client.get_parameter(t,start,stop,param_id,sampling=sampling,userid=userid, password=password)
    resp=requests.get(pfu)
    dparser=date_parser
    if dparser is None:
        dparser=common_date_parser
    try:
        data=pd.read_csv(io.StringIO(resp.text), comment="#",header=None, sep="\s+",names=col_names, parse_dates=["Time"], date_parser=dparser)
    except:
        data=pd.read_csv(io.StringIO(resp.text), comment="#", header=None, sep="\s+", names=get_column_names(resp.text), parse_dates=["Time"], date_parser=dparser)
    return data

def get_parameter(param_id, start_date, stop_date, col_names, date_parser=None, sampling=None):
    start,stop=start_date,stop_date
    if isinstance(start,datetime.datetime):
        start=start.strftime(DATE_FORMAT)
    if isinstance(stop,datetime.datetime):
        stop=stop.strftime(DATE_FORMAT)
    client=AMDARESTClient()
    t=client.auth()
    if t is None:
      print("Error getting authentification token")
      return
    pfu=client.get_parameter(t,start,stop,param_id,sampling=sampling)
    resp=requests.get(pfu)
    dparser=date_parser
    if dparser is None:
        dparser=common_date_parser
    try:
        data=pd.read_csv(io.StringIO(resp.text), comment="#",header=None, sep="\s+",names=col_names, parse_dates=["Time"], date_parser=dparser)
    except:
        data=pd.read_csv(io.StringIO(resp.text), comment="#", header=None, sep="\s+", names=get_column_names(resp.text), parse_dates=["Time"], date_parser=dparser)
    #os.system("rm {}".format(data_file))
    return data
def get_dataset(dataset_id, start_date, stop_date, date_parser=None, sampling=None):
    start,stop=start_date,stop_date
    if isinstance(start,datetime.datetime):
        start=start.strftime(DATE_FORMAT)
    if isinstance(stop,datetime.datetime):
        stop=stop.strftime(DATE_FORMAT)
    client=AMDARESTClient()
    t=client.auth()
    if t is None:
        print("Error getting authentification token")
        return
    pfu=client.get_dataset(t,start,stop,dataset_id,sampling=sampling)
    if pfu is None:
      return None
    #print("In amdaWSClient. get_dataset : pfu: {}".format(pfu))
    resp=requests.get(pfu)
    data=pd.read_csv(io.StringIO(resp.text), comment="#", header=None, sep="\s+")
    return data
def common_date_parser(x):
    if x.endswith("Z"):
        return datetime.datetime.strptime(x, DATE_FORMATZ)
    return datetime.datetime.strptime(x, DATE_FORMATZ)
def get_obs_tree():
    client=AMDARESTClient()
    t=client.auth()
    url=client.get_obs_data_tree()
    parser=etree.XMLParser(recover=True)
    return ObsTree(etree.parse(io.StringIO(requests.get(url).text), parser=parser))

