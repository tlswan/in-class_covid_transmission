#!/usr/bin/env python3
# coding: utf-8
"""
Simulate in-class infections and resulting hospitalizations and deaths over the course of a college semester
@author: tlswan
"""

import pandas as pd
import numpy as np
import math
import random
import datetime
from joblib import Parallel, delayed

from simulation_of_semester import semesters
from infection_outcomes import simulate_outcomes
from tqdm import tqdm


# ### Inputs

classrooms_data = pd.read_csv("pseudo_classrooms.csv")
schedules_data = pd.read_csv("pseudo_schedule.csv", index_col=0)

# ### Parallelize simulation model

def parallel_semester(days_in_semester, init_vax_prob, faculty_vax_rate, init_infec_prob, outside_infec_prob, asymptomatic_rate, classrooms_data, schedules_data, incubation_time, infectious_time, testing_policy, uvc, mask_inhale, mask_exhale, Ninf):
    tracking, active, initial, outside = semesters(days_in_semester, init_vax_prob, faculty_vax_rate, init_infec_prob, outside_infec_prob, asymptomatic_rate, classrooms_data, schedules_data, incubation_time, infectious_time, testing_policy, uvc, mask_inhale, mask_exhale, Ninf)
    semester_infections = tracking.loc[(tracking['day_0']==0) & (tracking['day_'+str(days_in_semester)]==1),'day_'+str(days_in_semester)] # identify students infected by end of semester who were not vaccinated or initially infected
    semester_infections = semester_infections.drop(outside) # identify students infected specifically in class
    infectable = len(schedules_data)-(len(outside) + tracking['day_0'].sum()) #subtract vaccinated, intial infections, and outside infections from total number of students

    semester_infections_output=pd.DataFrame(index=schedules_data.index)
    semester_infections_output["Output"]=0
    semester_infections_output.loc[semester_infections.index,"Output"]=1
    semester_infections_output = semester_infections_output["Output"].values

    vax_status_output=pd.DataFrame(index=schedules_data.index)
    vax_status_output["Vax_Status"]=tracking["day_0"]
    vax_status_output.loc[vax_status_output.index.isin(initial),"Vax_Status"] = 0 # remove initial infections
    vax_status_output = vax_status_output["Vax_Status"].values

    return semester_infections_output, vax_status_output


# ### Scenario Testing

# Constant parameters

R_semester = 1000  # number of replications of semester
incubation_time = 2 # assume not infectious yet this many days
infectious_time = 7 # assume infectious exactly this many days if no testing

weeks = 13 # number of weeks in semester
D = 7*weeks # number of days (including weekends) in semester


init_infec_prob = .01 #probability of infection at start of semester
outside_infec_prob = .001 # probability of infection during semester from outside of class (daily)
asymptomatic_rate = .4 # probability an infection shows no symptoms


# Varying parameters

run_no = 1

init_vax_prob = 0.95 # probability a student is vaccinated at beginning of semester
fac_vax_rate = 0.95 # probability an instructor is vaccinated at beginning of semester
testing_policy = True # Boolean
masking_inhale = 0.4 # effectiveness of masking for inhaling (0 if no masking policy in place)
masking_exhale = 0.4 # effectiveness of masking for exhaling (0 if no masking policy in place)
uvc = 0 # binary, whether UVC fans are installed in all classrooms or not
Ninf = 75 # k value for dose response function (higher values indicate lower transmissibilty)

# Run in parallel
cores = 1

start_time = datetime.datetime.now()
infections_output, vax_output = zip(*Parallel(n_jobs=cores)(delayed(parallel_semester)(D, init_vax_prob, fac_vax_rate, init_infec_prob, outside_infec_prob, asymptomatic_rate, classrooms_data, schedules_data, incubation_time, infectious_time, testing_policy, uvc, masking_inhale, masking_exhale, Ninf) for r in range(R_semester)))

infections_output = pd.DataFrame(infections_output)
infections_output.to_csv("run_"+str(run_no)+"_infections.csv")

vax_output = pd.DataFrame(vax_output)
vax_output.to_csv("run_"+str(run_no)+"_vaccinations.csv")

run_time = datetime.datetime.now()-start_time
print(str(run_no)+" complete in: "+str(run_time)+" at: "+str(datetime.datetime.now()))



# ### Simulate outcomes

#assign hospitalization rates & deaths rates|hospitalization by age (aka risk) group
students = np.where(schedules_data['risk_group']=='student')[0]
fac_25_to_39 = np.where((schedules_data['risk_group']=='20-29')|(schedules_data['risk_group']=='30-39'))[0]
fac_40_to_49 = np.where(schedules_data['risk_group']=='40-49')[0]
fac_50_to_59 = np.where(schedules_data['risk_group']=='50-59')[0]
fac_60_to_69 = np.where((schedules_data['risk_group']=='60-64')|(schedules_data['risk_group']=='65-69'))[0]
fac_over_70 = np.where((schedules_data['risk_group']=='70-74')|(schedules_data['risk_group']=='75+'))[0]

age_groups = [students,fac_25_to_39,fac_40_to_49,fac_50_to_59,fac_60_to_69,fac_over_70]
hosp_rates = [.006, .0273, .0546, .0873, .1501, .343]
death_rates = [.019, .019, .019, .0711, .1327, .3697]

#simulate hospitalizations and deaths for specified runs
start_time = datetime.datetime.now()

run_hosps = pd.DataFrame(dtype=float)
run_deaths = pd.DataFrame(dtype=float)

infections = pd.read_csv('run_'+str(run_no)+'_infections.csv',index_col=0)

for g in range(len(age_groups)):

    group = age_groups[g]
    infections_g =  infections.iloc[:,group].sum(axis=1)
    hosp_rate = hosp_rates[g]
    death_rate = death_rates[g]

    hospitalizations,deaths = zip(*Parallel(n_jobs=cores)(delayed(simulate_outcomes)(infections_g[i], hosp_rate, death_rate) for i in range(R_semester)))
    run_hosps['Run_'+str(run_no)+'_'+str(g)]=np.asarray(hospitalizations).reshape(-1)
    run_deaths['Run_'+str(run_no)+'_'+str(g)]=np.asarray(deaths).reshape(-1)

col_names = ['Run_'+str(run_no)+'_students', 'Run_'+str(run_no)+'_fac_25_to_39',
             'Run_'+str(run_no)+'_fac_40_to_49','Run_'+str(run_no)+'_fac_50_to_59',
             'Run_'+str(run_no)+'_fac_60_to_69','Run_'+str(run_no)+'_fac_over_70']

run_hosps.columns = col_names
run_deaths.columns = run_hosps.columns

run_hosps.to_csv("run_"+str(run_no)+"_hosps.csv")
run_deaths.to_csv("run_"+str(run_no)+"_deaths.csv")

run_time = datetime.datetime.now()-start_time
print(run_time)
