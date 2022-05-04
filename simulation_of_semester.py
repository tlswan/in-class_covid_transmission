#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulate infection transfer among all classes across single semester
@author: tlswan
"""

import pandas as pd
import numpy as np
import math
import random
from classroom_level_infections import classes
from dose_response_functions import dose_response
from length_of_infections import infectious_period


#run semester of classes given students' infections states at start of semester and return estimate of new infections from classes
def semesters(days_in_semester, init_vax_prob, faculty_vax_rate, init_infec_prob, outside_infec_prob, asymptomatic_rate, classrooms_data, schedules_data, incubation_time,infectious_time, testing_policy, uvc, mask_inhale, mask_exhale, Ninf):

    day_names = ['day_'+str(i) for i in range(days_in_semester+1)]
    dow = pd.Series(["S","M","Tu","W","Th","F","S"])

    # initialize infection tracking and active infections dataframes
    students = pd.DataFrame(index=schedules_data.index)
    students.index.name = 'Student_ID'

    students['Vax_status']=np.random.binomial(n=1, p=init_vax_prob, size=students.shape[0]) # random process

    students.loc[schedules_data['risk_group']!='student','Vax_status'] = np.random.binomial(n=1, p=faculty_vax_rate, size=students.loc[schedules_data['risk_group']!='student'].shape[0]) # apply faculty vax rate random process

    students_per_test_day = math.ceil(len(students)/5)
    students['Test_day'] = random.sample(["M"]*students_per_test_day+["Tu"]*students_per_test_day+["W"]*students_per_test_day+
                                         ["Th"]*students_per_test_day+["F"]*students_per_test_day, len(students)) #assign weekday test day to students

    tracking_infections = pd.DataFrame(0, columns= day_names,index=students.index) # 1: vaccinated/prev infected by end of day-- value carries into all subsequent days
    tracking_infections.loc[:,"day_0":"day_"+str(days_in_semester)] =  students['Vax_status'].values[:,None] # set day 0 infections & onward to vaccination status

    active_infections = pd.DataFrame(0, columns= day_names[1:days_in_semester+1],index=students.index) # 1: infectious at start of day
    not_vaccinated = tracking_infections.loc[tracking_infections["day_0"]==0,"day_0"]
    initial_infections = pd.Series(np.random.binomial(n=1, p=init_infec_prob, size=not_vaccinated.shape[0]), index=not_vaccinated.index) # random process setting student infections at start of day 1 (excluding vaccinated students)
    initial_infections = initial_infections.loc[initial_infections.values==1].index
    active_infections = infectious_period(testing_policy, 0, days_in_semester, dow, students, active_infections, initial_infections, asymptomatic_rate, 0, infectious_time) #set intial infections lengths based on testing policy as if infected 2 days before school start
    tracking_infections.loc[tracking_infections["day_0"]==0,"day_0":"day_"+str(days_in_semester)] =  active_infections.loc[tracking_infections["day_0"]==0,'day_1'].values[:,None] # set day 0 infections & onward to initial infections for those not vaccinated

    outside_infections = []

    for d in range(days_in_semester):
        day = dow[d%7]
        if (day=='S'): continue # skip weekend days

        # add in class infections to new infections
        day_classes = classrooms_data[(classrooms_data['Days'].str.contains(day))] # get classes on day d

        daily_infections = pd.DataFrame(0, columns=["Exposure"],index=students.index)
        for c in day_classes['class_id'].values:
                infectable_students, exposure = classes(d+1,c,classrooms_data, uvc, mask_inhale, mask_exhale, schedules_data,tracking_infections, active_infections) # random process setting student infections at end of class
                daily_infections.loc[infectable_students,"Exposure"]= daily_infections["Exposure"]+exposure #add class exposure to previous daily exposure

        daily_infections["P(Infection)"]= daily_infections["Exposure"].apply(lambda exposure : dose_response(exposure, Ninf)) #calculate dose response function for each student
        daily_infections["Outcome"]= daily_infections["P(Infection)"].apply(lambda infect_prob: np.random.binomial(n=1, p=infect_prob)) #assign infection from probability of infection by bernoulli dist

        infected_students = daily_infections.loc[daily_infections["Outcome"]==1].index.values.tolist()

        # add outside infections to new infections
        never_infected = tracking_infections.loc[tracking_infections["day_"+str(d+1)]==0,"day_"+str(d+1)] # identify those who could be infected outside classrooms on day d
        infected_students_o =  pd.Series(np.random.binomial(n=1, p=outside_infec_prob, size=never_infected.shape[0]), index=never_infected.index) # infect infectable students w outside infection probability
        infected_students_o = infected_students_o.loc[infected_students_o==1]
        if infected_students_o.size >0:
            outside_infections.extend(infected_students_o.index.values.tolist()) # add outside infections to semseter long outside infections list
            infected_students.extend(infected_students_o.index.values.tolist()) # add outside infections to new active infections

        infected_students = list(set(infected_students)) #remove duplicates

        if len(infected_students)>0:
            #assign infections to all future days in tracking
            tracking_infections.loc[infected_students,"day_"+str(d+1):"day_"+str(days_in_semester)]=1
            # assign period of infectiousness to infected students
            active_infections = infectious_period(testing_policy, d, days_in_semester, dow, students, active_infections, infected_students, asymptomatic_rate, incubation_time, infectious_time)

    return tracking_infections, active_infections, initial_infections, outside_infections
