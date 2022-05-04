# in-class_covid_transmission
Open source documentation for COVID-19 aerosol transmission simulation-based risk analysis for in-person learning

The file pseudo_classrooms.csv contains artificially generated data for 1,000 courses for a college semester, when and where they meet, and the dimensions and airflow of their meeting space. This data is matched with the course ID in row 1 of "schedule.csv" to identify shared classroom spaces of students and faculty over the course of the semester.

The file pseudo_schedules.csv contains artifically generated data for 10,000 students and 1,000 faculty assigning them to courses from "pseudo_classrooms.csv" with each student or faculty represented by a row indicating if that individual was enrolled in the course (1) or not (0). The final column indicates the risk group of the individual, identifying them as a student or their age grouping for faculty

The file "classroom_risk_simulation.py" is the primary script for running the simulation to estimate infections, hospitalizations, and deaths with all other .py files including functions that are used in the primary script. The primary script also contains a function for parallelizing the simulation.
