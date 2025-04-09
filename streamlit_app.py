import streamlit as st
import pandas as pd
import plotly.express as px
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.set_page_config(page_title="Fund Misuse Detection", layout="wide")

# -------------------- THEME TOGGLE -------------------- #
dark_mode = st.sidebar.toggle("🌙 Enable Dark Mode", value=False)
if dark_mode:
    st.markdown("""
        <style>
        body { background-color: #0e1117; color: white; }
        .stSlider > div { color: white; }
        .css-1aumxhk, .css-1v0mbdj, .st-bw { background-color: #1e1e1e !important; }
        .stDataFrame { background-color: #262730 !important; }
        </style>
    """, unsafe_allow_html=True)

# -------------------- FILE UPLOADER -------------------- #
st.sidebar.header("📁 Upload your CSV")
uploaded_file = st.sidebar.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        df.dropna(inplace=True)
    except Exception as e:
        st.error(f"❌ Failed to read uploaded file: {e}")
        st.stop()

    # -------------------- SIDEBAR OPTIONS -------------------- #
    st.sidebar.header("📊 Select numeric columns")
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    selected_columns = st.sidebar.multiselect("Select numeric columns", numeric_columns, default=numeric_columns)

    sensitivity = st.sidebar.slider("📉 Sensitivity", 0.01, 1.0, 0.5)

    # -------------------- ANOMALY DETECTION -------------------- #
    def detect_anomalies(df, sensitivity):
        df['AnomalyScore'] = abs(df[selected_columns] - df[selected_columns].mean()).sum(axis=1)
        threshold = df['AnomalyScore'].quantile(1 - sensitivity)
        anomalies = df[df['AnomalyScore'] > threshold]
        return anomalies

    anomalies = detect_anomalies(df, sensitivity)

    # -------------------- EMAIL FUNCTION -------------------- #
    def send_email_alert(receiver_email, anomaly_count):
        sender_email = "your_email@gmail.com"
        password = "your_app_password"  # Use app password or ENV variable

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "🚨 Fund Misuse Alert"
        msg["From"] = sender_email
        msg["To"] = receiver_email

        html = f"""
        <html><body>
            <h3>⚠️ Alert: {anomaly_count} anomalies detected in fund usage data.</h3>
            <p>Please review your dashboard immediately.</p>
        </body></html>
        """
        msg.attach(MIMEText(html, "html"))

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            server.quit()
            st.success("📤 Email alert sent successfully!")
        except Exception as e:
            st.error(f"Failed to send email: {e}")

    # -------------------- MAIN UI -------------------- #
    st.title("📈 Fund Misuse Detection Dashboard")
    st.markdown("An AI-driven tool to identify anomalies in fund allocation and utilization.")

    st.subheader("🔍 Anomaly Detection Table")
    st.dataframe(anomalies, use_container_width=True)

    # -------------------- PLOTS -------------------- #
    if 'Department' in df.columns:
        dept_count = anomalies['Department'].value_counts().reset_index()
        dept_count.columns = ['Department', 'Count']
        fig = px.bar(
            dept_count,
            x='Department',
            y='Count',
            title="Anomalies by Department",
            color='Count',
            color_continuous_scale='reds' if not dark_mode else 'reds_r',
        )
        st.plotly_chart(fig, use_container_width=True)

    # -------------------- EMAIL FORM -------------------- #
    st.subheader("📧 Send Email Alert")
    receiver_email = st.text_input("Recipient Email")
    if st.button("Send Alert"):
        if receiver_email:
            send_email_alert(receiver_email, anomalies.shape[0])
        else:
            st.warning("Please enter a recipient email.")

else:
    st.warning("📂 Please upload a CSV file to proceed.")
