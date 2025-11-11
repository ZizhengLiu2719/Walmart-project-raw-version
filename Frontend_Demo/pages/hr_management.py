import streamlit as st
import pandas as pd
import requests
import json

st.set_page_config(page_title="HR Management Dashboard", layout="wide")

# GraphQL endpoint
GRAPHQL_URL = 'http://localhost:4000/graphql'

def send_graphql_query(query):
    """Send GraphQL query to the API"""
    try:
        headers = {'Content-Type': 'application/json'}
        payload = {'query': query}
        response = requests.post(GRAPHQL_URL, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f'Error: Received status code {response.status_code}'
    except requests.exceptions.ConnectionError:
        return False, f'Error: Cannot connect to {GRAPHQL_URL}. Please ensure DataFusion API is running.'
    except requests.exceptions.Timeout:
        return False, 'Error: Request timeout. API may be slow or unresponsive.'
    except Exception as e:
        return False, f'Error: {str(e)}'

def fetch_employees_data():
    """Fetch all employees from GraphQL API"""
    query = """
    query {
        Employees {
            employees {
                id
                first_name
                last_name
                role
                department
                salary
            }
        }
    }
    """
    try:
        success, response = send_graphql_query(query)
        if success and response and isinstance(response, dict) and 'data' in response:
            if response['data'] and 'Employees' in response['data']:
                if response['data']['Employees'] and 'employees' in response['data']['Employees']:
                    employees = response['data']['Employees']['employees']
                    if employees:
                        return pd.DataFrame(employees)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching employees data: {str(e)}")
        return pd.DataFrame()

def fetch_finances_data():
    """Fetch all finance records from GraphQL API"""
    query = """
    query {
        Finances {
            list {
                id
                transactionDate
                description
                amount
                currency
                category
            }
        }
    }
    """
    try:
        success, response = send_graphql_query(query)
        if success and response and isinstance(response, dict) and 'data' in response:
            if response['data'] and 'Finances' in response['data']:
                if response['data']['Finances'] and 'list' in response['data']['Finances']:
                    finances = response['data']['Finances']['list']
                    if finances:
                        return pd.DataFrame(finances)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching finances data: {str(e)}")
        return pd.DataFrame()

########################################
#     HR Management Dashboard
########################################

# Header
st.title("🏢 Human Resource Management Dashboard")
st.markdown("### Integrated view of Finances and Employees data")

# Back button
if st.button("← Back to Homepage"):
    st.switch_page("pages/homepage.py")

# Check API connection
with st.expander("ℹ️ Connection Status", expanded=False):
    st.info(f"""
    **GraphQL API Endpoint:** {GRAPHQL_URL}
    
    **Required Services:**
    - DataFusion API (Port 4000)
    - Employees_JSON Service (Port 8001)
    - Finances_CSV Service (Port 8085)
    
    If you see errors below, please ensure all services are running.
    """)

st.markdown("---")

# Create tabs for better organization
tab1, tab2, tab3 = st.tabs(["👥 Employees", "💰 Finances", "📊 Overview"])

########################################
# TAB 1: Employees Data
########################################
with tab1:
    st.header("📋 Employee Directory")
    
    with st.spinner("Loading employee data..."):
        employees_df = fetch_employees_data()
    
    if not employees_df.empty:
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Employees", len(employees_df))
        with col2:
            avg_salary = employees_df['salary'].mean()
            st.metric("Average Salary", f"${avg_salary:,.0f}")
        with col3:
            total_payroll = employees_df['salary'].sum()
            st.metric("Total Payroll", f"${total_payroll:,.0f}")
        with col4:
            num_departments = employees_df['department'].nunique()
            st.metric("Departments", num_departments)
        
        st.markdown("---")
        
        # Display data table
        st.subheader("Employee Details")
        
        # Format the dataframe for better display
        display_df = employees_df.copy()
        display_df['Full Name'] = display_df['first_name'] + ' ' + display_df['last_name']
        display_df['Salary'] = display_df['salary'].apply(lambda x: f"${x:,.0f}")
        
        # Reorder columns
        display_df = display_df[['id', 'Full Name', 'role', 'department', 'Salary']]
        display_df.columns = ['ID', 'Full Name', 'Role', 'Department', 'Salary']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Department breakdown
        st.markdown("---")
        st.subheader("📊 Department Breakdown")
        dept_counts = employees_df['department'].value_counts()
        col1, col2 = st.columns(2)
        with col1:
            st.bar_chart(dept_counts)
        with col2:
            st.dataframe(
                dept_counts.reset_index(),
                column_config={
                    "department": "Department",
                    "count": "Employee Count"
                },
                hide_index=True
            )
    else:
        st.error("❌ Unable to load employee data. Please ensure the DataFusion API is running.")

########################################
# TAB 2: Finances Data
########################################
with tab2:
    st.header("💳 Financial Transactions")
    
    with st.spinner("Loading financial data..."):
        finances_df = fetch_finances_data()
    
    if not finances_df.empty:
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Transactions", len(finances_df))
        with col2:
            total_amount = finances_df['amount'].sum()
            st.metric("Total Amount", f"${total_amount:,.2f}")
        with col3:
            avg_transaction = finances_df['amount'].mean()
            st.metric("Avg Transaction", f"${avg_transaction:,.2f}")
        with col4:
            num_categories = finances_df['category'].nunique()
            st.metric("Categories", num_categories)
        
        st.markdown("---")
        
        # Display data table
        st.subheader("Transaction Details")
        
        # Format the dataframe
        display_df = finances_df.copy()
        display_df['amount'] = display_df['amount'].apply(lambda x: f"${x:,.2f}")
        display_df.columns = ['ID', 'Transaction Date', 'Description', 'Amount', 'Currency', 'Category']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Category breakdown
        st.markdown("---")
        st.subheader("📊 Category Breakdown")
        
        # Calculate sum by category
        finances_df['amount_numeric'] = pd.to_numeric(finances_df['amount'], errors='coerce')
        category_totals = finances_df.groupby('category')['amount_numeric'].sum().sort_values(ascending=False)
        
        col1, col2 = st.columns(2)
        with col1:
            st.bar_chart(category_totals)
        with col2:
            category_df = category_totals.reset_index()
            category_df.columns = ['Category', 'Total Amount']
            category_df['Total Amount'] = category_df['Total Amount'].apply(lambda x: f"${x:,.2f}")
            st.dataframe(category_df, hide_index=True)
    else:
        st.error("❌ Unable to load financial data. Please ensure the DataFusion API is running.")

########################################
# TAB 3: Overview (Combined View)
########################################
with tab3:
    st.header("📈 Combined Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👥 Employee Summary")
        if not employees_df.empty:
            st.metric("Total Employees", len(employees_df))
            st.metric("Average Salary", f"${employees_df['salary'].mean():,.0f}")
            st.metric("Total Payroll", f"${employees_df['salary'].sum():,.0f}")
            
            st.markdown("**Top Roles:**")
            role_counts = employees_df['role'].value_counts().head(5)
            for role, count in role_counts.items():
                st.write(f"• {role}: {count}")
        else:
            st.warning("No employee data available")
    
    with col2:
        st.subheader("💰 Finance Summary")
        if not finances_df.empty:
            # Ensure amount_numeric column exists
            if 'amount_numeric' not in finances_df.columns:
                finances_df['amount_numeric'] = pd.to_numeric(finances_df['amount'], errors='coerce')
            
            st.metric("Total Transactions", len(finances_df))
            st.metric("Total Amount", f"${finances_df['amount_numeric'].sum():,.2f}")
            st.metric("Avg Transaction", f"${finances_df['amount_numeric'].mean():,.2f}")
            
            st.markdown("**Top Categories:**")
            category_totals = finances_df.groupby('category')['amount_numeric'].sum().sort_values(ascending=False).head(5)
            for category, amount in category_totals.items():
                st.write(f"• {category}: ${amount:,.2f}")
        else:
            st.warning("No financial data available")
    
    st.markdown("---")
    
    # Correlation insight (if both datasets available)
    if not employees_df.empty and not finances_df.empty:
        st.subheader("💡 Business Insights")
        
        # Ensure amount_numeric column exists
        if 'amount_numeric' not in finances_df.columns:
            finances_df['amount_numeric'] = pd.to_numeric(finances_df['amount'], errors='coerce')
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"""
            **Payroll vs Revenue**
            - Total Payroll: ${employees_df['salary'].sum():,.0f}
            - Total Transactions: ${finances_df['amount_numeric'].sum():,.2f}
            """)
        
        with col2:
            avg_salary = employees_df['salary'].mean()
            avg_transaction = finances_df['amount_numeric'].mean()
            st.info(f"""
            **Per Employee Metrics**
            - Avg Salary: ${avg_salary:,.0f}
            - Avg Transaction: ${avg_transaction:,.2f}
            - Transactions per Employee: {len(finances_df) / len(employees_df):.1f}
            """)
        
        with col3:
            st.info(f"""
            **Department Distribution**
            - Departments: {employees_df['department'].nunique()}
            - Categories: {finances_df['category'].nunique()}
            - Data Sources: 2 (Employees + Finances)
            """)

st.markdown("---")
st.caption("📊 Data powered by Walmart DataFusion API | Last updated: Real-time")

