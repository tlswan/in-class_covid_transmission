#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Determine infections occuring in a classroom & from student and class schedules,
student infection histories, active student infections, and exposure/dose response parameters
@author: tlswan
"""

import pandas as pd
import numpy as np

from dose_response_functions import steady_state_dose

#run day of classes given students' daily infections states and return new infections
def classes(day,course,classroom_data, UVC, mask_inhale, mask_exhale, schedule_data, tracking_infections, active_infections) :

    # room characteristics
    room_area = float(classroom_data.loc[classroom_data['class_id']==str(course),'room_area']) # get area of room of course
    room_height = float(classroom_data.loc[classroom_data['class_id']==str(course),'room_height']) # get height of room
    minutes = int(classroom_data.loc[classroom_data['class_id']==str(course),'class_time']) # time in class in minutes
    airflow = float(classroom_data.loc[classroom_data['class_id']==str(course),'ACH']) # air changes per hour

    # infected students
    class_students = pd.Series(schedule_data.loc[(schedule_data[course]==1)&(schedule_data['risk_group']=='student')].index) # all students in course
    init_class_infections_stud = sum(active_infections["day_"+str(day)].loc[class_students]) # students in course actively infectious at start of day represented by 1

    # infected faculty
    class_fac = pd.Series(schedule_data.loc[(schedule_data[course]==1)&(schedule_data['risk_group']!='student')].index) # all faculty in class
    init_class_infections_fac = sum(active_infections["day_"+str(day)].loc[class_fac]) # faculty in course actively infectious at start of day represented by 1

    # infectable students & faculty
    class_member = pd.Series(schedule_data.loc[(schedule_data[course]==1)].index) # all students & faculty in class
    tracked_class_infections = tracking_infections["day_"+str(day)].loc[class_member] # infectable people in course at start of day represented by 0
    infectable = tracked_class_infections.loc[(tracked_class_infections==0)] # students and fac able to be infected
    init_class_infections = init_class_infections_stud + init_class_infections_fac

    # caclulate exposure and probability of infection
    exposure = 0
    if (init_class_infections>0 and infectable.size>0):
        exposure = steady_state_dose(room_height,room_area, UVC, airflow, mask_inhale, mask_exhale, minutes, init_class_infections_stud, init_class_infections_fac)  #run well-mixed room model

    return infectable.index, exposure
