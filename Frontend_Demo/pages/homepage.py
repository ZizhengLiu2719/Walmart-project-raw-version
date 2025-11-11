import streamlit as st
import pandas as pd

st.set_page_config(page_title="Employee Service Portal", layout="wide")

def render_space(num = 1):
    if num > 10:
        num = 10
    for _ in range(0, num):
        st.markdown("##")

def render_header():
    col1, col2 = st.columns([6, 1])
    with col1:
        st.image("assets/walmart_logo.png", width=140)
    with col2:
        st.image("assets/user_avatar.png", width=50)
    st.divider()

def render_welcome_card():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("assets/welcome_graphic.png", width="stretch")
    with col2:
        st.markdown("### Welcome back, Alex 👋")
        st.markdown("Here are your employee services at a glance.")
        st.markdown('<span class="accent-pill">Active Employee</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

image_size = 64
# Helper to render an image inside a column using nested sub-columns.
# We use asymmetric ratios so the image can be nudged slightly to the right.
def centered_image(col, path, ratios=(3, 3, 2)):
    left, center, right = col.columns(list(ratios))
    with center:
        st.image(path, width=image_size)

def render_service_tiles():
    col1, col2, col3, col4, col5, col6 = st.columns(6)




    with col1:
        centered_image(col1, "assets/icon_hr.png")
        if st.button("HR Management", use_container_width=True):
            st.switch_page("pages/hr_management.py")

    with col2:
        centered_image(col2, "assets/icon_payroll.png")
        st.button("Payroll", use_container_width=True)

    with col3:
        centered_image(col3, "assets/icon_schedule.png")
        st.button("My Schedule", use_container_width=True)

    with col4:
        centered_image(col4, "assets/icon_training.png")
        st.button("Training", use_container_width=True)

    with col5:
        centered_image(col5, "assets/icon_benefits.png")
        st.button("Benefits", use_container_width=True)

    with col6:
        st.markdown("<div style='font-size: 48px; text-align: center; margin-bottom: 8px;'>🚛</div>", unsafe_allow_html=True)
        if st.button("Logistics", use_container_width=True):
            st.switch_page("pages/logistics.py")

def render_employee_directory():
    employees = [
        {"name": "Jamie Roberts", "role": "Store Manager", "ext": "x421", "avatar": "assets/user_avatar.png"},
        {"name": "Priya Shah", "role": "Cash Lead", "ext": "x114", "avatar": "assets/user_avatar.png"},
        {"name": "Carlos Mendez", "role": "Stock Supervisor", "ext": "x233", "avatar": "assets/user_avatar.png"},
    ]

    st.markdown("## Employees")

    css = """
        <style>
        .emp-name {
        font-size: 80px;      /* desired size */
        font-weight: 600;     /* optional */
        display: block;       /* keeps it on its own line */
        margin-top: 4px;      /* optional spacing */
        }
        </style>
        """

    st.markdown(css, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)

    image_size = 64

    emp = employees[0]

    with col1:
        centered_image(col1, emp["avatar"], ratios=(3, 3, 1))
        st.button(f'''{emp["role"]} • {emp["ext"]} \n\n {emp["name"]}''', type="tertiary", use_container_width=True)

    emp = employees[1]

    with col2:
        centered_image(col2, emp["avatar"], ratios=(3, 3, 1))
        st.button(f'''{emp["role"]} • {emp["ext"]} \n\n {emp["name"]}''', type="tertiary", use_container_width=True)

    emp = employees[2]

    with col3:
        centered_image(col3, emp["avatar"], ratios=(3, 3, 1))
        st.button(f'''{emp["role"]} • {emp["ext"]} \n\n {emp["name"]}''', type="tertiary", use_container_width=True)

def render_ticket_board():
    st.markdown("## 📝 Recent Tickets")

    tickets = pd.DataFrame([
        {"id":"TCK-1001","subject":"Register malfunction","status":"In Progress","owner":"Carlos M","updated":"2025-09-20"},
        {"id":"TCK-1002","subject":"Password reset","status":"Resolved","owner":"IT","updated":"2025-09-21"},
        {"id":"TCK-1003","subject":"Pallet spill","status":"Open","owner":"Facilities","updated":"2025-09-22"},
    ])

    def status_dot(status):
        color = {
            "Open": "#D67019",
            "In Progress": "#0071CE",
            "Resolved": "#4BB543"
        }.get(status, "#6c757d")
        return f'<span style="color:{color}; font-size:18px;">●</span>'

    for _, row in tickets.iterrows():
        st.markdown(
            f"""
            <div class="card" style="margin-bottom:8px;">
                {status_dot(row['status'])} <strong>{row['subject']}</strong><br>
                <span class='small-muted'>{row['owner']} • {row['updated']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

def render_metrics():
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("SLA Met", "97%")
    c2.metric("Avg Response", "2h 20m")
    c3.metric("Requests Today", "12")
    c4.metric("Active Users", "628")


########################################
#              Homepage
########################################

render_header()

render_welcome_card()

if st.button("Test Query Page", use_container_width=True):
    st.switch_page("pages/queryPage.py")

if st.button("Transport", use_container_width=True):
    st.switch_page("pages/transportWarehousePage.py")

render_metrics()

render_space()

render_service_tiles()

render_space()

render_employee_directory()

render_ticket_board()
