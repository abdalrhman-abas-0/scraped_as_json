import os 
from time import sleep
from outputs_m import o_handler
from scrapers_m import s_handler, scraper
from f_inputs import r_inputs
from f_scrapers import stage_tracker
from inputs_m.inputs import TXT_TRACKER, RESULT_PAGE_COLUMN, NO_OF_RESULTS_IN_A_PAGE
from tqdm import tqdm
import json 
from time import time

def main():

    os.system('cls')

    start = time()
    
    # extracts the txt_tracker file name (saved or newly created)
    search_subject, search_location, URL, first_soup,pages_to_scrape ,page_counter, results_scraped, save_index, s_profile, txt_tracker, date_time = r_inputs()

    # instantiate the necessary classes
    current = s_handler.pre_scraper(URL,page_counter)
    scrape = scraper.scrapers()
    save = o_handler.outputs(txt_tracker,search_subject, search_location,save_index)
    
    # initiate the stage tracker function to continue an old scraping project
    stage = stage_tracker(txt_tracker, TXT_TRACKER)
    
    print('stage:', stage)
    
    if stage == 1 :
        site = URL
        first_page = True
        p_name = 'primary'
        
        if page_counter < len(pages_to_scrape) or page_counter == 1:
            
            url_list = current.next_page(pages_to_scrape) 
 
            with tqdm(total=(len(url_list)),unit ="search page", desc ="primary scraper") as pbar:
                for url in url_list :
                    
                    if first_page == True:
                        soup = first_soup # the html from the available_pages function
                        first_page = False
                    else:
                        soup = current.requests_maker(url,previous_page)
                        
                    scrape.primary(soup, save.results_list)
                        
                    pbar.update(1)

                    sleep(1)
                    
                    if len(save.results_list) == 0:
                        with open("blocked.html", "w", encoding= 'utf8') as f:
                            f.write(f"""{soup}""")
                            print("connection broken !!")
                        break
                    
                    previous_page = url
                    
                    save.lists_to_json(site, p_name)
                    save.reset_outputs(p_name)
                
        stage += 1
      
    if stage >= 2:
        p_name = 'primary'  
        #building the primary df to use it to scrape the secondary df
        primary_df, df_index = save.build_df(p_name, RESULT_PAGE_COLUMN, s_profile)
        print(f"{len(primary_df)} results scraped successfully.")
        
        if stage == 2:
            # reset the outputs handler attributes
            save.reset_outputs()
            stage += 1
            
    blocked = False 
    
    if stage == 3: 
        
        vpn_active = False
        end_scraper = False
        s_name = 'secondary'
        scraping_list = primary_df[RESULT_PAGE_COLUMN][df_index:]
        results_tracker = len(scraping_list)# a variable as an index can't be used to track the scraping in case of duplicated urls
        previous_profile = URL
        
        # initiate the secondary scraper
        with tqdm(total=len(primary_df[df_index:]),unit ="listing", desc ="secondary scraper") as pbar:
            
            for profile in scraping_list :  
                
                while True:
                    
                    if end_scraper == True: 
                        break
                         
                    try:   
                        soup = current.requests_maker(profile ,previous_profile)    
                        scrape.secondary(soup, save.results_list, profile)                       
                        break
                    
                    except:
                        current.sound_alarm()
                        while vpn_active == False:
                            sleep(2)
                            with open(r'scrapers_m\controls.json', 'r') as J:    
                                data = json.load(J)
                                vpn_active = data["vpn_active"]
                                end_scraper = data["end_scraper"]
                                
                        data["vpn_active"] = False
                        vpn_active = data["vpn_active"]
                        with open(r'scrapers_m\controls.json', 'w+') as J:
                            json.dump(data, J)
   
                
                if end_scraper == True: 
                    break
                
                # back end requests  
                sleep(0.5)
                
                schools_back_end= current.back_end(profile, "schools")
                schools_json = scrape.back_end_json(schools_back_end, "schools")
                
                sleep(0.5)

                fire_back_end = current.back_end(profile, "fire")
                fire_json = scrape.back_end_json(fire_back_end, "fire")
                
                back_end_info = {
                    "schools":schools_json,
                    "fire factor score":fire_json
                    }
                # adding the values of the back_end_info to the main listing dict
                save.results_list[-1] = save.results_list[-1] | back_end_info
                  
                results_tracker -= 1
                  
                previous_profile = profile  
                
                pbar.update(1)

                if (len(save.results_list) % NO_OF_RESULTS_IN_A_PAGE) == 0 :
                    save.lists_to_json(profile, s_name)
                    save.reset_outputs(s_name)
                
                # incase of the last page scraped had less than 20 results in it
                if results_tracker == 0 and len(save.results_list) > 0:
                    save.lists_to_json(profile, s_name)
                    save.reset_outputs(s_name)
                    
        stage += 1
        s_name = 'secondary'
    else:
        s_name = 'secondary'
        print(f'{results_scraped} secondary files are already scraped.')
        stage += 1
    
    if stage >= 4 and blocked == False:    
        #building the primary df to use it to scrape the secondary df
        secondary_df, df_index = save.build_df(s_name, RESULT_PAGE_COLUMN, s_profile)
        print(f"{len(secondary_df)} resluts scraped successfully.")

        # combine the primary and secondary dataframes 
        combined = save.combine_df(primary_df, secondary_df, date_time)
        print(f'done, scraped {combined} results in {int((time()-start)//60)}m {int((time()-start)%60)}s.')
        
    else:
        save.lists_to_json(profile, s_name)
        save.reset_outputs(s_name)
        print(f'error scraped {results_tracker} of {len(scraping_list)} results only in {int((time()-start)//60)}m {int((time()-start)%60)}s.')
   
if __name__ == '__main__':
    main()          

