# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 12:32:50 2020

@author: crist
"""
import datetime as dt

class measurement_class():
    def __init__(self,row, date, index):
        """
        """
        
        if len(index) == 3:
            
            data = [row[index[0]], row[index[1]], row[index[2]]]
            dates =[date[index[0]],date[index[1]],date[index[2]]]
            
            for j in range(len(data)):
                for k in range(4):
                    if data[j][k+1] == '':
                        data[j][k+1] = '9999'
            
            self.unit = data[0][0]
            self.m1 = [int(data[0][1]),int(data[1][1]),int(data[2][1])]
            self.m2 = [int(data[0][2]),int(data[1][2]),int(data[2][2])]
            self.m3 = [int(data[0][3]),int(data[1][3]),int(data[2][3])]
            self.m4 = [int(data[0][4]),int(data[1][4]),int(data[2][4])]
            
            year_1 = dates[0].year
            year_2 = dates[1].year
            year_3 = dates[2].year
            chk_year_1 = (year_1 != 2000 and year_1 != 2080)
            chk_year_2 = (year_2 != 2000 and year_2 != 2080)
            chk_year_3 = (year_3 != 2000 and year_3 != 2080)
            
            if chk_year_1:
                date1 = dt.datetime(dates[0].year, dates[0].month, dates[0].day)
                delta2 = dt.timedelta(hours=dates[1].hour, minutes = dates[1].minute, seconds = dates[1].second)
                delta3 = dt.timedelta(hours=dates[2].hour, minutes = dates[2].minute, seconds = dates[2].second)
                dates[1] = date1 + delta2
                dates[2] = date1 + delta3
                
            elif chk_year_2:
                date2 = dt.datetime(dates[1].year, dates[1].month, dates[1].day)
                delta1 = dt.timedelta(hours=dates[0].hour, minutes = dates[0].minute, seconds = dates[0].second)
                delta3 = dt.timedelta(hours=dates[2].hour, minutes = dates[2].minute, seconds = dates[2].second)
                dates[0] = date2 + delta1
                dates[2] = date2 + delta3

            elif chk_year_3:
                date3 = dt.datetime(dates[2].year, dates[2].month, dates[2].day)
                delta1 = dt.timedelta(hours=dates[0].hour, minutes = dates[0].minute, seconds = dates[0].second)
                delta2 = dt.timedelta(hours=dates[1].hour, minutes = dates[1].minute, seconds = dates[1].second)
                dates[0] = date3 + delta1
                dates[1] = date3 + delta2
                
            self.date = [dates[0],dates[1],dates[2]]
            
            lat = 0.0
            lon = 0.0
            pos_check = True
            alt_check = True
            press_check = True
            temp_check = True
            
            for i in data:
                if i[6] == 'S':
                    lat = -1
                elif i[6] == 'N':
                    lat = 1
                
                if i[8] == 'W':
                    lon = -1
                elif i[8] == 'E':
                    lon = 1
                
                if pos_check and (abs(lat) > 0.0) and (abs(lon) > 0.0):
                    self.position = [lat*float(i[5]),lon*float(i[7])]
                    pos_check = False
                if alt_check and i[15] != '':
                    self.altitude = float(i[15])
                    alt_check = False
                elif alt_check and i[18] != '':
                    self.altitude = float(i[18])
                    alt_check = False
                    
                if  press_check and i[17] != '':
                    self.pressure = float(i[17])
                    press_check = False
                    
                if temp_check and i[16] != '':
                    self.temperature = float(i[16])
                    temp_check = False                   
                    
            if pos_check == True:
                self.position = [lat,lon]                
            
            if alt_check == True:
                self.altitude = 9999.99 
 
            if press_check == True:
                self.pressure = 0.0
                
            if temp_check == True:
                 self.temperature = 99.9
                
                
        elif len(index) == 2:
            
            data = [row[index[0]], row[index[1]]]
            dates =[date[index[0]],date[index[1]]]
            
            for j in range(len(data)):
                for k in range(4):
                    if data[j][k+1] == '':
                        data[j][k+1] = '9999'
            
            self.unit = data[0][0]
            self.m1 = [int(data[0][1]),int(data[1][1])]
            self.m2 = [int(data[0][2]),int(data[1][2])]
            self.m3 = [int(data[0][3]),int(data[1][3])]
            self.m4 = [int(data[0][4]),int(data[1][4])]
 
            year_1 = dates[0].year
            year_2 = dates[1].year
            chk_year_1 = (year_1 != 2000 and year_1 != 2080)
            chk_year_2 = (year_2 != 2000 and year_2 != 2080)
            
            if chk_year_1:
                date1 = dt.datetime(dates[0].year, dates[0].month, dates[0].day)
                delta2 = dt.timedelta(hours=dates[1].hour, minutes = dates[1].minute, seconds = dates[1].second)
                dates[1] = date1 + delta2
                
            elif chk_year_2:
                date2 = dt.datetime(dates[1].year, dates[1].month, dates[1].day)
                delta1 = dt.timedelta(hours=dates[0].hour, minutes = dates[0].minute, seconds = dates[0].second)
                dates[0] = date2 + delta1
                               
            self.date = [dates[0],dates[1]]
            
            lat = 0.0
            lon = 0.0
            pos_check = True
            alt_check = True
            press_check = True
            temp_check = True
            
            for i in data:
                if i[6] == 'S':
                    lat = -1
                elif i[6] == 'N':
                    lat = 1
                
                if i[8] == 'W':
                    lon = -1
                elif i[8] == 'E':
                    lon = 1
                
                if pos_check and (abs(lat) > 0.0) and (abs(lon) > 0.0):
                    self.position = [lat*float(i[5]),lon*float(i[7])]
                    pos_check = False
                if alt_check and i[15] != '':
                    self.altitude = float(i[15])
                    alt_check = False
                elif alt_check and i[18] != '':
                    self.altitude = float(i[18])
                    alt_check = False
                    
                if  press_check and i[17] != '':
                    self.pressure = float(i[17])
                    press_check = False
                    
                if temp_check and i[16] != '':
                    self.temperature = float(i[16])
                    temp_check = False                   
                    
            if pos_check == True:
                self.position = [lat,lon]                
            
            if alt_check == True:
                self.altitude = 9999.99 
 
            if press_check == True:
                self.pressure = 0.0
                
            if temp_check == True:
                 self.temperature = 99.9
        
        elif len(index) == 1:
                        
            data = [row[index[0]]]
            
            for j in range(len(data)):
                for k in range(4):
                    if data[j][k+1] == '':
                        data[j][k+1] = '9999'
            
            self.unit = data[0][0]
            self.m1 = [int(data[0][1])]
            self.m2 = [int(data[0][2])]
            self.m3 = [int(data[0][3])]
            self.m4 = [int(data[0][4])]
            
            self.date = [date[index[0]]]
            
            lat = 0.0
            lon = 0.0
            pos_check = True
            alt_check = True
            press_check = True
            temp_check = True
            
            for i in data:
                if i[6] == 'S':
                    lat = -1
                elif i[6] == 'N':
                    lat = 1
                
                if i[8] == 'W':
                    lon = -1
                elif i[8] == 'E':
                    lon = 1
                
                if pos_check and (abs(lat) > 0.0) and (abs(lon) > 0.0):
                    self.position = [lat*float(i[5]),lon*float(i[7])]
                    pos_check = False
                if alt_check and i[15] != '':
                    self.altitude = float(i[15])
                    alt_check = False
                elif alt_check and i[18] != '':
                    self.altitude = float(i[18])
                    alt_check = False
                    
                if  press_check and i[17] != '':
                    self.pressure = float(i[17])
                    press_check = False
                    
                if temp_check and i[16] != '':
                    self.temperature = float(i[16])
                    temp_check = False                   
                    
            if pos_check == True:
                self.position = [lat,lon]                
            
            if alt_check == True:
                self.altitude = 9999.99 
 
            if press_check == True:
                self.pressure = 0.0
                
            if temp_check == True:
                 self.temperature = 99.9
