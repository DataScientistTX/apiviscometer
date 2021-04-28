# -*- coding: utf-8 -*-
"""
Created on Sun Dec 27 01:50:49 2020

@author: Admin
"""

import streamlit as st
import numpy as np
from scipy.optimize import curve_fit   
import math
import matplotlib.pyplot as plt
plt.style.use('default')

def YPLfunction(y, tauy, K, m):
    return tauy + K*y**m

def PLfunction(y, K2, n):
    return  K2*y**n

def rheology_PL(sigma,shearrate):
    shearstress = np.asarray(sigma) * 1.066 * 0.4788 #unit conversion   
    popt, pcov = curve_fit(PLfunction,shearrate,shearstress)
    K,m =popt[0],popt[1]
    residuals = shearstress- PLfunction(shearrate, popt[0],popt[1])
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((shearstress-np.mean(shearstress))**2)
    r_squared = 1 - (ss_res / ss_tot)       
    return K,m,r_squared

def rheology_YPL(sigma,shearrate):       
    #Trying the fit for YPL model
    shearstress = np.asarray(sigma) * 1.066 * 0.4788 #unit conversion         
    popt, pcov = curve_fit(YPLfunction,shearrate,shearstress)
    tauy,K,m = popt[0],popt[1],popt[2]
    residuals = shearstress- YPLfunction(shearrate, popt[0],popt[1],popt[2])
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((shearstress-np.mean(shearstress))**2)
    r_squared = 1 - (ss_res / ss_tot)
    
    if tauy<0:
        K,m,r_squared = rheology_PL(sigma,shearrate)
        tauy = 0
    return tauy,K,m,r_squared
#Let's define the r_squared calculation for Bingham Plastic model
    
def BPr2(stressmeasured,stresscalculated,shearrate):
    residuals = stressmeasured- stresscalculated
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((stressmeasured-np.mean(stressmeasured))**2)
    r_squared = 1 - (ss_res / ss_tot)   
    return r_squared

def main():
    
    st.header("Drilling Fluid Rheological Model Parameters")
    st.write("This web-app is used to analyze API rotational viscometer data by comparing various rheological models.")
    st.write("The rheological constants for Yield Power-law (YPL - also called Herschel-Bulkley), Power-law, and Bingham-Plastic models are calculated and compared.")
    st.write("Please enter API viscometer readings using the slider on the left side.")

    shearrate = [1021.4,510.7,340.5,170.2,10.2,5.1]

    box600 = st.sidebar.slider('Viscometer Dial Reading at 600 RPM',  min_value = 0, value = 50, max_value = 60, step=1)
    box300 = st.sidebar.slider('Viscometer Dial Reading at 300 RPM',  min_value = 0, value = 36, max_value = 60, step=1)
    box200 = st.sidebar.slider('Viscometer Dial Reading at 200 RPM',  min_value = 0, value = 30, max_value = 60, step=1)
    box100 = st.sidebar.slider('Viscometer Dial Reading at 100 RPM',  min_value = 0, value = 20, max_value = 60, step=1)
    box6 = st.sidebar.slider('Viscometer Dial Reading at 6 RPM',  min_value = 0, value = 7, max_value = 60, step=1)
    box3 = st.sidebar.slider('Viscometer Dial Reading at 3 RPM', min_value = 0, value = 6, max_value = 60, step=1)
    
    if box6<box3:
        box6=box3
    
    if box100<box6:
        box100=box6
        
    if box200<box100:
        box200 = box100
        
    if box300<box200:
        box300 = box200
        
    if box600<box300:
        box600=box300
       
    sigma = [box600,box300,box200,box100,box6,box3]

    tauy_YPL,K_YPL,m_YPL,r2_YPL = rheology_YPL(sigma,shearrate)
    K_PL,m_PL,r2_PL = rheology_PL(sigma,shearrate)
    shearstress = np.asarray(sigma) * 1.066 * 0.4788 #unit conversion    
    
    slope = (shearstress[0] - shearstress[1])/511
    intercept = (2*shearstress[1] - shearstress[0])

    sigmacalcBP = []
    for i in shearrate:
        calculation = intercept + slope*i
        sigmacalcBP.append(calculation)
    r2_BP = BPr2(shearstress,sigmacalcBP,shearrate)

    sigmacalcYPL = tauy_YPL + K_YPL*shearrate**m_YPL
    sigmacalcPL = K_PL*shearrate**m_PL

    st.subheader ("Herschel Bulkley (Yield Power Law) Model Rheological Constants")
    st.write("Yield stress ($t_{y}$) is", round(tauy_YPL,2), "$Pa$")
    st.write("Consistency index (K) is", round(K_YPL,4), "$Pa.s^{n}$")
    st.write("Flow index (n) is", round(m_YPL,2))
    st.write("Coefficient of determination ($R^2$) is", round(r2_YPL,3))
     
    st.subheader ("Power-Law Model Rheological Constants")
    st.write("Consistency index (K) is", round(K_PL,4), "$Pa.s^{n}$")
    st.write("Flow index (n) is", round(m_PL,2))
    st.write("Coefficient of determination ($R^2$) is", round(r2_PL,3))
    
    st.subheader ("Bingham Plastic Model Rheological Constants")
    st.write("Plastic viscosity (PV) is", sigma[0]-sigma[1] , "$cp$") 
    st.write("Yield point (YP) is", 2*sigma[1]-sigma[0], "$lb/100ft^2$")
    st.write("Coefficient of determination ($R^2$) is", round(r2_BP,3))
    
    fig = plt.figure(figsize=(8,5))
    ax = fig.add_subplot(1,1,1)
    
    ax.scatter(x=shearrate,y=shearstress,label="Measured viscometer data", color="red")

    ax.plot(shearrate,sigmacalcYPL,label="Yield Power-law model fit",color="blue")
    ax.plot(shearrate,sigmacalcPL,label="Power-law model fit",color="orange")
    ax.plot(shearrate,sigmacalcBP,label="Bingham Plastic model Fit",color="green")    

    ax.set_xlabel("Shear Rate (1/s)")
    ax.set_ylabel("Shear Stress (Pa)")
    ax.set_xlim(0,1200)
    ax.set_ylim(0,round(max(shearstress)+10,0))
    ax.legend()
    st.write(fig)
    
    if r2_YPL > r2_BP and r2_YPL>r2_PL:
        st.subheader("Yield power law (YPL) model provides the best fit to the data.")
        
    if r2_PL >= r2_BP and r2_PL>=r2_YPL:
        st.subheader("Power law (PL) model provides the best fit to the data.")
    
    if r2_BP >= r2_PL and r2_BP>=r2_YPL:
        st.subheader("Bingham plastic (BP) model provides the best fit to the data.")
    
    
    st.write("Developer: Sercan Gul (sercan.gul@gmail.com, https://github.com/sercangul)")
    st.write("Source code: https://github.com/sercangul/apiviscometer")
if __name__ == "__main__":
    main()
