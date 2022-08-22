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

def import_aeronet_data():
    """

    Returns
    -------
    data : Dictionary
        The measurements for each instrument.
    code : Dictionary
        The code for each measure.

    """

    # Code Dictionary
    index_data = [0,1,4,5,6,9,18,21,24,25,26,64,71,72,73,74,74,76,77,78,79,80]
    #Main Path
    path = "Code/../../aeronet"
    # Data File Path
    data_folder = os.listdir(path)
    
    folder_data = []
    for file in data_folder:
        file_data = []
        counter = 0
        with open(path + "/" + file) as csvfile:
            frame = csv.reader(csvfile)
            counter = 0
            header2 = []
            for row in frame:
                data = {}
                
                
                if counter == 6:
                    header = row
                    for index in index_data:
                        header2.append(row[index])
                        
                elif counter > 6:
                    for index in index_data:    
                        data[header[index]] = row[index]
                    file_data.append(data)
                counter += 1
        folder_data.append(file_data)
        
    return folder_data, header2
 
def aeronet_day_dict(folder_data, header):
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
    for data in folder_data:
        with open('Code/../../aeronet_data/'+ data[0][header[12]] + '_' + data[0][header[0]].replace(':','_') +'.json', "w") as outfile:  
            json.dump(data, outfile) 
    return True      

if __name__ == "__main__":
    folder_data, header = import_aeronet_data()
    aeronet_day_dict(folder_data, header)