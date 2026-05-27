import streamlit as st
import pandas as pd
import plotly.express as px

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="APL Logistics Dashboard",
    page_icon="🚛",
    layout="wide"
)

# ====================== LOAD DATA ======================
@st.cache_data
def load_data():
    df = pd.read_csv("sample_logistics.csv", encoding="latin1")
    # Calculate Delay Gap if not present
    if 'Delay Gap' not in df.columns:
        df['Delay Gap'] = df['Days for shipping (real)'] - df['Days for shipment (scheduled)']
    return df

df = load_data()

# ====================== SIDEBAR FILTERS ======================
st.sidebar.header("🔍 Filters")

market_filter = st.sidebar.multiselect("Market", options=sorted(df['Market'].unique()), default=df['Market'].unique())
region_filter = st.sidebar.multiselect("Order Region", options=sorted(df['Order Region'].unique()), default=df['Order Region'].unique())
shipping_filter = st.sidebar.multiselect("Shipping Mode", options=sorted(df['Shipping Mode'].unique()), default=df['Shipping Mode'].unique())
segment_filter = st.sidebar.multiselect("Customer Segment", options=sorted(df['Customer Segment'].unique()), default=df['Customer Segment'].unique())

# Apply filters
filtered_df = df[
    df['Market'].isin(market_filter) &
    df['Order Region'].isin(region_filter) &
    df['Shipping Mode'].isin(shipping_filter) &
    df['Customer Segment'].isin(segment_filter)
]

# ====================== HEADER ======================
st.title("🚛 APL Logistics - Supply Chain Analytics Dashboard")
st.markdown("### Delivery Performance | Risk Analysis | Regional Insights")

# ====================== KPI ROW ======================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Orders", f"{len(filtered_df):,}")

with col2:
    on_time_rate = (len(filtered_df[filtered_df['Delay Gap'] <= 0]) / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
    st.metric("On-Time Delivery Rate", f"{on_time_rate:.1f}%")

with col3:
    avg_delay = filtered_df['Delay Gap'].mean()
    st.metric("Avg Delay", f"{avg_delay:.2f} days")

with col4:
    late_risk = filtered_df['Late_delivery_risk'].mean() * 100
    st.metric("Late Delivery Risk", f"{late_risk:.1f}%")

st.divider()

# ====================== TABS ======================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Delivery Overview", 
    "⚠️ Delay Risk Analysis", 
    "🚚 Shipping Modes", 
    "🌍 Regional & Market"
])

with tab1:
    st.subheader("Delivery Performance Overview")
    col_a, col_b = st.columns(2)
    
    with col_a:
        fig = px.pie(filtered_df, names='Delivery Performance', title="On-Time vs Delayed")
        st.plotly_chart(fig, use_container_width=True)
    
    with col_b:
        fig = px.histogram(filtered_df, x='Delay Gap', nbins=30, title="Delay Gap Distribution")
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Late Delivery Risk Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            x=['No Risk', 'High Risk'],
            y=filtered_df['Late_delivery_risk'].value_counts().values,
            color=['green', 'red'],
            title="Late Delivery Risk Count"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.box(filtered_df, x='Delivery Performance', y='Delay Gap', title="Delay by Performance")
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Shipping Mode Comparison")
    col1, col2 = st.columns(2)
    
    mode_delay = filtered_df.groupby('Shipping Mode')['Delay Gap'].mean().reset_index()
    mode_risk = filtered_df.groupby('Shipping Mode')['Late_delivery_risk'].mean().reset_index()
    
    with col1:
        fig = px.bar(mode_delay, x='Shipping Mode', y='Delay Gap', title="Avg Delay by Shipping Mode", color='Delay Gap')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(mode_risk, x='Shipping Mode', y='Late_delivery_risk', title="Late Risk % by Shipping Mode")
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("Regional & Market Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        region_delay = filtered_df.groupby('Order Region')['Delay Gap'].mean().nlargest(10).reset_index()
        fig = px.bar(region_delay, x='Order Region', y='Delay Gap', title="Top 10 Regions by Delay")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        market_risk = filtered_df.groupby('Market')['Late_delivery_risk'].mean().reset_index()
        fig = px.bar(market_risk, x='Market', y='Late_delivery_risk', title="Late Risk by Market")
        st.plotly_chart(fig, use_container_width=True)

st.caption("Supply Chain Analytics Dashboard | Powered by Streamlit")
