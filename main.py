import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy as np
import plotly.express as px
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.add_vertical_space import add_vertical_space
from auth_helper import login_user
from cost_forecasting import forecast_cost

# --- Neon-glow and glassmorphism styling ---
st.markdown(
    """<style>
    html, body, [class*="css"]  {
        background-color: #0f0f0f;
        color: #ffffff;
    }
    .main {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 4px 30px rgba(0, 255, 255, 0.2);
        backdrop-filter: blur(5px);
        border: 1px solid rgba(0, 255, 255, 0.3);
    }
    .st-emotion-cache-1avcm0n {
        background-color: transparent;
    }
    .stMetricValue {
        color: #00f7ff !important;
        font-weight: bold;
    }
    /* Make the container use full width */
    .block-container {
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True
)


if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("## 🔐 Login")
    email = st.text_input("Enter your email").strip().lower()
    if st.button("Login"):
        if login_user(email):
            st.session_state.authenticated = True
            st.session_state.email = email
            st.success("✅ Login successful")
            st.rerun()
        else:
            st.error("❌ Access Denied. Email not authorized.")
    st.stop()


conn = st.connection("gsheets", type=GSheetsConnection)

df = conn.read(worksheet="Leads")
df = df.dropna(how = "all")



# --- Sidebar Navigation ---
with st.sidebar:
    st.markdown("""
        <h2 style='color:#00f7ff;'>⚡ Lead Analysis </h2>
        <hr style='border-top: 1px solid #00f7ff;'>
    """, unsafe_allow_html=True)
    page = st.radio("Navigate", [
        "Performance Dashboard", "Lead Quality","Conversion Analysis",
         "Cost Analysis","Lead Overview", "Duplicate Leads"
    ])

# --- Lead Overview Page ---
if page == "Performance Dashboard":
    

    df["Cost"] = pd.to_numeric(df["Cost"], errors="coerce")
    df["Converted Count"] = pd.to_numeric(df["Converted Count"], errors="coerce")
    df["Appointments Completed"] = pd.to_numeric(df["Appointments Completed"], errors="coerce")
    df["Number of Outbound Calls"] = pd.to_numeric(df["Number of Outbound Calls"], errors="coerce")

    def format_currency(value):
        if value >= 1_000_000:
            return f"${value / 1_000_000:.2f}M"
        elif value >= 1_000:
            return f"${value / 1_000:.2f}K"
        else:
            return f"${value:.2f}"


    total_leads = len(df)
    outbound_calls = df["Number of Outbound Calls"].sum()
    converted = df["Converted Count"].sum()
    cost = df["Cost"].sum()
    formatted_cost = format_currency(cost)
    cpl = round(cost / total_leads, 2)
    cpa = round(cost / converted, 2) if converted > 0 else 0

    style_metric_cards(border_left_color="#82f7b0")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Total Leads", total_leads)
    col2.metric("Outbound Calls", outbound_calls)
    col3.metric("Converted", converted)
    col4.metric("Total Cost", formatted_cost)
    col5.metric("CPA", f"${cpa:,.2f}")
    col6.metric("CPL", f"${cpl:,.2f}")

    st.markdown("""
        <h3 style='color:#ffffff;'>📊 Breakdown by Source</h3>
    """, unsafe_allow_html=True)

    # Styles
    st.markdown("""
        <style>
        .custom-card {
            border-radius: 10px;
            padding: 1.2rem;
            background-color: #ffffff;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
            border-left: 5px solid #82f7b0;
            margin-bottom: 1rem;
        }

        .custom-title {
            font-size: 1.2rem;
            font-weight: 700;
            margin-bottom: 0.6rem;
            color: #222;
        }

        .custom-metrics {
            font-size: 1rem;
            color: #333;
            line-height: 1.6;
            font-weight: 500;
        }

        .custom-metrics span {
            display: inline-block;
            margin-right: 1.5rem;
        }
        </style>
    """, unsafe_allow_html=True)

    grouped = df.groupby("Lead Source").agg({
        "Lead ID": "count",
        "Converted Count": "sum",
        "Number of Outbound Calls": "sum",
        "Cost": "sum"
    }).reset_index()

    grouped["CPL"] = round(grouped["Cost"] / grouped["Lead ID"], 2)
    grouped["CPA"] = round(grouped["Cost"] / grouped["Converted Count"].replace(0, np.nan), 2)

    rows = grouped.reset_index(drop=True)

    for i in range(0, len(rows), 2):
        col1, col2 = st.columns(2)

        # Card 1
        with col1:
            row = rows.iloc[i]
            st.markdown(f"""
                <div class="custom-card">
                    <div class="custom-title">{row['Lead Source']}</div>
                    <div class="custom-metrics">
                        <span>Leads: <strong>{int(row['Lead ID'])}</strong></span>
                        <span>Converted: <strong>{int(row['Converted Count'])}</strong></span>
                        <span>Calls: <strong>{int(row['Number of Outbound Calls'])}</strong></span>
                    </div>
                    <div class="custom-metrics">
                        <span>Cost: <strong>${row['Cost']:.2f}</strong></span>
                        <span>CPA: <strong>${row['CPA'] if not np.isnan(row['CPA']) else 0:.2f}</strong></span>
                        <span>CPL: <strong>${row['CPL']:.2f}</strong></span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # Card 2 if available
        if i + 1 < len(rows):
            with col2:
                row = rows.iloc[i + 1]
                st.markdown(f"""
                    <div class="custom-card">
                        <div class="custom-title">{row['Lead Source']}</div>
                        <div class="custom-metrics">
                            <span>Leads: <strong>{int(row['Lead ID'])}</strong></span>
                            <span>Converted: <strong>{int(row['Converted Count'])}</strong></span>
                            <span>Calls: <strong>{int(row['Number of Outbound Calls'])}</strong></span>
                        </div>
                        <div class="custom-metrics">
                            <span>Cost: <strong>${row['Cost']:.2f}</strong></span>
                            <span>CPA: <strong>${row['CPA'] if not np.isnan(row['CPA']) else 0:.2f}</strong></span>
                            <span>CPL: <strong>${row['CPL']:.2f}</strong></span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)


# --- Lead Quality Page ---
elif page == "Lead Quality":
    st.title("📈 Lead Quality Dashboard")

    total_leads = len(df)
    duplicate_count = df.duplicated(subset=["First Name", "Zip Code"], keep=False).sum()
    lead_source_counts = df["Lead Source"].value_counts()
    leads_by_state = df["State"].value_counts()

    style_metric_cards(border_left_color="#00f7ff", border_radius_px=10)
    #st.metric("Total Leads", total_leads)
    #st.metric("Duplicate Leads", duplicate_count)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Leads", total_leads)
        fig1 = px.pie(names=lead_source_counts.index, values=lead_source_counts.values,
                      title="Lead Source Distribution", color_discrete_sequence=px.colors.sequential.Teal)
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.metric("Duplicate Leads", duplicate_count)
        fig2 = px.bar(x=leads_by_state.index, y=leads_by_state.values,
                      title="Leads by State", color=leads_by_state.values,
                      color_continuous_scale="Teal")
        st.plotly_chart(fig2, use_container_width=True)


# --- Conversion Analysis Page ---
elif page == "Conversion Analysis":
    st.title("🔄 Conversion Analysis")

    # Date conversions
    df["Created Date"] = pd.to_datetime(df["Created Date"], errors="coerce")
    df["Approval Date"] = pd.to_datetime(df["Approval Date"], errors="coerce")

    # Basic Metrics
    total_leads = len(df)
    converted_leads = df["Converted Count"].sum()
    conversion_rate = round((converted_leads / total_leads) * 100, 2) if total_leads > 0 else 0
    avg_days = round((df[df["Converted Count"] == 1]["Approval Date"] - df["Created Date"]).dt.days.mean(), 2)

    # --- New Metrics ---
    # 1. Lead to Set: Percent Completed in Calling
    lead_to_set = round((converted_leads / total_leads) * 100, 2) if total_leads > 0 else 0

    # 2. Set to Sit: Percent Completed in Appointment
    appointments_completed = df["Appointments Completed"].sum()
    set_to_sit = round((appointments_completed / converted_leads) * 100, 2) if converted_leads > 0 else 0

    # 3. Sit to Close-Won: Percent Completed in Closing
    closed_won_count = df[df["Stage"].str.lower() == "closed-won"]["Appointments Completed"].count()
    sit_to_close = round((closed_won_count / appointments_completed) * 100, 2) if appointments_completed > 0 else 0

    # 4. Net Pull Through: Leads that actually became paying customers
    net_pull_through = round((closed_won_count / total_leads) * 100, 2) if total_leads > 0 else 0

    # Optional: You can style your metrics here
    style_metric_cards(border_left_color="#fa5bff")


    # Display Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Conversion Rate (%)", conversion_rate)
    with col2:
        st.metric("Avg Days to Convert", avg_days)
    with col3:
        st.metric("Lead to Set (%)", lead_to_set)

    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric("Set to Sit (%)", set_to_sit)
    with col5:
        st.metric("Sit to Close-Won (%)", sit_to_close)
    with col6:
        st.metric("Net Pull Through (%)", net_pull_through)

    # --- Net Pull Through State-wise ---
    state_group = df.groupby("State").agg(
        total_leads=("Lead ID", "count"),
        closed_won=("Stage", lambda x: (x.str.lower() == "closed-won").sum())
    ).reset_index()
    state_group["net_pull_through"] = round((state_group["closed_won"] / state_group["total_leads"]) * 100, 2)

    fig_state = px.bar(
        state_group,
        x="State",
        y="net_pull_through",
        color="net_pull_through",
        color_continuous_scale="Viridis",
        title="📊 Net Pull Through by State (%)",
        labels={"net_pull_through": "Net Pull Through (%)"}
    )
    

    # --- Net Pull Through Lead Source-wise ---
    source_group = df.groupby("Lead Source").agg(
        total_leads=("Lead ID", "count"),
        closed_won=("Stage", lambda x: (x.str.lower() == "closed-won").sum())
    ).reset_index()
    source_group["net_pull_through"] = round((source_group["closed_won"] / source_group["total_leads"]) * 100, 2)

    fig_source = px.bar(
        source_group,
        x="Lead Source",
        y="net_pull_through",
        color="net_pull_through",
        color_continuous_scale="Plasma",
        title="📊 Net Pull Through by Lead Source (%)",
        labels={"net_pull_through": "Net Pull Through (%)"}
    )
    
    st.markdown("### 📈 Net Pull Through Breakdown")
    
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.plotly_chart(fig_state, use_container_width=True)
    with chart_col2:
        st.plotly_chart(fig_source, use_container_width=True)




# --- Cost Analysis Page ---
elif page == "Cost Analysis":
    st.title("💸 Cost Breakdown")

    df["Cost"] = pd.to_numeric(df["Cost"], errors="coerce")
    df["Converted Count"] = pd.to_numeric(df["Converted Count"], errors="coerce")
    total_cost = df["Cost"].sum()
    total_leads = len(df)
    total_converted = df["Converted Count"].sum()

    cpl = round(total_cost / total_leads, 2)
    cpa = round(total_cost / total_converted, 2) if total_converted else 0

    style_metric_cards(border_left_color="#ffb74d")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Cost", total_cost)
    col2.metric("CPL", cpl)
    col3.metric("CPA", cpa)

    st.subheader("📍 Cost by State (Map)")
    geo_df = df.groupby("State").agg({"Cost": "sum"}).reset_index()
    fig_map = px.choropleth(geo_df, locationmode="USA-states", locations="State",
                            color="Cost", scope="usa", color_continuous_scale="Plasma")
    st.plotly_chart(fig_map, use_container_width=True)


# --- Lead Overview ---
elif page == "Lead Overview":
    st.title("🔍 Lead Overview")
    st.dataframe(df)


# --- Duplicate Leads Page ---
elif page == "Duplicate Leads":
    st.title("🧬 Duplicate Leads")
    duplicates = df[df.duplicated(subset=["State", "Zip Code", "First Name"], keep=False)]
    st.dataframe(duplicates)

# Add a footer
add_vertical_space(3)
st.markdown(
    "<p style='text-align:center;color:#444;font-size:13px;'>Made with 💙 by Naman • LMS Dashboard v2.0</p>",
    unsafe_allow_html=True
)
