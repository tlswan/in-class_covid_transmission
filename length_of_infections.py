#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Assign length of infection to individually infected students
@author: tlswan
"""

import pandas as pd
import numpy as np

# update active infections based on testing policy
def infectious_period(testing_policy, day, days_in_semester, dow, students, active_infections, infected_students, asymptomatic_rate, incubation_time, infectious_time):

    start_infectious_date = day+1+incubation_time
    if(start_infectious_date <= days_in_semester):

        # assign % students with asymptomatic infection
        asymptomatic_infections =  pd.Series(np.random.binomial(n=1, p=asymptomatic_rate, size=len(infected_students)), index=infected_students)

        if (testing_policy == True):
            for s in infected_students:

                # symptomatic infections: 1 day infectiousness
                if asymptomatic_infections[s]==0: active_infections.loc[infected_students,"day_"+str(start_infectious_date)]=1

                # asymptomatic infections: # days til next test from start_infectious_date + 1 day test turnaround time
                else:
                    # set infectious days equal to number of days between start_infectious_date and test_day plus one turnaround day
                    start_infectious_date = day+1+incubation_time
                    test_day = students.loc[s,'Test_day'] # get dow of testing
                    infectious_start_day = dow[start_infectious_date%7] # get day infection becomes detectable
                    # set infectious period equal to time between start_infectious_date and test date
                    infectious_time = dow[dow==test_day].index[0]-dow[dow==infectious_start_day].index[0]
                    if infectious_time<0: infectious_time=infectious_time+7
                    end_infectious_date = min(start_infectious_date+infectious_time,days_in_semester)
                    active_infections.loc[s,"day_"+str(start_infectious_date):"day_"+str(end_infectious_date)]=1

        else:
            for s in infected_students:

                # symptomatic infections: 1 day infectiousness
                if asymptomatic_infections[s]==0: active_infections.loc[infected_students,"day_"+str(start_infectious_date)]=1

                # asymptomatic infections: infectious_time
                else:
                    end_infectious_date = min(start_infectious_date+infectious_time,days_in_semester)
                    active_infections.loc[infected_students,"day_"+str(start_infectious_date):"day_"+str(end_infectious_date)]=1

    return active_infections
