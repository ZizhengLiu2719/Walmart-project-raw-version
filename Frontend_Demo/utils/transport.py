import requests
import pandas as pd
import json

TRANSPORT_GRAPHQL_URL = 'http://localhost:4000/graphql' 

'''
File for managing API access with the transport data provider
'''

def send_query(transport_id=None, status=None):
    """
    Send a GraphQL query to the Transport service.
    If transport_id is provided, query by ID.
    If status is provided, query by status.
    Otherwise, get the full list.
    """
    if transport_id:
        query = f"""
            query {{
                Transport {{
                    byId(id: \"{transport_id}\") {{
                        id
                        vehicleType
                        origin
                        destination
                        departureTime
                        arrivalTime
                        status
                        area
                    }}
                }}
            }}
        """
    elif status:
        query = f"""
            query {{
                Transport {{
                    byStatus(status: \"{status}\") {{
                        id
                        vehicleType
                        origin
                        destination
                        departureTime
                        arrivalTime
                        status
                        area
                    }}
                }}
            }}
        """
    else:
        query = """
            query {
                Transport {
                    list {
                        id
                        vehicleType
                        origin
                        destination
                        departureTime
                        arrivalTime
                        status
                        area
                    }
                }
            }
        """
    try:
        headers = {'Content-Type': 'application/json'}
        payload = {'query': query}
        response = requests.post(TRANSPORT_GRAPHQL_URL, headers=headers, json=payload)
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
    Flattens each transport record into a row.
    """
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception:
            return pd.DataFrame()
    # Unwrap envelope
    records = None
    if isinstance(data, dict):
        records = (data.get('data') or {}).get('Transport') if data.get('data') else None
        if isinstance(records, dict):
            records = records.get('list') or records.get('byStatus') or records.get('byId') or records
        if records is None:
            if 'list' in data:
                records = data.get('list')
            elif 'Transport' in data and isinstance(data['Transport'], dict):
                records = data['Transport'].get('list')
    if not isinstance(records, list):
        if isinstance(records, dict):
            records = [records]
        else:
            if isinstance(data, list) and all(isinstance(i, dict) for i in data):
                records = data
            else:
                return pd.DataFrame()
    df = pd.DataFrame(records)
    # Coerce types
    if not df.empty:
        for col in ['departureTime', 'arrivalTime']:
            if col in df:
                df[col] = pd.to_datetime(df[col], errors='coerce')
    return df
