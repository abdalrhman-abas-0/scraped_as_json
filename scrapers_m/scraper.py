""" this module contains the scraper/parser methods"""
from bs4 import BeautifulSoup
import re # just importing json in the same file as the class scraper is enough to pass it into the class#   
import json   
import pandas as pd  

class scrapers():
    """this calls is used to contain the scrapers."""
    
    def primary(self,soup:BeautifulSoup, results_list:list): # one profile at a time
        """ used to get the primary info of each result from the search page.
            after scraping each page it appends the scrape output to an external list.

        Args:
            soup (BeautifulSoup object): the soup object of the page.
            results_list (list): the list where the scraped results are appended

        """
        
        container = soup.select('ul[data-testid="property-list-container"]')
        
        try: # avoid sponsored results if exists
            property_list = container[1].select('li[data-testid="result-card"]')
        except:
            property_list = container[0].select('li[data-testid="result-card"]')

        for P in property_list:# iterates through the results displayed on the page
            
            listing_page = 'https://www.realtor.com'+P.find('a', attrs= {'data-testid':"property-anchor"})['href']
            status = P.select("[class*='statusLabelSection']")[0].text
            
            P = P.find_all('div', re.compile(r'.+property-wrap'))[0]
            
            price = P.select("[class*='srp-page-price']")[0].text
            address = P.select("[class*='card-bottom']")[0].text
            
            property_description = P.select("[class*='property-meta list-unstyled property-meta-srpPage']")[0].text
            
            try:
                bed_rooms = re.search(r'\d+bed', property_description)[0]
            except:
                bed_rooms = '0bed'
            
            try:
                bath_rooms = re.search(r'\d+bath', property_description)[0]
            except:
                bath_rooms = '0bath'
            
            try:
                parameter = re.search(r'\d+sqf', property_description)[0]
            except:
                'not specified!'
            
            
            try:
                lot_area = re.search(r'(\d+|\d+.\d+)\D+\slot', property_description)[0]
            except:
                lot_area = 'without a lot!'
            

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
            for key, value in result.items():
                if value == '':
                    result[key] = "Not Listed" 
                        
            results_list.append(result)
            
        
    
    def secondary (self, soup:BeautifulSoup, results_list:list, profile:str):
        """ to get the specific info of each result page.
            after scraping each page it appends the scrape output to an external list.
            
        Args:
            soup (BeautifulSoup object): the soup object of the page.
            results_list (list): the list where the scraped results are appended
            profile (str): the url of the result page.
            
        """
      
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
            
        try:
            environmental_risk = soup.find('section', attrs={'data-label':"Environmental Risk"}).text
        except:
            pass            
 
            
        # extracting the property details from the webpage's json property details
        property_details = "not available"
        
        try:
            property_details = {}

            jason_response = soup.find(id = "__NEXT_DATA__")

            json_str = re.search(r'{.+(?=</script>$)', str(jason_response))[0]
            jason_response = json.loads(json_str)
            jason_property_details_element = jason_response["props"]["pageProps"]["initialState"]["propertyDetails"]["details"]

            for detail in jason_property_details_element:
                value =""
                key= detail["category"]
                values = str(detail["text"]).replace("', '", "\n")
                property_details[key] = re.sub(r"[\[''\]]", r"", values)
        except:
            pass   
        
        try:
            flood_factor_score = jason_response["props"]["pageProps"]["initialProps"]["property"]["local"]["flood"]["flood_factor_score"]
        except:
            flood_factor_score = "not available"
            
        try:       
            try:
                provider = jason_response["props"]["pageProps"]["initialProps"]["property"]["branding"][0]["name"]
            except:
                provider = jason_response["props"]["pageProps"]["initialProps"]["property"]["consumer_advertisers"][1]["name"]
        except:
            provider = "not available"  
            
        try:
            try:
                provider_url = jason_response["props"]["pageProps"]["initialProps"]["property"]["provider_url"]["href"]
            except:
                provider_url = jason_response["props"]["pageProps"]["initialProps"]["property"]["consumer_advertisers"][1]["href"]
        except:
            provider_url = "not available"  

        try:
            try:
                provider_phone = jason_response["props"]["pageProps"]["initialProps"]["property"]["consumer_advertisers"][1]["phone"]
            except:
                provider_phone = jason_response["props"]["pageProps"]["initialProps"]["property"]["consumer_advertisers"][0]["phone"]
        except:
            provider_phone = "not available"  
            
             
        #extracting the property history (tax & price)
        property_price_history = "not available"
        property_tax_history = "not available"
        
        try:
            # the property history element
            property_history = soup.find(id ="content-property_history").find_all("tbody")
        except:
            pass  
        
        # price history
        try:
            local_property_price = []
            columns_list = ["Date", "Event", "Price", "Price/Sq Ft", "Source"]

            local_property_price_element = property_history[0].find_all("tr")
            for row_element in local_property_price_element:
                row = []
                row_element = row_element.find_all('td')
                for value in row_element:
                    value = value.text
                    row.append(value)
                #creating a pandas array (list of lists)
                local_property_price.append(row)
            # convert the array to dataframe
            price_df = pd.DataFrame(local_property_price, columns = columns_list)
            # added the profile url to each row of the df as it will be the unique key for each value when constructing a 
            # tables for price history
            price_df["profile"] = profile
            # convert the dataframe to dictionary then to a string as years years record changes for every listing 
            # and append it
            property_price_history = str(price_df.to_json())
        except:
            pass 
            
            
        # tax history    
        try:
            local_property_tax = []
            columns_list = ["Year","Taxes","Land","added to","Additions","equals","Total assessments"]

            # convert each row to a list
            local_property_tax_element = property_history[1].find_all("tr")
            for row_element in local_property_tax_element:
                row = []
                row_element = row_element.find_all('td')
                for value in row_element:
                    value = value.text
                    row.append(value)
                #creating a pandas array (list of lists)
                local_property_tax.append(row)
            # convert the array to dataframe
            tax_df = pd.DataFrame(local_property_tax, columns = columns_list)
            # added the profile url to each row of the df as it will be the unique key for each value when constructing a 
            # table for tax history
            tax_df["profile"] = profile
            # convert the dataframe to dictionary then to a string as years years record changes for every listing and append it
            property_tax_history = str(tax_df.to_json())
        except:
            pass
        
        listing_indicator  = soup.select("[class*='listing-indicatorCont']")[0].find_all('li')
        
        "extracting the listing indicators"
        property_type = "not available"
        display_period = "not available"
        price_per_foot = "not available"
        garage = "not available"
        year_built = "not available"    
        
        try:
            for indicator in listing_indicator:
                indicator= indicator.text

                if "Property Type" in indicator:
                    property_type = indicator[indicator.index('Property Type')+len('Property Type'):]
                    continue
                    
                if 'Time on realtor.com' in indicator:
                    display_period = indicator[indicator.index('Time on realtor.com')+len('Time on realtor.com'):]
                    continue
                    
                if 'Price per square feet' in indicator:
                    price_per_foot = indicator[indicator.index('Price per square feet')+len('Price per square feet'):]
                    continue
                    
                if 'Garage' in indicator:
                    garage = indicator[indicator.index('Garage')+len('Garage'):]
                    continue
                    
                if 'Year Built' in indicator:
                    year_built = indicator[indicator.index('Year Built')+len('Year Built'):]
                    continue
        except:
            pass        
                    
        listing= {
            "property type": property_type,
            "display period": display_period,
            "price per foot": price_per_foot,
            "garage":garage,
            "year built":year_built,
            "neighborhood": neighborhood,
            "property details": property_details,
            "monthly payment": monthly_payment,
            "environmental risk": environmental_risk,
            "property details": property_details,
            "property price history": property_price_history,
            "property tax history": property_tax_history,
            "flood factor score": flood_factor_score,
            "provider name" : provider,
            "provider phone": provider_phone,
            "provider page" : provider_url   
        }
        
        for key, value in listing.items():
            if value == '' or value == None :
                listing[key] = "not available"
                
        results_list.append(listing)
        
        
    def back_end_json (self, response:dict, request:str):
        """converts the soup object obtained from the backend using the website api to json.

        Args:
            soup (BeautifulSoup object): the soup object of the json response.
            request (str): the request name send to the server.
            
        Returns:
            json_response (dict): a dictionary fo the scraped data.

        """

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
                
        return json_response   
