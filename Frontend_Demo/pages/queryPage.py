import streamlit as st
import pandas as pd
import json
import utils.util as util
import utils.warehouse as wh

st.set_page_config(page_title="Employee Service Portal", layout="wide")

def display_warehouse_data(data_obj):
    # Load JSON (replace json.loads(raw_json) with your data source)
    raw_json = json.dumps(data_obj)

    data = json.loads(raw_json)

    # Build rows: flatten inventory entries and attach warehouse info
    df = wh.format_data(data)

    # Formatting columns
    if df.empty:
        df["warehouse_last_updated"] = pd.to_datetime(df["warehouse_last_updated"])
        df["restock_date"] = pd.to_datetime(df["restock_date"])
        df["unit_price"] = df["unit_price"].astype(float)
        df["total_value"] = df["quantity"] * df["unit_price"]

    # Streamlit UI
    st.title("Warehouse Inventory")

    st.dataframe(df.sort_values(["warehouse_id", "item_id"]).reset_index(drop=True))

    # # Filters (can't work without refreshing page as of now)
    # with st.expander("Filters"):
    #     wh_filter = st.multiselect("Warehouse", options=sorted(df["warehouse_name"].unique()) if not df.empty else [])
    #     cat_filter = st.multiselect("Category", options=sorted(df["category"].unique()) if not df.empty else [])
    #     min_qty, max_qty = st.slider("Quantity range", 0, int(df["quantity"].max()) if not df.empty else 0, (0, int(df["quantity"].max()) if not df.empty else 0))
    #     filtered = df.copy()
    #     if wh_filter:
    #         filtered = filtered[filtered["warehouse_name"].isin(wh_filter)]
    #     if cat_filter:
    #         filtered = filtered[filtered["category"].isin(cat_filter)]
    #     filtered = filtered[(filtered["quantity"] >= min_qty) & (filtered["quantity"] <= max_qty)]
    #     st.write(f"Filtered rows: {len(filtered)}")
    #     st.dataframe(filtered)


########################################
#           Dashboard Page
########################################

# Set page title
st.title('GraphQL Query Interface')

if st.button("back to homepage"):
    st.switch_page("pages/homepage.py")

# Create a text area for user to input GraphQL query
query = st.text_area('Enter your GraphQL query:', height=200)


# Create a button to execute the query
if st.button('Execute Query'):
    data_obj = util.send_custom_query(query)

    st.json(data_obj)

if st.button("Send test query (Warehouse)"):
    success, data_obj = wh.send_query()

    if success:
        st.json(data_obj, expanded=False)
        display_warehouse_data(data_obj)
    else:
        st.toast(data_obj)

st.markdown("---")  # Add a divider

# New button for HR Management
st.markdown("### 📊 Dashboard Access")
if st.button("🏢 Human Resource Management (Finances ↔ Employees)", use_container_width=True, type="primary"):
    st.switch_page("pages/hr_management.py")