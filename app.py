# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 17:01:23 2021

@author: sercan
"""
#Import libraries--------------------------------------------------------------
import streamlit as st
import numpy as np
from scipy.optimize import curve_fit   
import matplotlib.pyplot as plt
plt.style.use('default')

#Define curve fitting functions------------------------------------------------
#y-shear rate
#K-consistency index
#n-flow behavior index
#ty-yield stress

def YPLfunction(y, ty, K, n):
    return ty + K*y**n

def PLfunction(y, K, n):
    return  K*y**n

def BPfunction(y,PV,YP):
    return YP + PV*y

#Perform curve fitting and calculate r2----------------------------------------
#PL - power law
#YPL - yield power law
#BP - bingham plastic

def r2(residuals,shear_stress,shear_rate):
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((shear_stress-np.mean(shear_stress))**2)
    return 1 - (ss_res / ss_tot) 

def PL(shear_stress,shear_rate):
    popt, pcov = curve_fit(PLfunction,shear_rate,shear_stress)
    K,m =popt[0],popt[1]
    residuals = shear_stress- PLfunction(shear_rate, popt[0],popt[1])
    r_squared = r2(residuals,shear_stress,shear_rate)   
    return K,m,r_squared

def YPL(shear_stress,shear_rate):          
    popt, pcov = curve_fit(YPLfunction,shear_rate,shear_stress)
    ty,K,m = popt[0],popt[1],popt[2]
    residuals = shear_stress- YPLfunction(shear_rate, popt[0],popt[1],popt[2])
    r_squared = r2(residuals,shear_stress,shear_rate)  
    
    if popt[0]<0:
        K,m,r_squared = PL(shear_stress,shear_rate)
        ty = 0
    return ty,K,m,r_squared
  
def BP(shear_stress,shear_rate):
    PV = (shear_stress[0] - shear_stress[1])/511
    YP = (2*shear_stress[1] - shear_stress[0])
    residuals = shear_stress- BPfunction(shear_rate, PV, YP)
    r_squared = r2(residuals,shear_stress,shear_rate) 
    return r_squared,PV, YP

#The header and initial comments for the users---------------------------------
st.header("Drilling Fluid Rheological Model Parameters")
st.write("This web-app is used to analyze API rotational viscometer data by comparing various rheological models.")
st.write("The rheological constants for Yield Power-law (YPL - also called Herschel-Bulkley), Power-law, and Bingham-Plastic models are calculated and compared.")
st.write("Please enter API viscometer readings using the slider on the left side.")
st.write("NOTE: If you are not using a 6-speed viscometer, and need to enter rotation speed manually, please see viscometerapi.herokuapp.com")
#Define shearrate and rpm values used in the viscometer (for 6-speed viscometer)
visc_rpm = [600,300,200,100,6,3]
shear_rate = np.asarray(visc_rpm) * 1.7011 #unit conversion from RPM to 1/s
dial_readings = []

#Generate the sidebards for dial reading entries-------------------------------
for i in range(6):
    globals()['entry_{}'.format(i)] = st.sidebar.slider(
        'Viscometer Dial Reading at  at {} RPM'.format(visc_rpm[i]), 
        min_value = 0, value = int(visc_rpm[i]/10), max_value = 100, step=1)
    dial_readings.append(globals()['entry_{}'.format(i)])

#Entries: if higher RPM value entered is lower than next one, make corrections-
for i in range(5):
    if dial_readings[i]<dial_readings[i+1]:
        dial_readings[i] = dial_readings[i+1]

#Perform curve fitting for all three rheological models------------------------
shear_stress = np.asarray(dial_readings) * 0.5104 #1.066 * 0.4788 #unit conversion from DR to Pascal

ty_YPL,K_YPL,n_YPL,r2_YPL = YPL(shear_stress,shear_rate)
K_PL,n_PL,r2_PL = PL(shear_stress,shear_rate)
r2_BP,PV,YP = BP(shear_stress,shear_rate)

#Denoised values for visuals---------------------------------------------------
shear_stress_calc_YPL = YPLfunction(shear_rate, ty_YPL, K_YPL, n_YPL)
shear_stress_calc_PL = PLfunction(shear_rate, K_PL, n_PL)
shear_stress_calc_BP = BPfunction(shear_rate, PV, YP)

#Printing out the rheological constants for each model-------------------------
st.subheader ("Herschel Bulkley (Yield Power Law) Model Rheological Constants")
st.write("Yield stress ($t_{y}$) is", round(ty_YPL,2), "$Pa$")
st.write("Consistency index (K) is", round(K_YPL,4), "$Pa.s^{n}$")
st.write("Flow index (n) is", round(n_YPL,2))
st.write("Coefficient of determination ($R^2$) is", round(r2_YPL,3))
 
st.subheader ("Power-Law Model Rheological Constants")
st.write("Consistency index (K) is", round(K_PL,4), "$Pa.s^{n}$")
st.write("Flow index (n) is", round(n_PL,2))
st.write("Coefficient of determination ($R^2$) is", round(r2_PL,3))

st.subheader ("Bingham Plastic Model Rheological Constants")
st.write("Plastic viscosity (PV) is", dial_readings[0]-dial_readings[1] , "$cp$") 
st.write("Yield point (YP) is", 2*dial_readings[1]-dial_readings[0], "$lb/100ft^2$")
st.write("Coefficient of determination ($R^2$) is", round(r2_BP,3))

#Visuazalization---------------------------------------------------------------
fig = plt.figure(figsize=(8,5))
ax = fig.add_subplot(1,1,1)

ax.scatter(x=shear_rate,y=shear_stress,
           label="Measured viscometer data", color="red")

ax.plot(shear_rate,shear_stress_calc_YPL,
        label="Yield Power-law model fit",color="blue")

ax.plot(shear_rate,shear_stress_calc_PL,
        label="Power-law model fit",color="orange")

ax.plot(shear_rate,shear_stress_calc_BP,
        label="Bingham Plastic model Fit",color="green")    

ax.set_xlabel("Shear Rate (1/s)")
ax.set_ylabel("Shear Stress (Pa)")
ax.set_xlim(0,round(max(shear_rate)+40,0))
ax.set_ylim(0,round(max(shear_stress)+10,0))
ax.legend()

#Write the figure to streamlit-------------------------------------------------
st.write(fig)

#Deciding the best fit to the data---------------------------------------------
if round(r2_BP,3) >= round(r2_PL,3) and round(r2_BP,3) >=round(r2_YPL,3):
    st.subheader("Bingham plastic (BP) model provides the best fit to the data.")

elif round(r2_PL,3) >= round(r2_BP,3) and round(r2_PL,3) >= round(r2_YPL,3):
    st.subheader("Power law (PL) model provides the best fit to the data.")

else:
    st.subheader("Yield power law (YPL) model provides the best fit to the data.")
    
#Final remarks-----------------------------------------------------------------
st.write("Developer: Sercan Gul (sercan.gul@gmail.com, https://github.com/sercangul)")
st.write("Source code: https://github.com/sercangul/apiviscometer")