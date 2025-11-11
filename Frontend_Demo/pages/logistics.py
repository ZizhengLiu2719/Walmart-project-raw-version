import streamlit as st
import pandas as pd
import utils.transport as transport_util
import utils.nws as nws_util
from datetime import datetime, timedelta

st.set_page_config(page_title="Logistics Dashboard", layout="wide")

def render_header():
    col1, col2 = st.columns([6, 1])
    with col1:
        st.image("assets/walmart_logo.png", width=140)
    with col2:
        st.image("assets/user_avatar.png", width=50)
    st.divider()

def match_transports_with_weather(transport_df, weather_df):
    """
    Match transports with weather alerts based on area and time overlap.
    Returns a list of matches with risk assessment.
    """
    matches = []
    
    for idx, transport in transport_df.iterrows():
        transport_area = transport.get('area', '')
        departure = transport.get('departureTime')
        arrival = transport.get('arrivalTime')
        
        if pd.isna(departure) or pd.isna(arrival):
            continue
            
        for _, alert in weather_df.iterrows():
            # Use 'Area' field name to match XML structure
            alert_area = alert.get('Area', '')
            effective = alert.get('Effective')
            expires = alert.get('Expires')
            
            if pd.isna(effective) or pd.isna(expires):
                continue
            
            # Check if areas match (fuzzy matching - contains check)
            area_match = False
            if transport_area and alert_area:
                # Normalize areas for comparison
                t_area_norm = transport_area.lower().replace(',', '').replace('  ', ' ')
                a_area_norm = alert_area.lower().replace(',', '').replace('  ', ' ')
                
                # Check if there's overlap in area names
                t_parts = set(t_area_norm.split())
                a_parts = set(a_area_norm.split())
                area_match = bool(t_parts & a_parts)
            
            if not area_match:
                continue
            
            # Check time overlap
            time_overlap = (departure <= expires and arrival >= effective)
            
            if time_overlap:
                # Calculate risk level
                event_type = alert.get('Event', '').lower()
                risk_level = 'Medium'
                if 'tornado' in event_type or 'severe' in event_type:
                    risk_level = 'High'
                elif 'watch' in event_type or 'advisory' in event_type:
                    risk_level = 'Low'
                
                matches.append({
                    'transport_id': transport.get('id'),
                    'vehicle_type': transport.get('vehicleType'),
                    'origin': transport.get('origin'),
                    'destination': transport.get('destination'),
                    'area': transport_area,
                    'status': transport.get('status'),
                    'departure': departure,
                    'arrival': arrival,
                    'alert_event': alert.get('Event'),
                    'alert_summary': alert.get('Summary'),
                    'alert_effective': effective,
                    'alert_expires': expires,
                    'risk_level': risk_level
                })
    
    return pd.DataFrame(matches)

def render_risk_metrics(matched_df, transport_df, weather_df):
    """Display key risk metrics at the top of the page"""
    st.markdown("## 🚨 Logistics Risk Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_transports = len(transport_df)
    
    # Handle empty matched_df - count unique transports, not match instances
    if len(matched_df) > 0 and 'risk_level' in matched_df.columns and 'transport_id' in matched_df.columns:
        # Count unique transports at risk (Medium or High)
        at_risk_ids = matched_df[matched_df['risk_level'].isin(['High', 'Medium'])]['transport_id'].unique()
        at_risk = len(at_risk_ids)
        
        # Count unique transports at high risk
        high_risk_ids = matched_df[matched_df['risk_level'] == 'High']['transport_id'].unique()
        high_risk = len(high_risk_ids)
    else:
        at_risk = 0
        high_risk = 0
    
    active_alerts = len(weather_df)
    
    safe_transports = total_transports - at_risk
    
    col1.metric("Total Active Transports", total_transports)
    col2.metric("Transports at Risk", at_risk, delta=f"{safe_transports} safe", delta_color="inverse")
    col3.metric("High Risk Routes", high_risk)
    col4.metric("Active Weather Alerts", active_alerts)
    
    st.markdown("<br>", unsafe_allow_html=True)

def render_risk_alerts(matched_df):
    """Display urgent risk alerts for high-priority situations"""
    # Handle empty dataframe or missing columns
    if len(matched_df) == 0 or 'risk_level' not in matched_df.columns:
        return
    
    high_risk = matched_df[matched_df['risk_level'] == 'High']
    
    if len(high_risk) > 0:
        st.markdown("### ⚠️ High Priority Alerts")
        for _, row in high_risk.iterrows():
            st.markdown(
                f"""
                <div class="card" style="background-color: #fff3cd; border-left: 4px solid #ff6b6b; margin-bottom: 12px; padding: 16px;">
                    <strong style="color: #d63031;">🚛 Transport #{row['transport_id']} - {row['vehicle_type']}</strong><br>
                    <span style="color: #2d3436;"><strong>Route:</strong> {row['origin']} → {row['destination']}</span><br>
                    <span style="color: #636e72;"><strong>Area:</strong> {row['area']}</span><br>
                    <span style="color: #e17055;"><strong>Weather Event:</strong> {row['alert_event']}</span><br>
                    <span style="color: #636e72;">{row['alert_summary']}</span><br>
                    <span style="font-size: 12px; color: #636e72;">Active: {row['alert_effective'].strftime('%H:%M')} - {row['alert_expires'].strftime('%H:%M')}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown("<br>", unsafe_allow_html=True)

def render_transport_weather_table(matched_df):
    """Display detailed table of transport-weather matches"""
    st.markdown("### 📊 Transport & Weather Correlation")
    
    if len(matched_df) == 0:
        st.info("✓ No active weather alerts affecting current transports.")
        return
    
    # Add risk color coding
    def risk_color(risk):
        colors = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢'}
        return colors.get(risk, '⚪')
    
    display_df = matched_df.copy()
    display_df['Risk'] = display_df['risk_level'].apply(risk_color) + ' ' + display_df['risk_level']
    display_df['Route'] = display_df['origin'] + ' → ' + display_df['destination']
    display_df['Transport Window'] = display_df['departure'].dt.strftime('%H:%M') + ' - ' + display_df['arrival'].dt.strftime('%H:%M')
    display_df['Alert Window'] = display_df['alert_effective'].dt.strftime('%H:%M') + ' - ' + display_df['alert_expires'].dt.strftime('%H:%M')
    
    table_df = display_df[[
        'transport_id', 'vehicle_type', 'Route', 'area', 'status',
        'Transport Window', 'alert_event', 'Alert Window', 'Risk'
    ]].rename(columns={
        'transport_id': 'ID',
        'vehicle_type': 'Vehicle',
        'area': 'Area',
        'status': 'Status',
        'alert_event': 'Weather Event'
    })
    
    st.dataframe(table_df, use_container_width=True, hide_index=True)
    st.markdown("<br>", unsafe_allow_html=True)

def render_all_transports(transport_df, matched_df):
    """Display all transports with risk indicators"""
    st.markdown("### 🚛 All Active Transports")
    
    # Mark which transports are at risk
    at_risk_ids = set(matched_df['transport_id'].unique()) if len(matched_df) > 0 else set()
    
    display_df = transport_df.copy()
    display_df['Risk Status'] = display_df['id'].apply(
        lambda x: '⚠️ At Risk' if str(x) in [str(i) for i in at_risk_ids] else '✓ Clear'
    )
    display_df['Route'] = display_df['origin'] + ' → ' + display_df['destination']
    
    if 'departureTime' in display_df.columns and 'arrivalTime' in display_df.columns:
        display_df['Schedule'] = display_df['departureTime'].dt.strftime('%H:%M') + ' - ' + display_df['arrivalTime'].dt.strftime('%H:%M')
    else:
        display_df['Schedule'] = 'N/A'
    
    table_df = display_df[['id', 'vehicleType', 'Route', 'area', 'status', 'Schedule', 'Risk Status']].rename(columns={
        'id': 'ID',
        'vehicleType': 'Vehicle',
        'area': 'Area',
        'status': 'Status'
    })
    
    st.dataframe(table_df, use_container_width=True, hide_index=True)
    st.markdown("<br>", unsafe_allow_html=True)

def render_weather_alerts(weather_df):
    """Display all active weather alerts"""
    st.markdown("### 🌩️ Active Weather Alerts")
    
    if len(weather_df) == 0:
        st.info("No active weather alerts.")
        return
    
    display_df = weather_df.copy()
    
    if 'Effective' in display_df.columns and 'Expires' in display_df.columns:
        display_df['Active Period'] = display_df['Effective'].dt.strftime('%H:%M') + ' - ' + display_df['Expires'].dt.strftime('%H:%M')
    else:
        display_df['Active Period'] = 'N/A'
    
    table_df = display_df[['Event', 'Area', 'Active Period', 'Summary']].rename(columns={
        'Event': 'Event Type',
        'Area': 'Area',
        'Summary': 'Details'
    })
    
    st.dataframe(table_df, use_container_width=True, hide_index=True)

def render_statistics(matched_df, transport_df):
    """Display statistical breakdown"""
    st.markdown("### 📈 Risk Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Transport Status Distribution")
        if len(transport_df) > 0 and 'status' in transport_df.columns:
            status_counts = transport_df['status'].value_counts()
            st.bar_chart(status_counts)
        else:
            st.info("No transport data available.")
    
    with col2:
        st.markdown("#### Risk Level Distribution")
        if len(matched_df) > 0 and 'risk_level' in matched_df.columns:
            risk_counts = matched_df['risk_level'].value_counts()
            st.bar_chart(risk_counts)
        else:
            st.info("No weather-related risks detected.")

########################################
#          Logistics Dashboard
########################################

render_header()

# Back to home button at top
if st.button("← Back to Home", key="top_home_button"):
    st.switch_page("pages/homepage.py")

st.title("🚚 Logistics & Weather Monitoring")
st.markdown("Real-time correlation of transport operations with weather conditions")
st.markdown("<br>", unsafe_allow_html=True)

# Fetch data from both services
with st.spinner("Loading transport data..."):
    transport_success, transport_data = transport_util.send_query()

with st.spinner("Loading weather alerts..."):
    weather_success, weather_data = nws_util.send_query()

# Process data
if transport_success and weather_success:
    transport_df = transport_util.format_data(transport_data)
    weather_df = nws_util.format_data(weather_data)
    
    if not transport_df.empty and not weather_df.empty:
        # Match transports with weather
        matched_df = match_transports_with_weather(transport_df, weather_df)
        
        # Render dashboard sections
        render_risk_metrics(matched_df, transport_df, weather_df)
        render_risk_alerts(matched_df)
        render_transport_weather_table(matched_df)
        
        col1, col2 = st.columns(2)
        with col1:
            render_all_transports(transport_df, matched_df)
        with col2:
            render_weather_alerts(weather_df)
        
        render_statistics(matched_df, transport_df)
        
    elif transport_df.empty:
        st.warning("⚠️ No transport data available.")
        if not weather_df.empty:
            render_weather_alerts(weather_df)
    elif weather_df.empty:
        st.warning("⚠️ No weather alert data available.")
        if not transport_df.empty:
            render_all_transports(transport_df, pd.DataFrame())
    else:
        st.error("No data available from either service.")
else:
    if not transport_success:
        st.error(f"Failed to load transport data: {transport_data}")
    if not weather_success:
        st.error(f"Failed to load weather data: {weather_data}")

# Back to home button
st.markdown("<br><br>", unsafe_allow_html=True)
if st.button("← Back to Home", type="secondary"):
    st.switch_page("pages/homepage.py")
