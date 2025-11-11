import requests
import json
import pandas as pd
import utils.util as util

'''
File for managing api access with the warehouse data provider
'''

def send_query(warehouseId = None):
    warehouses = ""
    if warehouseId is None:
        warehouses = "warehouses"
    else:
        warehouses = f"warehousesById(id: \"{warehouseId}\")"

    query = f"""
        query MyExampleWarehouseQuery {{
            Warehouse {{
                {warehouses} {{
                    id
                    name
                    location
                    last_updated
                    inventory {{
                        id
                        name
                        category
                        quantity
                        restock_date
                        supplier
                        unit_price
                    }}
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
    Convert JSON-like Python objects (as returned by json.loads)
    into a pandas DataFrame suitable for Streamlit usage.

    Expected input shapes (handled heuristically):
      - A dict with top-level key 'data' -> 'Warehouse' -> 'warehouses' (list)
      - A dict representing a single warehouse
      - A list/tuple of such dict(s)

    The function will flatten inventory items so each row represents
    one inventory item augmented with its warehouse metadata.

    Returns a pandas.DataFrame. On empty or unrecognized input,
    returns an empty DataFrame.
    """
    # If input is a JSON string, try to parse it
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception:
            return pd.DataFrame()

    # Unwrap common envelope structures
    # If the input is a list and contains dicts, try to find the dict with 'data'
    if isinstance(data, (list, tuple)):
        # prefer a dict that has 'data' key
        chosen = None
        for el in data:
            if isinstance(el, dict) and 'data' in el:
                chosen = el
                break
        if chosen is None and len(data) > 0 and isinstance(data[0], dict):
            chosen = data[0]
        if chosen is None:
            return pd.DataFrame()
        data = chosen

    # Drill down to warehouses list if present
    warehouses = None
    if isinstance(data, dict):
        warehouses = (data.get('data') or {}).get('Warehouse') if data.get('data') else None
        if isinstance(warehouses, dict):
            # warehouses may be nested further
            warehouses = warehouses.get('warehouses') or warehouses.get('warehousesById') or warehouses

        if warehouses is None:
            # maybe data itself is the Warehouse object
            if 'warehouses' in data:
                warehouses = data.get('warehouses')
            elif 'Warehouse' in data and isinstance(data['Warehouse'], dict):
                warehouses = data['Warehouse'].get('warehouses')

    # At this point, warehouses should be a list of warehouses
    if not isinstance(warehouses, list):
        # If a single warehouse dict was provided, wrap it
        if isinstance(warehouses, dict):
            warehouses = [warehouses]
        else:
            # try to interpret `data` itself as a warehouse list
            if isinstance(data, list) and all(isinstance(i, dict) for i in data):
                warehouses = data
            else:
                return pd.DataFrame()

    rows = []
    for wh in warehouses:
        if not isinstance(wh, dict):
            continue

        # Normalize warehouse fields with common key fallbacks
        wh_id = wh.get('id') or wh.get('warehouse_id') or wh.get('warehouseId')
        wh_name = wh.get('name') or wh.get('warehouse_name')
        wh_location = wh.get('location') or wh.get('warehouse_location')
        wh_last_updated = util.parse_date(wh.get('last_updated') or wh.get('lastUpdated') or wh.get('updated'))

        inventory = wh.get('inventory') or wh.get('items') or []
        if inventory is None:
            inventory = []

        # If inventory is a dict keyed by id, convert to list
        if isinstance(inventory, dict):
            inventory = list(inventory.values())

        for item in inventory:
            if not isinstance(item, dict):
                continue

            item_id = item.get('id') or item.get('item_id') or item.get('itemId')
            item_name = item.get('name') or item.get('item_name')
            category = item.get('category')
            quantity = item.get('quantity') or item.get('qty') or 0
            restock_date = util.parse_date(item.get('restock_date') or item.get('restockDate'))
            supplier = item.get('supplier')
            unit_price = item.get('unit_price') or item.get('price') or item.get('unitPrice')

            row = {
                'warehouse_id': wh_id,
                'warehouse_name': wh_name,
                'warehouse_location': wh_location,
                'warehouse_last_updated': wh_last_updated,
                'item_id': item_id,
                'item_name': item_name,
                'category': category,
                'quantity': quantity,
                'restock_date': restock_date,
                'supplier': supplier,
                'unit_price': unit_price,
            }
            rows.append(row)

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    # Try to coerce types and compute total value where possible
    try:
        df['warehouse_last_updated'] = pd.to_datetime(df['warehouse_last_updated'], errors='coerce')
    except Exception:
        pass

    try:
        df['restock_date'] = pd.to_datetime(df['restock_date'], errors='coerce')
    except Exception:
        pass

    # Coerce numeric types
    try:
        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0)
    except Exception:
        df['quantity'] = 0

    try:
        df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce')
    except Exception:
        df['unit_price'] = pd.NA

    # Compute total value when possible
    try:
        df['total_value'] = df['quantity'] * df['unit_price']
    except Exception:
        df['total_value'] = pd.NA

    return df

