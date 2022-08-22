# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 23:43:23 2020

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
    data = []
    
    #Main Path
    path = "Code/../../Ozono"
    # Data File Path
    data_folder = os.listdir(path)
    for file in data_folder:
            
        if file[-3:]=='dat':
            #Open Document
            with open(path + "/" + file) as csvfile:
                frame = csv.reader(csvfile)
                counter = 0
                for row in frame:
                    if counter >= 45:
                        data_row = row[0].split(' ')
                        data_line = []
                        for i in data_row:
                            data_line.append(float(i))
                        data.append(data_line)
                    counter += 1
                    
    return np.array(data)

def value(lamb0, struct):
    return np.interp(lamb0, struct[:,0], struct[:,1], left= 0, right= 0)

def got_o3(dobson, lamb0, struct):
    return np.around(np.interp(lamb0, struct[:,0], struct[:,1], left= 0, right= 0)*dobson*1e-3, 3)

if __name__ == "__main__":
    
    na = 6.02214e23
    ma = 47.997
    ro = 2.14e-3
    
    db = 300
    
    data = import_data()
    plt.figure()
    plt.grid()
    plt.semilogy(data[:,0],data[:,1],data[:,0],data[:,2],data[:,0],data[:,3])
    
    lamb = 1e-3*data[:,0]
    cs_0 = data[:,3]
    absortion = na*ro/ma*cs_0
    
    struct = np.ones([len(lamb), 2])
    struct[:,0] = struct[:,0] * lamb
    struct[:,1] = struct[:,1] * absortion
    
    list_struct = np.ndarray.tolist(struct)
    
    with open('Code/../../Ozono/absortion.json', "w") as outfile:  
        json.dump(list_struct, outfile) 
    
    plt.figure()
    plt.grid()
    plt.semilogy(lamb,absortion)
    
    plt.figure()
    plt.grid()
    plt.semilogy(lamb,db*1e-3*absortion)
    
    a = np.linspace(0.35,0.9,1000)
    b = got_o3(304,a,struct)
    
    plt.figure()
    plt.grid()
    plt.plot(a,b)
    
    with open('Code/../../Ozono/absortion.json', 'r') as file:
        json_file = json.load(file)
    r_struc = np.array(json_file)
 