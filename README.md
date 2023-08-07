Tessa Swanson
tessaswanson.com

# in-class_covid_transmission
This repo provides information and code on how to evaluate COVID-19 aerosol transmission simulation-based risk analysis for in-person learning. See https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0271750 for description of methodology and parameter values.

The file pseudo_classrooms.csv contains generated data for 1,000 artificial courses for a college semester, when and where they meet, and the dimensions and airflow of their meeting space. This data is matched with the course ID in row 1 of "schedule.csv" to identify shared classroom spaces of students and faculty over the course of the semester.

The file pseudo_schedules.csv contains generated data for 10,000 artificial students and 1,000 artificial faculty assigning them to courses from "pseudo_classrooms.csv" with each student or faculty represented by a row indicating if that individual was enrolled in the course (1) or not (0). The final column indicates the risk group of the individual, identifying them as a student or by their age grouping for faculty.

The file "classroom_risk_simulation.py" is the primary script for running the simulation to estimate infections, hospitalizations, and deaths with all other .py files including functions that are used in the primary script. The primary script also contains a function for parallelizing the simulation. See simulation process diagram below for all steps included in the simulation model.


![Fig1](https://user-images.githubusercontent.com/43580228/166741984-05131385-c604-48a6-9087-6322f142236e.jpg)
