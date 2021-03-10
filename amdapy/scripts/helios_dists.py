from datetime import date, time, datetime, timedelta
import os
import pathlib
import urllib.error
from urllib.error import URLError
from collections import OrderedDict
import warnings

import astropy.constants as constants
import astropy.units as u
import numpy as np
import pandas as pd

#from bs4 import BeautifulSoup
import requests
use_hdf = True 
helios_dir="/home/aschulz/data_insertions/helios"

def timefilter(data, starttime, endtime):
    """
    Puts data in a single dataframe, and filters it between times.
    Parameters
    ----------
    data : :class:`pandas.DataFrame` or list
        Input data. If a list, ``pd.concat(data)`` will be run to put it in
        a DataFrame.
    starttime : datetime.datetime
        Start of interval.
    endtime : datetime.datetime
        End of interval.
    Returns
    -------
    out : :class:`pandas.DataFrame`
        Filtered data.
    """
    if len(data) == 0:
        raise RuntimeError(
            'No data available between {} and {}'.format(starttime, endtime))
    if isinstance(data, list):
        data = pd.concat(data)
    # Get time values
    if 'Time' in data.columns:
        time = data['Time']
    elif 'Time' in data.index.names:
        time = data.index.get_level_values('Time')
    else:
        raise KeyError('The label "Time" was not found in '
                       'the dataframe columns or index')

    data = data[(time > starttime) &
                (time < endtime)]
    # Assume if this fails we have a multi-index that already has time in it
    if ('Time' in data.columns) and (len(data.index.shape) == 1):
        data = data.set_index('Time', drop=True)

    return data
def get_electron_dists(path):
    extensions=["hdm.0","hdm.1","ndm.0","ndm.1"]
    distlist=[]
    # checking if the file exists should be done before calling this function
    if path.endswith("electron_dists.hdf"):
        # current file is an hdf file
        today_dist=pd.read_hdf(path)
        return today_dist
    elif path[-5:] in extensions:
        el=path.split("/")
        probe=el[4].split("_")[1]
        year=el[5]
        doy=el[6]
        hour, minute, second = _dist_filename_to_hms(path)
        try:
            d = electron_dist_single(probe, year, doy,
                                     hour, minute, second)
        except RuntimeError as err:
            strerr = 'No electron distribution function data in file'
            if str(err) == strerr:
                return
            raise err
        if d is None:
            return

        t = datetime.combine(starttime.date(),
                            time(hour, minute, second))
        t=datetime(year=int(year),hour=hour,minute=minutes,second=second)+timedelta(days=int(doy)-1)
        d['Time'] = t
        if verbose:
            print(t)
        todays_dist.append(d)
        return d
    return

        
def electron_dists(probe, starttime, endtime, remove_advect=False,
                   verbose=False):
    """
    Return 2D electron distributions between *starttime* and *endtime*
    Parameters
    ----------
    probe : int
        Helios probe to import data from. Must be 1 or 2.
    starttime : datetime.datetime
        Start of interval
    endtime : datetime.datetime
        End of interval
    remove_advect : bool
        If *False*, the distribution is returned in
        the spacecraft frame.
        If *True*, the distribution is
        returned in the solar wind frame, by subtracting the spacecraft
        velocity from the velcoity of each bin. Note this significantly
        slows down reading in the distribution.
    verbose : bool
        If ``True``, print dates when loading files. Default is ``False``.
    Returns
    -------
    dists : pandas.DataFrame
        Electron distribution functions
    """
    extensions = ['hdm.0', 'hdm.1', 'ndm.0', 'ndm.1']
    distlist = []

    # Loop through each day
    starttime_orig = starttime
    while starttime < endtime:
        year = starttime.year
        doy = starttime.strftime('%j')
        if verbose:
            print('Loading electron dists from year', year, 'doy', doy)
        # Directory for today's distribution files
        dist_dir = _dist_file_dir(probe, year, doy)
        print("electron_dists : {}".format(dist_dir))
        # If directory doesn't exist, print error and continue
        if not os.path.exists(dist_dir):
            print('No electron distributions available for year', year,
                  'doy', doy)
            starttime += timedelta(days=1)
            continue

        # Locaiton of hdf file to save to/load from
        hdffile = 'h' + probe + str(year) + str(doy).zfill(3) +\
            'electron_dists.hdf'
        hdffile = os.path.join(dist_dir, hdffile)
        if os.path.isfile(hdffile):
            todays_dist = pd.read_hdf(hdffile)
            distlist.append(todays_dist)
            starttime += timedelta(days=1)
            continue

        todays_dist = []
        # Get every distribution function file present for this day
        for f in os.listdir(dist_dir):
            path = os.path.join(dist_dir, f)
            # Check for distribution function
            if path[-5:] in extensions:
                hour, minute, second = _dist_filename_to_hms(path)
                try:
                    d = electron_dist_single(probe, year, doy,
                                             hour, minute, second)
                except RuntimeError as err:
                    strerr = 'No electron distribution function data in file'
                    if str(err) == strerr:
                        continue
                    raise err
                if d is None:
                    continue

                t = datetime.combine(starttime.date(),
                                     time(hour, minute, second))
                d['Time'] = t
                if verbose:
                    print(t)
                todays_dist.append(d)

        if todays_dist == []:
            starttime += timedelta(days=1)
            continue
        todays_dist = pd.concat(todays_dist)
        todays_dist = todays_dist.set_index('Time', append=True)
        if use_hdf:
            todays_dist.to_hdf(hdffile, key='electron_dists', mode='w')
        distlist.append(todays_dist)
        starttime += timedelta(days=1)

    if distlist == []:
        raise RuntimeError('No electron data available for times ' +
                           str(starttime_orig) + ' to ' + str(endtime))
    return timefilter(distlist, starttime_orig, endtime)
def _dist_file_dir(probe, year, doy):
    return os.path.join(helios_dir, "helios_{}".format(probe), "{}".format(year), "{}".format(int(doy)))
    return os.path.join(helios_dir,
                        'helios{}'.format(probe),
                        'dist',
                        '{}'.format(year),
                        '{}'.format(int(doy)))
def _dist_filename_to_hms(path):
    """Given distribution filename, extract hour, minute, second"""
    # year = int(path[-21:-19]) + 1900
    # doy = int(path[-18:-15])
    hour = int(path[-14:-12])
    minute = int(path[-11:-9])
    second = int(path[-8:-6])
    return hour, minute, second
def electron_dist_single(probe, year, doy, hour, minute, second,
                         remove_advect=False):
    """
    Read in 2D electron distribution function.
    Parameters
    ----------
    probe : int, str
        Helios probe to import data from. Must be 1 or 2.
    year : int
        Year
    doy : int
        Day of year
    hour : int
        Hour.
    minute : int
        Minute
    second : int
        Second
    remove_advect : bool
        If ``False``, the distribution is returned in
        the spacecraft frame.
        If ``True``, the distribution is
        returned in the solar wind frame, by subtracting the spacecraft
        velocity from the velcoity of each bin. Note this significantly
        slows down reading in the distribution.
    Returns
    -------
    dist : pandas.DataFrame
        2D electron distribution function
    """
    probe = _check_probe(probe)
    f, filename = _loaddistfile(probe, year, doy, hour, minute, second)
    startline = None
    for i, line in enumerate(f):
        # Find start of electron distribution function
        if line[0:4] == ' 2-D':
            startline = i + 2
            # Throw away next line (just has max of distribution)
            f.readline()
            # Throw away next line (just has table headings)
            if f.readline()[0:27] == ' no electron data available':
                return None
            break
    nlines = None
    for i, line in enumerate(f):
        if 'Degree, Pizzo correction' in line:
            break
    nlines = i + 1
    if startline is None:
        return None
    ##########################################
    # Read and process electron distribution #
    ##########################################
    # Arguments for reading in data
    readargs = {'usecols': [0, 1, 2, 3, 4, 5],
                'names': ['Az', 'E_bin', 'pdf', 'counts', 'vx', 'vy'],
                'delim_whitespace': True,
                'skiprows': startline,
                'nrows': nlines}
    # Read in data
    dist = pd.read_csv(filename, **readargs)
    if dist.empty:
        return None

    # Remove spacecraft abberation
    # Assumes that spacecraft motion is always in the ecliptic (x-y)
    # plane
    if remove_advect:
        params = distparams_single(probe, year, doy, hour, minute, second)
        dist['vx'] += params['helios_vr']
        dist['vy'] += params['helios_v']
    # Convert to SI units
    dist[['vx', 'vy']] *= 1e3
    dist['pdf'] *= 1e12
    # Calculate spherical coordinates of energy bins
    dist['|v|'], _, dist['phi'] =\
        _cart2sph(dist['vx'], dist['vy'], 0)
    # Calculate bin energy assuming particles are electrons
    dist['E_electron'] = 0.5 * constants.m_e.value *\
        ((dist['|v|']) ** 2)

    # Convert to multi-index using Azimuth and energy bin
    dist = dist.set_index(['E_bin', 'Az'])
    f.close()
    return dist
def _check_probe(probe):
    probe = str(probe)
    assert probe == '1' or probe == '2', 'Probe number must be 1 or 2'
    return probe
def _loaddistfile(probe, year, doy, hour, minute, second):
    """
    Method to load a Helios distribution file.
    Returns opened file and location of file if file exists. If file doesn't
    exist raises an OSError.
    Parameters
    ----------
    probe : int, str
        Helios probe to import data from. Must be 1 or 2.
    year : int
        Year
    doy : int
        Day of year
    hour : int
        Hour.
    minute : int
        Minute
    second : int
        Second
    Returns
    -------
    f : file
        Opened distribution function file
    filename : str
        Filename of opened file
    """
    probe = _check_probe(probe)
    # Work out location of file
    yearstring = str(year)[-2:]
    filedir = _dist_file_dir(probe, year, doy)
    filename = os.path.join(filedir,
                            'h' + probe + 'y' + yearstring +
                            'd' + str(doy).zfill(3) +
                            'h' + str(hour).zfill(2) +
                            'm' + str(minute).zfill(2) +
                            's' + str(second).zfill(2) + '_')

    # Try to open distribution file
    for extension in ['hdm.0', 'hdm.1', 'ndm.0', 'ndm.1']:
        try:
            f = open(filename + extension)
            filename += extension
        except OSError:
            continue

    if 'f' not in locals():
        raise OSError('Could not find file with name ' +
                      filename[:-1])
    else:
        return f, filename
def _cart2sph(x, y, z):
    """
    Given cartesian co-ordinates returns shperical co-ordinates.
    Parameters
    ----------
    x : array_like
        x values
    y : array_like
        y values
    z : array_like
        z values
    Returns
    -------
    r : array_like
        r values
    theta : array_like
        Elevation angles defined from the x-y plane towards the z-axis.
        Angles are in the range [-pi/2, pi/2].
    phi : array_like
        Azimuthal angles defined in the x-y plane, clockwise about the
        z-axis, from the x-axis. Angles are in the range [-pi, pi].
    """
    xy = x**2 + y**2
    r = np.sqrt(xy + z**2)
    theta = np.arctan2(z, np.sqrt(xy))
    phi = np.arctan2(y, x)
    return r, theta, phi
def get_time(df):
    print(df)
    print("aop'iqezghzôqeigh", df.iloc["Time",:])
    print("numpy shape : {}".format(df.to_numpy().shape))
    print("in get_time : {}".format(df.columns))
    T=df["Time"]
    previous_t=None
    for i in range(T.shape[1]):
        if i==0:
            previous_t=T[i]
            print("Time : {}".format(previous_t))
        else:
            if T[i]!=previous_t:
                previous_t=T[i]
                print("Time : {}".format(previous_t))
def get_time(df):
    n=df.index.shape[0]
    T=[]
    prev_t=None
    for i in range(n):
        e_bin,az,t=df.index[i]
        t=pd.to_datetime(t,unit="s")
        if i==0:
            T.append(t)
            prev_t==t
        else:
            if t != prev_t:
                T.append(t)
                prev_t=t
    return np.array(T,dtype=object)
def get_t_pos(t,t_l):
    return np.where(t==t_l)[0]
def get_data_as_ndarray(data):
    # get time vector
    T=data["Time"].unique()
    n=T.shape[0]
    ans=np.full((n,16,8,8),np.nan)
    N=data.shape[0]
    from amdapy.ddtime import dt_to_seconds
    for i in range(n):
        sec=T[i].astype('datetime64[s]').astype('int')
        # get the target slice
        slice_=data[data["Time"]==T[i]]
        for r in range(slice_.shape[0]):
            row=slice_.iloc[r,:]
            e_b=row["E_bin"].item()
            az=row["Az"]
            new_r=row.to_numpy()[-8:]
            new_r[0]=new_r[0].timestamp()
            print("old row : {}".format(row))
            print("new row : {}".format(new_r))
            if not np.isnan(new_r[0]):
                ans[i,e_b-1,az-1,:]=new_r
            else:
                print("Error : {}".format(new_r))
        t_=sec*np.ones(ans[i,:,:,0].shape)
        ans[i,:,:,0]=t_
    return ans
def save_dataset(data,brief,destination):
    t0,t1=data[0,0,0,0],data[-1,0,0,0]
    sddt=DDTime.from_utctimestamp(t0)
    filename="{}_{}.nc".format(brief,sddt.replace("\0",""))
    if len(filename)>17:
        filename="{}_{}.nc".format(brief,sddt[:17-len(brief)-1-3])
    path=os.path.join(destination,filename)
    print("save_dataset filename : {}".format(path))

    dataset=Dataset(path,mode="w",format="NETCDF3_CLASSIC")
    dataset.createDimension("TimeLength",17)
    dataset.createDimension("Time",None)
    dataset.createDimension("ebins",16)
    dataset.createDimension("azimuts",8)

    # create variables
    dataset.createVariable("Time",float,("Time"))
    dataset.createVariable("pdf",float,("Time","ebins","azimuts"))
    print(np.sum(np.isnan(data[:,:,:,2])))
    ##aa=data[:,:,:,2]
    ##aa[np.isnan(aa) ]=0
    ##data[:,:,:,2]=aa
    ##print(np.sum(np.isnan(data[:,:,:,2])))
    dataset.createVariable("counts",float,("Time","ebins","azimuts"))
    ##print("Good counts")
    dataset.createVariable("vx",float,("Time","ebins","azimuts"))
    dataset.createVariable("vy",float,("Time","ebins","azimuts"))
    dataset.createVariable("V",float,("Time","ebins","azimuts"))
    dataset.createVariable("phi",float,("Time","ebins","azimuts"))
    dataset.createVariable("E_electron",float,("Time","ebins","azimuts"))
    dataset.createVariable("StartTime","c",("TimeLength"))
    dataset.createVariable("StopTime","c",("TimeLength"))

    # set data
    dataset.variables["Time"][:]=data[:,0,0,0]
    dataset.variables["pdf"][:]=data[:,:,:,1]
    dataset.variables["counts"][:]=data[:,:,:,2]
    dataset.variables["vx"][:]=data[:,:,:,3]
    dataset.variables["vy"][:]=data[:,:,:,4]
    dataset.variables["V"][:]=data[:,:,:,5]
    dataset.variables["phi"][:]=data[:,:,:,6]
    dataset.variables["E_electron"][:]=data[:,:,:,7]
    dataset.variables["StartTime"][:]=sddt
    dataset.variables["StopTime"][:]=DDTime.from_utctimestamp(t1)
    dataset.sync()
    dataset.close()

if __name__=="__main__":
    import argparse
    import matplotlib.pyplot as plt
    from amdapy.ddtime import DDTime
    import gc
    from netCDF4 import Dataset
    parser=argparse.ArgumentParser()
    parser.add_argument("-p","--probe", help="probe index (1 or 2)", type=int, default=1)
    args=parser.parse_args()

    destination="/home/aschulz/data_insertions/helios{}_edists".format(args.probe)
    if not os.path.exists(destination):
        os.system("mkdir -p {}".format(destination))
    brief="edist"

    date0=datetime(1973,1,1)
    while date0<datetime(2022,1,1):
        date1=date0+timedelta(days=1)
        try:
            print("electron data")
            data=electron_dists(str(args.probe),date0,date1)
        except Exception as e:
            date0=date1
            print("erre getting dat {}".format(e))
            continue
        date0=date1
        if not data is None:
            try:
                # create the netcdf dataset now
                data=data.reset_index()
                data=data.sort_values("Time")
                # try to get the filename here
                a,b=data["Time"].iloc[0],data["Time"].iloc[-1]
                a=pd.to_datetime(a,unit="s")
                ddlen=17-len(brief)-1-3
                f="{}/{}_{}.nc".format(destination,brief,DDTime.from_datetime(a)[:ddlen])
                if os.path.exists(f):
                    print("file {} exists. skipping".format(f))
                    continue
                # get time vector
                da=get_data_as_ndarray(data)
                save_dataset(da,brief,destination)
            except:
                print("Exception")
                continue
    data=None

