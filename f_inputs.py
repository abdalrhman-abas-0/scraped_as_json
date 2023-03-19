''' reformating the inputs in the proper way '''

from inputs_m.i_handler import i_handlers
from scrapers_m.s_handler import pre_scraper
from inputs_m.inputs import  * 

def r_inputs ():
    """ initiates the inputs_m module to get the key inputs necessary for scraping.

    Returns:
        search_subject(str): the subject of which the search is being conducted.
        search_location(str): the location of which the search is being conducted.
        URL(str): the original url of the first page. 
        first_soup(BeautifulSoup): soup object of the first page.
        pages_to_scrape(list): the pages that will be scraped 
            after checking the pages available for a certain search on the website.
        page_counter(int): the pages scraped count.
        results_scraped(int): results scraped count.
        save_index(int): the number of the last saved file (primary/secondary).
        s_profile(str): the URL of the last scraped result page.
        txt_tracker(str): the name of the .txt file which records the scraping process.
        date_time(str): the beginning time of the scraping process.
    """    
    handlers_c =  i_handlers() 
    pre_scraper_c = pre_scraper(URL)
    first_soup = pre_scraper_c.requests_maker(URL)
     
    search_subject, search_location = handlers_c.handler(URL)
    page_counter, results_scraped, save_index, s_profile, txt_tracker, date_time = handlers_c.record(TXT_TRACKER, URL, search_subject, search_location)
    pages_to_scrape = handlers_c.available_pages(first_soup, PAGES_TO_SCRAPE, page_counter)
    return search_subject, search_location, URL, first_soup, pages_to_scrape ,page_counter, results_scraped, save_index, s_profile, txt_tracker, date_time