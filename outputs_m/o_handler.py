"""this module contains the class which manages the scraping outputs. 
"""
import os
import pandas as pd

class outputs():
    """ this class contains all the methods that manages the 
        scraping outputs.
        
    Attributes:
        results_scraped (int): no. of the scraped results.
        results_list (list): a container for the scraping outputs.
        bot_name (str): the scraper stage name 'EX: primary'
    """    
    results_scraped = 0
    results_list = []
    bot_name = None
    
    def __init__(self, txt_tracker: str, search_subject: str, search_location: str,save_index= 0):
        """ this __init__ method's turns it's parameters into a class level attributes.  

        Attributes:
            txt_tracker (str): the name of the .txt file which contains a record 
                of the scraping process.
            search_subject(str): the subject of the search.
            search_location(str): the location of the search.
            save_index (str, optional): the no. of last saved json file which contains the scraping output.
        """        
        assert save_index >= 0 , 'save index is less than 0 !!'
        self.save_index = save_index
        self.txt_tracker = txt_tracker
        self.search_subject = search_subject
        self.search_location = search_location
        
        
    def reset_outputs (self, bot_name:str = None):
        """ this method is used to empty the outputs list & zero out 
            the save_index and the results_scraped.
            
            it will empty the results_list for when each part of the output is saved 
            'as a .json file for example' when iterating through pages, it will additionally 
            zero out the save_index and the results_scraped when finishing a scraping stage.
            

        Args:
            bot_name (str, optional): the scraper stage name 'EX: primary'.
                Defaults to None.
        """        
        self.bot_name = bot_name
        self.results_list = []
        
        if self.bot_name is None:
            self.results_scraped = 0
            self.save_index = 0
            
            
    def lists_to_json(self, site:str , bot_name: str):
        """ this method saves the contents of the results_list in .json files.

            it will save the .json files in 'Outputs files' file.
            
        Args:
            site (str): the URL of the last page scraped successfully.
            bot_name (str): the scraping stage name 'EX: primary/secondary'.
        """        
              
        # changing the directory to the to the finished scraped files folder   
        os.chdir('Outputs files')    
        
        df = pd.DataFrame(self.results_list)
        
        df.to_json(f"Realator  {self.search_subject} in {self.search_location} {self.save_index} {bot_name}.json", orient = None)
        
        try:
            file = open((self.txt_tracker),'a') 
        except:
            file = open((self.txt_tracker),'w') 
                  
        file.write('\n')
        file.write (f"Realator  {self.search_subject} in {self.search_location} {self.save_index} {bot_name}.json") 
        file.write('\n')
        file.write(F'{site}')   
        file.close() 
        
        self.results_scraped += len(self.results_list)
        self.save_index +=  1
        
        # navigating back to the original directory
        os.chdir(os.path.normpath(os.getcwd() + os.sep + os.pardir))

        

    def build_df (self, bot_name: str, result_page_column: str, s_profile= False):
        """ this method concatenates multiple .json files and build a DataFrame from it 
            and saves this DataFrame as a .json file.
        
            it searches the txt scraping record file for the scraped files sub-.json files 
            for a scraping stage 'EX: primary' and concatenate it into one DataFrame and 
            saves it as a .json file then it returns the pandas DataFrame and the
            number of the last concatenated sub-.json file. 

        Args:
            bot_name (str): the scraping stage name 'EX: primary/secondary'.
            result_page_column (str): _description_
            s_profile (bool, optional): _description_. Defaults to False.

        Returns:
            df (pandas.DataFrame): data frame of the concatenated main file.
            df_index (int): the number of the last page scraped successfully.
        """        
    
        # the start of the saved primary index to use it to resume a secondary scrape
        df_index = 0 

        # concatenating all the Secondary dataframes to one data frame
        # changing the directory to the to the finished scraped files folder   
        os.chdir('Outputs files')
        
        file = open(self.txt_tracker,'r')
        
        if bot_name.upper() in file.read():
            # constructing a dataframe out of the maine files if it's jason is already saved
            # the file must be closed and reopened in order to execute any code under the if condition
            file.close()
            file = open(self.txt_tracker,'r')    
            for line in file :
                if bot_name.upper() in line:
                    main_json = line.strip('\n')
                    df = pd.read_json(main_json)

        else:
            # the file must be closed and reopened in order to execute any code under the if condition
            file.close() 
            file = open(self.txt_tracker,'r')     
            for line in file: 
                J_file = line.strip('\n')
                if f'{bot_name}.json' in line:
                    if  f' 0 {bot_name}.json' in line:
                        df0 = pd.read_json(J_file)
                        continue
                    try: 
                        df = pd.concat([df0, pd.read_json(J_file)], axis=0, ignore_index= True)
                        df0 = df 
                    except:
                        pass
                    df = df0
            df = df0
          
        # saving the main file and appending it's name in the txt file in upper case
        df.to_json(f"Realator {bot_name.upper()} {self.search_subject} in {self.search_location}.json", orient = None)
        file = open(self.txt_tracker,'a')            
        file.write('\n')
        file.write (f"Realator {bot_name.upper()} {self.search_subject} in {self.search_location}.json")  
        file.close() 
    
        # deleting all the concatenated {bot_name} data frames
        file = open(self.txt_tracker,'r')
        for line in file:
            if f'{bot_name}' in line:
                try:
                    os.remove(line.strip('\n'))
                except:
                    pass
        file.close()
        
        # navigating back to the original directory
        os.chdir(os.path.normpath(os.getcwd() + os.sep + os.pardir))
        
        if bot_name == 'primary' and s_profile is not False: # incase of resuming an old project
            df_index = int(df[result_page_column][df[result_page_column] == s_profile].index[0]) + 1
            
        return df ,df_index 

        
    def combine_df (self, primary_df: pd.DataFrame, secondary_df: pd.DataFrame, date_time:str):
        """it merges the DataFrames of the primary and secondary stages and saves it as .json file. 

        Args:
            primary_df (pd.DataFrame): the results DataFrame of the primary stage.
            secondary_df (pd.DataFrame): the results DataFrame of the secondary stage.
            date_time (str): the date of the beginning of the scraping process.

        Returns:
            df_length(int): the length of the merged DataFrame.
        """         
        os.chdir('Outputs files') 
                
        file = open(self.txt_tracker,'r')
           
        df_combined = primary_df.join(secondary_df)    
        df_combined.to_json(f"Realator {self.search_subject} in {self.search_location} at {date_time}.json", orient = None)
        
        # deleting all the concatenated {bot_name} data frames
        file = open(self.txt_tracker,'r')
        for line in file:
            try:
                os.remove(line.strip('\n'))
            except:
                pass
        file.close()
        
        # deleting the txt_tracker file it self after saving the final output file
        os.remove(self.txt_tracker)
        
        os.chdir(os.path.normpath(os.getcwd() + os.sep + os.pardir))
        df_length = len(df_combined)
        return df_length  