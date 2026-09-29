-- schema.sql
-- Enterprise Marketing Performance & Capital Allocation Analytics
-- Relational Star Schema for Multi-Channel Attribution and Financial Analytics

DROP TABLE IF EXISTS fact_orders;
DROP TABLE IF EXISTS fact_customer_touchpoints;
DROP TABLE IF EXISTS fact_daily_campaign_performance;
DROP TABLE IF EXISTS fact_customer_ltv;
DROP TABLE IF EXISTS dim_campaigns;
DROP TABLE IF EXISTS dim_channels;

-- 1. Dimension: Channels
CREATE TABLE dim_channels (
    channel_id INTEGER PRIMARY KEY,
    channel TEXT NOT NULL UNIQUE,
    channel_type TEXT NOT NULL,
    strategic_intent TEXT NOT NULL
);

-- 2. Dimension: Campaigns
CREATE TABLE dim_campaigns (
    campaign_id TEXT PRIMARY KEY,
    channel TEXT NOT NULL,
    strategic_intent TEXT NOT NULL,
    FOREIGN KEY (channel) REFERENCES dim_channels(channel)
);

-- 3. Fact: Daily Campaign Performance (Aggregated Ad Spend & Funnel)
CREATE TABLE fact_daily_campaign_performance (
    date TEXT NOT NULL,
    campaign_id TEXT NOT NULL,
    channel TEXT NOT NULL,
    channel_type TEXT NOT NULL,
    strategic_intent TEXT NOT NULL,
    impressions INTEGER NOT NULL,
    clicks INTEGER NOT NULL,
    spend_inr REAL NOT NULL,
    leads INTEGER NOT NULL,
    direct_conversions INTEGER NOT NULL,
    direct_revenue_inr REAL NOT NULL,
    cpc_inr REAL,
    ctr_pct REAL,
    cpa_inr REAL,
    direct_roas REAL,
    PRIMARY KEY (date, campaign_id),
    FOREIGN KEY (channel) REFERENCES dim_channels(channel)
);

-- 4. Fact: Customer Touchpoints (Individual Multi-Touch Journey)
CREATE TABLE fact_customer_touchpoints (
    touchpoint_id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    channel TEXT NOT NULL,
    step_order INTEGER NOT NULL,
    total_steps INTEGER NOT NULL,
    is_first_touch INTEGER NOT NULL,
    is_last_touch INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (channel) REFERENCES dim_channels(channel)
);

-- 5. Fact: Orders (Transaction Grain)
CREATE TABLE fact_orders (
    order_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    order_number INTEGER NOT NULL,
    order_date TEXT NOT NULL,
    order_value_gross REAL NOT NULL,
    discount_inr REAL NOT NULL,
    order_value_net REAL NOT NULL,
    cogs_inr REAL NOT NULL,
    gross_profit_inr REAL NOT NULL,
    acquisition_channel_first TEXT NOT NULL,
    acquisition_channel_last TEXT NOT NULL,
    is_repeat INTEGER NOT NULL,
    margin_pct REAL
);

-- 6. Fact: Customer LTV & Demographics
CREATE TABLE fact_customer_ltv (
    user_id TEXT PRIMARY KEY,
    acquisition_date TEXT NOT NULL,
    acquisition_channel_first TEXT NOT NULL,
    acquisition_channel_last TEXT NOT NULL,
    geography TEXT NOT NULL,
    city_tier TEXT NOT NULL,
    customer_segment TEXT NOT NULL,
    total_orders INTEGER NOT NULL,
    lifetime_revenue_inr REAL NOT NULL,
    lifetime_gross_profit_inr REAL NOT NULL,
    tenure_days INTEGER NOT NULL
);

-- Performance Indexes
CREATE INDEX idx_camp_perf_channel ON fact_daily_campaign_performance(channel);
CREATE INDEX idx_camp_perf_date ON fact_daily_campaign_performance(date);
CREATE INDEX idx_touch_user ON fact_customer_touchpoints(user_id);
CREATE INDEX idx_touch_channel ON fact_customer_touchpoints(channel);
CREATE INDEX idx_orders_user ON fact_orders(user_id);
CREATE INDEX idx_orders_date ON fact_orders(order_date);
CREATE INDEX idx_cust_acq_first ON fact_customer_ltv(acquisition_channel_first);
CREATE INDEX idx_cust_acq_last ON fact_customer_ltv(acquisition_channel_last);
