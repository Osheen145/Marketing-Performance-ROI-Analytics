"""
app.py
Enterprise Marketing Performance & Capital Allocation Analytics
Executive Streamlit Dashboard (1-Page Executive View)

Run with: streamlit run dashboard/app.py
"""

import os
import sqlite3
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Marketing Performance & ROI Analytics | Executive Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling for C-Suite Executive Elegance
st.markdown("""
<style>
    .main-header {
        font-size: 26px;
        font-weight: 800;
        color: #1a202c;
        margin-bottom: 2px;
    }
    .sub-header {
        font-size: 14px;
        color: #4a5568;
        margin-bottom: 20px;
    }
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-label {
        font-size: 12px;
        font-weight: 600;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #2b6cb0;
        margin-top: 4px;
    }
    .metric-sub {
        font-size: 11px;
        color: #a0aec0;
        margin-top: 2px;
    }
    .decision-banner {
        background-color: #ebf8ff;
        border-left: 4px solid #3182ce;
        padding: 14px 18px;
        border-radius: 4px;
        margin-bottom: 24px;
    }
</style>
""", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "marketing_analytics.db")
CLEANED_DIR = os.path.join(BASE_DIR, "data", "cleaned")

@st.cache_data
def load_dashboard_data():
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Funnel Performance
    funnel_df = pd.read_sql_query("""
        SELECT 
            channel,
            channel_type,
            strategic_intent,
            SUM(impressions) as impressions,
            SUM(clicks) as clicks,
            SUM(spend_inr) as spend,
            SUM(leads) as leads,
            SUM(direct_conversions) as conversions,
            SUM(direct_revenue_inr) as direct_revenue
        FROM fact_daily_campaign_performance
        GROUP BY channel
    """, conn)
    
    # 2. Orders & Margins
    orders_df = pd.read_sql_query("""
        SELECT 
            acquisition_channel_last as channel,
            SUM(order_value_net) as net_revenue,
            SUM(cogs_inr) as cogs,
            SUM(gross_profit_inr) as gross_profit
        FROM fact_orders
        GROUP BY acquisition_channel_last
    """, conn)

    # 3. Customer LTV & CAC
    ltv_df = pd.read_sql_query("""
        SELECT 
            acquisition_channel_first as channel,
            COUNT(user_id) as customers,
            AVG(lifetime_revenue_inr) as avg_ltv_rev,
            AVG(lifetime_gross_profit_inr) as avg_ltv_profit
        FROM fact_customer_ltv
        GROUP BY acquisition_channel_first
    """, conn)
    
    conn.close()
    
    mta_df = pd.read_csv(os.path.join(CLEANED_DIR, "mta_model_comparison.csv"))
    rec_df = pd.read_csv(os.path.join(CLEANED_DIR, "budget_optimization_recommendation.csv"))
    
    return funnel_df, orders_df, ltv_df, mta_df, rec_df

funnel_df, orders_df, ltv_df, mta_df, rec_df = load_dashboard_data()

# -------------------------------------------------------------
# Header & Business Problem
# -------------------------------------------------------------
st.markdown('<div class="main-header">Growth & Financial Analytics: Marketing Performance & ROI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Executive Decision Console · Executive Decision Console · Osheen Dongre</div>', unsafe_allow_html=True)

st.markdown("""
<div class="decision-banner">
    <strong>Core Business Problem:</strong> <em>"The company spends ₹6.13 Crore across 8 channels. Which channels generate profitable customers — not just cheap clicks?"</em><br>
    <strong>The Keystone Question:</strong> <em>"If I give you another ₹10 lakh next month, where should you spend it — and what do you expect to get back?"</em>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# Top KPI Metric Cards (5-7 deliberate KPIs)
# -------------------------------------------------------------
total_spend = funnel_df['spend'].sum()
total_direct_rev = funnel_df['direct_revenue'].sum()
total_orders_rev = orders_df['net_revenue'].sum()
total_gross_profit = orders_df['gross_profit'].sum()
total_customers = ltv_df['customers'].sum()

blended_cac = total_spend / total_customers
blended_roas = total_orders_rev / total_spend
blended_ltv_cac = (total_gross_profit / total_customers) / blended_cac
net_profit_contribution = total_gross_profit - total_spend

kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)

with kpi1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Annual Spend</div>
        <div class="metric-value">₹{total_spend/1e7:.2f} Cr</div>
        <div class="metric-sub">8 Active Channels</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Net Revenue</div>
        <div class="metric-value">₹{total_orders_rev/1e7:.2f} Cr</div>
        <div class="metric-sub">Attributed Net GMV</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Blended ROAS</div>
        <div class="metric-value">{blended_roas:.2f}x</div>
        <div class="metric-sub">Net Revenue / Spend</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Blended CAC</div>
        <div class="metric-value">₹{blended_cac:,.0f}</div>
        <div class="metric-sub">{total_customers:,} Acquired Users</div>
    </div>
    """, unsafe_allow_html=True)

with kpi5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">LTV : CAC</div>
        <div class="metric-value">{blended_ltv_cac:.2f}x</div>
        <div class="metric-sub">12-Month Margin Ratio</div>
    </div>
    """, unsafe_allow_html=True)

with kpi6:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Net Profit Contribution</div>
        <div class="metric-value">₹{net_profit_contribution/1e7:.2f} Cr</div>
        <div class="metric-sub">Gross Margin - Ad Spend</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------------------
# Row 1: Channel Efficiency Matrix & Attribution Comparison
# -------------------------------------------------------------
col_left, col_right = st.columns([1.1, 1])

with col_left:
    st.subheader("1. Channel Efficiency Matrix (ROAS vs CAC)")
    # Merge funnel with LTV
    perf_merge = funnel_df.merge(ltv_df, on='channel', how='left')
    perf_merge['cac'] = round(perf_merge['spend'] / perf_merge['customers'], 2)
    perf_merge['roas'] = round(perf_merge['direct_revenue'] / perf_merge['spend'], 2)
    
    fig_matrix = px.scatter(
        perf_merge,
        x='cac',
        y='roas',
        size='spend',
        color='strategic_intent',
        text='channel',
        hover_name='channel',
        labels={'cac': 'Customer Acquisition Cost (INR)', 'roas': 'Direct ROAS (x)', 'spend': 'Spend (INR)'},
        height=380
    )
    fig_matrix.add_hline(y=3.0, line_dash="dash", line_color="green", annotation_text="Healthy ROAS Threshold (3.0x)")
    fig_matrix.add_vline(x=3500, line_dash="dash", line_color="orange", annotation_text="CAC Guardrail (₹3,500)")
    fig_matrix.update_traces(textposition='top center')
    fig_matrix.update_layout(margin=dict(l=20, r=20, t=30, b=20), legend=dict(orientation="h", y=-0.25))
    st.plotly_chart(fig_matrix, use_container_width=True)

with col_right:
    st.subheader("2. Multi-Touch Attribution: Exposing the Last-Touch Trap")
    attr_model = st.selectbox(
        "Select Attribution Lens to Compare against Last-Touch:",
        options=["First-Touch (Top-of-Funnel)", "Linear (Equitable Journey)", "Position-Based (40-20-40)"],
        index=0
    )
    
    comp_col = 'first_touch' if "First" in attr_model else ('linear' if "Linear" in attr_model else 'position_based')
    
    fig_mta = go.Figure()
    fig_mta.add_trace(go.Bar(
        x=mta_df['channel'],
        y=mta_df['last_touch'] / 1e5,
        name='Last-Touch Revenue',
        marker_color='#e74c3c'
    ))
    fig_mta.add_trace(go.Bar(
        x=mta_df['channel'],
        y=mta_df[comp_col] / 1e5,
        name=f'{attr_model} Revenue',
        marker_color='#2b6cb0'
    ))
    fig_mta.update_layout(
        barmode='group',
        yaxis_title="Attributed Revenue (Lakh INR)",
        height=380,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", y=-0.25)
    )
    st.plotly_chart(fig_mta, use_container_width=True)

# -------------------------------------------------------------
# Row 2: The Keystone ₹10 Lakh Budget Reallocation Simulator
# -------------------------------------------------------------
st.markdown("---")
st.subheader("3. Executive Decision Simulator: Allocating the Incremental ₹10 Lakh")
st.caption("Compare your custom allocation against the Algorithmic Marginal ROAS Recommendation in real-time.")

sim_col1, sim_col2 = st.columns([1.2, 1])

with sim_col1:
    st.markdown("**Simulate Your Monthly Budget Distribution:**")
    user_alloc = {}
    
    c1, c2 = st.columns(2)
    with c1:
        user_alloc['Meta_Ads_Retargeting'] = st.slider("Meta Retargeting (₹)", 0, 500000, 350000, 25000)
        user_alloc['Affiliate_Partner_Network'] = st.slider("Affiliate Network (₹)", 0, 400000, 300000, 25000)
        user_alloc['Meta_Ads_Prospecting'] = st.slider("Meta Prospecting (₹)", 0, 300000, 150000, 25000)
        user_alloc['LinkedIn_Sponsored'] = st.slider("LinkedIn B2B (₹)", 0, 300000, 150000, 25000)
    with c2:
        user_alloc['Email_CRM_Automation'] = st.slider("Email Automations (₹)", 0, 100000, 50000, 10000)
        user_alloc['Google_Search_Brand'] = st.slider("Google Search Brand (₹)", 0, 300000, 0, 25000)
        user_alloc['Google_Search_Generic'] = st.slider("Google Generic Search (₹)", 0, 300000, 0, 25000)
        user_alloc['YouTube_Video_Ads'] = st.slider("YouTube Video Ads (₹)", 0, 300000, 0, 25000)

    total_sim_spend = sum(user_alloc.values())
    if total_sim_spend == 1000000:
        st.success(f"Budget Fully Allocated: Exactly ₹{total_sim_spend:,.0f} (₹10 Lakh)")
    else:
        st.warning(f"Current Total: ₹{total_sim_spend:,.0f} / ₹10,00,000 (Variance: ₹{1000000 - total_sim_spend:,.0f})")

with sim_col2:
    st.markdown("**Projected Financial Returns (Your Plan vs Algorithm):**")
    
    # Calculate user projected return
    mroas_map = dict(zip(rec_df['Channel'], rec_df['Expected_Marginal_ROAS']))
    user_inc_rev = sum([user_alloc[ch] * mroas_map.get(ch, 2.0) for ch in user_alloc])
    user_inc_profit = (user_inc_rev * 0.52) - total_sim_spend
    
    algo_rev = rec_df['Expected_Incremental_Revenue_INR'].sum()
    algo_profit = rec_df['Expected_Incremental_Profit_INR'].sum()
    
    res_df = pd.DataFrame({
        "Metric": ["Incremental Spend", "Projected Incremental Revenue", "Projected Net Profit", "Blended Marginal ROAS"],
        "Your Allocation": [f"₹{total_sim_spend:,.0f}", f"₹{user_inc_rev:,.0f}", f"₹{user_inc_profit:,.0f}", f"{user_inc_rev/max(1, total_sim_spend):.2f}x"],
        "Algorithmic Optimal": ["₹10,00,000", f"₹{algo_rev:,.0f}", f"₹{algo_profit:,.0f}", f"{algo_rev/1000000:.2f}x"]
    })
    st.table(res_df)
    
    st.info("""
    **Analyst Takeaway:**
    Pouring money into Google Search Brand yields diminished returns because query volume is capped. 
    The highest incremental profits come from capturing middle-funnel intent via **Meta Retargeting** and **Affiliates**, while refilling the pipeline with **Meta Prospecting** and **LinkedIn**.
    """)

# -------------------------------------------------------------
# Recommendations
# -------------------------------------------------------------
st.markdown("---")
st.subheader("4. Strategic Action Playbook (3 Ranked Decisions)")
r1, r2, r3 = st.columns(3)
with r1:
    st.markdown("""
    **1. Scale Middle-Funnel & Affiliates (+₹6.5 Lakh)**
    - Reallocate ₹3.5L to Meta Retargeting and ₹3.0L to Affiliate Partners.
    - Captures high-intent buyers before ad fatigue.
    - **Expected Return: ₹25.05 Lakh Revenue (3.85x mROAS)**.
    """)
with r2:
    st.markdown("""
    **2. Replenish Pipeline & High-LTV Buyers (+₹3.0 Lakh)**
    - Allocate ₹1.5L to Meta Prospecting and ₹1.5L to LinkedIn B2B.
    - Secures enterprise cohorts with ₹6,800+ AOV.
    - **Expected Return: ₹8.18 Lakh Revenue + High 12M LTV**.
    """)
with r3:
    st.markdown("""
    **3. Protect Top-of-Funnel & Cap Brand Search (₹0 Change)**
    - Maintain YouTube video budget for first-touch discovery.
    - Freeze Google Brand Search expansion to stop bidding against organic rank.
    - **Saves: ₹1.8 Lakh in wasted search CPC inflation**.
    """)
