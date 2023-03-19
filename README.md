# **scraped_as_json**

* This project is a scraper template which can perform a seamless successful scraping process even if it faced a power outage or the site blocked the scraper and save the outputs as json files.
* it's intended to work as a template suitable to be modified to work with many scraping libraries and across many sites.
* it can use many scraping libraries like: BeautifulSoup, httpx, Selenium, and more.

# Project Structure:

* This scraper consists mainly of 3 sub-packages and 2 module plus the run file:

```bash
scraped_as_json:
│   f_inputs.py
│   f_scrapers.py
|   LICENSE.py
│   README.md
│   requirements.txt
│   run.py
│   __init__.py
│
├───inputs_m
│       inputs.py
│       i_handler.py
│       __init__.py
│
├───Outputs files
├───outputs_m
│       o_handler.py
│       __init__.py
│
└───scrapers_m
        back_end.json
        controls.json
        scraper.py
        s_handler.py
        __init__.py
```

> **the "Outputs files" folder is where the out .json files and the .txt tracker file will be saved.**

# Project Functionality:

## there are 5 stages of the scraping process:

### **0. pre scraping stage**:

in this stage the inputs evaluated, modified to suit the program and the amount of results available for a certain scraping project, then it checks if it will continue an old scrape if yes it looks for the record of the old scrape in the .txt file which is already been input by the user in the input file if not the program creates a new .txt file to record the current scraping process.

### **1. *primary stage***:

the program scrapes the results from the primary pagination pages available for a search and saves them page by page in .json file.

### **2. saving the Primary files**:

in this stage the program builds a pandas DataFrame for each primary file and save it as one main .json file then it deletes the primary .json files for each page.

### **3. *secondary stage***:

this stage extracts the URLs for each result from the primary DataFrame built in the previous stage and scrape the results one by one or as asynchronous chunks and saves the results as .json files.

### **4.saving the Secondary files**:

as stage no. 2 This stage also builds a DataFrame from these files and saves it as one .json file then it deletes all the secondary files.

### **5.joining the DataFrames**:

In this stage the primary and secondary stages are joined and saved into one file and the .txt file, primary & secondary files are deleted.

> this stage from which the program will begin running from incase of continuing an uncompleted scraping is determined by f_scrapers module after looking to the last step taken by the scraper in the .txt file which is saved in the scrapers_m sub-module and automatically erased after completion.

# How To Use :

* to configure the scraper some code adjustments are needed across the following modules/files:-

## 1. Inputs module:

| Variable                | Functionality                                                                                                             |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| URL                     | the url of the first page to scrape.                                                                                      |
| SITE_NAME               | the name of the website being scraped.                                                                                    |
| PAGES_TO_SCRAPE         | no. of pages desired to be scrapped.                                                                                      |
| TXT_TRACKER             | the name of the .txt file that contains the record of unsuccessful scrapes, enter"no" if new scraping process is desired. |
| NO_OF_RESULTS_IN_A_PAGE | the no. of results per page, or the length of the secondary json file that saves the outputs for the secondary stage.     |
| RESULT_PAGE_COLUMN      | the name of the column that will store the URLs for the secondary stage.                                                  |
| SITE_WITH_DOMAINE       | the name of the website with its domain.                                                                                  |

---

## 2. controls.json:

* only the headers part is needed to be changed to suite the new site being scraped as the url, method and body variables are just there as a remainder to the correct request to get the headers of incase the headers in use got expired.

```json
"headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1"
        }
```

## 3. back_end.json:

* change the url, headers & the date to send with the post request (schools & fire).

> the (schools & fire) keys corresponds to the request body which well be sent a data in the post request.

```json
{"url":"https://www.realtor.com/api/v1/hulk?client_id=rdc-x&schema=vesta", 
    "headers": {
      "accept": "application/json",
      "accept-language": "en-US,en;q=0.9",
      "content-type": "application/json",
      },
  "schools": [{"query":\"\\nquery GetSchoolData($propertyId: ID!)"}, "home(property_id: $propertyId)"],
  "fire": [{"query":\"\\nquery GetFireTrend($propertyId: ID!)"}, "home(property_id: $propertyId)"],
  "method": "POST"
}
```

* to send the correct data with post request and get the desired response the keys (EX:"schools", "fire") must be plugged in the following methods in back end requests section under stage 3 part the run module, Example:

```python
      
        # back end requests  
        sleep(0.5)

        schools_back_end= current.back_end(profile, "schools")
        schools_json = scrape.back_end_json(schools_back_end, "schools")
```

## 4. i_handler module:

* change the following script under the handler method so that it returns the search_subject & search_location in an appropriate manner.

```python
class i_handlers ():  

    def handler(self,URL:str):  
        URL = URL.replace("-", "_")
        search_subject = re.search(r"(?<=www.realtor.com/)\w+(?=/)", URL)[0]
        search_location = re.sub(r"\d+", r"", URL[URL.index(search_subject) + len(search_subject)+1:]).strip("_").replace("/", "-")
      
        return search_subject, search_location
```

* the following try and except block should also be change to get the number of pages available for a certain search in the web site being scraped.

```python
   def available_pages(self, soup:BeautifulSoup, pages_to_scrape:int, page_counter:int):
        try:
            results_available = int(soup.select('div[aria-label="pagination"] > a')[-2].text)
        except:
            results_available = 1
```

## 5. scrapers module:

* change the code in the following methods in the scrapers class to suite the site to be scraped:

### 1- primary method:

```python
class scrapers():
  
    def primary(self,soup:BeautifulSoup, results_list:list): # one profile at a time
        # THE NEW CODE SHOULD BE PLACED FROM HERE.... 
        container = soup.select('ul[data-testid="property-list-container"]')
      
        try: # avoid sponsored results if exists
            property_list = container[1].select('li[data-testid="result-card"]')
        except:
            property_list = container[0].select('li[data-testid="result-card"]')

        for P in property_list:# iterates through the results displayed on the page
```

```python
      
        result = {
            "listing page":listing_page,
            "status":status,
            "price":price,
            "address":address,
            "bed rooms":bed_rooms,
            "bath rooms":bath_rooms,
            "parameter":parameter,
            "lot area":lot_area   
        }
        # TO THIS PART BUT THE  RESULT DICT ABOVE WHICH CONTAINS THE INFO SCRAPED FORM 
        # EACH RESULT ON THE PAGE SHOULD ALWAYS BE NAMED "result".
        for key, value in result.items():
            if value == '':
                result[key] = "Not Listed" 
                  
        results_list.append(result)
```

### 2- secondary method:

```python
    def secondary (self, soup:BeautifulSoup, results_list:list, profile:str):
        # THE NEW CODE SHOULD BE PLACED FROM HERE....
        neighborhood = "not available"
        monthly_payment = "not available"
        environmental_risk = "not available"
        try:
            neighborhood = soup.find('section', attrs={'data-label':"Neighborhood"}).text
        except:
            pass          
              
        try:
            monthly_payment = soup.find('section', attrs={'data-label':"Monthly Payment"}).text
        except:
            pass          
```

```python
        listing= {
            "property type": property_type,
            "display period": display_period,
            "price per foot": price_per_foot,
            "garage":garage,
            "year built":year_built,  
        }
        # TO THIS PART BUT THE  RESULT DICT ABOVE WHICH CONTAINS THE INFO SCRAPED FORM 
        # EACH RESULT ON THE PAGE SHOULD ALWAYS BE NAMED "listing".
        for key, value in listing.items():
            if value == '' or value == None :
                listing[key] = "not available"
              
        results_list.append(listing)
```

### 3-  back_end_json method:

```python
    def back_end_json (self, response:dict, request:str):
        # ADJUST THE FOLLOWING BLOCK TO EXTRACT THE DESIRED INFORMATION OUT OF 
        # THE JSON RESPONSE (RESPONSE) GIVEN BY THE BACK_END METHOD IN 
        # THE PRE_SCRAPER CLASS IN THE S_HANDLER MODULE.
        if request == "schools":
            try:
                json_response = response["data"]["home"]["schools"]["schools"]
                for s in json_response: # deleting the unnecessary values from the dictionary
                    del( s['slug_id'])
            except:
                json_response = "not available"
        else:
            try:
                json_response = response["data"]["home"]["local"]["wildfire"]["fire_factor_score"]
            except:
                json_response = "not available"
```

# How To Manage:

## managing the scraping process is done through the controls.json and can be done while the program is running using the following variables:

* change user: if true it changes the user agent for each request made.
* vpn_active: if the program is blocked by the web site it will make a beep sound for the user to active a VPN service manually if available and after activation the user must change it's value to true then the program will set it back to false and continue the scraping process.
* end_scraper: if it sat to true it will terminate the program.
