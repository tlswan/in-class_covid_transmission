#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
From list of infected individuals, assign outcomes
@author: tlswan
"""

import pandas as pd
import numpy as np

def simulate_outcomes(infections_results_row,hosp_rate, death_rate):

    hospitalizations = pd.Series(dtype=float)
    deaths = pd.Series(dtype=float)

    current_hospitalizations = pd.Series(np.random.binomial(n=infections_results_row, p=hosp_rate, size=100)) # simulate 100 replications of hospitalizations per semester infections replication
    hospitalizations = hospitalizations.append(current_hospitalizations)

    for j in range(current_hospitalizations.size):
        current_deaths=pd.Series(np.random.binomial(n = current_hospitalizations[j], p=death_rate, size=1000)) # simulate 1000 replications of deaths per semester hospitalizations replication
        deaths = deaths.append(current_deaths)

    return hospitalizations, deaths
