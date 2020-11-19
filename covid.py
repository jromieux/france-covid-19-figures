#!/usr/bin/env python3

# to run the file in python shell:
# exec(open('your_directory_path/covid.py').read())
# NOTE: Windows path is given with '\' and python only accepts '/'

import csv
# importing datetime module 
from datetime import *

##########################################################################################
#																						 #
# 						 	1- SET BEGINNING OF THE ANALYSIS							 #
#																						 #
##########################################################################################

# date(year, month, day) 
DAY_ZERO = date(2020, 2, 2) 

# This data is only use to start forecasting from a specific date
DAY_START_FORECASTING = date(2020, 10, 1) 

##########################################################################################
#																						 #
# 						 	         2- SET FILTERS	    								 #
#																						 #
##########################################################################################

#FILTER_CODE = "DEP-34" #"DEP-75" #"FRA"
FILTER_CODE = input("Enter a departement number (ex. 75) or FRA for France:\n")
FILTER_CODE = FILTER_CODE.upper()
if FILTER_CODE.isdigit():
    PLT_TITLE = "Dept. "+FILTER_CODE
    FILTER_CODE = "DEP-"+FILTER_CODE
else:
    PLT_TITLE = "France"
    
if FILTER_CODE == "FRA":
    FILTER_SRC_TYPE = "opencovid19-fr" #"ministere-sante" # "opencovid19-fr"
else:
    FILTER_SRC_TYPE = "sante-publique-france-data"

##########################################################################################
#																						 #
# 						 	     3- SETUP CONSTANTS	    								 #
#																						 #
##########################################################################################

CSV_DELIMITER=','

COL_DATE=0
COL_GRAN=1
COL_CODE=2
COL_NOM=3

COL_DECES=8
COL_REA=10
COL_HOSP=11
COL_NEW_HOSP=12

COL_SRC_TYPE=19

##########################################################################################
#																						 #
# 						 	     4- INIT VARIABLES	    								 #
#																						 #
##########################################################################################
nb_deces = []
nb_deces_per_day = []
nb_rea = []
nb_new_hosp = []
nb_hosp = []
days = []
days_number=[]

nb_days=0
curr_deces = 0

day_index_start_forecasting=0

##########################################################################################
#																						 #
# 					     5- UPLOAD RAW DATA (CSV FILE)	   								 #
#																						 #
##########################################################################################

# get data from https://www.data.gouv.fr/fr/datasets/chiffres-cles-concernant-lepidemie-de-covid19-en-france/#_
# install requests module
import requests
data_url = 'https://raw.githubusercontent.com/opencovid19-fr/data/master/dist/chiffres-cles.csv'
r = requests.get(data_url)

##########################################################################################
#																						 #
# 					  			   6- PARSE CSV FILE	   								 #
#																						 #
##########################################################################################

readCSV = csv.reader(r.content.decode('utf-8').splitlines(), delimiter=CSV_DELIMITER)
next(readCSV) # skip first line of the file
for row in readCSV:
    # Get current date
    y, m, d = [int(x) for x in row[COL_DATE].replace('_','-').split('-')] 
    day = date(y, m, d)
    
    if row[COL_SRC_TYPE]==FILTER_SRC_TYPE and row[COL_CODE]==FILTER_CODE and day >= DAY_ZERO:
        days_number.append(int(nb_days))
        if day == DAY_START_FORECASTING:
            day_index_start_forecasting = nb_days
        nb_days = nb_days + 1
        days.append(day)

        if row[COL_NEW_HOSP].isdigit():
            nb_new_hosp.append(int(row[COL_NEW_HOSP]))
        else:
            nb_new_hosp.append(0)
        
        if row[COL_DECES].isdigit():
            nb_deces.append(int(row[COL_DECES]))
            nb_deces_per_day.append(int(row[COL_DECES]) - curr_deces)
            curr_deces = int(row[COL_DECES])
        else:
            nb_deces.append(0)
            
        if row[COL_REA].isdigit():
            nb_rea.append(int(row[COL_REA]))
        else:
            nb_rea.append(0)
            
        if row[COL_HOSP].isdigit():
            nb_hosp.append(int(row[COL_HOSP]))
        else:
            nb_hosp.append(0)

##########################################################################################
#																						 #
# 									7- PLOT DATA										 #
#																						 #
##########################################################################################

# These imports are required to display the month in french
import locale, datetime
locale.setlocale(locale.LC_ALL, 'french')
from matplotlib.dates import DateFormatter
formatter = DateFormatter('%B')

# Import for plotting curves
import matplotlib.pyplot as plt
# Close any open window
plt.close('all')

# FIGURE 1
plt.figure(1)
plt.bar(days, nb_deces_per_day, align='center', alpha=0.5, color='red')
plt.xlabel('mois')
plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
plt.title(PLT_TITLE + " - Nouveaux deces")

# FIGURE 2
plt.figure(2)
plt.bar(days, nb_new_hosp, align='center', alpha=0.5, color='purple')
plt.xlabel('mois')
plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
plt.title(PLT_TITLE + " - Nouvelles hospitalisations")

# FIGURE 0
plt.figure(0)
plt.plot(days, nb_hosp, '-', color='purple', label='Hospitalisation')
plt.plot(days, nb_deces, '-', color='red', label='Deces')
plt.plot(days, nb_rea, '-', color='orange', label='Reanimation')
#plt.ylabel('Nombre')
plt.xlabel('mois')
plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
plt.title(PLT_TITLE + " - Nombre de personnes")
plt.legend()

##########################################################################################
#																						 #
# 									8- FORECASTING										 #
#																						 #
##########################################################################################

# # https://towardsdatascience.com/basic-curve-fitting-of-scientific-data-with-python-9592244a2509
# # Import curve fitting package from scipy
# from scipy.optimize import curve_fit
# import numpy as np
# 
# # Function to calculate the exponential with constants a and b
# def exponential(x, a, b):
#     return a*np.exp(b*x)
# 
# pars, cov = curve_fit(f=exponential, xdata=days_number[day_index_start_forecasting:], ydata=nb_hosp[day_index_start_forecasting:], p0=[0, 0], bounds=(-np.inf, np.inf))
# pars_rea, cov_rea = curve_fit(f=exponential, xdata=days_number[day_index_start_forecasting:], ydata=nb_rea[day_index_start_forecasting:], p0=[0, 0], bounds=(-np.inf, np.inf))
# pars_deces, cov_deces = curve_fit(f=exponential, xdata=days_number[day_index_start_forecasting:], ydata=nb_deces[day_index_start_forecasting:], p0=[0, 0], bounds=(-np.inf, np.inf))
# 
# # Get the standard deviations of the parameters (square roots of the # diagonal of the covariance)
# stdevs = np.sqrt(np.diag(cov))
# # Calculate the residuals
# res = nb_hosp[day_index_start_forecasting:] - exponential(np.array(days_number[day_index_start_forecasting:]), *pars)
# 
# # Plot the fit data as an overlay on the scatter data
# plt.figure(0)
# plt.plot(days[day_index_start_forecasting:], exponential(np.array(days_number[day_index_start_forecasting:]), *pars), linestyle='--', color='purple')
# plt.plot(days[day_index_start_forecasting:], exponential(np.array(days_number[day_index_start_forecasting:]), *pars_rea), linestyle='--', color='orange')
# plt.plot(days[day_index_start_forecasting:], exponential(np.array(days_number[day_index_start_forecasting:]), *pars_deces), linestyle='--', color='red')

##########################################################################################
#																						 #
# 								8- DISPLAY RESULTS										 #
#																						 #
##########################################################################################

# Show all figures
plt.show()


