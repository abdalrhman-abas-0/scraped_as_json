"""
this file contains the inputs necessary for a scraping project.
"""

URL = "https://www.realtor.com/realestateandhomes-search/Circle-C-Ranch_Austin_TX/type-single-family-home"
"""the url of the first page to scrape."""

SITE_NAME = 'Realator'
"""the name of the website being scraped."""

SITE_WITH_DOMAINE = 'realtor.com'
"""the name of the website with it's domaine"""

PAGES_TO_SCRAPE = 1
"no. of pages desired to be scraped."

TXT_TRACKER = "no"
"""the name of the .txt file that contains the record of unsuccessful scrapes, 
    enter"no" if new scraping process is desired."""

NO_OF_RESULTS_IN_A_PAGE = 20
""" the no. of results per page, 
    or the length of the secondary json file that saves the outputs for the secondary stage."""

RESULT_PAGE_COLUMN = "listing page"
""" the name of the column that will store the URLs for the secondary stage."""