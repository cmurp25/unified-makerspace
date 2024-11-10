""" 
    Required file for log_equipment folder directory to be treated as 
    a sub-package of the visit/ folder directory.
    
    Why does this need to be a sub-package?
        - log_equipment.py requires the use of some functions in log_visit.py
          and importing gets a little weird.
"""