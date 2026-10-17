#Author C. Junger, S. Schoder, v2 2024 03 04
import numpy as np

# fan characteristics
dpts = 128.0 # total-to-static pressure difference
#dpts = 225.4
#dpts = 134.7
vol_flowrate = 1.4 # volumetric flow
#vol_flowrate = 0.5
#vol_flowrate = 1.0

# 0.5, 1.0
D = 0.5 # Laufraddurchmesser
n = 1486.0 # rotational speed 1/min
u = np.pi*D*n/60 # rotational velocity m/s
a = 343.0 # speed of sound
eta = 0.53 # total-to-static efficiency from measurement
#eta = 0.35
#eta = 0.45

print("Measeurement")
print("L_W = ",87.3,"dB")
#print("L_W = ",85.5,"dB")
#print("L_W = ",93.0,"dB")


## VDI 2801
# parameter
L_wspez = 42.0 # spezifischer Schallleistungspegel
gamma = 5.0 # Machzahlexponent

# sound power
L_W = L_wspez + 10 * np.log10(vol_flowrate) + 5*(gamma-1) * np.log10(dpts)
print("VDI 2801")
print("L_W = ",L_W,"dB")


## VDI 3731
# parameter
dp0 = 1.0 
vol_flowrate0 = 1.0
m = 3.16 # Machzahlexponent
L_wspez = 96.6 # dB spezifischer Schallleistungspegel

# sound power
L_W = L_wspez + 10 * np.log10((dpts/dp0)*(vol_flowrate/vol_flowrate0) *(1.0/eta-1)) + 10 * m * np.log10(u/a)

print("VDI 3731")
print("L_W = ",L_W,"dB")
