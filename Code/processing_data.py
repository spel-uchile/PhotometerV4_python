"""
Created on Tue Aug 11 17:25:50 2020

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

def import_data():
    """

    Returns
    -------
    data : Dictionary
        The measurements for each instrument.
    code : Dictionary
        The code for each measure.

    """
    # Data Dictionary
    data = {}
    # Code Dictionary
    code = {}
    
    #Main Path
    path = "Code/../../Datos"
    # Data File Path
    data_folder = os.listdir(path)
    for folder in data_folder:
        data_files = os.listdir(path + "/" + folder)
        
        # Reading data documents
        for file in data_files:
            #Open Document
            with open(path + "/" + folder + "/" + file) as csvfile:
                frame = csv.reader(csvfile)
    
                for row in frame:
                    if len(row) == 17 and row[5]=='':
                        measurement_code = row[0]+row[7]+row[8]+row[9]+row[10]+row[11]+row[12]
                    else:
                        measurement_code = row[0]+row[9]+row[10]+row[11]+row[12]+row[13]+row[14]
                    try:
                        #Code check
                        cod_buff = code[row[0]]
                        #try:
                        #cod_buff.index(measurement_code)
                        #except ValueError:
                        cod_buff.append(measurement_code)
                        code[row[0]] = cod_buff
                        
                            #Data introduce
                        buff = data[row[0]]
                        buff.append(row)
                        data[row[0]] = buff
        
                        
                    except KeyError:
                        data[row[0]] = [row]
                        code[row[0]] = [measurement_code]
    return data, code

def patch(data, code):
    """
    This function corrects the data without pressure measurement, but with 
    altitude given by the GPS
    
    Parameters
    ----------
    data : Dictionary
        The measurements for each instrument.
    code : Dictionary
        The code for each measure.

    Returns
    -------
    data : Dictionary
        The measurements for each instrument.
    code : Dictionary
        The code for each measure.
        
    P: Pressure Corrected
    I: Impossible to use
    U: Umposotioned    
    D: Wrong Date
    T: No Time

    """
    #Patch for repair measurements
    p_0 = 1013.25
    l = 0.00979
    t_0 = 288.16
    g = 9.80665
    m = 0.02896968
    r_0 = 8.314462618
    
    for key in data.keys():
        buff = data[key]
        buff_code = code[key]
        print(key)
        
        for measurement in range(len(buff)):
            print(buff[measurement])
            if len(buff[measurement]) == 17:
                buff_measurement = []
                buff_measurement.append(buff[measurement][0])
                buff_measurement.append(buff[measurement][1])
                buff_measurement.append(buff[measurement][2])
                buff_measurement.append(buff[measurement][3])
                buff_measurement.append(buff[measurement][4])
                
                if buff[measurement][6] == '':
                    buff_measurement.append('-1')
                    buff_measurement.append('-1')
                    buff_measurement.append('-1')
                    buff_measurement.append('-1')
                    for j in range(7,17,1):
                        if buff[measurement][j] == '':    
                            buff_measurement.append('-1')
                        else:
                            buff_measurement.append(buff[measurement][j])
                    buff[measurement] = buff_measurement
                    buff_code[measurement]+= 'U'


                else:
                    for j in range(5,17,1):
                        if buff[measurement][j] == '':    
                            buff_measurement.append('-1')
                        else:
                            buff_measurement.append(buff[measurement][j])
                    buff_measurement.append('-1')
                    buff_measurement.append('-1')
            else:
                buff_measurement = buff[measurement]
                 
            if buff_measurement[17] == '' or buff_measurement[17] == '-1':
                try:
                    h = float(buff_measurement[15])
                    if h > 0:
                        p = p_0*(1-((l*h)/t_0))**((g*m)/(r_0*l))
                        buff_measurement[17] = str(p)
                        buff_code[measurement]+= 'P'
                except ValueError:
                    buff_code[measurement]+= 'I'
            buff[measurement] = buff_measurement  
        data[key] = buff
        code[key] = buff_code
    return data, code

def time_estruct(data, code):
    """

    Parameters
    ----------
    data : TYPE
        DESCRIPTION.
    code : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """  
    # Date Dictionary
    date = {}
    time = {}
    
    for key in data.keys():
        buff = data[key]
        buff_code = code[key]
            
        for measurement in range(len(buff)):
            #print(key)
            year = int(buff[measurement][11])
            month = int(buff[measurement][10])
            day = int(buff[measurement][9])
            hour = int(buff[measurement][12])
            minute = int(buff[measurement][13])
            second = int(buff[measurement][14])
            
            if year == 2000:
                time_measurement = dt.timedelta(hours=hour, minutes = minute, seconds = second)
                date_measurement = dt.datetime(year, 1, 1) + time_measurement
                buff_code[measurement]+= 'D'
            elif year == 2080:
                time_measurement = dt.timedelta(hours=hour, minutes = minute, seconds = second)
                date_measurement = dt.datetime(year, 1, 1) + time_measurement
                buff_code[measurement]+= 'T'
            else:
                time_measurement = dt.timedelta(hours=hour, minutes = minute, seconds = second)
                date_measurement = dt.datetime(year, month, day) + time_measurement
            try:
                date_buff = date[key]
                date_buff.append(date_measurement)
                date[key] = date_buff
                
                time_buff = time[key]
                time_buff.append(time_measurement)
                time[key] = time_buff
            except KeyError:
                date[key] = [date_measurement]
                time[key] = [time_measurement]
    return date, time, code

def measure_struct(data):
    """    
    Parameters
    ----------
    data : Dictionary
        DESCRIPTION.

    Returns
    -------
    Dictionary

    """
    delta = dt.timedelta(minutes = 1)
    measurement_database = {}
    for key in time.keys():
        buff_data = data[key]
        buff = time[key]
        buff_date = date[key]
        
        index_group = []
        contador = 0
        
        
        while contador < len(buff)-2:

            measure_1 = buff[contador]
            measure_2 = buff[contador + 1]
            measure_3 = buff[contador + 2]
                
            if (measure_2 - measure_1 < delta):
                index_group.append(contador)
                index_group.append(contador + 1)
                if (measure_3 - measure_2 < delta):
                    index_group.append(contador + 2)
                    contador += 3
                else:
                    contador += 2
            else:
                contador += 1
             
            measurement_data = mc.measurement_class(buff_data, buff_date, index_group)
            try:
                measure_buff = measurement_database[key]
                measure_buff.append(measurement_data)
                measurement_database[key] = measure_buff
            except KeyError:
                measurement_database[key] = [measurement_data]
            index_group = []    
    return measurement_database

def data_day(unit, date, measurement_structure):
    """

    Parameters
    ----------
    unit : str
        DESCRIPTION.
    date : datetime
        DESCRIPTION.

    Returns
    -------
    List.

    """
    end = date + dt.timedelta(hours = 23,minutes = 59, seconds = 59)
    measures = []
    for i in measurement_structure[unit]:
        try:
            if i.date[0] <= end and i.date[0] >= date:
                measures.append(i)
        except AttributeError:
            pass
    return measures

def data_day_dict(unit, date, measurement_structure):
    """

    Parameters
    ----------
    unit : str
        DESCRIPTION.
    date : datetime
        DESCRIPTION.

    Returns
    -------
    List.

    """
    end = date + dt.timedelta(hours = 23,minutes = 59, seconds = 59)
    measures = []
    for i in measurement_structure[unit]:
        try:
            if i.date[0] <= end and i.date[0] >= date:
                
                str_date =[]
                for j in i.date:
                    str_date.append(str(j))
                    
                dict_measures = {"altitude": i.altitude, "date": str_date, "m1":i.m1,
                                "m2": i.m2, "m3": i.m3, "m4":i.m4, "position": i.position,
                                "pressure": i.pressure, "temperature": i.temperature, "unit": i.unit}                

                measures.append(dict_measures)
                
        except AttributeError:
            pass

    if measures != []:
        with open('Code/../../stgonet_data/'+ unit + '_' + str(date.day)+'_'+str(date.month)+'_'+str(date.year)+ '.json', "w") as outfile:  
            json.dump(measures, outfile) 
    return measures


def plot_day(unit, date, measures):
    date_day1 =[]
    data_day1 = []
    mx1 = []
    mn1 = []
    
    date_day2 =[]
    data_day2 = []
    mx2 = []
    mn2 = []
    
    date_day3 =[]
    data_day3 = []
    mx3 = []
    mn3 = []
    
    date_day4 =[]
    data_day4 = []
    mx4 = []
    mn4 = []
    for i in measures:
        m1 =[]
        for j in i.m1:
            if j >= 50 and j <= 3800 :
                m1.append(j)
        if len(m1) != 0:
            av1 = sum(m1)/len(m1)
            lb1 = av1-min(m1)
            ub1 = max(m1) - av1
            mx1.append(ub1)
            mn1.append(lb1)
            date_day1.append(i.date[1])
            data_day1.append(av1)
            
        m2 =[]
        for j in i.m2:
            if j >= 50 and j <= 3800 :
                m2.append(j)
        if len(m2) != 0:
            av2 = sum(m2)/len(m2)
            lb2 = av2-min(m2)
            ub2 = max(m2) - av2
            mx2.append(ub2)
            mn2.append(lb2)
            date_day2.append(i.date[1])
            data_day2.append(av2)               

        m3 =[]
        for j in i.m3:
            if j >= 50 and j <= 3800 :
                m3.append(j)
        if len(m3) != 0:
            av3 = sum(m3)/len(m3)
            lb3 = av3-min(m3)
            ub3 = max(m3) - av3
            mx3.append(ub3)
            mn3.append(lb3)
            date_day3.append(i.date[1])
            data_day3.append(av3)

        m4 =[]
        for j in i.m4:
            if j >= 50 and j <= 3800 :
                m4.append(j)

        if len(m4) != 0:
            av4 = sum(m4)/len(m4)
            lb4 = av4-min(m4)
            ub4 = max(m4) - av4
            mx4.append(ub4)
            mn4.append(lb4)
            date_day4.append(i.date[1])
            data_day4.append(av4)
    
    if date_day1 != []:        
        fig1,ax1 = plt.subplots(figsize=(12.8,9.6))   
        ax1.errorbar(date_day1, data_day1, yerr=[mn1,mx1], fmt='.')
        fig1.autofmt_xdate()
        ax1.grid(True)
        ax1.fmt_xdata= mdates.DateFormatter('%Y-%b-%d %H:%M')
        ax1.set_title(unit +' Sensor 1 '+str(date1)[0:10])
        plt.savefig('Code/../../Figures/'+ unit + ' ' + str(date1)[0:10] +' Sensor 1 ')

    if date_day2 != []:        
        fig2,ax2 = plt.subplots(figsize=(12.8,9.6))  
        ax2.errorbar(date_day2, data_day2, yerr=[mn2,mx2], fmt='.')
        fig2.autofmt_xdate()
        ax2.grid(True)
        ax2.fmt_xdata= mdates.DateFormatter('%Y-%b-%d %H:%M')
        ax2.set_title(unit +' Sensor 2 '+str(date1)[0:10])
        plt.savefig('Code/../../Figures/'+ unit + ' ' + str(date1)[0:10] +' Sensor 2 ')

    if date_day3 != []:        
        fig3,ax3 = plt.subplots(figsize=(12.8,9.6))
        ax3.errorbar(date_day3, data_day3, yerr=[mn3,mx3], fmt='.')
        fig3.autofmt_xdate()
        ax3.grid(True)
        ax3.fmt_xdata= mdates.DateFormatter('%Y-%b-%d %H:%M')
        ax3.set_title(unit +' Sensor 3 '+str(date1)[0:10])
        plt.savefig('Code/../../Figures/'+ unit + ' ' + str(date1)[0:10] +' Sensor 3 ')

    if date_day4 != []:        
        fig4,ax4 = plt.subplots(figsize=(12.8,9.6))    
        ax4.errorbar(date_day4, data_day4, yerr=[mn4,mx4], fmt='.')
        fig4.autofmt_xdate()
        ax4.grid(True)
        ax4.fmt_xdata= mdates.DateFormatter('%Y-%b-%d %H:%M')
        ax4.set_title(unit +' Sensor 4 '+str(date1)[0:10])
        plt.savefig('Code/../../Figures/'+ unit + ' ' + str(date1)[0:10] +' Sensor 4 ')

    return True

def plot_day_log(unit, date, measures):
    date_day1 =[]
    data_day1 = []
    mx1 = []
    mn1 = []
    
    date_day2 =[]
    data_day2 = []
    mx2 = []
    mn2 = []
    
    date_day3 =[]
    data_day3 = []
    mx3 = []
    mn3 = []
    
    date_day4 =[]
    data_day4 = []
    mx4 = []
    mn4 = []
    for i in measures:
        m1 =[]
        for j in i.m1:
            if j >= 50 and j <= 3800 :
                m1.append(j)
        if len(m1) != 0:
            av1 = np.log(sum(m1)/len(m1))
            lb1 = av1-np.log(min(m1))
            ub1 = np.log(max(m1)) - av1
            mx1.append(ub1)
            mn1.append(lb1)
            date_day1.append(i.date[1])
            data_day1.append(av1)
            
        m2 =[]
        for j in i.m2:
            if j >= 50 and j <= 3800 :
                m2.append(j)
        if len(m2) != 0:
            av2 = np.log(sum(m2)/len(m2))
            lb2 = av2-np.log(min(m2))
            ub2 = np.log(max(m2)) - av2
            mx2.append(ub2)
            mn2.append(lb2)
            date_day2.append(i.date[1])
            data_day2.append(av2)               

        m3 =[]
        for j in i.m3:
            if j >= 50 and j <= 3800 :
                m3.append(j)
        if len(m3) != 0:
            av3 = np.log(sum(m3)/len(m3))
            lb3 = av3-np.log(min(m3))
            ub3 = np.log(max(m3)) - av3
            mx3.append(ub3)
            mn3.append(lb3)
            date_day3.append(i.date[1])
            data_day3.append(av3)

        m4 =[]
        for j in i.m4:
            if j >= 50 and j <= 3800 :
                m4.append(j)

        if len(m4) != 0:
            av4 = np.log(sum(m4)/len(m4))
            lb4 = av4-np.log(min(m4))
            ub4 = np.log(max(m4)) - av4
            mx4.append(ub4)
            mn4.append(lb4)
            date_day4.append(i.date[1])
            data_day4.append(av4)
    
    if date_day1 != []:        
        fig1,ax1 = plt.subplots(figsize=(12.8,9.6))   
        ax1.errorbar(date_day1, data_day1, yerr=[mn1,mx1], fmt='.')
        fig1.autofmt_xdate()
        ax1.grid(True)
        ax1.fmt_xdata= mdates.DateFormatter('%Y-%b-%d %H:%M')
        ax1.set_title(unit +' Sensor 1 '+str(date1)[0:10])
        plt.savefig('Code/../../Figures/'+ str(date1)[0:10] + ' ' + unit +' Sensor 1 ')

    if date_day2 != []:        
        fig2,ax2 = plt.subplots(figsize=(12.8,9.6))     
        ax2.errorbar(date_day2, data_day2, yerr=[mn2,mx2], fmt='.')
        fig2.autofmt_xdate()
        ax2.grid(True)
        ax2.fmt_xdata= mdates.DateFormatter('%Y-%b-%d %H:%M')
        ax2.set_title(unit +' Sensor 2 '+str(date1)[0:10])
        plt.savefig('Code/../../Figures/'+ str(date1)[0:10] + ' ' + unit +' Sensor 2 ')

    if date_day3 != []:        
        fig3,ax3 = plt.subplots(figsize=(12.8,9.6)) 
        ax3.errorbar(date_day3, data_day3, yerr=[mn3,mx3], fmt='.')
        fig3.autofmt_xdate()
        ax3.grid(True)
        ax3.fmt_xdata= mdates.DateFormatter('%Y-%b-%d %H:%M')
        ax3.set_title(unit +' Sensor 3 '+str(date1)[0:10])
        plt.savefig('Code/../../Figures/'+ str(date1)[0:10] + ' ' + unit +' Sensor 3 ')

    if date_day4 != []:        
        fig4,ax4 = plt.subplots(figsize=(12.8,9.6))  
        ax4.errorbar(date_day4, data_day4, yerr=[mn4,mx4], fmt='.')
        fig4.autofmt_xdate()
        ax4.grid(True)
        ax4.fmt_xdata= mdates.DateFormatter('%Y-%b-%d %H:%M')
        ax4.set_title(unit +' Sensor 4 '+str(date1)[0:10])
        plt.savefig('Code/../../Figures/'+ str(date1)[0:10] + ' ' + unit +' Sensor 4 ')

    return True

if __name__ == "__main__":
    data, code = import_data()
    data, code = patch(data, code)
    date, time, code = time_estruct(data, code)    
    measurement_structure = measure_struct(data)
    
    #unit = "001"
    date1 = dt.datetime(2020, 1, 1)

    for key in data.keys():  
        print(key)
        date1 = dt.datetime(2020, 1, 1)
        while date1 != dt.datetime(2020, 12, 31):
    
            dict_measures = data_day_dict(key, date1, measurement_structure)
            measures = data_day(key, date1, measurement_structure)
            plot_day(key, date1, measures)
            
            date1 += dt.timedelta(days = 1)
 
