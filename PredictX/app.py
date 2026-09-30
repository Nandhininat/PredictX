import os
import sqlite3
from datetime import date

import pandas as pd
import streamlit as st

from database.database import create_database, DB_NAME
from services.login import show_login
from ml_model.predict import predict_machine

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

st.set_page_config(
    page_title="PredictX",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

create_database()

# ---------------- SESSION ----------------
defaults = {
    "logged_in": False,
    "user_id": None,
    "user_name": "",
    "user_role": "user",
    "page": "Dashboard"
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------------- CSS ----------------
st.markdown("""
<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

.block-container {
    padding-top: 1rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#073b5c 0%,#062c45 100%);
}
[data-testid="stSidebar"] * {
    color: white !important;
}
[data-testid="stSidebar"] .stButton > button {
    border: 1px solid rgba(255,255,255,.10);
    background: rgba(255,255,255,.05);
    color: white !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,.15);
}

.main-title {
    font-size: 32px;
    font-weight: 800;
    color: #12344d;
}
.subtitle {
    color: #718096;
    font-size: 15px;
}
.section-title {
    font-size: 21px;
    font-weight: 750;
    color: #12344d;
    margin-top: 12px;
}
.metric-card {
    background: white;
    padding: 18px;
    border-radius: 15px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 4px 15px rgba(0,0,0,.06);
}
.metric-title {
    color: #718096;
    font-size: 14px;
}
.metric-value {
    color: #12344d;
    font-size: 30px;
    font-weight: 800;
}
.machine-card {
    background: white;
    border: 1px solid #e5e7eb;
    padding: 16px;
    border-radius: 12px;
    margin-bottom: 10px;
}
.topbar {
    background: white;
    padding: 12px 20px;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    margin-bottom: 20px;
}
.login-wrap {
    text-align:center;
    margin-top:70px;
}
.login-logo {
    font-size:44px;
    font-weight:850;
    color:#12344d;
}
.login-subtitle {
    color:#718096;
    margin-bottom:25px;
}
.small-muted {
    color:#718096;
    font-size:13px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- DB HELPERS ----------------
def conn():
    return sqlite3.connect(DB_NAME)

def get_machines():
    c = conn()
    df = pd.read_sql_query(
        "SELECT * FROM machines ORDER BY id", c
    )
    c.close()
    return df

def get_sensor_data():
    c = conn()
    df = pd.read_sql_query(
        "SELECT * FROM sensor_data ORDER BY id DESC", c
    )
    c.close()
    return df

def get_predictions():
    c = conn()
    df = pd.read_sql_query(
        "SELECT * FROM predictions ORDER BY id DESC", c
    )
    c.close()
    return df

def get_maintenance():
    c = conn()
    df = pd.read_sql_query(
        "SELECT * FROM maintenance ORDER BY id DESC", c
    )
    c.close()
    return df

def get_users():
    c = conn()
    df = pd.read_sql_query(
        "SELECT id,name,email,role FROM users ORDER BY id DESC", c
    )
    c.close()
    return df

def save_prediction(machine_id, temperature, vibration, speed, result):
    c = conn()
    c.execute("""
        INSERT INTO sensor_data
        (machine_id,temperature,vibration,speed)
        VALUES (?,?,?,?,?)
    """, (machine_id, temperature, vibration, speed))

    c.execute("""
        INSERT INTO predictions
        (machine_id,health_score,rul,alert,recommendation)
        VALUES (?,?,?,?,?)
    """, (
        machine_id,
        result["health_score"],
        result["rul"],
        result["alert"],
        result["recommendation"]
    ))
    c.commit()
    c.close()

# ---------------- LOGIN ----------------
if not st.session_state.logged_in:
    show_login()
    st.stop()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown(
        "<div style='font-size:28px;font-weight:800;'>🏭 PredictX</div>",
        unsafe_allow_html=True
    )
    st.caption("INTELLIGENT MAINTENANCE")
    st.divider()

    pages = [
        ("📊 Dashboard", "Dashboard"),
        ("📡 Telemetry", "Telemetry"),
        ("🤖 AI Prediction", "AI Prediction"),
        ("📈 History", "History"),
        ("📊 Analytics", "Analytics"),
        ("🔧 Maintenance", "Maintenance"),
        ("🔔 Notifications", "Notifications"),
        ("⚙️ Settings", "Settings")
    ]

    for label, page in pages:
        if st.button(label, use_container_width=True):
            st.session_state.page = page

    if st.session_state.user_role == "admin":
        if st.button("🛠️ Admin", use_container_width=True):
            st.session_state.page = "Admin"

    st.divider()
    st.write(f"👤 **{st.session_state.user_name}**")
    st.caption(f"Role: {st.session_state.user_role}")

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_name = ""
        st.session_state.user_role = "user"
        st.session_state.page = "Dashboard"
        st.rerun()

# ---------------- TOP BAR ----------------
t1, t2, t3 = st.columns([7, 1, 1])
with t1:
    st.markdown(
        "<div class='topbar'>🏭 <b>PredictX</b> "
        "&nbsp;&nbsp; Intelligent Predictive Maintenance</div>",
        unsafe_allow_html=True
    )
with t2:
    st.write("🔔")
with t3:
    st.write("👤")

# ---------------- DASHBOARD ----------------
if st.session_state.page == "Dashboard":
    st.markdown(
        "<div class='main-title'>PredictX Dashboard</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='subtitle'>Live Health Status Overview and Asset Monitoring</div>",
        unsafe_allow_html=True
    )

    machines = get_machines()
    predictions = get_predictions()

    total_assets = len(machines)

    if predictions.empty:
        avg_health = 100
        healthy = warning = critical = 0
    else:
        avg_health = int(predictions["health_score"].mean())
        healthy = int((predictions["alert"] == "Healthy").sum())
        warning = int((predictions["alert"] == "Warning").sum())
        critical = int((predictions["alert"] == "Critical").sum())

    c1,c2,c3,c4 = st.columns(4)
    values = [
        ("🏭 Total Assets", total_assets),
        ("❤️ System Health", f"{avg_health}%"),
        ("⚠️ Warnings", warning),
        ("🚨 Critical", critical)
    ]
    for col, (title, value) in zip([c1,c2,c3,c4], values):
        with col:
            st.markdown(
                f"<div class='metric-card'><div class='metric-title'>{title}</div>"
                f"<div class='metric-value'>{value}</div></div>",
                unsafe_allow_html=True
            )

    st.write("")
    st.markdown(
        "<div class='section-title'>Live Health Status Overview</div>",
        unsafe_allow_html=True
    )
    z1,z2,z3 = st.columns(3)
    with z1:
        st.success(f"🟢 Healthy Zone\n\n{healthy} healthy predictions")
    with z2:
        st.warning(f"🟡 Warning Zone\n\n{warning} warning predictions")
    with z3:
        st.error(f"🔴 Critical Zone\n\n{critical} critical predictions")

    left,right = st.columns([1,2])
    with left:
        st.markdown(
            "<div class='section-title'>Overall Health Score</div>",
            unsafe_allow_html=True
        )
        st.metric("System Health", f"{avg_health}%")
        st.progress(avg_health / 100)
        if avg_health >= 70:
            st.success("System operating normally.")
        elif avg_health >= 40:
            st.warning("System requires attention.")
        else:
            st.error("Immediate maintenance recommended.")

    with right:
        st.markdown(
            "<div class='section-title'>Health Trend</div>",
            unsafe_allow_html=True
        )
        if not predictions.empty:
            st.line_chart(
                predictions[["health_score"]].reset_index(drop=True)
            )
        else:
            st.info("Run an AI prediction to create the trend.")

    st.markdown(
        "<div class='section-title'>🏭 Machine Overview</div>",
        unsafe_allow_html=True
    )
    if machines.empty:
        st.info("No machines available.")
    else:
        st.dataframe(
            machines, use_container_width=True, hide_index=True
        )

# ---------------- TELEMETRY ----------------
elif st.session_state.page == "Telemetry":
    st.markdown(
        "<div class='main-title'>📡 Telemetry Analysis</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='subtitle'>Monitor machine sensor values and upload CSV logs</div>",
        unsafe_allow_html=True
    )

    uploaded = st.file_uploader("📂 Upload Telemetry CSV", type=["csv"])
    if uploaded:
        data = pd.read_csv(uploaded)
        st.success("CSV uploaded successfully!")
        st.dataframe(data, use_container_width=True, hide_index=True)

    st.divider()
    machines = get_machines()

    if machines.empty:
        st.warning("No machines available.")
    else:
        for _, m in machines.iterrows():
            with st.expander(
                f"🏭 {m['machine_id']} — {m['machine_name']} "
                f"({m['location']})"
            ):
                a,b,c = st.columns(3)
                a.metric("Temperature", "— °C")
                b.metric("Vibration", "—")
                c.metric("Speed", "— RPM")
                st.caption(
                    f"Type: {m['machine_type']} | Location: {m['location']}"
                )

# ---------------- AI PREDICTION ----------------
elif st.session_state.page == "AI Prediction":
    st.markdown(
        "<div class='main-title'>🤖 AI / ML Prediction</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='subtitle'>LSTM-based machine health prediction</div>",
        unsafe_allow_html=True
    )

    machines = get_machines()
    if machines.empty:
        st.warning("No machines available.")
    else:
        selected = st.selectbox(
            "🏭 Select Machine",
            machines["machine_id"].tolist()
        )

        c1,c2,c3 = st.columns(3)
        temperature = c1.number_input(
            "🌡 Temperature (°C)", 0.0, 150.0, 60.0, 0.1
        )
        vibration = c2.number_input(
            "📳 Vibration", 0.0, 10.0, 1.5, 0.1
        )
        speed = c3.number_input(
            "⚙ Speed (RPM)", 0.0, 3000.0, 1450.0, 10.0
        )

        if st.button("🤖 Run AI Prediction", use_container_width=True):
            result = predict_machine(
                temperature, vibration, speed
            )
            save_prediction(
                selected, temperature, vibration, speed, result
            )

            st.success("AI prediction completed successfully!")

            r1,r2,r3 = st.columns(3)
            r1.metric("❤️ Health Score", f"{result['health_score']}%")
            r2.metric("⏳ Estimated RUL", f"{result['rul']} hours")
            r3.metric("🚨 Status", result["alert"])

            st.progress(result["health_score"] / 100)

            if result["alert"] == "Healthy":
                st.success("🟢 Machine is Healthy")
            elif result["alert"] == "Warning":
                st.warning("🟡 Machine requires attention")
            else:
                st.error("🔴 Critical condition detected")

            st.info(
                f"🔧 Recommendation: {result['recommendation']}"
            )

            st.markdown(
                "<div class='section-title'>Top Failure Drivers</div>",
                unsafe_allow_html=True
            )
            drivers = pd.DataFrame({
                "Parameter": ["Temperature", "Vibration", "Speed"],
                "Value": [temperature, vibration, speed],
                "Risk Weight": ["40%", "40%", "20%"]
            })
            st.dataframe(
                drivers, use_container_width=True, hide_index=True
            )

            if result["lstm_available"]:
                st.success("LSTM model loaded and forecast generated.")
            else:
                st.info(
                    "LSTM model files are not available yet. "
                    "The interpretable health-risk calculation is being used."
                )

# ---------------- HISTORY ----------------
elif st.session_state.page == "History":
    st.markdown(
        "<div class='main-title'>📈 Prediction & Sensor History</div>",
        unsafe_allow_html=True
    )

    predictions = get_predictions()
    sensors = get_sensor_data()

    st.markdown(
        "<div class='section-title'>🤖 Prediction History</div>",
        unsafe_allow_html=True
    )
    if predictions.empty:
        st.info("No prediction history available.")
    else:
        st.dataframe(
            predictions, use_container_width=True, hide_index=True
        )
        st.line_chart(
            predictions[["health_score"]].reset_index(drop=True)
        )

    st.divider()
    st.markdown(
        "<div class='section-title'>📡 Sensor History</div>",
        unsafe_allow_html=True
    )
    if sensors.empty:
        st.info("No sensor records available.")
    else:
        st.dataframe(
            sensors, use_container_width=True, hide_index=True
        )

# ---------------- ANALYTICS ----------------
elif st.session_state.page == "Analytics":
    st.markdown(
        "<div class='main-title'>📊 Analytics</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='subtitle'>Machine health, risk and sensor analytics</div>",
        unsafe_allow_html=True
    )

    predictions = get_predictions()
    sensors = get_sensor_data()

    if predictions.empty:
        st.info("Run an AI prediction first to generate analytics.")
    else:
        avg = round(predictions["health_score"].mean())
        best = int(predictions["health_score"].max())
        lowest = int(predictions["health_score"].min())

        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Average Health", f"{avg}%")
        c2.metric("Best Health", f"{best}%")
        c3.metric("Lowest Health", f"{lowest}%")
        c4.metric("Total Predictions", len(predictions))

        st.divider()
        st.markdown(
            "<div class='section-title'>❤️ Health Score Trend</div>",
            unsafe_allow_html=True
        )
        st.line_chart(
            predictions[["health_score"]].reset_index(drop=True)
        )

        left,right = st.columns(2)
        with left:
            st.markdown(
                "<div class='section-title'>🚨 Alert Distribution</div>",
                unsafe_allow_html=True
            )
            st.bar_chart(predictions["alert"].value_counts())

        with right:
            st.markdown(
                "<div class='section-title'>⏳ RUL Analysis</div>",
                unsafe_allow_html=True
            )
            st.line_chart(
                predictions[["rul"]].reset_index(drop=True)
            )

        st.divider()
        st.markdown(
            "<div class='section-title'>📡 Sensor Analytics</div>",
            unsafe_allow_html=True
        )
        if not sensors.empty:
            st.line_chart(
                sensors[["temperature","vibration","speed"]]
                .reset_index(drop=True)
            )
            st.dataframe(
                sensors, use_container_width=True, hide_index=True
            )

# ---------------- MAINTENANCE ----------------
elif st.session_state.page == "Maintenance":
    st.markdown(
        "<div class='main-title'>🔧 Maintenance Management</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='subtitle'>Schedule and track machine maintenance activities</div>",
        unsafe_allow_html=True
    )

    machines = get_machines()
    if not machines.empty:
        selected = st.selectbox(
            "Select Machine",
            machines["machine_id"].tolist()
        )
        mtype = st.selectbox(
            "Maintenance Type",
            [
                "Preventive Maintenance",
                "Corrective Maintenance",
                "Inspection",
                "Replacement"
            ]
        )
        description = st.text_area(
            "Maintenance Description",
            placeholder="Example: Check bearings and lubrication"
        )
        mdate = st.date_input("Maintenance Date", date.today())

        if st.button(
            "🔧 Save Maintenance Record",
            use_container_width=True
        ):
            if not description.strip():
                st.warning("Please enter description.")
            else:
                c = conn()
                c.execute("""
                    INSERT INTO maintenance
                    (machine_id,maintenance_type,description,maintenance_date)
                    VALUES (?,?,?,?)
                """, (selected, mtype, description, str(mdate)))
                c.commit()
                c.close()
                st.success("Maintenance record saved!")
                st.rerun()
    else:
        st.warning("No machines available.")

    st.divider()
    history = get_maintenance()
    st.markdown(
        "<div class='section-title'>📋 Maintenance History</div>",
        unsafe_allow_html=True
    )
    if history.empty:
        st.info("No maintenance records available.")
    else:
        st.dataframe(
            history, use_container_width=True, hide_index=True
        )

# ---------------- NOTIFICATIONS ----------------
elif st.session_state.page == "Notifications":
    st.markdown(
        "<div class='main-title'>🔔 Notifications</div>",
        unsafe_allow_html=True
    )
    predictions = get_predictions()

    if predictions.empty:
        st.success("No alerts. System is waiting for predictions.")
    else:
        critical = predictions[predictions["alert"] == "Critical"]
        warning = predictions[predictions["alert"] == "Warning"]
        healthy = predictions[predictions["alert"] == "Healthy"]

        if not critical.empty:
            for _, row in critical.head(10).iterrows():
                st.error(
                    f"🚨 {row['machine_id']} — Critical | "
                    f"Health {row['health_score']}%"
                )

        if not warning.empty:
            for _, row in warning.head(10).iterrows():
                st.warning(
                    f"⚠️ {row['machine_id']} — Warning | "
                    f"Health {row['health_score']}%"
                )

        if critical.empty and warning.empty:
            st.success(
                f"✅ All recorded predictions are healthy "
                f"({len(healthy)} records)."
            )

# ---------------- SETTINGS ----------------
elif st.session_state.page == "Settings":
    st.markdown(
        "<div class='main-title'>⚙️ Settings</div>",
        unsafe_allow_html=True
    )

    st.subheader("👤 Profile")
    st.write(f"Name: **{st.session_state.user_name}**")
    st.write(f"Role: **{st.session_state.user_role}**")

    st.subheader("📊 System")
    st.info(
        "PredictX uses SQLite for storage, Streamlit for the dashboard, "
        "and an LSTM demonstration model for sensor forecasting."
    )

    st.subheader("🔄 Reset Session")
    if st.button("Reset Page to Dashboard"):
        st.session_state.page = "Dashboard"
        st.rerun()

# ---------------- ADMIN ----------------
elif st.session_state.page == "Admin":
    if st.session_state.user_role != "admin":
        st.error("Admin access required.")
        st.stop()

    st.markdown(
        "<div class='main-title'>🛠️ Admin Dashboard</div>",
        unsafe_allow_html=True
    )

    machines = get_machines()
    users = get_users()
    predictions = get_predictions()
    maintenance = get_maintenance()

    a1,a2,a3,a4 = st.columns(4)
    a1.metric("👥 Users", len(users))
    a2.metric("🏭 Machines", len(machines))
    a3.metric("🤖 Predictions", len(predictions))
    a4.metric("🔧 Maintenance", len(maintenance))

    st.divider()
    st.markdown(
        "<div class='section-title'>➕ Add New Machine</div>",
        unsafe_allow_html=True
    )

    c1,c2 = st.columns(2)
    machine_id = c1.text_input("Machine ID", placeholder="M006")
    machine_name = c1.text_input("Machine Name", placeholder="Motor 6")
    machine_type = c2.text_input(
        "Machine Type", placeholder="Electric Motor"
    )
    location = c2.text_input("Location", placeholder="Plant A")

    if st.button("➕ Add Machine", use_container_width=True):
        if not all([
            machine_id.strip(),
            machine_name.strip(),
            machine_type.strip(),
            location.strip()
        ]):
            st.warning("Please fill all fields.")
        else:
            c = conn()
            try:
                c.execute("""
                    INSERT INTO machines
                    (machine_id,machine_name,machine_type,location)
                    VALUES (?,?,?,?)
                """, (
                    machine_id.strip(),
                    machine_name.strip(),
                    machine_type.strip(),
                    location.strip()
                ))
                c.commit()
                st.success("Machine added successfully!")
                st.rerun()
            except sqlite3.IntegrityError:
                st.error("Machine ID already exists.")
            finally:
                c.close()

    st.divider()
    st.markdown(
        "<div class='section-title'>🏭 Machine Management</div>",
        unsafe_allow_html=True
    )
    machines = get_machines()
    st.dataframe(
        machines, use_container_width=True, hide_index=True
    )

    if not machines.empty:
        delete_id = st.selectbox(
            "Select Machine to Delete",
            machines["machine_id"].tolist()
        )
        if st.button("🗑️ Delete Machine"):
            c = conn()
            c.execute(
                "DELETE FROM machines WHERE machine_id=?",
                (delete_id,)
            )
            c.commit()
            c.close()
            st.success("Machine deleted.")
            st.rerun()

    st.divider()
    st.markdown(
        "<div class='section-title'>👥 Registered Users</div>",
        unsafe_allow_html=True
    )
    st.dataframe(
        users, use_container_width=True, hide_index=True
    )

    st.divider()
    st.markdown(
        "<div class='section-title'>📄 PDF Summary Report</div>",
        unsafe_allow_html=True
    )

    if not predictions.empty:
        report_machine = st.selectbox(
            "Select Machine for Report",
            predictions["machine_id"].unique(),
            key="report_machine"
        )

        if st.button("📄 Generate PDF Report", use_container_width=True):
            rows = predictions[
                predictions["machine_id"] == report_machine
            ]
            latest = rows.iloc[0]

            os.makedirs("reports", exist_ok=True)
            path = os.path.join(
                "reports", f"{report_machine}_report.pdf"
            )

            pdf = canvas.Canvas(path, pagesize=A4)
            pdf.setFont("Helvetica-Bold", 22)
            pdf.drawString(180, 800, "PredictX Machine Health Report")

            pdf.setFont("Helvetica", 12)
            y = 750
            lines = [
                f"Machine ID: {report_machine}",
                f"Health Score: {latest['health_score']}%",
                f"Estimated RUL: {latest['rul']} hours",
                f"Alert Status: {latest['alert']}",
                f"Prediction Time: {latest['predicted_at']}",
                "",
                "Recommendation:",
                str(latest.get("recommendation", "Monitor machine regularly."))
            ]

            for line in lines:
                pdf.drawString(60, y, line)
                y -= 28

            pdf.drawString(
                60, 500,
                "PredictX - Intelligent Predictive Maintenance"
            )
            pdf.drawString(
                60, 480,
                "& Asset Health Monitoring"
            )
            pdf.save()

            with open(path, "rb") as f:
                st.download_button(
                    "⬇️ Download PDF",
                    f,
                    file_name=os.path.basename(path),
                    mime="application/pdf"
                )
    else:
        st.info("Run at least one prediction before generating a report.")

st.divider()
st.caption(
    "PredictX © 2026 | Intelligent Predictive Maintenance "
    "& Asset Health Monitoring"
)
