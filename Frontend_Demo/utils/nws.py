import requests
import pandas as pd
import json

NWS_GRAPHQL_URL = 'http://localhost:4000/graphql'

'''
File for managing API access with the National Weather Service data provider
'''

def send_query(alert_id=None):
    """
    Send a GraphQL query to the NWS service.
    If alert_id is provided, query by ID.
    Otherwise, get the full alert list.
    """
    if alert_id:
        query = f"""
            query {{
                NationalWeatherService {{
                    alertById(id: {alert_id}) {{
                        Event
                        Effective
                        Expires
                        Area
                        Summary
                    }}
                }}
            }}
        """
    else:
        query = """
            query {
                NationalWeatherService {
                    alertList {
                        WeatherAlert {
                            Event
                            Effective
                            Expires
                            Area
                            Summary
                        }
                    }
                }
            }
        """
    try:
        headers = {'Content-Type': 'application/json'}
        payload = {'query': query}
        response = requests.post(NWS_GRAPHQL_URL, headers=headers, json=payload)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f'Error: Received status code {response.status_code}'
    except Exception as e:
        return False, f'Error executing query: {str(e)}'

def format_data(data):
    """
    Convert JSON-like Python objects (as returned by json.loads)
    into a pandas DataFrame suitable for Streamlit or analysis.
    Flattens each weather alert into a row.
    """
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception:
            return pd.DataFrame()
    # Unwrap envelope
    alerts = None
    if isinstance(data, dict):
        nws = (data.get('data') or {}).get('NationalWeatherService') if data.get('data') else None
        if isinstance(nws, dict):
            alerts = nws.get('alertList') or nws.get('alertById') or nws
            if isinstance(alerts, dict):
                alerts = alerts.get('WeatherAlert') or alerts
        if alerts is None:
            if 'WeatherAlert' in data:
                alerts = data.get('WeatherAlert')
            elif 'NationalWeatherService' in data and isinstance(data['NationalWeatherService'], dict):
                alerts = data['NationalWeatherService'].get('alertList')
    if not isinstance(alerts, list):
        if isinstance(alerts, dict):
            alerts = [alerts]
        else:
            if isinstance(data, list) and all(isinstance(i, dict) for i in data):
                alerts = data
            else:
                return pd.DataFrame()
    df = pd.DataFrame(alerts)
    # Coerce types
    if not df.empty:
        for col in ['Effective', 'Expires']:
            if col in df:
                df[col] = pd.to_datetime(df[col], errors='coerce')
    return df
