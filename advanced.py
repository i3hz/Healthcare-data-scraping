import requests
import pandas as pd
from yelpapi import YelpAPI
import time
from bs4 import BeautifulSoup
import re

def get_business_details(yelp_api, business_id):
    """Get detailed business information including management/founder details"""
    try:
        # Get detailed business info
        details = yelp_api.business_query(id=business_id)
        
        # Extract website if available
        website = details.get('url', '')
        
        # Initialize management and email info
        management_team = None
        email = None
        
        # If website exists, scrape it for management info and email
        if website:
            try:
                response = requests.get(website, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for common management team patterns
                management_patterns = [
                    "founder", "owner", "dentist", "dr.", "doctor",
                    "chief", "president", "director", "ceo"
                ]
                
                # Search for management info in text
                text_content = soup.get_text().lower()
                for pattern in management_patterns:
                    match = re.search(f"{pattern}[:\s]+([\w\s.]+)", text_content, re.IGNORECASE)
                    if match:
                        management_team = match.group(1).strip()
                        break
                
                # Search for email
                email_pattern = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}'
                email_matches = re.findall(email_pattern, response.text)
                if email_matches:
                    # Filter out common no-reply emails
                    valid_emails = [e for e in email_matches if 'noreply' not in e.lower()]
                    if valid_emails:
                        email = valid_emails[0]
                
            except Exception as e:
                print(f"Error scraping website {website}: {e}")
        
        return {
            'management_team': management_team,
            'email': email,
            'website': website
        }
    except Exception as e:
        print(f"Error getting business details: {e}")
        return {
            'management_team': None,
            'email': None,
            'website': None
        }

def fetch_clinics_api(api_key, location, limit=50):
    yelp_api = YelpAPI(api_key)
    
    try:
        # Initialize offset for pagination
        offset = 0
        all_businesses = []
        
        while len(all_businesses) < limit:
            response = yelp_api.search_query(
                term='dental clinics',
                location=location,
                limit=50,  # Max allowed per request
                offset=offset
            )
            
            businesses = response['businesses']
            if not businesses:
                break
                
            for business in businesses:
                # Get additional details for each business
                print(f"Processing {business['name']}...")
                details = get_business_details(yelp_api, business['id'])
                
                business_data = {
                    'Company Name': business['name'],
                    'Address': ' '.join(business['location']['display_address']),
                    'Phone': business.get('phone', ''),
                    'Rating': business.get('rating', ''),
                    'Review_Count': business.get('review_count', ''),
                    'Management Team': details['management_team'],
                    'Email': details['email'],
                    'Website': details['website']
                }
                all_businesses.append(business_data)
                
                # Respect rate limits
                time.sleep(1)
                
                if len(all_businesses) >= limit:
                    break
            
            offset += len(businesses)
            
        return pd.DataFrame(all_businesses)
        
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()

# Usage
api_key = 'BERvGyW8G_vVAGr4jFec3_gKjFjh-AlUNwt9tv0OQeeEkFZ8mAtgrNrWu59F2ACrsxF1xcZQBnJodeDzlvTkMwPewaLOCqpjiu5jwmZt7NNFdCbbvgl1cOVkyDZyZ3Yx'

# Create DataFrame with expanded information
df = fetch_clinics_api(api_key, 'United States', limit=100)  # Adjust limit as needed

# Save to CSV with all fields
df.to_csv('dental_clinics_detailed.csv', index=False)
print(f"Saved {len(df)} records to dental_clinics_detailed.csv")