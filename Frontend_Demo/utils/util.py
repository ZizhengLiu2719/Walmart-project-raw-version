from datetime import datetime
import pandas as pd
import requests

'''
General use utilities
'''

def parse_date(s):
    # attempts to parse th date into a datetime format
    
    # Try multiple common formats; strip timezone parentheses text
    if not s:
        return pd.NaT
    # remove trailing parenthetical timezone note if present
    s2 = s.split(" GMT")[0].strip()
    # recognizable format like "Sun Aug 24 2025 19:00:00"
    for fmt in ("%a %b %d %Y %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s2, fmt)
        except Exception:
            pass
    # fallback: let pandas try
    return pd.to_datetime(s, errors="coerce")

def send_custom_query(query):
    # a function to send any query you want

    try:
        # GraphQL endpoint URL (hardcoded)
        url = 'http://localhost:4000/graphql'
        
        # Prepare the request
        headers = {'Content-Type': 'application/json'}
        payload = {'query': query}
        
        # Send POST request to GraphQL endpoint
        response = requests.post(url, headers=headers, json=payload)
        
        # Check if request was successful
        if response.status_code == 200:
            # Display the result in a nice JSON format
            return True, response.json()
        else:
            return False, f'Error: Received status code {response.status_code}'
            
    except Exception as e:
        return False, f'Error executing query: {str(e)}'