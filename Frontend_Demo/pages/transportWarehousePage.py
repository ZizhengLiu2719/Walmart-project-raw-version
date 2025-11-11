import streamlit as st
import pandas as pd
import json
import utils.util as util
import utils.warehouse as wh
import utils.transport_alt as tp
from datetime import datetime

st.set_page_config(page_title="Employee Service Portal", layout="wide")

def display_warehouse_data(df):
    # Streamlit UI
    st.markdown("### Warehouse Inventory")

    # drop columns we dont need to see
    df = df.loc[:, df.columns != 'warehouse_location']

    st.dataframe(df.sort_values(["warehouse_id", "item_id"]).reset_index(drop=True), hide_index=True)

def display_transport_data(df):
    # Streamlit UI
    st.markdown("### Transport Data")

    # Prefer sorting by departure_time then arrival_time then id when available
    sort_cols = [c for c in ['departure_time', 'arrival_time', 'id'] if c in df.columns]
    if not df.empty and sort_cols:
        st.dataframe(df.sort_values(sort_cols).reset_index(drop=True), hide_index=True)
    else:
        st.dataframe(df)

def display_active_shipments(transport_df, warehouse_df=None):
    """
    Render active shipments (status PENDING or IN_TRANSIT) using Streamlit built-ins.

    transport_df: DataFrame returned from `tp.format_data`.
    warehouse_df: optional DataFrame returned from `wh.format_data` to link origin -> warehouse info.
    """
    st.subheader("Active Shipments")

    # Basic checks
    if transport_df is None or transport_df.empty:
        st.info("No transport records available.")
        return

    if 'status' not in transport_df.columns:
        st.info("Transport data does not contain a 'status' column.")
        return

    # filter active shipments
    status_series = transport_df['status'].astype(str).str.upper()
    active_mask = status_series.isin(['PENDING', 'IN_TRANSIT'])
    active = transport_df[active_mask].copy()

    if active.empty:
        st.info("No active shipments (PENDING or IN_TRANSIT).")
        return

    columns = 4
    active = active.head(columns)

    # create columns and place each metric into columns with wrapping
    cols = st.columns(columns)
    for i, (_, row) in enumerate(active.iterrows()):
        dest = row.get('destination')
        id = row.get('id')
        arrival = row.get('arrival_time')
        status = row.get('status')
        if status == 'IN_TRANSIT':
            color = "normal"
        else:
            color = "off"

        arrival = datetime.fromisoformat(str(arrival))
        formattedArrivalDT = arrival.strftime('%b %d, %I:%M %p')

        target_col = cols[i % columns]

        target_col.metric(f"ID: {id} \n\n Destination: {dest} \n\n Estimated Arrival:", value=formattedArrivalDT, delta=status, delta_color=color, border=True)


def transport_insights(df):
    """
    Show quick transport-level KPIs and charts.
    """

    # High-level metrics
    total = len(df)
    in_transit = int((df['status'].astype(str).str.upper() == 'IN_TRANSIT').sum())
    pending = int((df['status'].astype(str).str.upper() == 'PENDING').sum())
    delivered = int((df['status'].astype(str).str.upper() == 'DELIVERED').sum())

    # Average transit time (hours) when both departure and arrival exist
    transit_durations = (df['arrival_time'] - df['departure_time']).dt.total_seconds().div(3600)
    avg_transit_hours = float(transit_durations.dropna().mean()) if not transit_durations.dropna().empty else None

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Shipments", total, border=True)
    c2.metric("In Transit", in_transit, border=True)
    c3.metric("Pending", pending, border=True)
    if avg_transit_hours is not None:
        c4.metric("Avg Transit (hrs)", f"{avg_transit_hours:.1f}", border=True)
    else:
        c4.metric("Avg Transit (hrs)", "N/A", border=True)


def warehouse_insights(df):
    """
    Show warehouse-level KPIs and top SKUs.
    """

    total_warehouses = df['warehouse_id'].nunique()
    total_skus = df['item_id'].nunique()
    total_units = int(df['quantity'].sum()) if 'quantity' in df.columns else None
    total_value = df['total_value'].sum() if 'total_value' in df.columns else None

    a, b, c, d = st.columns(4)
    a.metric("Warehouses", total_warehouses, border=True)
    b.metric("Unique SKUs", total_skus, border=True)
    c.metric("Total Units", total_units if total_units is not None else "N/A", border=True)
    d.metric("Inventory Value", f"${total_value:,.2f}" if total_value is not None and not pd.isna(total_value) else "N/A", border=True)

    st.markdown("### Top items by quantity")
    try:
        top_items = df.groupby(['item_id', 'item_name'], dropna=False)['quantity'].sum().reset_index()
        top_items = top_items.sort_values('quantity', ascending=False).head(10)
        st.dataframe(top_items.reset_index(drop=True), hide_index=True)
    except Exception:
        pass


def combined_origin_inventory_insight(transport_df, warehouse_df):
    """
    Combine transport and warehouse data by matching transport.origin to warehouse_id or warehouse_name.
    Shows shipments per origin and the inventory totals for matched warehouses.
    """
    st.subheader("Origin -> Warehouse Impact")

    # Aggregate transport by origin
    tgroup = transport_df.copy()
    tgroup['origin_clean'] = tgroup['origin'].astype(str)
    shipments_by_origin = tgroup.groupby('origin_clean').agg(
        shipments_count=('id', 'count'),
        in_transit_count=('status', lambda s: (s.astype(str).str.upper() == 'IN_TRANSIT').sum()),
        next_departure=('departure_time', 'min')
    ).reset_index()

    # Aggregate warehouse by id and name
    wagg = warehouse_df.groupby(['warehouse_id', 'warehouse_name'], dropna=False).agg(
        warehouse_total_units=('quantity', 'sum'),
        warehouse_total_value=('total_value', 'sum'),
        unique_skus=('item_id', 'nunique')
    ).reset_index()

    # For each origin try to match warehouse_id or warehouse_name
    rows = []
    for _, r in shipments_by_origin.iterrows():
        origin = r['origin_clean']
        matched = wagg[(wagg['warehouse_id'].astype(str) == str(origin)) | (wagg['warehouse_name'].astype(str) == str(origin))]
        if not matched.empty:
            # aggregate matched warehouses
            total_units = int(matched['warehouse_total_units'].sum())
            total_value = matched['warehouse_total_value'].sum()
            skus = int(matched['unique_skus'].sum())
        else:
            total_units = None
            total_value = None
            skus = None

        rows.append({
            'origin': origin,
            'shipments': int(r['shipments_count']),
            'in_transit': int(r['in_transit_count']),
            'next_departure': r['next_departure'],
            'matched_total_units': total_units,
            'matched_total_value': total_value,
            'matched_unique_skus': skus
        })

    out_df = pd.DataFrame(rows).sort_values('shipments', ascending=False)

    # Show summary table
    # format next_departure nicely when present
    if 'next_departure' in out_df.columns:
        try:
            out_df['next_departure'] = pd.to_datetime(out_df['next_departure'])
            out_df['next_departure'] = out_df['next_departure'].dt.strftime('%Y-%m-%d %H:%M')
        except Exception:
            pass

    st.dataframe(out_df.reset_index(drop=True), hide_index=True)

    # For the top 3 origins, show an expander with the top items in the matched warehouse(s)
    top_origins = out_df.head(3)['origin'].tolist()
    for origin in top_origins:
        exp = st.expander(f"Details for origin: {origin}")
        matched_wh = warehouse_df[(warehouse_df['warehouse_id'].astype(str) == str(origin)) | (warehouse_df['warehouse_name'].astype(str) == str(origin))]
        if not matched_wh.empty:
            summary = matched_wh.groupby(['item_id', 'item_name'], dropna=False).agg(total_qty=('quantity', 'sum')).reset_index()
            summary = summary.sort_values('total_qty', ascending=False).head(10)
            exp.dataframe(summary.reset_index(drop=True), hide_index=True)
        else:
            exp.write("No matching warehouse found for this origin.")

# Set page title
st.title('GraphQL Query Interface')

WHSuccess, WHDataObject = wh.send_query()
TPSuccess, TPDataObject = tp.send_query()

if WHSuccess and TPSuccess:
    WHdf = wh.format_data(WHDataObject)
    TPdf = tp.format_data(TPDataObject)

    display_active_shipments(TPdf, WHdf)

    try:
        transport_insights(TPdf)
    except Exception:
        # avoid breaking the UI if insight fails
        st.write("Transport insights could not be rendered.")

    try:
        warehouse_insights(WHdf)
    except Exception:
        st.write("Warehouse insights could not be rendered.")

    try:
        combined_origin_inventory_insight(TPdf, WHdf)
    except Exception:
        st.write("Combined origin/warehouse insight could not be rendered.")

    display_warehouse_data(WHdf)

    display_transport_data(TPdf)

else:
    if not WHSuccess:
        st.toast(WHDataObject)
        st.error(WHDataObject)
    else:
        st.toast(TPDataObject)
        st.error(TPDataObject)


