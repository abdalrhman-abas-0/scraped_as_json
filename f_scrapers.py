""" stage definer module
"""
import os

def stage_tracker(txt_tracker,TXT_TRACKER):
    """ defined the stage from which the program will start running.
    
        it defines the stage from which the program will run after looking to the 
        recorded steps in the TXT_TRACKER file if an uncompleted scraping project 
        s desired to be continued and incase of starting a new scraping project
        it will start from stage 1.
        
    Args:
        txt_tracker (str): a return of the r_inputs function in the f_inputs module.
            it's defaults to "no" if a new scraping project is initiated.
        TXT_TRACKER (str): the user original input in the input file. 

    Returns:
        stage(int): defines the stage from which the program will start running.
    """    
    os.chdir('Outputs files')
    stage = 0
    
    if TXT_TRACKER.lower() == 'no':
        stage = 1
        
    else:
        try: 
            file = open(txt_tracker,'r').read()
            stage = 0
            
            if 'SECONDARY' in file:
                stage = 4
            
            elif 'secondary' in file:
                stage = 3
            
            elif 'PRIMARY' in file:
                stage = 2
                
            else:# 'primary' in file
                stage = 1  
 
        except:
            print(f'{txt_tracker} is not located in "Outputs files"!!')
            
    os.chdir(os.path.normpath(os.getcwd() + os.sep + os.pardir))
    
    return stage