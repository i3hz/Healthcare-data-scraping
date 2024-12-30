import requests
import pandas as pd
from yelpapi import YelpAPI

def fetch_clinics_api(api_key, location, limit=50):
    yelp_api = YelpAPI(api_key)
    
    try:
        response = yelp_api.search_query(
            term='dental clinics',
            location=location,
            limit=limit
        )
        
        businesses = response['businesses']
        clinic_data = [{
            'Name': business['name'],
            'Address': ' '.join(business['location']['display_address']),
            'Phone': business.get('phone', ''),
            'Rating': business.get('rating', ''),
            'Review_Count': business.get('review_count', '')
        } for business in businesses]
        
        return pd.DataFrame(clinic_data)
        
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()

# Usage
api_key = 'BERvGyW8G_vVAGr4jFec3_gKjFjh-AlUNwt9tv0OQeeEkFZ8mAtgrNrWu59F2ACrsxF1xcZQBnJodeDzlvTkMwPewaLOCqpjiu5jwmZt7NNFdCbbvgl1cOVkyDZyZ3Yx'  # Get this from https://www.yelp.com/developers
df = fetch_clinics_api(api_key, 'United States')
df.to_csv('dental_clinics.csv', index=False)