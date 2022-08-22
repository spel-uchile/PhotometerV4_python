# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 19:21:58 2020

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

global tau1
global alpha
global v
global res
global p
global am
global ozo
global ozo_model
global ozo_mu


def load_ozone_model():
    with open('Code/../../Ozono/absortion.json', 'r') as file:
        json_file = json.load(file)
    r_struc = np.array(json_file)
    return r_struc

def got_o3(dobson, lamb0, struct):
    return np.round(np.interp(lamb0, struct[:,0], struct[:,1], left= 0, right= 0)*dobson*1e-3,3)

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
    
    r_earth = 6371
    
    if cut == 0:
        xband = 3
    
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
        
        h = 26-0.1*np.abs(lat)
        
        v =(r_earth+alt*1e-3)**2/(r_earth+h)**2
        
        i['mu'] = 1/np.sqrt(1-v*np.sin(zenith*np.pi/180)**2)
    
    if cloud_filter != 0:
        for i in range(len(stgo_data)):
            delta = max(stgo_data[i][name])-min(stgo_data[i][name])
            if delta < 75:
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
                if j >= 100 and j <= 3800 :
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
    temperature = []
    amu = []

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
            amu.append(data['mu'])
            temperature.append(data['temperature'])
            
        except KeyError:
            pass
    return m, date, seconds, pressure, air_mass, amu, r, altitude, temperature, np.mean(latitude), np.mean(longitude)
 
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

def interpolate(m, pressure, altitude, airmass, amu, r, seconds, aero_seconds):
    
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
    iamu = np.interp(aero_seconds, seconds, amu, left=0, right=0)
    ir = np.interp(aero_seconds, seconds, r, left=0, right=0)
    
    delv = np.where(iairmass==0)
    im1 = np.delete(im1,np.where(im1==0))
    im2 = np.delete(im2,np.where(im2==0))
    im3 = np.delete(im3,np.where(im3==0))
    ipressure = np.delete(ipressure,np.where(ipressure==0))
    ialtitude = np.delete(ialtitude,np.where(ialtitude==0))
    iairmass = np.delete(iairmass,np.where(iairmass==0))
    iamu = np.delete(iamu,np.where(iamu==0))
    ir = np.delete(ir,np.where(ir==0))
    
    
    return im1, im2, im3, ipressure, ialtitude, iairmass, iamu, ir, delv

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
    
    return np.round(a*(lmbd)**(-(b+c*lmbd+d/lmbd)),3)

def amgstrom_interpolation(lamb2, amgs, tau):
    aero_lamb = np.array([1020,1640,340,380,440,500,675,870])*1e-3
    idx = (np.abs(aero_lamb - lamb2)).argmin()
    return np.round(tau[:,idx]*(lamb2/aero_lamb[idx])**(-amgs),3)   

def rmse_calibration(x):
    """
    x=[lambda, v0, eta]
    """
    return np.sqrt(np.sum(((amgstrom_interpolation(x[0],alpha,tau1))-((np.log(x[1]/(res**2))-np.log(v-4)-reyleigh(x[0])*(p/1013.25)*am-got_o3(ozo,x[2],ozo_model)*ozo_mu)/am))**2)/len(v))

def rmse_calibrationv3(x):
    """
    x=[lambda, v0, eta]
    """
    return np.sqrt(np.sum(((amgstrom_interpolation(x[0],alpha,tau1))-((np.log(x[1]/(res**2))-np.log(v-4)-reyleigh(x[0])*(p/1013.25)*am)/am))**2)/len(v))

def stgo_aod(x,earth_sun_dis,vmeasure,press, air_mass, mu, ozone):
    return ((np.log(x[1]/(earth_sun_dis**2))-np.log(vmeasure)-reyleigh(x[0])*(press/1013.25)*air_mass-got_o3(ozone,x[2],ozo_model)*mu)/air_mass)

def stgo_aodv3(x,earth_sun_dis,vmeasure,press, air_mass):
    return ((np.log(x[1]/(earth_sun_dis**2))-np.log(vmeasure)-reyleigh(x[0])*(press/1013.25)*air_mass)/air_mass)

def aero_aod(x, tau, alpha_amg):
    return tau*x[0]**(-alpha_amg)

def plot_day(unit, time, m_mean,  m_max = [], m_min = [], aero_time= [], aero_data=[], sensor = ' No Identified '):
    
    if len(m_mean) != 0:
    
        fig,ax = plt.subplots(figsize=(12.8,9.6))
            
        if (len(m_max) != 0) and (len(m_min) != 0):
            ax.errorbar(time, m_mean, yerr=[m_mean-m_min,m_max-m_mean], fmt='.-')
        else: 
            ax.errorbar(time, m_mean, fmt='.-')
                            
        if (len(aero_time) != 0) and (len(aero_data) != 0):
            ax.errorbar(np.array(aero_time), aero_data, fmt='k.-')
            
        fig.autofmt_xdate()
        
        ax.set_ylim(0.0,0.52)
        ax.grid(True)
        
        ax.set_title(unit +' '+sensor+' '+str(time[0])[0:10])
        plt.savefig('Code/../../Out/AOD_FIG/'+ unit + ' ' + sensor + ' ' + str(time[0])[0:10] + '.png')
        
        with open('Code/../../Out/AOD_CSV/'+ unit + ' ' + sensor + ' ' + str(time[0])[0:10] + '.csv', 'w', newline = '') as csvfile:
            csvwriter = csv.writer(csvfile)
            if (len(m_max) != 0) and (len(m_min) != 0):
                csvwriter.writerow(['Sensor AOD'])
                aod_csv = np.array([time, m_max, m_mean, m_min])
                aod_csv = aod_csv.tolist()
                
                for i in range(len(aod_csv[0])):
                    csvwriter.writerow([aod_csv[0][i], aod_csv[1][i], aod_csv[2][i], aod_csv[3][i]])               
                    
            else:
                csvwriter.writerow(['Sensor AOD'])
                aod_csv = np.array([time, m_mean])
                aod_csv = aod_csv.tolist()
                
                for i in range(len(aod_csv[0])):
                    csvwriter.writerow([aod_csv[0][i], aod_csv[1][i]])               
                            
            if (len(aero_time) != 0) and (len(aero_data) != 0):
                csvwriter.writerow(['AERONET AOD'])
                aero_csv = np.array([np.array(aero_time), aero_data])
                aero_csv = aero_csv.tolist()

                for i in range(len(aero_csv[0])):
                    csvwriter.writerow([aero_csv[0][i], aero_csv[1][i]])                
    return True

def plot_hist(unit, data, sensor = ' No Identified '):

    fig,ax = plt.subplots(figsize=(12.8,9.6))
    
    ax.hist(data, bins = int(np.sqrt(len(data))))
    ax.grid(True)
        
    ax.set_title(unit + ' histogram ' + sensor)
    plt.savefig('Code/../../Out/RMSE/'+ unit + ' ' + sensor + ' histogram.png')
        
    return True

if __name__ == "__main__":
    stgo_unit = '010'
    aero_unit = '835'
    aero_unit2 = '760'
    ozo_model = load_ozone_model()
    
    with open('Code/../../Calibration/'+ stgo_unit +'.json', 'r') as file:
        json_file = json.load(file)
        #r_struc = np.array(json_file)
        print(stgo_unit)
        
        #if True:
        lb = 0.35
        ub = 0.75
        
        x1 = np.array(json_file['x1'])
        d1 = np.array(json_file['date1'])
        x2 = np.array(json_file['x2'])
        d2 = np.array(json_file['date2'])
        x3 = np.array(json_file['x3'])
        d3 = np.array(json_file['date3'])
        x4 = np.array(json_file['x4'])
        d4 = np.array(json_file['date4'])
        
        if len(x1) != 0:
            x10 = x1[:,0]
            x11 = x1[:,1]
            x12 = x1[:,2]
            
            x1fl = x10 > lb
            x1fu = x10 < ub
            x1f = np.logical_and(x1fl,x1fu)
            chk1 = len(x10[x1f])
                                
            print('x1')
            print(chk1/8)
            if chk1 != 0:
                x10m = np.median(x10[x1f])
                x10a = np.mean(x10[x1f])
                x11m = np.median(x11[x1f])
                x11a = np.mean(x11[x1f])
                x12m = np.median(x12[x1f])
                x12a = np.mean(x12[x1f])
                
                v11 =[x10m, x11m, x12m]
                v12 =[x10a, x11a, x12a]
                

                print(x10m)
                print(x10a)
                print(x11m)
                print(x11a)
                print(x12m)
                print(x12a)
                                    
            else:
                print(stgo_unit +' Sensor 1 no tiene datos de calibración')

        else:
            chk1 = 0
            print(stgo_unit +' Sensor 1 no tiene datos')
            
        if len(x2) != 0:
            x20 = x2[:,0]
            x21 = x2[:,1]
            x22 = x2[:,2]
            
            x2fl = x20 > lb
            x2fu = x20 < ub
            x2f = np.logical_and(x2fl,x2fu)
            chk2 = len(x20[x2f])
            
            print('x2')
            print(chk2/8)
            if chk2 != 0:
                x20m = np.median(x20[x2f])
                x20a = np.mean(x20[x2f])
                x21m = np.median(x21[x2f])
                x21a = np.mean(x21[x2f])
                x22m = np.median(x22[x2f])
                x22a = np.mean(x22[x2f])
                
                v21 =[x20m, x21m, x22m]
                v22 =[x20a, x21a, x22a]
                
                print(x20m)
                print(x20a)
                print(x21m)
                print(x21a)
                print(x22m)
                print(x22a)
              
            else:
                print(stgo_unit +' Sensor 2 no tiene datos de calibración') 

        else:
            chk2 = 0
            print(stgo_unit +' Sensor 2 no tiene datos')                    

        if len(x3) != 0:
            x30 = x3[:,0]
            x31 = x3[:,1]
            x32 = x3[:,2]
            
            x3fl = x30 > lb
            x3fu = x30 < ub
            x3f = np.logical_and(x3fl,x3fu)
            chk3 = len(x30[x3f])
            
            print('x3')
            print(chk3/8)
            if chk3 != 0:
                x30m = np.median(x30[x3f])
                x30a = np.mean(x30[x3f])
                x31m = np.median(x31[x3f])
                x31a = np.mean(x31[x3f])
                x32m = np.median(x32[x3f])
                x32a = np.mean(x32[x3f])
                
                v31 =[x30m, x31m, x32m]
                v32 =[x30a, x31a, x32a]
                
                print(x30m)
                print(x30a)
                print(x31m)
                print(x31a)
                print(x32m)
                print(x32a)
 
            else:
                print(stgo_unit +' Sensor 3 no tiene datos de calibración')               
 
        else:
            chk3 = 0
            print(stgo_unit +' Sensor 3 no tiene datos')
            
        if len(x4) != 0:
            x40 = x4[:,0]
            x41 = x4[:,1]
            x42 = x4[:,2]
            
            x4fl = x40 > lb
            x4fu = x40 < ub
            x4f = np.logical_and(x4fl,x4fu)
            chk4 = len(x40[x4f])

            print('x4')
            print(chk4/8)                
            if chk4 != 0:
                x40m = np.median(x40[x4f])
                x40a = np.mean(x40[x4f])
                x41m = np.median(x41[x4f])
                x41a = np.mean(x41[x4f])
                x42m = np.median(x42[x4f])
                x42a = np.mean(x42[x4f])
                
                v41 =[x40m, x41m, x42m]
                v42 =[x40a, x41a, x42a]
                
                print(x40m)
                print(x40a)
                print(x41m)
                print(x41a)
                print(x42m)
                print(x42a)


            else:
                print(stgo_unit +' Sensor 4 no tiene datos de calibración')
                
        else:
            chk4 = 0
            print(stgo_unit +' Sensor 4 no tiene datos')
 
        with open('Code/../../Out/CV/'+ stgo_unit +'.csv', 'w', newline = '') as csvfile:
            csvwriter = csv.writer(csvfile)
            
            csvwriter.writerow(['Calibration constansts Sensor 1'])
            if chk1 != 0:
                plot_hist(stgo_unit, x10[x1f], 'Sensor 1 wavelength')
                plot_hist(stgo_unit, x11[x1f], 'Sensor 1 v0')
                plot_hist(stgo_unit, x12[x1f], 'Sensor 1 wavelength o3')
                
                x1_csv = np.array([d1[x1f], x10[x1f],x11[x1f], x12[x1f]])
                x1_csv = x1_csv.tolist()
                
                for i in range(len(x1_csv[0])):
                    csvwriter.writerow([x1_csv[0][i][0:10],x1_csv[1][i],x1_csv[2][i],x1_csv[3][i]])               
                
                csvwriter.writerow(['Selected constansts Sensor 1']) 
                csvwriter.writerow(v11)
                csvwriter.writerow(v12)
                
            csvwriter.writerow(['Calibration constansts Sensor 2'])
            if chk2 != 0:
                plot_hist(stgo_unit, x20[x2f], 'Sensor 2 wavelength')
                plot_hist(stgo_unit, x21[x2f], 'Sensor 2 v0')
                plot_hist(stgo_unit, x22[x2f], 'Sensor 2 wavelength o3')
                
                x2_csv = np.array([d2[x2f], x20[x2f],x21[x2f],x22[x2f]])
                x2_csv = x2_csv.tolist()
                
                for i in range(len(x2_csv[0])):
                    csvwriter.writerow([x2_csv[0][i][0:10],x2_csv[1][i],x2_csv[2][i],x2_csv[3][i]])
                
                csvwriter.writerow(['Selected constansts Sensor 2']) 
                csvwriter.writerow(v21)
                csvwriter.writerow(v22)
                
            csvwriter.writerow(['Calibration constansts Sensor 3'])
            if chk3 != 0:
                plot_hist(stgo_unit, x30[x3f], 'Sensor 3 wavelength')
                plot_hist(stgo_unit, x31[x3f], 'Sensor 3 v0')
                plot_hist(stgo_unit, x32[x3f], 'Sensor 3 wavelength o3')
                
                x3_csv = np.array([d3[x3f], x30[x3f],x31[x3f],x32[x3f]])
                x3_csv = x3_csv.tolist()
                
                for i in range(len(x3_csv[0])):
                    csvwriter.writerow([x3_csv[0][i][0:10],x3_csv[1][i],x3_csv[2][i],x3_csv[3][i]])
                
                csvwriter.writerow(['Selected constansts Sensor 3']) 
                csvwriter.writerow(v31)
                csvwriter.writerow(v32)
                
            csvwriter.writerow(['Calibration constansts Sensor 4'])
            if chk4 != 0:
                plot_hist(stgo_unit, x40[x4f], 'Sensor 4 wavelength')
                plot_hist(stgo_unit, x41[x4f], 'Sensor 4 v0')
                plot_hist(stgo_unit, x42[x4f], 'Sensor 4 wavelength o3')
                
                x4_csv = np.array([d4[x4f], x40[x4f],x41[x4f],x42[x4f]])
                x4_csv = x4_csv.tolist()
                
                for i in range(len(x4_csv[0])):
                    csvwriter.writerow([x4_csv[0][i][0:10],x4_csv[1][i],x4_csv[2][i], x4_csv[3][i]])
                
                csvwriter.writerow(['Selected constansts Sensor 4']) 
                csvwriter.writerow(v41)
                csvwriter.writerow(v42)
                
    datei = dt.datetime(2020, 1, 1)
    
    rmse11 =[]
    rmse21 =[]
    rmse31 =[]
    rmse41 =[]
    rmse12 =[]
    rmse22 =[]
    rmse32 =[]
    rmse42 =[]
    
    aod_1 = []
    aod_2 = []
    aod_3 = []
    aod_4 = []
    aaod_1 = []
    aaod_2 = []
    aaod_3 = []
    aaod_4 = []
    
    amgstromv4 = []
    amgstromv42 = []
    aamgstrom = []
    
    while datei != dt.datetime(2021, 1, 1):
 
        day = datei.day
        month = datei.month
        year = datei.year
        

        cut = 0
        cloud_filter = 1
   
    
        date_day = dt.date(year, month, day)
        
        stgo_data = load_stgo_data(stgo_unit, date_day)
        aero_data = load_aero_data(aero_unit, date_day)
        aero_data2 = load_aero_data(aero_unit2, date_day)
                
        if (stgo_data != []):
               
            stgo_data = stgo_filter(stgo_data, cut, cloud_filter)
                
            m1, date1, seconds1, pressure1, airmass1, amu1, r1, altitude1, temperature1, latitude1, longitude1 = stgo_useful_data(stgo_data, 'm1')
            m2, date2, seconds2, pressure2, airmass2, amu2, r2, altitude2, temperature2, latitude2, longitude2 = stgo_useful_data(stgo_data, 'm2')
            m3, date3, seconds3, pressure3, airmass3, amu3, r3, altitude3, temperature3, latitude3, longitude3 = stgo_useful_data(stgo_data, 'm3')
            m4, date4, seconds4, pressure4, airmass4, amu4, r4, altitude4, temperature4, latitude4, longitude4 = stgo_useful_data(stgo_data, 'm4')
            
            if (aero_data != []):
                aero_data = aeronet_filter(aero_data)
                aero_data2 = aeronet_filter(aero_data2)
            
                t1, aero_lamb, amgstrom, aero_date, aero_seconds, ozone, aero_latitude, aero_longitude, aero_air_mass = aero_useful_data_v2(aero_data)
                t12, aero_lamb2, amgstrom2, aero_date2, aero_seconds2, ozone2, aero_latitude2, aero_longitude2, aero_air_mass2 = aero_useful_data_v2(aero_data2)
                
                if m1 != []:
                    m11, m12, m13, ipressure1, ialtitude1, iairmass1, iamu1, ir1, del1 = interpolate(m1, pressure1, altitude1, airmass1, amu1, r1, seconds1, aero_seconds)
                    am11, am12, am13, apressure1, aaltitude1, aairmass1, aamu1, ar1, adel1 = interpolate(m1, pressure1, altitude1, airmass1, amu1, r1, seconds1, seconds1)
                    aozone1 = np.interp(seconds1, aero_seconds, ozone)
                if m2 != []:
                    m21, m22, m23, ipressure2, ialtitude2, iairmass2, iamu2, ir2, del2 = interpolate(m2, pressure2, altitude2, airmass2, amu2, r2, seconds2, aero_seconds)
                    am21, am22, am23, apressure2, aaltitude2, aairmass2, aamu2, ar2, adel2 = interpolate(m2, pressure2, altitude2, airmass2, amu2, r2, seconds2, seconds2)
                    aozone2 = np.interp(seconds2, aero_seconds, ozone)
                if m3 != []:
                    m31, m32, m33, ipressure3, ialtitude3, iairmass3, iamu3, ir3, del3 = interpolate(m3, pressure3, altitude3, airmass3, amu3, r3, seconds3, aero_seconds)
                    am31, am32, am33, apressure3, aaltitude3, aairmass3, aamu3, ar3, adel3 = interpolate(m3, pressure3, altitude3, airmass3, amu3, r3, seconds3, seconds3)
                    aozone3 = np.interp(seconds3, aero_seconds, ozone)
                if m4 != []:
                    m41, m42, m43, ipressure4, ialtitude4, iairmass4, iamu4, ir4, del4 = interpolate(m4, pressure4, altitude4, airmass4, amu4, r4, seconds4, aero_seconds) 
                    am41, am42, am43, apressure4, ialtitude4, aairmass4, aamu4, ar4, adel4 = interpolate(m4, pressure4, altitude4, airmass4, amu4, r4, seconds4, seconds4) 
                    aozone4 = np.interp(seconds4, aero_seconds, ozone)
            
                if (np.abs(aero_latitude-latitude1)<0.005) and (np.abs(aero_longitude-longitude1)<0.005):
# Caso de intrumento con datos de calibracion
                    print('unidad '+ stgo_unit +' Tiene datos de calibracion '+ str(day) +'/'+ str(month) + '/' + str(year))

                    if m1 != [] and chk1:
                        dt1 = np.delete(t1,del1,0)
                        damg = np.delete(amgstrom,del1)
                        dozo = np.delete(ozone,del1)
                        tau1 = np.concatenate([dt1,dt1,dt1])
                        alpha = np.concatenate([damg, damg, damg])
                        v = np.concatenate([m11,m12,m13])
                        res = np.concatenate([ir1,ir1,ir1])
                        p = np.concatenate([ipressure1,ipressure1,ipressure1])
                        am = np.concatenate([iairmass1,iairmass1,iairmass1])
                        ozo_mu = np.concatenate([iamu1,iamu1,iamu1])
                        ozo = np.concatenate([dozo,dozo,dozo])

                        response11 = rmse_calibration(v11)
                        response12 = rmse_calibration(v12)
                        
                        aod_111 = stgo_aod(v11, ir1, m11, ipressure1, iairmass1, iamu1, np.delete(ozone,del1))
                        aod_121 = stgo_aod(v11, ir1, m12, ipressure1, iairmass1, iamu1, np.delete(ozone,del1))
                        aod_131 = stgo_aod(v11, ir1, m13, ipressure1, iairmass1, iamu1, np.delete(ozone,del1))
            
                        aod_a111 = stgo_aod(v11, ar1, am11, apressure1, aairmass1, aamu1, aozone1)
                        aod_a121 = stgo_aod(v11, ar1, am12, apressure1, aairmass1, aamu1, aozone1)
                        aod_a131 = stgo_aod(v11, ar1, am13, apressure1, aairmass1, aamu1, aozone1)
            
                        aod_112 = stgo_aod(v12, ir1, m11, ipressure1, iairmass1, iamu1, np.delete(ozone,del1))
                        aod_122 = stgo_aod(v12, ir1, m12, ipressure1, iairmass1, iamu1, np.delete(ozone,del1))
                        aod_132 = stgo_aod(v12, ir1, m13, ipressure1, iairmass1, iamu1, np.delete(ozone,del1))
            
                        time_1 = np.delete(np.array(aero_date),del1)
                        times_1 = np.delete(np.array(aero_seconds),del1)
                        
                        itemp1 = np.interp(aero_seconds, seconds1, temperature1, left=0, right=0)
                        temp_1 = np.delete(np.array(itemp1),del1)
        
                        aero_aod11 = amgstrom_interpolation(v11[0], amgstrom, t1)
                        aero_aod12 = amgstrom_interpolation(v12[0], amgstrom, t1)
                   
                        plot_day(stgo_unit, time_1, aod_121, m_max=aod_111, m_min=aod_131, aero_time= aero_date, aero_data = aero_aod11, sensor = 'Sensor 1 C')     
                        plot_day(stgo_unit, date1, aod_a121, m_max=aod_a111, m_min=aod_a131, aero_time= aero_date, aero_data = aero_aod11, sensor = 'Sensor 1 C NI')     
                        
                        aod_1 = aod_1 + aod_111.tolist() + aod_121.tolist() + aod_131.tolist()
                        aaod_1 = aaod_1 + np.delete(aero_aod11,del1).tolist() + np.delete(aero_aod11,del1).tolist() + np.delete(aero_aod11,del1).tolist()

                    if m2 != [] and chk2:
                        dt2 = np.delete(t1,del2,0)
                        damg = np.delete(amgstrom,del2)
                        dozo = np.delete(ozone,del2)
                        tau1 = np.concatenate([dt2,dt2,dt2])
                        alpha = np.concatenate([damg, damg, damg])
                        v = np.concatenate([m21,m22,m23])
                        res = np.concatenate([ir2,ir2,ir2])
                        p = np.concatenate([ipressure2,ipressure2,ipressure2])
                        am = np.concatenate([iairmass2,iairmass2,iairmass2])
                        ozo_mu = np.concatenate([iamu2,iamu2,iamu2])
                        ozo = np.concatenate([dozo,dozo,dozo])
                        
                        response21 = rmse_calibration(v21)
                        response22 = rmse_calibration(v22)

                        aod_211 = stgo_aod(v21, ir2, m21, ipressure2, iairmass2, iamu2, np.delete(ozone,del2))
                        aod_221 = stgo_aod(v21, ir2, m22, ipressure2, iairmass2, iamu2, np.delete(ozone,del2))
                        aod_231 = stgo_aod(v21, ir2, m23, ipressure2, iairmass2, iamu2, np.delete(ozone,del2))
            
                        aod_a211 = stgo_aod(v21, ar2, am21, apressure2, aairmass2, aamu2, aozone2)
                        aod_a221 = stgo_aod(v21, ar2, am22, apressure2, aairmass2, aamu2, aozone2)
                        aod_a231 = stgo_aod(v21, ar2, am23, apressure2, aairmass2, aamu2, aozone2)
            
                        aod_212 = stgo_aod(v22, ir2, m21, ipressure2, iairmass2, iamu2, np.delete(ozone,del2))
                        aod_222 = stgo_aod(v22, ir2, m22, ipressure2, iairmass2, iamu2, np.delete(ozone,del2))
                        aod_232 = stgo_aod(v22, ir2, m23, ipressure2, iairmass2, iamu2, np.delete(ozone,del2))
            
                        time_2 = np.delete(np.array(aero_date),del2)
                        times_2 = np.delete(np.array(aero_seconds),del2)
                        
                        itemp2 = np.interp(aero_seconds, seconds2, temperature2, left=0, right=0)
                        temp_2 = np.delete(np.array(itemp2),del2)
        
                        aero_aod21 = amgstrom_interpolation(v21[0], amgstrom, t1)
                        aero_aod22 = amgstrom_interpolation(v22[0], amgstrom, t1)
                        
                        plot_day(stgo_unit, time_2, aod_221, m_max=aod_211, m_min=aod_231, aero_time= aero_date, aero_data = aero_aod21, sensor = 'Sensor 2 C')    
                        plot_day(stgo_unit, date2, aod_a221, m_max=aod_a211, m_min=aod_a231, aero_time= aero_date, aero_data = aero_aod21, sensor = 'Sensor 2 C NI')

                        aod_2 = aod_2 + aod_211.tolist() + aod_221.tolist() + aod_231.tolist()
                        aaod_2 = aaod_2 + np.delete(aero_aod21,del2).tolist() + np.delete(aero_aod21,del2).tolist() + np.delete(aero_aod21,del2).tolist()                    
                        
                    if m3 != [] and chk3:
                        dt3 = np.delete(t1,del3,0)
                        damg = np.delete(amgstrom,del3)
                        dozo = np.delete(ozone,del3)
                        tau1 = np.concatenate([dt3,dt3,dt3])
                        alpha = np.concatenate([damg, damg, damg])
                        v = np.concatenate([m31,m32,m33])
                        res = np.concatenate([ir3,ir3,ir3])
                        p = np.concatenate([ipressure3,ipressure3,ipressure3])
                        am = np.concatenate([iairmass3,iairmass3,iairmass3])
                        ozo_mu = np.concatenate([iamu3,iamu3,iamu3])
                        ozo = np.concatenate([dozo,dozo,dozo])
                        
                        response31 = rmse_calibration(v31)
                        response32 = rmse_calibration(v32)
                        
                        aod_311 = stgo_aod(v31, ir3, m31, ipressure3, iairmass3, iamu3, np.delete(ozone,del3))
                        aod_321 = stgo_aod(v31, ir3, m32, ipressure3, iairmass3, iamu3, np.delete(ozone,del3))
                        aod_331 = stgo_aod(v31, ir3, m33, ipressure3, iairmass3, iamu3, np.delete(ozone,del3))

                        aod_a311 = stgo_aod(v31, ar3, am31, apressure3, aairmass3, aamu3, aozone3)
                        aod_a321 = stgo_aod(v31, ar3, am32, apressure3, aairmass3, aamu3, aozone3)
                        aod_a331 = stgo_aod(v31, ar3, am33, apressure3, aairmass3, aamu3, aozone3) 
            
                        aod_312 = stgo_aod(v32, ir3, m31, ipressure3, iairmass3, iamu3, np.delete(ozone,del3))
                        aod_322 = stgo_aod(v32, ir3, m32, ipressure3, iairmass3, iamu3, np.delete(ozone,del3))
                        aod_332 = stgo_aod(v32, ir3, m33, ipressure3, iairmass3, iamu3, np.delete(ozone,del3))
            
                        time_3 = np.delete(np.array(aero_date),del3)
                        times_3 = np.delete(np.array(aero_seconds),del3)
                        
                        itemp3 = np.interp(aero_seconds, seconds3, temperature3, left=0, right=0)
                        temp_3 = np.delete(np.array(itemp3),del3)
        
                        aero_aod31 = amgstrom_interpolation(v31[0], amgstrom, t1)
                        aero_aod32 = amgstrom_interpolation(v32[0], amgstrom, t1)                                
                    
                        plot_day(stgo_unit, time_3, aod_321, m_max=aod_311, m_min=aod_331, aero_time= aero_date, aero_data = aero_aod31, sensor = 'Sensor 3 C')
                        plot_day(stgo_unit, date3, aod_a321, m_max=aod_a311, m_min=aod_a331, aero_time= aero_date, aero_data = aero_aod31, sensor = 'Sensor 3 C NI')
                        
                        aod_3 = aod_3 + aod_311.tolist() + aod_321.tolist() + aod_331.tolist()
                        aaod_3 = aaod_3 + np.delete(aero_aod31,del3).tolist() + np.delete(aero_aod31,del3).tolist() + np.delete(aero_aod31,del3).tolist()
                            
                    if m4 != [] and chk4:
                        dt4 = np.delete(t1,del4,0)
                        damg = np.delete(amgstrom,del4)
                        dozo = np.delete(ozone,del4)
                        tau1 = np.concatenate([dt4,dt4,dt4])
                        alpha = np.concatenate([damg, damg, damg])
                        v = np.concatenate([m41,m42,m43])
                        res = np.concatenate([ir4,ir4,ir4])
                        p = np.concatenate([ipressure4,ipressure4,ipressure4])
                        am = np.concatenate([iairmass4,iairmass4,iairmass4])
                        ozo_mu = np.concatenate([iamu4,iamu4,iamu4])
                        ozo = np.concatenate([dozo,dozo,dozo])

                        response41 = rmse_calibration(v41)
                        response42 = rmse_calibration(v42)
                        
                        aod_411 = stgo_aod(v41, ir4, m41, ipressure4, iairmass4, iamu4, np.delete(ozone,del4))
                        aod_421 = stgo_aod(v41, ir4, m42, ipressure4, iairmass4, iamu4, np.delete(ozone,del4))
                        aod_431 = stgo_aod(v41, ir4, m43, ipressure4, iairmass4, iamu4, np.delete(ozone,del4))

                        aod_a411 = stgo_aod(v41, ar4, am41, apressure4, aairmass4, aamu4, aozone4)
                        aod_a421 = stgo_aod(v41, ar4, am42, apressure4, aairmass4, aamu4, aozone4)
                        aod_a431 = stgo_aod(v41, ar4, am43, apressure4, aairmass4, aamu4, aozone4) 
            
                        aod_412 = stgo_aod(v42, ir4, m41, ipressure4, iairmass4, iamu4, np.delete(ozone,del4))
                        aod_422 = stgo_aod(v42, ir4, m42, ipressure4, iairmass4, iamu4, np.delete(ozone,del4))
                        aod_432 = stgo_aod(v42, ir4, m43, ipressure4, iairmass4, iamu4, np.delete(ozone,del4))
            
                        time_4 = np.delete(np.array(aero_date),del4)
                        times_4 = np.delete(np.array(aero_seconds),del4)
                        
                        itemp4 = np.interp(aero_seconds, seconds4, temperature4, left=0, right=0)
                        temp_4 = np.delete(np.array(itemp4),del4)
        
                        aero_aod41 = amgstrom_interpolation(v41[0], amgstrom, t1)
                        aero_aod42 = amgstrom_interpolation(v42[0], amgstrom, t1)
                        
                        plot_day(stgo_unit, time_4, aod_421, m_max=aod_411, m_min=aod_431, aero_time= aero_date, aero_data = aero_aod41, sensor = 'Sensor 4 C')    
                        plot_day(stgo_unit, date4, aod_a421, m_max=aod_a411, m_min=aod_a431, aero_time= aero_date, aero_data = aero_aod41, sensor = 'Sensor 4 C NI')
 
                        aod_4 = aod_4 + aod_411.tolist() + aod_421.tolist() + aod_431.tolist()
                        aaod_4 = aaod_4 + np.delete(aero_aod41,del4).tolist() + np.delete(aero_aod41,del4).tolist() + np.delete(aero_aod41,del4).tolist()
                        
                    if m1!=[] and chk1:
                        rmse11.append([str(datei)[0:10], response11])
                        rmse12.append([str(datei)[0:10], response12])
                    if m2!=[] and chk2:    
                        rmse21.append([str(datei)[0:10], response21])
                        rmse22.append([str(datei)[0:10], response22])
                    if m3!=[] and chk3:
                        rmse31.append([str(datei)[0:10], response31])
                        rmse32.append([str(datei)[0:10], response32])
                    if m4!=[] and chk4:
                        rmse41.append([str(datei)[0:10], response41])
                        rmse42.append([str(datei)[0:10], response42])
                        
                    len_val = np.array([len(times_1),len(times_2),len(times_3),len(times_4)])
                    min_val = np.min(len_val)
                    len_min_val = len_val == min_val
                    wavelength = 1e3*np.array([v11[0], v21[0], v31[0], v41[0]])
                    wavelength2 = 1e3*np.array([v21[0], v41[0]])
                    
                    cont = 0
                    for k in len_min_val:
                        if k:
                            if cont == 0:
                                a_1 = np.interp(times_1, times_1, (aod_111+aod_121+aod_131)/3)
                                a_2 = np.interp(times_1, times_2, (aod_211+aod_221+aod_231)/3)
                                a_3 = np.interp(times_1, times_3, (aod_311+aod_321+aod_331)/3)
                                a_4 = np.interp(times_1, times_4, (aod_411+aod_421+aod_431)/3)
                                ams = np.delete(amgstrom,del1)
                            elif cont == 1:
                                a_1 = np.interp(times_2, times_1, (aod_111+aod_121+aod_131)/3)
                                a_2 = np.interp(times_2, times_2, (aod_211+aod_221+aod_231)/3)
                                a_3 = np.interp(times_2, times_3, (aod_311+aod_321+aod_331)/3)
                                a_4 = np.interp(times_2, times_4, (aod_411+aod_421+aod_431)/3)
                                ams = np.delete(amgstrom,del2)
                            elif cont == 2:
                                a_1 = np.interp(times_3, times_1, (aod_111+aod_121+aod_131)/3)
                                a_2 = np.interp(times_3, times_2, (aod_211+aod_221+aod_231)/3)
                                a_3 = np.interp(times_3, times_3, (aod_311+aod_321+aod_331)/3)
                                a_4 = np.interp(times_3, times_4, (aod_411+aod_421+aod_431)/3)
                                ams = np.delete(amgstrom,del3)
                            elif cont == 3:
                                a_1 = np.interp(times_4, times_1, (aod_111+aod_121+aod_131)/3)
                                a_2 = np.interp(times_4, times_2, (aod_211+aod_221+aod_231)/3)
                                a_3 = np.interp(times_4, times_3, (aod_311+aod_321+aod_331)/3)
                                a_4 = np.interp(times_4, times_4, (aod_411+aod_421+aod_431)/3)
                                ams = np.delete(amgstrom,del4)
                                
                            for l in range(len(ams)):
                                aamgstrom.append(ams[l])
                                slope, intercept = np.polyfit(np.log(wavelength), np.array([np.log(a_1[l]),np.log(a_2[l]),np.log(a_3[l]),np.log(a_4[l])]),1)
                                slopev2 = pv.atmosphere.angstrom_alpha(a_2[l], wavelength2[0], a_4[l], wavelength2[1])
                                amgstromv4.append(-slope)
                                amgstromv42.append(slopev2) 
                            
                            break
                        else:
                            cont += 1
                    
                        
                else:
# Caso instrumento en terreno
                    print('unidad '+ stgo_unit +' lejos de intrumento patron '+ str(day) +'/'+ str(month) + '/' + str(year))
                    if m1 != [] and chk1:
                        
                        aod_111 = stgo_aod(v11, ir1, m11, ipressure1, iairmass1, iamu1, np.delete(ozone,del1))
                        aod_121 = stgo_aod(v11, ir1, m12, ipressure1, iairmass1, iamu1, np.delete(ozone,del1))
                        aod_131 = stgo_aod(v11, ir1, m13, ipressure1, iairmass1, iamu1, np.delete(ozone,del1))
            
                        aod_a111 = stgo_aod(v11, ar1, am11, apressure1, aairmass1, aamu1, aozone1)
                        aod_a121 = stgo_aod(v11, ar1, am12, apressure1, aairmass1, aamu1, aozone1)
                        aod_a131 = stgo_aod(v11, ar1, am13, apressure1, aairmass1, aamu1, aozone1)
            
                        aod_112 = stgo_aod(v12, ir1, m11, ipressure1, iairmass1, iamu1, np.delete(ozone,del1))
                        aod_122 = stgo_aod(v12, ir1, m12, ipressure1, iairmass1, iamu1, np.delete(ozone,del1))
                        aod_132 = stgo_aod(v12, ir1, m13, ipressure1, iairmass1, iamu1, np.delete(ozone,del1))
            
                        time_1 = np.delete(np.array(aero_date),del1)
                        
                        itemp1 = np.interp(aero_seconds, seconds1, temperature1, left=0, right=0)
                        temp_1 = np.delete(np.array(itemp1),del1)
        
                        aero_aod11 = amgstrom_interpolation(v11[0], amgstrom, t1)
                        aero_aod12 = amgstrom_interpolation(v12[0], amgstrom, t1)
                   
                        plot_day(stgo_unit, time_1, aod_121, m_max=aod_111, m_min=aod_131, aero_time= aero_date, aero_data = aero_aod11, sensor = 'Sensor 1 O')     
                        plot_day(stgo_unit, date1, aod_a121, m_max=aod_a111, m_min=aod_a131, aero_time= aero_date, aero_data = aero_aod11, sensor = 'Sensor 1 O NI')     
                   
                    if m2 != [] and chk2:

                        aod_211 = stgo_aod(v21, ir2, m21, ipressure2, iairmass2, iamu2, np.delete(ozone,del2))
                        aod_221 = stgo_aod(v21, ir2, m22, ipressure2, iairmass2, iamu2, np.delete(ozone,del2))
                        aod_231 = stgo_aod(v21, ir2, m23, ipressure2, iairmass2, iamu2, np.delete(ozone,del2))
            
                        aod_a211 = stgo_aod(v21, ar2, am21, apressure2, aairmass2, aamu2, aozone2)
                        aod_a221 = stgo_aod(v21, ar2, am22, apressure2, aairmass2, aamu2, aozone2)
                        aod_a231 = stgo_aod(v21, ar2, am23, apressure2, aairmass2, aamu2, aozone2)
            
                        aod_212 = stgo_aod(v22, ir2, m21, ipressure2, iairmass2, iamu2, np.delete(ozone,del2))
                        aod_222 = stgo_aod(v22, ir2, m22, ipressure2, iairmass2, iamu2, np.delete(ozone,del2))
                        aod_232 = stgo_aod(v22, ir2, m23, ipressure2, iairmass2, iamu2, np.delete(ozone,del2))
            
                        time_2 = np.delete(np.array(aero_date),del2)
                        
                        itemp2 = np.interp(aero_seconds, seconds2, temperature2, left=0, right=0)
                        temp_2 = np.delete(np.array(itemp2),del2)
        
                        aero_aod21 = amgstrom_interpolation(v21[0], amgstrom, t1)
                        aero_aod22 = amgstrom_interpolation(v22[0], amgstrom, t1)
                        
                        plot_day(stgo_unit, time_2, aod_221, m_max=aod_211, m_min=aod_231, aero_time= aero_date, aero_data = aero_aod21, sensor = 'Sensor 2 O')    
                        plot_day(stgo_unit, date2, aod_a221, m_max=aod_a211, m_min=aod_a231, aero_time= aero_date, aero_data = aero_aod21, sensor = 'Sensor 2 O NI')
                        
                    if m3 != [] and chk3:

                        aod_311 = stgo_aod(v31, ir3, m31, ipressure3, iairmass3, iamu3, np.delete(ozone,del3))
                        aod_321 = stgo_aod(v31, ir3, m32, ipressure3, iairmass3, iamu3, np.delete(ozone,del3))
                        aod_331 = stgo_aod(v31, ir3, m33, ipressure3, iairmass3, iamu3, np.delete(ozone,del3))

                        aod_a311 = stgo_aod(v31, ar3, am31, apressure3, aairmass3, aamu3, aozone3)
                        aod_a321 = stgo_aod(v31, ar3, am32, apressure3, aairmass3, aamu3, aozone3)
                        aod_a331 = stgo_aod(v31, ar3, am33, apressure3, aairmass3, aamu3, aozone3) 
            
                        aod_312 = stgo_aod(v32, ir3, m31, ipressure3, iairmass3, iamu3, np.delete(ozone,del3))
                        aod_322 = stgo_aod(v32, ir3, m32, ipressure3, iairmass3, iamu3, np.delete(ozone,del3))
                        aod_332 = stgo_aod(v32, ir3, m33, ipressure3, iairmass3, iamu3, np.delete(ozone,del3))
            
                        time_3 = np.delete(np.array(aero_date),del3)
                        
                        itemp3 = np.interp(aero_seconds, seconds3, temperature3, left=0, right=0)
                        temp_3 = np.delete(np.array(itemp3),del3)
        
                        aero_aod31 = amgstrom_interpolation(v31[0], amgstrom, t1)
                        aero_aod32 = amgstrom_interpolation(v32[0], amgstrom, t1)                                
                    
                        plot_day(stgo_unit, time_3, aod_321, m_max=aod_311, m_min=aod_331, aero_time= aero_date, aero_data = aero_aod31, sensor = 'Sensor 3 O')
                        plot_day(stgo_unit, date3, aod_a321, m_max=aod_a311, m_min=aod_a331, aero_time= aero_date, aero_data = aero_aod31, sensor = 'Sensor 3 O NI')
                         
                    if m4 != [] and chk4:
   
                        aod_411 = stgo_aod(v41, ir4, m41, ipressure4, iairmass4, iamu4, np.delete(ozone,del4))
                        aod_421 = stgo_aod(v41, ir4, m42, ipressure4, iairmass4, iamu4, np.delete(ozone,del4))
                        aod_431 = stgo_aod(v41, ir4, m43, ipressure4, iairmass4, iamu4, np.delete(ozone,del4))

                        aod_a411 = stgo_aod(v41, ar4, am41, apressure4, aairmass4, aamu4, aozone4)
                        aod_a421 = stgo_aod(v41, ar4, am42, apressure4, aairmass4, aamu4, aozone4)
                        aod_a431 = stgo_aod(v41, ar4, am43, apressure4, aairmass4, aamu4, aozone4) 
            
                        aod_412 = stgo_aod(v42, ir4, m41, ipressure4, iairmass4, iamu4, np.delete(ozone,del4))
                        aod_422 = stgo_aod(v42, ir4, m42, ipressure4, iairmass4, iamu4, np.delete(ozone,del4))
                        aod_432 = stgo_aod(v42, ir4, m43, ipressure4, iairmass4, iamu4, np.delete(ozone,del4))
            
                        time_4 = np.delete(np.array(aero_date),del4)
                        
                        itemp4 = np.interp(aero_seconds, seconds4, temperature4, left=0, right=0)
                        temp_4 = np.delete(np.array(itemp4),del4)
        
                        aero_aod41 = amgstrom_interpolation(v41[0], amgstrom, t1)
                        aero_aod42 = amgstrom_interpolation(v42[0], amgstrom, t1)
                        
                        plot_day(stgo_unit, time_4, aod_421, m_max=aod_411, m_min=aod_431, aero_time= aero_date, aero_data = aero_aod41, sensor = 'Sensor 4 O')    
                        plot_day(stgo_unit, date4, aod_a421, m_max=aod_a411, m_min=aod_a431, aero_time= aero_date, aero_data = aero_aod41, sensor = 'Sensor 4 O NI')
              
                   
            else:
# Caso Con datos de terreno, pero no de aeronet
                print('unidad '+ aero_unit +' No tiene datos '+ str(day) +'/'+ str(month) + '/' + str(year))
                
                if m1 != []:
                    m11, m12, m13, ipressure1, ialtitude1, iairmass1, iamu1, ir1, del1 = interpolate(m1, pressure1, altitude1, airmass1, amu1, r1, seconds1, seconds1)
                if m2 != []:
                    m21, m22, m23, ipressure2, ialtitude2, iairmass2, iamu2, ir2, del2 = interpolate(m2, pressure2, altitude2, airmass2, amu2, r2, seconds2, seconds2)
                if m3 != []:
                    m31, m32, m33, ipressure3, ialtitude3, iairmass3, iamu3, ir3, del3 = interpolate(m3, pressure3, altitude3, airmass3, amu3, r3, seconds3, seconds3)
                if m4 != []:
                    m41, m42, m43, ipressure4, ialtitude4, iairmass4, iamu4, ir4, del4 = interpolate(m4, pressure4, altitude4, airmass4, amu4, r4, seconds4, seconds4) 
    
                if m1 != [] and chk1:
                    
                    aod_111 = stgo_aod(v11, ir1, m11, ipressure1, iairmass1, iamu1, np.delete(ozone,del1))
                    aod_121 = stgo_aod(v11, ir1, m12, ipressure1, iairmass1, iamu1, np.delete(ozone,del1))
                    aod_131 = stgo_aod(v11, ir1, m13, ipressure1, iairmass1, iamu1, np.delete(ozone,del1))
        
                    aod_112 = stgo_aod(v12, ir1, m11, ipressure1, iairmass1, iamu1, np.delete(ozone,del1))
                    aod_122 = stgo_aod(v12, ir1, m12, ipressure1, iairmass1, iamu1, np.delete(ozone,del1))
                    aod_132 = stgo_aod(v12, ir1, m13, ipressure1, iairmass1, iamu1, np.delete(ozone,del1))
        
                    time_1 = date1
    
                    plot_day(stgo_unit, time_1, aod_121, m_max=aod_111, m_min=aod_131, sensor = 'Sensor 1 NA')     
                            
                if m2 != [] and chk2:

                    aod_211 = stgo_aod(v21, ir2, m21, ipressure2, iairmass2, iamu2, np.delete(ozone,del2))
                    aod_221 = stgo_aod(v21, ir2, m22, ipressure2, iairmass2, iamu2, np.delete(ozone,del2))
                    aod_231 = stgo_aod(v21, ir2, m23, ipressure2, iairmass2, iamu2, np.delete(ozone,del2))
        
                    aod_212 = stgo_aod(v22, ir2, m21, ipressure2, iairmass2, iamu2, np.delete(ozone,del2))
                    aod_222 = stgo_aod(v22, ir2, m22, ipressure2, iairmass2, iamu2, np.delete(ozone,del2))
                    aod_232 = stgo_aod(v22, ir2, m23, ipressure2, iairmass2, iamu2, np.delete(ozone,del2))
        
                    time_2 = date2
                    
                    plot_day(stgo_unit, time_2, aod_221, m_max=aod_211, m_min=aod_231, sensor = 'Sensor 2 NA')     
 
                if m3 != [] and chk3:
                    
                    aod_311 = stgo_aod(v31, ir3, m31, ipressure3, iairmass3, iamu3, np.delete(ozone,del3))
                    aod_321 = stgo_aod(v31, ir3, m32, ipressure3, iairmass3, iamu3, np.delete(ozone,del3))
                    aod_331 = stgo_aod(v31, ir3, m33, ipressure3, iairmass3, iamu3, np.delete(ozone,del3))
        
                    aod_312 = stgo_aod(v32, ir3, m31, ipressure3, iairmass3, iamu3, np.delete(ozone,del3))
                    aod_322 = stgo_aod(v32, ir3, m32, ipressure3, iairmass3, iamu3, np.delete(ozone,del3))
                    aod_332 = stgo_aod(v32, ir3, m33, ipressure3, iairmass3, iamu3, np.delete(ozone,del3))
        
                    time_3 = date3
                    
                    plot_day(stgo_unit, time_3, aod_321, m_max=aod_311, m_min=aod_331, sensor = 'Sensor 3 NA')     
 
                if m4 != [] and chk4:

                    aod_411 = stgo_aod(v41, ir4, m41, ipressure4, iairmass4, iamu4, np.delete(ozone,del4))
                    aod_421 = stgo_aod(v41, ir4, m42, ipressure4, iairmass4, iamu4, np.delete(ozone,del4))
                    aod_431 = stgo_aod(v41, ir4, m43, ipressure4, iairmass4, iamu4, np.delete(ozone,del4))
        
                    aod_412 = stgo_aod(v42, ir4, m41, ipressure4, iairmass4, iamu4, np.delete(ozone,del4))
                    aod_422 = stgo_aod(v42, ir4, m42, ipressure4, iairmass4, iamu4, np.delete(ozone,del4))
                    aod_432 = stgo_aod(v42, ir4, m43, ipressure4, iairmass4, iamu4, np.delete(ozone,del4))
        
                    time_4 = date4
     
                    plot_day(stgo_unit, time_4, aod_421, m_max=aod_411, m_min=aod_431, sensor = 'Sensor 4 NA')     
                    

        else:
            if stgo_data == []:
                if aero_data == []:
# Caso sin datos de AERONET y prototipo
                    print('unidades '+ aero_unit + ' y ' + stgo_unit +' No tiene datos '+ str(day) +'/'+ str(month) + '/' + str(year))
                else:
# Caso sin datos de prototipo
                    print('unidad '+ stgo_unit +' No tiene datos '+ str(day) +'/'+ str(month) + '/' + str(year))
                
            else:
# Error No caracterizado
                print('Error deconcoido de datos '+ str(day) +'/'+ str(month) + '/' + str(year))
    

             
        
        datei += dt.timedelta(days = 1) 
        
    with open('Code/../../Out/RMSE/'+ stgo_unit +'_RMSE.csv', 'w', newline = '') as csvfile:
        csvwriter = csv.writer(csvfile)
        
        
        if chk1 != 0:
            csvwriter.writerow(['RMSE11 Sensor 1'])
            
            for i in range(len(rmse11)):
                csvwriter.writerow(rmse11[i])               
            
            csvwriter.writerow(['RMSE12 Sensor 1'])
            
            for i in range(len(rmse12)):
                csvwriter.writerow(rmse12[i])
                
        if chk2 != 0:
            csvwriter.writerow(['RMSE21 Sensor 2'])
            
            for i in range(len(rmse21)):
                csvwriter.writerow(rmse21[i])               
            
            csvwriter.writerow(['RMSE22 Sensor 2'])
            
            for i in range(len(rmse22)):
                csvwriter.writerow(rmse22[i])
                
        if chk3 != 0:
            csvwriter.writerow(['RMSE31 Sensor 3'])
            
            for i in range(len(rmse31)):
                csvwriter.writerow(rmse31[i])               
            
            csvwriter.writerow(['RMSE32 Sensor 3'])
            
            for i in range(len(rmse32)):
                csvwriter.writerow(rmse32[i])
        
        if chk4 != 0:
            csvwriter.writerow(['RMSE11 Sensor 4'])
            
            for i in range(len(rmse41)):
                csvwriter.writerow(rmse41[i])               
            
            csvwriter.writerow(['RMSE12 Sensor 4'])
            
            for i in range(len(rmse42)):
                csvwriter.writerow(rmse42[i])
    
    
    aod_1 = np.array(aod_1)
    aod_2 = np.array(aod_2)
    aod_3 = np.array(aod_3)
    aod_4 = np.array(aod_4)
    aaod_1 = np.array(aaod_1)
    aaod_2 = np.array(aaod_2)
    aaod_3 = np.array(aaod_3)
    aaod_4 = np.array(aaod_4)
    
    slope1, intercept1 = np.polyfit(aod_1, aaod_1,1)
    slope2, intercept2 = np.polyfit(aod_2, aaod_2,1)
    slope3, intercept3 = np.polyfit(aod_3, aaod_3,1)
    slope4, intercept4 = np.polyfit(aod_4, aaod_4,1)
    
    rmse_aod1 = np.sqrt(np.sum((aaod_1-aod_1)**2)/len(aod_1))
    rmse_aod12 = np.sqrt(np.sum((aaod_1-(1.054*aod_1-0.005))**2)/len(aod_1))
    fig, ax = plt.subplots()
    plt.xlabel('V4')
    plt.ylabel('Cimel 835')
    plt.title('Scatter plot Cimel 835 v/s V4 (n = ' + str(len(aod_1))+')')
    ax.plot(aod_1, aaod_1,'.', label= str(v11[0]*1e3)[0:3] +' nm y='+str(slope1)[0:5]+'x+'+str(intercept1)[0:6], color = 'royalblue')
    ax.plot(aod_1, aod_1*slope1+intercept1, color='navy')
    legend = ax.legend()
    ax.grid()
    
    rmse_aod2 = np.sqrt(np.sum((aaod_2-aod_2)**2)/len(aod_2))
    rmse_aod22 = np.sqrt(np.sum((aaod_2-(0.948*aod_2+0.005))**2)/len(aod_2))
    fig, ax = plt.subplots()
    plt.xlabel('V4')
    plt.ylabel('Cimel 835')
    plt.title('Scatter plot Cimel 835 v/s V4 (n = ' + str(len(aod_2))+')')
    ax.plot(aod_2, aaod_2,'.', label= str(v21[0]*1e3)[0:3] +' nm y='+str(slope2)[0:5]+'x+'+str(intercept2)[0:6], color = 'royalblue')
    ax.plot(aod_2, aod_2*slope2+intercept2, color='navy')
    legend = ax.legend()
    ax.grid()
    
    rmse_aod3 = np.sqrt(np.sum((aaod_3-aod_3)**2)/len(aod_3))
    rmse_aod32 = np.sqrt(np.sum((aaod_3-(0.848*aod_3+0.0306))**2)/len(aod_3))
    fig, ax = plt.subplots()
    plt.xlabel('V4')
    plt.ylabel('Cimel 835')
    plt.title('Scatter plot Cimel 835 v/s V4 (n = ' + str(len(aod_3))+')')
    ax.plot(aod_3, aaod_3,'.', label= str(v31[0]*1e3)[0:3] +' nm y='+str(slope3)[0:5]+'x+'+str(intercept3)[0:6], color = 'royalblue')
    ax.plot(aod_3, aod_3*slope1+intercept3, color='navy')
    legend = ax.legend()
    ax.grid()

    rmse_aod4 = np.sqrt(np.sum((aaod_4-aod_4)**2)/len(aod_4))
    rmse_aod42 = np.sqrt(np.sum((aaod_4-(1.053*aod_4-0.006))**2)/len(aod_4))
    fig, ax = plt.subplots()
    plt.xlabel('V4')
    plt.ylabel('Cimel 835')
    plt.title('Scatter plot Cimel 835 v/s V4 (n = ' + str(len(aod_4))+')')
    ax.plot(aod_4, aaod_4,'.', label= str(v41[0]*1e3)[0:3] +' nm y='+str(slope4)[0:5]+'x+'+str(intercept4)[0:6], color = 'royalblue')
    ax.plot(aod_4, aod_4*slope4+intercept4, color='navy')
    legend = ax.legend()
    ax.grid()
    
    aamgstrom = np.array(aamgstrom)
    amgstromv4 = np.array(amgstromv4)
    amgstromv42 = np.array(amgstromv42)
    
    rmse_amg = np.sqrt(np.sum((aamgstrom-amgstromv4)**2)/len(amgstromv4))
    
    slopea, intercepta = np.polyfit(amgstromv4, aamgstrom,1)
    fig, ax = plt.subplots()
    plt.xlabel('V4')
    plt.ylabel('Cimel 835')
    plt.title('Scatter plot Cimel 835 v/s V4 (4 channels) (n = ' + str(len(amgstromv4))+')')
    ax.plot(amgstromv4, aamgstrom,'.', label= 'y='+str(slopea)[0:5]+'x+'+str(intercepta)[0:6], color = 'royalblue')
    ax.plot(amgstromv4, amgstromv4*slopea+intercepta, color='navy')
    legend = ax.legend()
    ax.grid()    
    
    rmse_amg2 = np.sqrt(np.sum((aamgstrom-amgstromv42)**2)/len(amgstromv42))
    slopea2, intercepta2 = np.polyfit(amgstromv42, aamgstrom,1)
    fig, ax = plt.subplots()
    plt.xlabel('V4')
    plt.ylabel('Cimel 835')
    plt.title('Scatter plot Cimel 835 v/s V4 (2 channels) (n = ' + str(len(amgstromv42))+')')
    ax.plot(amgstromv42, aamgstrom,'.', label= 'y='+str(slopea2)[0:5]+'x+'+str(intercepta2)[0:6], color = 'royalblue')
    ax.plot(amgstromv42, amgstromv42*slopea2+intercepta2, color='navy')
    legend = ax.legend()
    ax.grid()    
    #Log unit