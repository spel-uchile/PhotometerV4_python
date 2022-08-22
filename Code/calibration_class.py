# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 18:21:49 2020

@author: crist
"""
import os
import csv
import json
import datetime as dt
import measurement_class as mc
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import pvlib as pv

from scipy.optimize import minimize
from scipy import stats

global tau1
global alpha
global v
global res
global p
global am
global ozo
global ozo_model


###############################################################################
def load_ozone_model():
    with open('Code/../../Ozono/absortion.json', 'r') as file:
        json_file = json.load(file)
    r_struc = np.array(json_file)
    return r_struc

def got_o3(dobson, lamb0, struct):
    return np.around(np.interp(lamb0, struct[:,0], struct[:,1], left= 0, right= 0)*dobson*1e-3, 3)

def load_stgo_data(stgo_unit, date_day):
    data_path = "Code/../../stgonet_data"
    data_folder = os.listdir(data_path)

    data_unit = []
    data_day = []
    for i in data_folder:
    
        data_list = i.split('.')[0].split('_')
        data_day.append(dt.date(int(data_list[3]),int(data_list[2]), int(data_list[1])))
        data_unit.append(data_list[0])
 
    unit_index=[index for index, value in enumerate(data_unit) if value == stgo_unit]
    date_index=[index for index, value in enumerate(data_day) if value == date_day]
    found_index = list(set(unit_index).intersection(date_index))

    file_sample = [data_folder[x] for x in found_index]

    if file_sample != []:
        for sample in file_sample:
            with open(data_path+'/'+ sample, 'r') as file:
                json_file = json.load(file)
    else:
        json_file = []

    #unit_sample = [data_unit[x] for x in unit_index]
    #day_sample = [data_day[x] for x in date_index]
    
    return json_file

def load_aero_data(aero_unit, date_day):
    aeronet_path = "Code/../../aeronet_data"
    aeronet_folder = os.listdir(aeronet_path)

    aeronet_unit = []
    aeronet_day = []
    for i in aeronet_folder:
    
        aeronet_list = i.split('.')[0].split('_')
        aeronet_day.append(dt.date(int(aeronet_list[3]),int(aeronet_list[2]), int(aeronet_list[1])))
        aeronet_unit.append(aeronet_list[0])
    
    uaero_index=[index for index, value in enumerate(aeronet_unit) if value == aero_unit]
    daero_index=[index for index, value in enumerate(aeronet_day) if value == date_day]
    faero_index = list(set(uaero_index).intersection(daero_index))

    faero_sample = [aeronet_folder[x] for x in faero_index]

    if faero_sample != []:
        for sample in faero_sample:
            with open(aeronet_path+'/'+ sample, 'r') as file:
                json_aero_file = json.load(file)
    else:
        json_aero_file = []

    #uaero_sample = [aeronet_unit[x] for x in uaero_index]
    #day_sample = [aeronet_day[x] for x in daero_index]
    
    return json_aero_file

def stgo_filter(stgo_data, cut=0, cloud_filter = 0):
    
    stgo_data = mfilter(stgo_data, 'm1', cut, cloud_filter)
    stgo_data = mfilter(stgo_data, 'm2', cut, cloud_filter)
    stgo_data = mfilter(stgo_data, 'm3', cut, cloud_filter)
    stgo_data = mfilter(stgo_data, 'm4', cut, cloud_filter)

    return stgo_data

def mfilter(stgo_data, name, cut = 0, cloud_filter = 0):
    
    if cut == 0:
        xband = 30
    
    else:
        xband = 1.5
    
    dm1_max = []
    dm1_med = []
    dm1_min = []
    
    i_m1 = []
    m1_raw = []
    
    i_cloud = []
    
    for i in stgo_data:
        pd_date = pd.to_datetime(i['date'][0])
        lat = i['position'][0]
        lon = i['position'][1]
        alt = i['altitude']
        sp_frame = pv.solarposition.spa_python(pd_date, lat, lon, alt)
        zenith = sp_frame['zenith'][0]
        r = pv.solarposition.nrel_earthsun_distance(pd_date)
        m = pv.atmosphere.get_relative_airmass(zenith, model='young1994')
        i['r'] = r[0]
        i['m'] = m
    
    if cloud_filter != 0:
        for i in range(len(stgo_data)):
            delta = max(stgo_data[i][name])-min(stgo_data[i][name])
            if delta < 100:
                i_cloud.append(i)
    else:
        i_cloud = range(len(stgo_data))
    
    for i in i_cloud:
        pm1 = []
        for j in stgo_data[i][name]:
            if cloud_filter == 0:
                if j >= 50 and j <= 3800 :
                    pm1.append(j)
            else:
                if j >= 675 and j <= 3800 :
                    pm1.append(j)
                                
        if (len(pm1) != 0):
            i_m1.append(i)

    max_count = len(i_m1)-1
    if len(i_m1) != 0:
        for i in range(len(i_m1)):
            m1 =  []
            for j in stgo_data[i_m1[i]][name]:
                if j >= 50 and j <= 3800 :
                    m1.append(j)
                    
            if len(m1) == 3:
                m1_max = max(m1)
                m1_min = min(m1)
                m1_med = 0
                for j in m1:
                    if (j != m1_max) and (j != m1_min):
                        m1_med = j
                if m1_med == 0:
                    m1_med = sum(m1)/3
    
            elif len(m1) == 2:
                m1_max = max(m1)
                m1_min = min(m1)
                m1_med = sum(m1)/2
                    
            elif len(m1) == 1:
                m1_max = m1[0]
                m1_min = m1[0]
                m1_med = m1[0]
            
            m1_mes = [m1_max, m1_med, m1_min]
            m1_raw.append(m1_mes)
                    
            if i != 0 and i!=max_count:
                timestr_nm = stgo_data[i_m1[i-1]]['date'][0].split(' ')
                date_nm = timestr_nm[0].split('-')
                hour_nm = timestr_nm[1].split(':')
                time_nm = dt.datetime(int(date_nm[0]), int(date_nm[1]), int(date_nm[2]), int(hour_nm[0]), int(hour_nm[1]), int(hour_nm[2]))
    
                timestr_n = stgo_data[i_m1[i]]['date'][0].split(' ')
                date_n = timestr_n[0].split('-')
                hour_n = timestr_n[1].split(':')
                time_n = dt.datetime(int(date_n[0]), int(date_n[1]), int(date_n[2]), int(hour_n[0]), int(hour_n[1]), int(hour_n[2]))
                
                timestr_np = stgo_data[i_m1[i+1]]['date'][0].split(' ')
                date_np = timestr_np[0].split('-')
                hour_np = timestr_np[1].split(':')
                time_np = dt.datetime(int(date_np[0]), int(date_np[1]), int(date_np[2]), int(hour_np[0]), int(hour_np[1]), int(hour_np[2]))
        
                delta_t1 = dt.timedelta.total_seconds(time_n-time_nm)
                delta_t2 = dt.timedelta.total_seconds(time_np-time_n)
                mean_delta = (delta_t1+delta_t2)/2
                
                m1_m =  []
                m1_p =  []
                            
                for j in stgo_data[i_m1[i-1]][name]:
                    if j >= 50 and j <= 3800 :
                        m1_m.append(j)
    
                for j in stgo_data[i_m1[i+1]][name]:
                    if j >= 50 and j <= 3800 :
                        m1_p.append(j)                    
                
                if len(m1_m) == 3:
                    m1_mmax = max(m1_m)
                    m1_mmin = min(m1_m)
                    m1_mmed = 0
                    for j in m1_m:
                        if (j != m1_mmax) and (j != m1_mmin):
                            m1_mmed = j
                    if m1_mmed == 0:
                        m1_mmed = sum(m1)/3
                    
                elif len(m1_m) == 2:
                    m1_mmax = max(m1_m)
                    m1_mmin = min(m1_m)
                    m1_mmed = sum(m1_m)/2
                    
                elif len(m1_m) == 1:
                    m1_mmax = m1_m[0]
                    m1_mmin = m1_m[0]
                    m1_mmed = m1_m[0]
                                    
                if len(m1_p) == 3:
                    m1_pmax = max(m1_p)
                    m1_pmin = min(m1_p)
                    m1_pmed = 0
                    for j in m1_p:
                        if (j != m1_pmax) and (j != m1_pmin):
                            m1_pmed = j
                    if m1_pmed == 0:
                        m1_pmed = sum(m1)/3
                
                elif len(m1_p) == 2:
                    m1_pmax = max(m1_p)
                    m1_pmin = min(m1_p)
                    m1_pmed = sum(m1_p)/2
                    
                elif len(m1_p) == 1:
                    m1_pmax = m1_p[0]
                    m1_pmin = m1_p[0]
                    m1_pmed = m1_p[0]
                    
                dm1_max.append(((m1_pmax-m1_max)/delta_t2-(m1_max-m1_mmax)/delta_t1)/mean_delta)
                dm1_med.append(((m1_pmed-m1_med)/delta_t2-(m1_med-m1_mmed)/delta_t1)/mean_delta)
                dm1_min.append(((m1_pmin-m1_min)/delta_t2-(m1_min-m1_mmin)/delta_t1)/mean_delta)
            
            else: 
                dm1_max.append(0.0)
                dm1_med.append(0.0)
                dm1_min.append(0.0)
            
        qmax1 = np.percentile(dm1_max,25)
        qmax3 = np.percentile(dm1_max,75)
        
        dqmax = qmax3-qmax1
        ubmax = qmax3+xband*dqmax
        lbmax = qmax1-xband*dqmax
        
        qmed1 = np.percentile(dm1_med,25)
        qmed3 = np.percentile(dm1_med,75)
        
        dqmed = qmed3-qmed1
        ubmed = qmed3+xband*dqmed
        lbmed = qmed1-xband*dqmed
        
        qmin1 = np.percentile(dm1_min,25)
        qmin3 = np.percentile(dm1_min,75)
        
        dqmin = qmin3-qmin1
        ubmin = qmin3+xband*dqmin
        lbmin = qmin1-xband*dqmin
        
        for i in range(len(i_m1)):
            fm1 = []
            if (dm1_max[i] >= lbmax) and (dm1_max[i] <= ubmax):
                fm1.append(m1_raw[i][0])
            if (dm1_med[i] >= lbmed) and (dm1_med[i] <= ubmed):
                fm1.append(m1_raw[i][1])
            if (dm1_min[i] >= lbmin) and (dm1_min[i] <= ubmin):
                fm1.append(m1_raw[i][2])
            if fm1 != []:    
                stgo_data[i_m1[i]][name + '_filter'] = fm1
            
    return stgo_data

def aeronet_filter(aero_data):

    for data in aero_data:
        for key in data.keys():
            root = key[0:3]
            if root == '440':
                data[key] = float(data[key])
            elif root == 'AER':
                pass
            elif root == 'AOD':
                data[key] = float(data[key])
            elif root == 'NO2':
                data[key] = float(data[key])
            elif root == 'Opt':
                data[key] = float(data[key])
            elif root == 'Pre':
                data[key] = float(data[key])
            elif root == 'Ozo':
                data[key] = float(data[key])
            elif root == 'Sen':
                data[key] = float(data[key])
            elif root == 'Sit':
                data[key] = float(data[key])
            elif root == 'Sol':
                data[key] = float(data[key])
    return aero_data

def stgo_useful_data(stgo_data, sensor):
    m = []
    date = []
    seconds = []
    pressure = []
    altitude = []
    latitude = []
    longitude = []
    r = []
    air_mass = []

    for data in stgo_data:
        try:
            m.append(data[sensor + '_filter'])

            timestr_n = data['date'][0].split(' ')
            date_n = timestr_n[0].split('-')
            hour_n = timestr_n[1].split(':')
            ntime = dt.datetime(int(date_n[0]), int(date_n[1]), int(date_n[2]))
            time_n = dt.datetime(int(date_n[0]), int(date_n[1]), int(date_n[2]), int(hour_n[0]), int(hour_n[1]), int(hour_n[2]))
            date.append(time_n)
            seconds.append(dt.timedelta.total_seconds(time_n-ntime)-45)
            
            pressure.append(data['pressure'])
            
            altitude.append(data['altitude'])
            latitude.append(data['position'][0])
            longitude.append(data['position'][1])
            r.append(data['r'])
            air_mass.append(data['m'])
            
        except KeyError:
            pass
    return m, date, seconds, pressure, air_mass, r, altitude, np.mean(latitude), np.mean(longitude)
 
def aero_useful_data(aero_data):
    t1 = []
    amgstrom = []
    date = []
    seconds = []
    ozone = []
    latitude = []
    longitude = []

    for data in aero_data:
        try:
            aod = ['AOD_1020nm','AOD_1640nm','AOD_340nm','AOD_380nm','AOD_440nm','AOD_500nm','AOD_675nm','AOD_870nm']
            lamb = [1020,1640,340,380,440,500,675,870]
            #aod = ['AOD_380nm','AOD_440nm','AOD_500nm','AOD_675nm','AOD_870nm']
            #lamb = [380,440,500,675,870]
            temp_t1 = []
            ln_aod = []
            ln_lb = []
            amg = data['440-870_Angstrom_Exponent']
            
            for t in range(len(aod)):
                aot = data[aod[t]]
                wlgth = lamb[t]
                ln_aod.append(np.log(aot))
                ln_lb.append(np.log(wlgth*1e-3))
                temp_t1.append(np.exp(np.log(aot)+amg*np.log(wlgth*1e-3)))
            
            
            slope, intercept, r_value, p_value, std_err = stats.linregress(np.array(ln_lb), np.array(ln_aod))
            t1.append(np.exp(intercept))
            #print(-slope)
            #print(amg)
            #print(slope)
            
            amgstrom.append(amg)
            
            date_n = data['Date(dd:mm:yyyy)'].split(':')
            hour_n = data['Time(hh:mm:ss)'].split(':')
            ntime = dt.datetime(int(date_n[2]), int(date_n[1]), int(date_n[0]))
            time_n = dt.datetime(int(date_n[2]), int(date_n[1]), int(date_n[0]), int(hour_n[0]), int(hour_n[1]), int(hour_n[2]))
            
            date.append(time_n)
            seconds.append(dt.timedelta.total_seconds(time_n-ntime))
            
            ozone.append(data['Ozone(Dobson)'])
            
            latitude.append(data['Site_Latitude(Degrees)'])
            longitude.append(data['Site_Longitude(Degrees)'])
            
        except KeyError:
            print('Key problem')
    return t1, amgstrom, date, seconds, ozone, np.mean(latitude), np.mean(longitude)       

def aero_useful_data_v2(aero_data):
    t1 = []
    amgstrom = []
    date = []
    seconds = []
    ozone = []
    latitude = []
    longitude = []
    aero_air_mass = []

    for data in aero_data:
        try:
            aod = ['AOD_1020nm','AOD_1640nm','AOD_340nm','AOD_380nm','AOD_440nm','AOD_500nm','AOD_675nm','AOD_870nm']
            lamb = [1020,1640,340,380,440,500,675,870]
            #aod = ['AOD_380nm','AOD_440nm','AOD_500nm','AOD_675nm','AOD_870nm']
            #lamb = [380,440,500,675,870]
            row_t1 = []
            amg = data['440-870_Angstrom_Exponent']
            
            for t in range(len(aod)):
                aot = data[aod[t]]
                row_t1.append(aot)
            t1.append(row_t1)
        
            amgstrom.append(amg)
            
            date_n = data['Date(dd:mm:yyyy)'].split(':')
            hour_n = data['Time(hh:mm:ss)'].split(':')
            ntime = dt.datetime(int(date_n[2]), int(date_n[1]), int(date_n[0]))
            time_n = dt.datetime(int(date_n[2]), int(date_n[1]), int(date_n[0]), int(hour_n[0]), int(hour_n[1]), int(hour_n[2]))
            
            date.append(time_n)
            seconds.append(dt.timedelta.total_seconds(time_n-ntime))
            
            ozone.append(data['Ozone(Dobson)'])
            
            latitude.append(data['Site_Latitude(Degrees)'])
            longitude.append(data['Site_Longitude(Degrees)'])
            aero_air_mass.append(data['Optical_Air_Mass'])
            
        except KeyError:
            print('Key problem')
    return np.array(t1), np.array(lamb)*1e-3, np.array(amgstrom), date, seconds, ozone, np.mean(latitude), np.mean(longitude), np.array(aero_air_mass) 

def interpolate(m, pressure, altitude, airmass, r, seconds, aero_seconds):
    
    m1 = []
    m2 = []
    m3 = []
    for i in m:
        if len(i) == 3:
            m1.append(i[0])
            m2.append(i[1])
            m3.append(i[2])
        elif len(i) == 2:
            m1.append(i[0])
            m2.append(i[0])
            m3.append(i[1])
        elif len(i) == 1:
            m1.append(i[0])
            m2.append(i[0])
            m3.append(i[0])
            

    
    im1 = np.interp(aero_seconds, seconds, m1, left=0, right=0)
    im2 = np.interp(aero_seconds, seconds, m2, left=0, right=0)
    im3 = np.interp(aero_seconds, seconds, m3, left=0, right=0)
    apressure = np.interp(seconds, np.delete(seconds, np.where(np.isnan(pressure))), np.delete(pressure, np.where(np.isnan(pressure))))  
    ipressure = np.interp(aero_seconds, seconds, apressure, left=0, right=0)
    ialtitude = np.interp(aero_seconds, seconds, altitude, left=0, right=0)
    iairmass = np.interp(aero_seconds, seconds, airmass, left=0, right=0)
    ir = np.interp(aero_seconds, seconds, r, left=0, right=0)
    
    delv = np.where(iairmass==0)
    im1 = np.delete(im1,np.where(im1==0))
    im2 = np.delete(im2,np.where(im2==0))
    im3 = np.delete(im3,np.where(im3==0))
    ipressure = np.delete(ipressure,np.where(ipressure==0))
    ialtitude = np.delete(ialtitude,np.where(ialtitude==0))
    iairmass = np.delete(iairmass,np.where(iairmass==0))
    ir = np.delete(ir,np.where(ir==0))
    
    
    return im1, im2, im3, ipressure, ialtitude, iairmass, ir, delv

def aero_interpolate(m, seconds, aero_t1, amgs, ozone, aero_seconds):
    
    m1 = []
    m2 = []
    m3 = []
    for i in m:
        if len(i) == 3:
            m1.append(i[0])
            m2.append(i[1])
            m3.append(i[2])
        elif len(i) == 2:
            m1.append(i[0])
            m2.append(i[0])
            m3.append(i[1])
        elif len(i) == 1:
            m1.append(i[0])
            m2.append(i[0])
            m3.append(i[0])
    
    it1 = np.interp(seconds, aero_seconds, aero_t1, left=0, right=0)
    iamgs = np.interp(seconds, aero_seconds, amgs, left=0, right=0)
    iozone = np.interp(seconds, aero_seconds, ozone, left=0, right=0)
    delv = np.where(it1==0)
    it1 = np.delete(it1,np.where(it1==0))
    iamgs = np.delete(iamgs,np.where(iamgs==0))
    iozone = np.delete(iozone,np.where(iozone==0))
    
    return m1, m2, m3, it1, iamgs, iozone, delv 

def reyleigh(lmbd):
    if lmbd <= 0.5:
        a = 6.50362e-3
        b = 3.55212
        c = 1.35579
        d = 0.11563
    elif lmbd > 0.5:
        a = 8.64627e-3
        b = 3.99668
        c = 1.10298e-3
        d = 2.71393e-2
    
    return np.around(a*(lmbd)**(-(b+c*lmbd+d/lmbd)),3)

def amgstrom_interpolation(lamb2, amgs, tau):
    aero_lamb = np.array([1020,1640,340,380,440,500,675,870])*1e-3
    idx = (np.abs(aero_lamb - lamb2)).argmin()
    return np.round(tau[:,idx]*(lamb2/aero_lamb[idx])**(-amgs),3)   
    
def rmse_calibration(x):
    """
    x=[lambda, v0, eta]
    """
    return np.sqrt(np.sum(((amgstrom_interpolation(x[0],alpha,tau1))-((np.log(x[1]/(res**2))-np.log(v-4)-reyleigh(x[0])*(p/1013.25)*am-got_o3(ozo,x[0],ozo_model)*am)/am))**2)/len(v))

def rmse_calibrationv3(x):
    """
    x=[lambda, v0, eta]
    """
    return np.sqrt(np.sum(((amgstrom_interpolation(x[0],alpha,tau1))-((np.log(x[1]/(res**2))-np.log(v-4)-reyleigh(x[0])*(p/1013.25)*am)/am))**2)/len(v))

def stgo_aod(x,earth_sun_dis,vmeasure,press, air_mass, ozone):
    return ((np.log(x[1]/(earth_sun_dis**2))-np.log(vmeasure)-reyleigh(x[0])*(press/1013.25)*air_mass-got_o3(ozone,x[0],ozo_model)*air_mass)/air_mass)

def stgo_aodv3(x,earth_sun_dis,vmeasure,press, air_mass):
    return ((np.log(x[1]/(earth_sun_dis**2))-np.log(vmeasure)-reyleigh(x[0])*(press/1013.25)*air_mass)/air_mass)

def aero_aod(x, tau, alpha_amg):
    return tau*x[0]**(-alpha_amg)
           
if __name__ == "__main__":
    stgo_units = ['001','002','003','004','005','008','009','010']
    ozo_model = load_ozone_model()
    for stgo_unit in stgo_units:
        #stgo_unit = '010'
        aero_unit = '835'
        aero_unit2 = '760'
        
        cal_date1 = []
        cal_date2 = []
        cal_date3 = []
        cal_date4 = []
        x1 =[]
        x11 = []
        x2 =[]
        x12 = []
        x3 =[]
        x13 = []
        x4 =[]
        x14 = []
        
        datei = dt.datetime(2020, 1, 1)
        
        while datei != dt.datetime(2021, 1, 1):
            
            day = datei.day
            month = datei.month
            year = datei.year
            
            x0 = [0.5, 2047.0]
            x01 = [[1.02, 2047.0],[1.64, 2047.0],[0.34, 2047.0],[0.38, 2047.0],
                  [0.44, 2047.0],[0.6, 2047.0], [0.5, 2047.0], [0.675, 2047.0], 
                  [0.87, 2047.0]]
            
            if stgo_unit == '010':
                cut = 0
                cloud_filter = 1
            else:
                cut = 1
                cloud_filter = 0    
        
            date_day = dt.date(year, month, day)
            
            stgo_data = load_stgo_data(stgo_unit, date_day)
            aero_data = load_aero_data(aero_unit, date_day)
            aero_data2 = load_aero_data(aero_unit2, date_day)
                    
            if (stgo_data != []) and (aero_data != []):
                 
                stgo_data = stgo_filter(stgo_data, cut, cloud_filter)
                aero_data = aeronet_filter(aero_data)
                aero_data2 = aeronet_filter(aero_data2)
                    
                m1, date1, seconds1, pressure1, airmass1, r1, altitude1, latitude1, longitude1 = stgo_useful_data(stgo_data, 'm1')
                m2, date2, seconds2, pressure2, airmass2, r2, altitude2, latitude2, longitude2 = stgo_useful_data(stgo_data, 'm2')
                m3, date3, seconds3, pressure3, airmass3, r3, altitude3, latitude3, longitude3 = stgo_useful_data(stgo_data, 'm3')
                m4, date4, seconds4, pressure4, airmass4, r4, altitude4, latitude4, longitude4 = stgo_useful_data(stgo_data, 'm4')
                
                t1, aero_lamb, amgstrom, aero_date, aero_seconds, ozone, aero_latitude, aero_longitude, aero_air_mass = aero_useful_data_v2(aero_data)
                t12, aero_lamb2, amgstrom2, aero_date2, aero_seconds2, ozone2, aero_latitude2, aero_longitude2, aero_air_mass2 = aero_useful_data_v2(aero_data2)
                
                if (np.abs(aero_latitude-latitude1)<0.005) and (np.abs(aero_longitude-longitude1)<0.005):
                
                    print('unidad '+ stgo_unit +' Tiene datos de calibracion '+ str(day) +'/'+ str(month) + '/' + str(year))
                    if m1 != []:
                        m11, m12, m13, ipressure1, ialtitude1, iairmass1, ir1, del1 = interpolate(m1, pressure1, altitude1, airmass1, r1, seconds1, aero_seconds)
                    if m2 != []:
                        m21, m22, m23, ipressure2, ialtitude2, iairmass2, ir2, del2 = interpolate(m2, pressure2, altitude2, airmass2, r2, seconds2, aero_seconds)
                    if m3 != []:
                        m31, m32, m33, ipressure3, ialtitude3, iairmass3, ir3, del3 = interpolate(m3, pressure3, altitude3, airmass3, r3, seconds3, aero_seconds)
                    if m4 != []:
                        m41, m42, m43, ipressure4, ialtitude4, iairmass4, ir4, del4 = interpolate(m4, pressure4, altitude4, airmass4, r4, seconds4, aero_seconds)
    
                    if stgo_unit == '010':
                        if m1 != []:
                            dt1 = np.delete(t1,del1,0)
                            damg = np.delete(amgstrom,del1)
                            dozo = np.delete(ozone,del1)
                            tau1 = np.concatenate([dt1,dt1,dt1])
                            alpha = np.concatenate([damg, damg, damg])
                            v = np.concatenate([m11,m12,m13])
                            res = np.concatenate([ir1,ir1,ir1])
                            p = np.concatenate([ipressure1,ipressure1,ipressure1])
                            am = np.concatenate([iairmass1,iairmass1,iairmass1])
                            ozo = np.concatenate([dozo,dozo,dozo])
                            #plt.plot(v)
                            
                            for x in x01:
                                cal_date1.append(str(datei))
                                
                                response1 = minimize(rmse_calibrationv3, x, method = 'nelder-mead', options ={'disp':True})
                                if response1.fun < 0.4:
                                    x1.append(response1.x)
                                else:
                                    x1.append(np.array([0,0]))
                            
                                response12 = minimize(rmse_calibration, x, method = 'nelder-mead', options ={'disp':True})
                                if response12.fun < 0.4:
                                    x11.append(response12.x)
                                else:
                                    x1.append(np.array([0,0]))
                                    
                        if m2 != []:
                            dt2 = np.delete(t1,del2,0)
                            damg = np.delete(amgstrom,del2)
                            dozo = np.delete(ozone,del2)
                            tau1 = np.concatenate([dt2,dt2,dt2])
                            alpha = np.concatenate([damg, damg, damg])
                            v = np.concatenate([m21,m22,m23])
                            res = np.concatenate([ir2,ir2,ir2])
                            p = np.concatenate([ipressure2,ipressure2,ipressure2])
                            am = np.concatenate([iairmass2,iairmass2,iairmass2])
                            ozo = np.concatenate([dozo,dozo,dozo])
                            #plt.plot(v)
                            
                            for x in x01:
                                cal_date2.append(str(datei))
                                
                                response2 = minimize(rmse_calibrationv3, x, method = 'nelder-mead', options ={'disp':True})    
                                if response2.fun < 0.4:
                                    x2.append(response2.x)
                                else:
                                    x2.append(np.array([0,0]))
                            
                                response22 = minimize(rmse_calibration, x, method = 'nelder-mead', options ={'disp':True})
                                if response22.fun < 0.4:
                                    x12.append(response22.x)
                                else:
                                    x12.append(np.array([0,0]))
                        
                        if m3 != []:
                            dt3 = np.delete(t1,del3,0)
                            damg = np.delete(amgstrom,del3)
                            dozo = np.delete(ozone,del3)
                            tau1 = np.concatenate([dt3,dt3,dt3])
                            alpha = np.concatenate([damg, damg, damg])
                            v = np.concatenate([m31,m32,m33])
                            res = np.concatenate([ir3,ir3,ir3])
                            p = np.concatenate([ipressure3,ipressure3,ipressure3])
                            am = np.concatenate([iairmass3,iairmass3,iairmass3])
                            ozo = np.concatenate([dozo,dozo,dozo])
                            #plt.plot(v)
                            
                            for x in x01:
                                cal_date3.append(str(datei))
                                
                                response3 = minimize(rmse_calibrationv3, x, method = 'nelder-mead', options ={'disp':True})
                                if response3.fun < 0.4:
                                    x3.append(response3.x)
                                else:
                                    x3.append(np.array([0,0]))
                                response32 = minimize(rmse_calibration, x, method = 'nelder-mead', options ={'disp':True})
                                if response32.fun < 0.4:
                                    x13.append(response32.x)
                                else:
                                    x13.append(np.array([0,0]))
                        
                        if m4 != []:
                            dt4 = np.delete(t1,del4,0)
                            damg = np.delete(amgstrom,del4)
                            dozo = np.delete(ozone,del4)
                            tau1 = np.concatenate([dt4,dt4,dt4])
                            alpha = np.concatenate([damg, damg, damg])
                            v = np.concatenate([m41,m42,m43])
                            res = np.concatenate([ir4,ir4,ir4])
                            p = np.concatenate([ipressure4,ipressure4,ipressure4])
                            am = np.concatenate([iairmass4,iairmass4,iairmass4])
                            ozo = np.concatenate([dozo,dozo,dozo])
                            #plt.plot(v)
                        
                            for x in x01:
                                cal_date4.append(str(datei))
                                
                                response4 = minimize(rmse_calibrationv3, x, method = 'nelder-mead', options ={'disp':True})
                                if response4.fun < 0.4:
                                    x4.append(response4.x)
                                else:
                                    x4.append(np.array([0,0]))
                                    
                                response42 = minimize(rmse_calibration, x, method = 'nelder-mead', options ={'disp':True})
                                if response42.fun < 0.4:
                                    x14.append(response42.x)
                                else:
                                    x14.append(np.array([0,0]))
                        
                    else:
                        if m1 != []:
                            dt1 = np.delete(t1,del1,0)
                            damg = np.delete(amgstrom,del1)
                            dozo = np.delete(ozone,del1)
                            tau1 = dt1
                            alpha = damg
                            v = m11
                            res = ir1
                            p = ipressure1
                            am = iairmass1
                            ozo = dozo
                            #plt.plot(v)
                            
                            for x in x01:
                                cal_date1.append(str(datei))
                                
                                response1 = minimize(rmse_calibrationv3, x, method = 'nelder-mead', options ={'disp':True})
                                if response1.fun < 0.4:
                                    x1.append(response1.x)
                                else:
                                    x1.append(np.array([0,0]))
                        
                                response12 = minimize(rmse_calibration, x, method = 'nelder-mead', options ={'disp':True})
                                if response12.fun < 0.4:
                                    x11.append(response12.x)
                                else:
                                    x11.append(np.array([0,0]))
                        
                        if m2 != []:
                            dt2 = np.delete(t1,del2,0)
                            damg = np.delete(amgstrom,del2)
                            dozo = np.delete(ozone,del2)
                            tau1 = dt2
                            alpha = damg
                            v = m21
                            res = ir2
                            p = ipressure2
                            am = iairmass2
                            ozo = dozo
                            #plt.plot(v)
                            
                            for x in x01:
                                cal_date2.append(str(datei))
                                
                                response2 = minimize(rmse_calibrationv3, x, method = 'nelder-mead', options ={'disp':True})
                                if response2.fun < 0.4:
                                    x2.append(response2.x)
                                else:
                                    x2.append(np.array([0,0]))
                                
                                response22 = minimize(rmse_calibration, x, method = 'nelder-mead', options ={'disp':True})
                                if response22.fun < 0.4:
                                    x12.append(response22.x)
                                else:
                                    x12.append(np.array([0,0]))
                        
                        if m3 != []:
                            dt3 = np.delete(t1,del3,0)
                            damg = np.delete(amgstrom,del3)
                            dozo = np.delete(ozone,del3)
                            tau1 = dt3
                            alpha = damg
                            v = m31
                            res = ir3
                            p = ipressure3
                            am = iairmass3
                            ozo = dozo
                            #plt.plot(v)
                            
                            for x in x01:
                                cal_date3.append(str(datei))
                                
                                response3 = minimize(rmse_calibrationv3, x, method = 'nelder-mead', options ={'disp':True})
                                if response3.fun < 0.4:
                                    x3.append(response3.x)
                                else:
                                    x3.append(np.array([0,0]))
                                
                                response32 = minimize(rmse_calibration, x, method = 'nelder-mead', options ={'disp':True})
                                if response32.fun < 0.4:
                                    x13.append(response32.x)
                                else:
                                    x13.append(np.array([0,0]))
                                    
                        if m4 != []:
                            dt4 = np.delete(t1,del4,0)
                            damg = np.delete(amgstrom,del4)
                            dozo = np.delete(ozone,del4)
                            tau1 = dt4
                            alpha = damg
                            v = m41
                            res = ir4
                            p = ipressure4
                            am = iairmass4
                            ozo = dozo
                            #plt.plot(v)
                            
                            for x in x01:
                                cal_date4.append(str(datei))
                                
                                response4 = minimize(rmse_calibrationv3, x, method = 'nelder-mead', options ={'disp':True})
                                if response4.fun < 0.4:
                                    x4.append(response4.x)
                                else:
                                    x4.append(np.array([0,0]))
                                
                                response42 = minimize(rmse_calibration, x, method = 'nelder-mead', options ={'disp':True})
                                if response42.fun < 0.4:
                                    x14.append(response42.x)
                                else:
                                    x14.append(np.array([0,0]))
                
                
                
                    # aod_11 = stgo_aod(x11[0], ir1, m11, ipressure1, iairmass1, np.delete(ozone,del1))
                    # aod_12 = stgo_aod(x11[0], ir1, m12, ipressure1, iairmass1, np.delete(ozone,del1))
                    # aod_13 = stgo_aod(x11[0], ir1, m13, ipressure1, iairmass1, np.delete(ozone,del1))
                    
                    # aod_211 = stgo_aodv3(x1[0], ir1, m11, ipressure1, iairmass1)
                    # aod_221 = stgo_aodv3(x1[0], ir1, m12, ipressure1, iairmass1)
                    # aod_231 = stgo_aodv3(x1[0], ir1, m13, ipressure1, iairmass1)
                    
                    # time_1 = np.delete(np.array(aero_date),del1)
                
                    # aero_aod1 = amgstrom_interpolation(x11[0][0], amgstrom, t1)
                    
                    # plt.figure()
                    # plt.plot(np.array(aero_date), aero_aod1) 
                    # plt.plot(time_1, aod_11)
                
                    # plt.figure()
                    # plt.plot(np.array(aero_date), aero_aod1) 
                    # plt.plot(time_1, aod_11, time_1, aod_12, time_1, aod_13)
                
                
                    # aod_21 = stgo_aod(x12[0], ir2, m21, ipressure2, iairmass2, np.delete(ozone,del2))
                    # aod_22 = stgo_aod(x12[0], ir2, m22, ipressure2, iairmass2, np.delete(ozone,del2))
                    # aod_23 = stgo_aod(x12[0], ir2, m23, ipressure2, iairmass2, np.delete(ozone,del2))
                    
                    # aod_212 = stgo_aodv3(x2[0], ir2, m21, ipressure2, iairmass2)
                    # aod_222 = stgo_aodv3(x2[0], ir2, m22, ipressure2, iairmass2)
                    # aod_232 = stgo_aodv3(x2[0], ir2, m23, ipressure2, iairmass2)
                    
                    # time_2 = np.delete(np.array(aero_date),del2)
                
                    # aero_aod2 = amgstrom_interpolation(x12[0][0], amgstrom, t1)
                    
                    # plt.figure()
                    # plt.plot(np.array(aero_date), aero_aod2) 
                    # plt.plot(time_2, aod_21)
                    
                    # plt.figure()
                    # plt.plot(np.array(aero_date), aero_aod2) 
                    # plt.plot(time_2, aod_21, time_2, aod_22, time_2, aod_23)
                
                    # aod_31 = stgo_aod(x13[0], ir3, m31, ipressure3, iairmass3, np.delete(ozone,del3))
                    # aod_32 = stgo_aod(x13[0], ir3, m32, ipressure3, iairmass3, np.delete(ozone,del3))
                    # aod_33 = stgo_aod(x13[0], ir3, m33, ipressure3, iairmass3, np.delete(ozone,del3))
                    
                    # aod_213 = stgo_aodv3(x3[0], ir3, m31, ipressure3, iairmass3)
                    # aod_223 = stgo_aodv3(x3[0], ir3, m32, ipressure3, iairmass3)
                    # aod_233 = stgo_aodv3(x3[0], ir3, m33, ipressure3, iairmass3)
                    
                    # time_3 = np.delete(np.array(aero_date),del3)
                
                    # aero_aod3 = amgstrom_interpolation(x13[0][0], amgstrom, t1)
                    
                    # plt.figure()
                    # plt.plot(np.array(aero_date), aero_aod3) 
                    # plt.plot(time_3, aod_31)
                    
                    # plt.figure()
                    # plt.plot(np.array(aero_date), aero_aod3) 
                    # plt.plot(time_3, aod_31, time_3, aod_32, time_3, aod_33)
                
                    # aod_41 = stgo_aod(x14[0], ir4, m41, ipressure4, iairmass4, np.delete(ozone,del4))
                    # aod_42 = stgo_aod(x14[0], ir4, m42, ipressure4, iairmass4, np.delete(ozone,del4))
                    # aod_43 = stgo_aod(x14[0], ir4, m43, ipressure4, iairmass4, np.delete(ozone,del4))
                    
                    # aod_214 = stgo_aodv3(x4[0], ir4, m41, ipressure4, iairmass4)
                    # aod_224 = stgo_aodv3(x4[0], ir4, m42, ipressure4, iairmass4)
                    # aod_234 = stgo_aodv3(x4[0], ir4, m43, ipressure4, iairmass4)
                    
                    # time_4 = np.delete(np.array(aero_date),del4)
                
                    # aero_aod4 = amgstrom_interpolation(x14[0][0], amgstrom, t1)
                    
                    # plt.figure()
                    # plt.plot(np.array(aero_date), aero_aod4) 
                    # plt.plot(time_4, aod_41)
                    
                    # plt.figure()
                    # plt.plot(np.array(aero_date), aero_aod4) 
                    # plt.plot(time_4, aod_41, time_4, aod_42, time_4, aod_43)
                    
                    # print(x1)
                    # print(x11)
                    # print(x2)
                    # print(x12)
                    # print(x3)
                    # print(x13)
                    # print(x4)
                    # print(x14)
                    # print(np.mean(ozone))
                    
                    # aod0 = np.interp(aero_seconds, aero_seconds2, t12[:,0])
                    # aod1 = np.interp(aero_seconds, aero_seconds2, t12[:,1])
                    # aod2 = np.interp(aero_seconds, aero_seconds2, t12[:,2])
                    # aod3 = np.interp(aero_seconds, aero_seconds2, t12[:,3])
                    # aod4 = np.interp(aero_seconds, aero_seconds2, t12[:,4])
                    # aod5 = np.interp(aero_seconds, aero_seconds2, t12[:,5])
                    # aod6 = np.interp(aero_seconds, aero_seconds2, t12[:,6])
                    # aod7 = np.interp(aero_seconds, aero_seconds2, t12[:,7])
                    
                    # slope0, intercept0 = np.polyfit(t1[:,0], aod0,1)
                    # slope1, intercept1 = np.polyfit(t1[:,1], aod1,1)
                    # slope2, intercept2 = np.polyfit(t1[:,2], aod2,1)
                    # slope3, intercept3 = np.polyfit(t1[:,3], aod3,1)
                    # slope4, intercept4 = np.polyfit(t1[:,4], aod4,1)
                    # slope5, intercept5 = np.polyfit(t1[:,5], aod5,1)
                    # slope6, intercept6 = np.polyfit(t1[:,6], aod6,1)
                    # slope7, intercept7 = np.polyfit(t1[:,7], aod7,1)
                    
                    # fig, ax = plt.subplots()
                    # plt.xlabel('Cimel 760')
                    # plt.ylabel('Cimel 835')
                    # plt.title('Scatter plot Cimel 835 v/s Cimel 760')
                    # ax.plot(t1[:,0],aod0,'.', label='1020 nm y='+str(slope0)[0:4]+'x+'+str(intercept0)[0:3], color = 'darkgray')
                    # ax.plot(t1[:,1],aod1,'.', label='1640 nm y='+str(slope1)[0:4]+'x+'+str(intercept1)[0:3], color = 'black')
                    # ax.plot(t1[:,2],aod2,'.', label='340 nm y='+str(slope2)[0:4]+'x+'+str(intercept2)[0:3], color = 'indigo')
                    # ax.plot(t1[:,3],aod3,'.', label='380 nm y='+str(slope3)[0:4]+'x+'+str(intercept3)[0:3], color = 'orchid')
                    # ax.plot(t1[:,4],aod4,'.', label='440 nm y='+str(slope4)[0:4]+'x+'+str(intercept4)[0:3], color = 'royalblue')
                    # ax.plot(t1[:,5],aod5,'.', label='500 nm y='+str(slope5)[0:4]+'x+'+str(intercept5)[0:3], color = 'green')
                    # ax.plot(t1[:,6],aod6,'.', label='675 nm y='+str(slope6)[0:4]+'x+'+str(intercept6)[0:3], color = 'orange')
                    # ax.plot(t1[:,7],aod7,'.', label='870 nm y='+str(slope7)[0:4]+'x+'+str(intercept7)[0:3], color = 'red')
                    
                    # ax.plot(t1[:,0],t1[:,0]*slope0+intercept0, color='darkgray')
                    # ax.plot(t1[:,1],t1[:,1]*slope1+intercept1, color='black')
                    # ax.plot(t1[:,2],t1[:,2]*slope2+intercept2, color='indigo')
                    # ax.plot(t1[:,3],t1[:,3]*slope3+intercept3, color='orchid')
                    # ax.plot(t1[:,4],t1[:,4]*slope4+intercept4, color='royalblue')
                    # ax.plot(t1[:,5],t1[:,5]*slope5+intercept5, color='green')
                    # ax.plot(t1[:,6],t1[:,6]*slope6+intercept6, color='orange')
                    # ax.plot(t1[:,7],t1[:,7]*slope7+intercept7, color='red')
                    # legend = ax.legend()
                    # ax.grid()
                else:
                    print('unidad '+ stgo_unit +' lejos de intrumento patron '+ str(day) +'/'+ str(month) + '/' + str(year))
            else:
                if stgo_data == []:
                    print('unidad '+ stgo_unit +' No tiene datos '+ str(day) +'/'+ str(month) + '/' + str(year))
                elif aero_data == []:
                    print('unidad '+ aero_unit +' No tiene datos '+ str(day) +'/'+ str(month) + '/' + str(year))
                else:
                    print('Error deconcoido de datos '+ str(day) +'/'+ str(month) + '/' + str(year))
        
            datei += dt.timedelta(days = 1)            
            
        cal_date1 = np.array(cal_date1)
        cal_date2 = np.array(cal_date2)
        cal_date3 = np.array(cal_date3)
        cal_date4 = np.array(cal_date4)
        x1 = np.array(x1)
        x11 = np.array(x11)
        x2 = np.array(x2)
        x12 = np.array(x12)
        x3 = np.array(x3)
        x13 = np.array(x13)
        x4 = np.array(x4)
        x14 = np.array(x14)
        
        cal_struct = {'date1': np.ndarray.tolist(cal_date1),'x1_v3': np.ndarray.tolist(x1),'x1': np.ndarray.tolist(x11),
                      'date2': np.ndarray.tolist(cal_date2),'x2_v3': np.ndarray.tolist(x2),'x2': np.ndarray.tolist(x12),
                      'date3': np.ndarray.tolist(cal_date3),'x3_v3': np.ndarray.tolist(x3),'x3': np.ndarray.tolist(x13),
                      'date4': np.ndarray.tolist(cal_date4),'x4_v3': np.ndarray.tolist(x4),'x4': np.ndarray.tolist(x14)}
        
        with open('Code/../../Calibration/'+ stgo_unit +'.json', "w") as outfile:  
            json.dump(cal_struct, outfile) 