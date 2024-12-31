import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import logging
from googlemaps import Client
from typing import list,Dict
import os
from linkedin_api import Linkedin
import facebook_scraper as fs

class ClinicScraper:
    def __init__(self):
        self.setup_logging()
        self.setup_drivers()
        
    def setup_logging(self):
        logging.basicConfig(
            filename='scraper.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def setup_drivers(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(options=options)
        
    def get_google_maps_data(self, search_query, max_results=100):
        if not hasattr(self, 'gmaps_client'):
            api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
            self.gmaps_client = Client(api_key)
        places_result = []
        next_page_token = None
        while len(places_result)< max_results:
            response = self.gmaps_client.places(search_query, page_token=next_page_token)
            places_result.extend([{
                'name':place['name'],
                'address': place.get('formatted_address', ''),
                'rating': place.get('rating', 0.0),
                'location': place['geometry']['location'],
                'place_id': place['place_id']
            }for place in response.get('results', [])])
            next_page_token  = response.get('next_page_token')
            if not next_page_token:
                break
        return places_result[:max_results]
        
        
    def enrich_with_linkedin(self, company_name):
        try:
            pass
            # Note: Would need LinkedIn API credentials
        except Exception as e:
            logging.error(f"LinkedIn error for {company_name}: {e}")
            return None
            
    def find_facebook_page(self, company_name, location):
        try:
            # Note: Would need Facebook API credentials
            pass                    
            
        except Exception as e:
            logging.error(f"Facebook error for {company_name}: {e}")
            return None
            
    def find_email_on_website(self, website_url):
        try:
            response = requests.get(website_url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            email_pattern = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}'
            emails = re.findall(email_pattern, response.text)
            return emails[0] if emails else None
        except Exception as e:
            logging.error(f"Website scraping error for {website_url}: {e}")
            return None
            
    def scrape_clinics(self, max_results=1000):
        all_data = []
        
        # 1. First get basic data from Google Maps
        basic_data = self.get_google_maps_data("dental clinic", max_results)
        
        # 2. Enrich the data
        for clinic in basic_data:
            try:
                # Get LinkedIn data
                linkedin_data = self.enrich_with_linkedin(clinic['name'])
                
                # Find Facebook page
                facebook_url = self.find_facebook_page(clinic['name'], clinic['address'])
                
                # Find email from website
                email = self.find_email_on_website(clinic.get('website'))
                
                enriched_data = {
                    'Company Name': clinic['name'],
                    'Address': clinic['address'],
                    'Phone': clinic.get('phone'),
                    'Email': email,
                    'Website': clinic.get('website'),
                    'Management Team': linkedin_data['management_team'] if linkedin_data else None,
                    'LinkedIn URL': linkedin_data['linkedin_url'] if linkedin_data else None,
                    'Facebook URL': facebook_url
                }
                
                all_data.append(enriched_data)
                
                # Respect rate limits
                time.sleep(2)
                
            except Exception as e:
                logging.error(f"Error processing clinic {clinic['name']}: {e}")
                continue
                
        return pd.DataFrame(all_data)
        
    def save_results(self, df, filename='dental_clinics_data2.csv'):
        df.to_csv(filename, index=False)
        logging.info(f"Saved {len(df)} records to {filename}")
        
    def cleanup(self):
        self.driver.quit()

# Usage
if __name__ == "__main__":
    scraper = ClinicScraper()
    try:
        df = scraper.scrape_clinics()
        scraper.save_results(df)
    finally:
        scraper.cleanup()