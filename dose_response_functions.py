#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exposure and dose response functions
@author: tlswan
"""
# ### Room Dose Concentration Model

import math

# Well mixed room viral concentration function primarily referencing: "Evans M. Avoiding COVID-19: Aerosol Guidelines; 2020. https: //www.medrxiv.org/content/10.1101/2020.05.21.20108894v3.full.pdf"
def steady_state_dose(H_ft, A_ft, UVC, airflow, mask_inhale, mask_exhale, minutes_in_room, number_infected_students, number_infected_faculty):

    # Room parameters
    H = 0.3048*H_ft #convert units to metric
    A = .0929*A_ft
    V = H*A

    # Decay
    u_settle = .1 # settling speed of particle in meters/min
    tao_deactivate = 90 # infectivity decay of SARS-CoV-2 aerosol time in min (166 flu)
    tao_uv = 1/(0.377*115/100) #k*L*t_uv decay rate from UV fans DOW k=0.377 m^2/J L= 1 uW/cm2, t_i = 5s, t_60 = 115s
    # 0.377 m^2/J * 1 uW/cm2 * 115s * 10000 cm2/m2 * 1J/s/(1000000)uW # UVC binary variable turns this value on and off
    tao_settle = 20 #min (alt: u_settle*(H))

    tao_room = 60/airflow # airchanges approximation in min; airflow in ACH

    tao_a= 1/((1/tao_deactivate) + (1/tao_settle) + (UVC/tao_uv)) # timescale for aerosol decay in min (Evans section 6.2)
    f_a = tao_a / (tao_room + tao_a) # aerosol concentration decay factor (Evans eq 7)

    # Aerosol
    rho_0 = 1000 # viral load in saliva /nL
    r_src = 1*number_infected_students*(1-mask_exhale)+5*number_infected_faculty*(1-mask_exhale)# aerosol source rate  in nL/min (3 is occasional conversation, talkative ~4 nL/min, no talking ~1 nL/min) # potential for masking here, though evans paper assumes aerosols escape mask
    r_b = 10*(1-mask_inhale) #L/min breathing rate
    r_room = V/tao_room*1000 # m3/min converted to L/min

    # Concentration and exposure
    rho_A = rho_0 * (r_src / r_room) * f_a
    exposure = rho_A*r_b*minutes_in_room #(Evans eq 8)

    return exposure


# ### Dose Response Function

def dose_response(exposure_concentration, Ninf):

    prob_infection = 1-math.exp(-exposure_concentration/Ninf) # exponential dose response function

    return prob_infection
