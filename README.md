Tessa Swanson
tessaswanson.com

# in-class_covid_transmission
This repo provides information and code on how to evaluate COVID-19 aerosol transmission simulation-based risk analysis for in-person learning. See https://www.medrxiv.org/content/10.1101/2021.10.04.21263860v1 for description of methodology and parameter values.

The file pseudo_classrooms.csv contains generated data for 1,000 artificial courses for a college semester, when and where they meet, and the dimensions and airflow of their meeting space. This data is matched with the course ID in row 1 of "schedule.csv" to identify shared classroom spaces of students and faculty over the course of the semester.

The file pseudo_schedules.csv contains generated data for 10,000 artificial students and 1,000 artificial faculty assigning them to courses from "pseudo_classrooms.csv" with each student or faculty represented by a row indicating if that individual was enrolled in the course (1) or not (0). The final column indicates the risk group of the individual, identifying them as a student or by their age grouping for faculty.

The file "classroom_risk_simulation.py" is the primary script for running the simulation to estimate infections, hospitalizations, and deaths with all other .py files including functions that are used in the primary script. The primary script also contains a function for parallelizing the simulation. See simulation process diagram below for all steps included in the simulation model.

![simulation_diagram](https://user-images.githubusercontent.com/43580228/166741497-b09b84b3-6ec3-42b0-951d-10964ea1fb62.png)
