"""
Created on Mon March  4 2024

@author: C. Junger, S. Schoder
"""
import numpy as np

# fan characteristics
dpts = 128.0 # total-to-static pressure difference
vol_flowrate = 1.4 # volumetric flow
D = 0.5 # Laufraddurchmesser
n = 1486.0 # rotational speed 1/min
u = np.pi*D*n/60 # rotational velocity m/s
c0 = 343.0 # speed of sound
eta = 0.53 # total-to-static efficiency from measurement

z = 9.0 # number of blades
r_i = 0.248/2 # hub radius
r_o = 0.495/2 # tip radius
b = r_o - r_i # chord width
Psi = 0.9*np.pi # gradient of lift coefficient
rho = 1.225 # density
Tu = 0.07 # turbulent intensity

# this values should be in the range of 50% - 70% of blade hight
w = np.pi*(r_i+(r_o-r_i)*0.5)*n/30 # relative velocity in the middle of the blade
l = (0.103 + 0.058)/2 # mean chord length

Re = 1.5*10**5 # reynolds number
 
# turbulent inlet
P_ti = z*1/(48*np.pi) * rho/c0**3 * b * l* Psi**2 * w**6 * Tu**2
# turbulent boundary layer
P_tbl = z * 10**-7 * rho/c0**3 * (r_o-r_i)*0.7 * l * w**6
# vortex shedding
P_vs = z * 1/(120*np.pi) * rho/c0**3 * (r_o-r_i)*0.7 * l * w**6 * Re**-0.4

P = P_ti + P_tbl + P_vs


P0 = 10**-12

L = 10*np.log10(P/P0)

print("Sharland")
print("L_W = ",L,"dB")

print("Measeurement")
print("L_W = ",87.3,"dB")