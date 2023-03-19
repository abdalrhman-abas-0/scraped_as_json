# -*- coding: utf-8 -*-
"""
This module contains a class 'pre_scraper' which houses all the methods
concerned with crawling websites.

"""
import grequests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Firefox
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.events import EventFiringWebDriver, AbstractEventListener
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.options import Options
Firefox_options = Options()
Firefox_options.add_argument("--disable-extensions")
Firefox_options.add_argument("--disable-gpu")
Firefox_options.add_argument("--headless")
Firefox_options.add_argument("--start-maximized")
from fake_useragent import UserAgent
import winsound
import pandas
import httpx
import os
import json
from time import sleep

class pre_scraper():
    """this class contains all the objects intended to make get and post request to a website 
    
    Args:
        url (str): the url of the first search page.
        page_counter (int): the number of previously scraped page for the same search (if done before)

    Attributes:
        driver (selenium webdriver): this is used to crawler webpages using selenium.
        request_session (httpx.Client): session used to connect to the backend API.
    """
    
    driver = webdriver.Firefox(options=Firefox_options)
    request_session = httpx.Client()
    
    def __init__(self, url:str, page_counter:int=0):
        """ takes url & page counter drive multiple class attributes from them
        
            it defines the session object and set the headers for post or/and
            get requests on a class level

        Args:
            url (str): first page search url.
            page_counter (int, optional): no. of page previously scaped for the 
                same search. Defaults to 0.
        """ 
        
        # passing libraries, modules & functions inside a class 
        assert "realtor" in url, 'wrong url !!'
 
        self.url = url
        """str: first page search url."""        
        self.page_counter = page_counter
        """int: no.of page previously scaped for the same search."""
        self.previous_profile = url
        """str: previously scraped page for the current scraping process. 
            Defaults to the 'url'."""
        
        # gets the get requests headers from the controls file
        with open(r'scrapers_m\controls.json', 'r') as J:
            data = json.load(J)    
        self.headers = data["headers"]
        """dict: the headers for the get request exclusively."""
        
        
    def __change_headers (self, previous_profile:str):
        # this method changes mainly the headers & referer for each request also the users agent  
        # if it's enabled by changing the "change user" value to true in the controls.json file 
        
        #TODO: compile a script to change the proxies 

        self.headers["Referer"] = previous_profile
        
        with open(r'scrapers_m\controls.json', 'r') as J:
            data = json.load(J)
            change_user = data["change user"]
            
        if change_user == True: 
            self.headers["User-Agent"]  = UserAgent().random
            
        
    def requests_maker(self, site:str, previous_profile ='pre_scraping'):
        """takes the url and return a soup object or tell the no.of available pages for a search.

            if the previous_profile parameter is passed 'url' it well use httpx and return soup
            object if not the parameter defaults to' pre_scrapping' and will print the no.of pages
            available for the initiated search.  
            
        Args:
            site (str): the site url.
            previous_profile  (str, optional): the scraper either scraper or (primary/secondary).
                Defaults to 'pre_scraping'.
        Returns:
            soup(BeautifulSoup): a BeautifulSoup object ready to be to scrape by parsing it.
        """        
        # scraping the internet 
        if  previous_profile == 'pre_scraping':
            # selenium 
            self.driver.get(site)
            HTML = self.driver.page_source 
            soup = BeautifulSoup(HTML, "html.parser")
            self.driver.quit()
            
        else:

            self.__change_headers(previous_profile)
                
            # requests session
            while True: # accounting for the internet interruptions
                try:
                    webpage = httpx.get(site,  headers = self.headers)
                    break
                except:
                    sleep(2)
                    print('internet interruption !!')
                    
            soup = BeautifulSoup(webpage.text,"html.parser")      
            
        return soup
    
    
    def soup_pot (self, results_list:list, scraper:str, RESULT_PAGE_COLUMN:str = None):
        """ async crawler, takes a list of URLs and return a list of BueatifulSoup objects.

        Args:
            results_list (list): list of URLs.
            scraper (str): the stage of scraping 'primary/secondary'.
            RESULT_PAGE_COLUMN (str, optional): the url column index if pandas DataFrame is passed 
                results_list parameter instead of a list. Defaults to None.

        Returns:
            soup_listed(list): a list of BeautifulSoup objects for the crawled URLs.
        """        
        
        responses = []
        
        if scraper == 'primary':
            url_list = results_list
        else:
            url_list = results_list[RESULT_PAGE_COLUMN]
        
        for url in url_list:
            # uses change headers method to change the headers for each request made
            self.__change_headers(self.previous_profile)
            responses.append(grequests.get(url,headers = self.headers))
            self.previous_profile = url
            
        soup_map = grequests.map(responses)
        soup_listed = [BeautifulSoup(soup.content,"lxml") for soup in soup_map]
        
        return soup_listed
    
    
    def next_page(self,pages_to_scrape:list):
        """ takes a the number of pages to be scraped 'list' construct url for each page.

        Args:
            pages_to_scrape (list): _description_

        Returns:
            urls(list): list of the pages that will be scraped.
        """        
        urls = [ f'{self.url}/pg-{page}' if page == 1 else self.url for page in pages_to_scrape]
        
        return urls
    
    
    def back_end(self, profile:str, request:str):
        """ call the backend API and return a json response.
        
            tacks the url for each result page and call the API 
            to return a json response for the desired request.
            the data which will be sent in the post request is stored
            in 'scrapers_m\back_end.json' file.
            
        Args:
            profile (str): the result page url.
            request (str): the type of request to sent 'data to be posted'.

        Returns:
            response(json): json contains the desired info.
        """        
        
        with open(r'scrapers_m\back_end.json', 'r') as J:
            data = json.load(J)
            request_headers = data["headers"]
            url = data["url"]
            get_data = data[f"{request}"]
            data["headers"]["Referer"] = profile
            
        """ posting to the back end servers """      
        self.request_session.headers = request_headers
        while True: # accounting for the internet interruptions
            try:
                webpage = self.request_session.post(url, headers=request_headers, data = get_data)
                break
            except:
                sleep(2)
                print('internet interruption !!')
        
        response = webpage.json()   
         
        return response      
     
     
    def primary_df_slicer(self,df:pandas.DataFrame,chunk_size:int):
        """takes a pandas DataFrame 'URL column' and 
            divide it into multiple URLs lists with the desired length. 

        Args:
            df (pandas.DataFrame): the URL column in a DataFrame.
            chunk_size (int): the length of each URL list.
            
        Returns:
            chunk_list(list): list of URL lists.
        """              

        Chunk_count = len(df)//chunk_size
        if Chunk_count < len(df)/chunk_size:
            Chunk_count += 1
            
        chunk_count_list = list(range(Chunk_count))
            
        chunk_list = []
        beginning = 0
        end = 0
        for count in chunk_count_list:
            end += chunk_size
            if chunk_count_list.index(count) == chunk_count_list[-1]:
                end = None
            list_ = df[beginning:end]
            chunk_list.append(list_)
            beginning = end
            
        return chunk_list
    
    def sound_alarm (self):
        """an alarm when called it makes a sound.
        """        
        winsound.Beep(90, 100)
        winsound.Beep(1200, 100)
        winsound.Beep(1200, 100)
        winsound.Beep(1000, 300)
        winsound.Beep(900, 250)
        winsound.Beep(800, 200)
        
                
        