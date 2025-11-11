import requests
import json
import pandas as pd
import utils.util as util

'''
File for managing api access with the transport data provider
'''

def send_query(transportId = None, status = None):
    parameter = ""
    if transportId is not None:
        parameter = f" byId(id: {transportId})"
    elif status is not None:
        parameter = f" byStatus(status:\"{transportId}\")"
    else:
        parameter = "list"
        

    query = f"""
                query Transport {{
                    Transport {{
                        {parameter} {{
                            arrivalTime
                            destination
                            departureTime
                            id
                            origin
                            status
                            vehicleType
                        }}
                    }}
                }}
    """

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

def format_data(data):
    """
    Parse Transport-style JSON (shape like the provided `example.json`)
    into a pandas.DataFrame.

    Expected shapes handled heuristically:
      - {'data': {'Transport': {'list': [ ... ] }}}
      - {'data': {'Transport': [ ... ] }}
      - {'Transport': {'list': [...]}} or {'Transport': [...]} or {'list': [...]} or a raw list
      - Single Transport object (wrapped into a list)

    Returns a pandas.DataFrame with columns:
      id, origin, destination, departure_time, arrival_time, status, vehicle_type

    Returns an empty DataFrame for unrecognized/empty input.
    """
    # If input is a JSON string, try to parse it
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception:
            return pd.DataFrame()

    # If we got a list/tuple, try to find an envelope dict or treat as the list directly
    if isinstance(data, (list, tuple)):
        # prefer a dict that has 'data' key or 'Transport'
        chosen = None
        for el in data:
            if isinstance(el, dict) and ('data' in el or 'Transport' in el or 'list' in el):
                chosen = el
                break
        if chosen is None:
            # assume it's the list of transport items
            items = [el for el in data if isinstance(el, dict)]
            if not items:
                return pd.DataFrame()
            data = {'Transport': items}
        else:
            data = chosen

    # Unwrap common envelope structures
    transports = None
    if isinstance(data, dict):
        # data -> Transport
        if 'data' in data and isinstance(data['data'], dict):
            d = data['data']
            transports = d.get('Transport') or d.get('transport') or d.get('Transports')
        # top-level keys
        transports = transports or data.get('Transport') or data.get('transport') or data.get('Transports') or data.get('list')

    # If transports is a dict, it may contain a 'list' key
    if isinstance(transports, dict):
        transports = transports.get('list') or transports.get('transports') or transports.get('items') or transports

    # If nothing found yet, maybe data itself is a single transport object
    if transports is None:
        if isinstance(data, dict) and all(k in data for k in ('id', 'origin', 'destination')):
            transports = [data]
        else:
            return pd.DataFrame()

    # Normalize to a list
    if isinstance(transports, dict):
        transports = [transports]
    if not isinstance(transports, list):
        return pd.DataFrame()

    rows = []
    for item in transports:
        if not isinstance(item, dict):
            continue

        # Skip placeholder/test rows where field values are the field names
        placeholder = True
        for k in ('id', 'origin', 'destination', 'departureTime', 'arrivalTime', 'status', 'vehicleType'):
            v = item.get(k) or item.get(k.lower()) or item.get(k.replace('Time', '_time'))
            if v is None or v == '' or (isinstance(v, str) and v.strip() != k):
                placeholder = False
                break
        if placeholder:
            # this is the sentinel/placeholder row from example.json
            continue

        # normalize keys supporting camelCase and snake_case
        tid = item.get('id') or item.get('transport_id') or item.get('transportId')
        origin = item.get('origin') or item.get('from')
        destination = item.get('destination') or item.get('to')
        departure_raw = item.get('departureTime') or item.get('departure_time') or item.get('departure')
        arrival_raw = item.get('arrivalTime') or item.get('arrival_time') or item.get('arrival')
        status = item.get('status')
        vehicle_type = item.get('vehicleType') or item.get('vehicle_type')

        # parse dates using util if available, otherwise leave raw for pandas
        try:
            departure_parsed = util.parse_date(departure_raw)
        except Exception:
            departure_parsed = departure_raw
        try:
            arrival_parsed = util.parse_date(arrival_raw)
        except Exception:
            arrival_parsed = arrival_raw

        row = {
            'id': tid,
            'origin': origin,
            'destination': destination,
            'departure_time': departure_parsed,
            'arrival_time': arrival_parsed,
            'status': status,
            'vehicle_type': vehicle_type,
        }
        rows.append(row)

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    # Coerce datetimes
    try:
        df['departure_time'] = pd.to_datetime(df['departure_time'], errors='coerce')
    except Exception:
        pass
    try:
        df['arrival_time'] = pd.to_datetime(df['arrival_time'], errors='coerce')
    except Exception:
        pass

    # Coerce id to string (preserve non-numeric ids)
    try:
        df['id'] = df['id'].astype(str)
    except Exception:
        pass

    return df

