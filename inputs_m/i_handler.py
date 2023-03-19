"""this modules contains all the classes which prepares all 
    the inputs to be used in the scraping process
"""
import datetime
from bs4 import BeautifulSoup
import os
import re
from inputs_m.inputs import SITE_WITH_DOMAINE

class i_handlers ():
    """ this class have contains all the methods that deals with preparing 
        the inputs to be used in the scraping process
    """    
    
    def handler(self,URL:str):
        """ extracts the search_subject and the search_location form the URL.

        Args:
            URL (str): the search first page url.

        Returns:
            search_subject(str): the subject of the search.
            search_location(str): the location of the search.
        """        
        URL = URL.replace("-", "_")
        search_subject = re.search(r"(?<=www.realtor.com/)\w+(?=/)", URL)[0]
        search_location = re.sub(r"\d+", r"", URL[URL.index(search_subject)+ len(search_subject)+1:]).strip("_").replace("/", "-")
        
        return search_subject, search_location
    
    
    def record(self,TXT_TRACKER:str, URL:str, search_subject:str, search_location:str):
        """ extracts the info of a previous scraping process to continue upon it.

            it gets the necessary variables from the txt file which records the previous scraping process 
            progress if the previous scraping process was interrupted.
            
        Args:
            TXT_TRACKER (str): the name of the file which contains the scrape record.
            URL (str): the first search page URL.
            search_subject (str): the subject of the search.
            search_location (str): the location of the subject.

        Returns:
            page_counter (str): represents the no. of the search page 'page 6 , page 7, etc.'.
            results_scraped (str): the no. of the scraped results.
            save_index (str): the no. of last saved json file which contains the scraping output. 
            s_profile (str): the last url of the individual result page scraped.
            txt_tracker (str): the name of the .txt file which contains a 
                record of the scraping process.
            date_time (str): the date of the beginning of the scraping process.
        """        
        s_profile = False
        results_scraped = 0
        p_save_index = 0
        s_save_index = 0
        page_counter = 0
        save_index = 0
        
        # URL, page_counter: extract the last scraped page and it's number from the URL URL
        # Page_Index: getting the number of the last scraped page 
        # save_index: getting the index of the last scraped primary file
        
        txt_tracker = TXT_TRACKER.strip(" ").lower()
        if txt_tracker != "no":
            
            try:
                # changing the directory to the to the finished scraped files folder   
                os.chdir('Outputs files')
                file = open(txt_tracker , 'r')
                for line in file:
                    if 'secondary' in line:
                        s_save_index = int(re.search(r"\d+", line)[0])
                        continue
                    
                    if 'primary' in line:
                        p_save_index = int(re.search(r"\d+", line)[0])
                        continue
                    
                    if SITE_WITH_DOMAINE in line and URL in line:
                        try:
                            page_counter = int(re.search(r'\d+',line)[0])
                        except:
                            pass
                    
                    if SITE_WITH_DOMAINE in line and URL not in line:
                        s_profile = line.strip('\n')
                        
                results_scraped = p_save_index * 20 

                file.close()
                    
                date_time = re.search(r'\d{4}\-\d{2}\-\d{2}\s\d{2}\.\d{2}\.\d{2}',txt_tracker)[0]
                
                # setting the save index to be the secondary's if any secondary save index is found (secondary files scraped)
                # and to be primary save index if there are no secondary files scraped
                if s_save_index > 0:
                    save_index = s_save_index
                else:
                    save_index = p_save_index
                save_index +=1
                
            except FileNotFoundError :
                print(f'FileNotFoundError: TXT_TRACKER[{txt_tracker}], No such file or in "Outputs files" folder!')
                os._exit(0)
                
            finally:
                os.chdir(os.path.normpath(os.getcwd() + os.sep + os.pardir))
                
        else:
            date_time = str( f'{datetime.datetime.now()}')[:f'{datetime.datetime.now()}'.index('.')].replace(':','.')
            txt_tracker = f'tracker {search_subject} in {search_location} at {date_time}.txt'
        page_counter += 1   
        return page_counter, results_scraped, save_index, s_profile, txt_tracker, date_time 

    
    
    def available_pages(self, soup:BeautifulSoup, pages_to_scrape:int, page_counter:int):
        """ prints the no. of pages available for a certain search 
            and adjusts the no. of pages to be scraped accordingly 
            considering the last scraped page in case of building 
            upon a previous scraping process.

        Args:
            soup (BeautifulSoup): the BeautifulSoup object of the first search page.
            pages_to_scrape (int): the no. of pages intended to be scraped.
            page_counter (int): the no. of the last scraped page.

        Returns:
            pages_to_scrape(list): list by the no. of pages to be scraped.
        """        
        try:
            results_available = int(soup.select('div[aria-label="pagination"] > a')[-2].text)
        except:
            results_available = 1
        
        result_pages = f'{results_available} pages available.'

        pages_to_scrape =list(range(pages_to_scrape+1))[page_counter:]
            
        if len(pages_to_scrape) > results_available:
            pages_to_scrape = pages_to_scrape[:results_available]

        print(result_pages)
        return pages_to_scrape
    