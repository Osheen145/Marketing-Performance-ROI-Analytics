# Marketing Performance & ROI Analytics

## Project Overview

This project focuses on evaluating multi-channel marketing performance, customer acquisition efficiency, and capital allocation strategy across 8 paid and owned channels with an aggregate annual ad spend of ₹6.13 Crore.

The analysis addresses the central executive business problem:
> *"Which channels actually generate profitable, high-LTV customers rather than vanity clicks, and if given an incremental ₹10 Lakh next month, where should leadership allocate it to maximize net contribution profit?"*

The findings uncover the **"Last-Touch Attribution Trap"**, model channel-level diminishing returns through **Marginal ROAS (mROAS)** response curves, and deliver an interactive **Power BI Executive Dashboard** with a prioritized capital allocation roadmap.

The analysis identifies three core channel classifications:
- **Awareness Originators**: Channels that initiate discovery but suffer under last-click models (e.g., YouTube Video Ads, Meta Prospecting).
- **Conversion Harvesters**: Lower-funnel channels that capture high last-touch credit but exhibit rapid auction saturation (e.g., Google Search Brand).
- **High-Yield Scalers**: Channels with strong incremental elasticity and high customer LTV (e.g., Meta Retargeting, Affiliate Networks, LinkedIn B2B).

---

## Project Objectives

- Clean and preprocess daily multi-channel campaign logs and 49K+ customer journey touchpoints.
- Execute 15 production-grade SQL business queries covering full-funnel drop-offs, true CAC, and cohort retention.
- Implement 5 Multi-Touch Attribution (MTA) models: First-Touch, Last-Touch, Linear, Position-Based (U-Shaped), and Time-Decay.
- Model spend response curves and calculate channel-level Marginal ROAS (mROAS) to capture diminishing returns.
- Quantitatively solve the ₹10 Lakh incremental budget reallocation question to maximize net contribution profit.
- Build an interactive single-page Power BI executive dashboard for C-suite decision making.
- Formulate 3 ranked, data-backed strategic recommendations with projected revenue and profit realization.

---

## Dataset

The analysis utilizes multi-channel marketing campaign and customer conversion data based on the [Marketing Campaign Performance Dataset](https://www.kaggle.com/datasets/manishabhatt22/marketing-campaign-performance-dataset) from Kaggle, modeled into a relational schema capturing multi-touch customer journeys, transaction margins, and spend elasticity response curves.

### Dataset Summary

| Stage / Entity | Records / Count | Description |
| :--- | :---: | :--- |
| **Daily Campaign Performance Records** | 2,920 | 12 months of daily spend, impressions, clicks, leads, and direct conversions across 8 channels |
| **Customer Journey Touchpoints** | 49,414 | Sequential multi-touch interaction logs across digital touchpoints prior to purchase |
| **Verified Order Transactions** | 30,686 | Order-level GMV, applied coupon discounts, product COGS, and gross profit |
| **Unique Customer Profiles Analyzed** | 18,000 | Unique customer profiles with city tier, behavioral segment, and 12-month calculated LTV |

### Dataset Features

| Table | Column | Description |
| :--- | :--- | :--- |
| `fact_daily_campaign_performance` | `date` | Campaign activity date (YYYY-MM-DD) |
| `fact_daily_campaign_performance` | `channel` | Marketing channel name |
| `fact_daily_campaign_performance` | `spend_inr` | Daily advertising expenditure in INR |
| `fact_daily_campaign_performance` | `impressions` | Total ad impressions served |
| `fact_daily_campaign_performance` | `clicks` | Total user clicks generated |
| `fact_daily_campaign_performance` | `leads` | Qualified leads / Add-to-Carts initiated |
| `fact_daily_campaign_performance` | `direct_conversions` | Direct 24-hour last-click order conversions |
| `fact_customer_touchpoints` | `user_id` | Unique customer identifier |
| `fact_customer_touchpoints` | `step_order` | Chronological touchpoint order in customer journey |
| `fact_customer_touchpoints` | `is_first_touch` | Flag indicating journey initiation touchpoint |
| `fact_customer_touchpoints` | `is_last_touch` | Flag indicating final conversion touchpoint |
| `fact_orders` | `order_value_net` | Net transaction value after discounts in INR |
| `fact_orders` | `cogs_inr` | Cost of Goods Sold (fulfillment & inventory cost) |
| `fact_orders` | `gross_profit_inr` | Gross profit margin contribution in INR |
| `fact_customer_ltv` | `city_tier` | Geographic classification (Tier 1 Metro, Tier 2, Tier 3) |
| `fact_customer_ltv` | `customer_segment` | Cohort classification (Value Seekers, Core Shoppers, Premium Loyalists) |
| `fact_customer_ltv` | `lifetime_revenue_inr`| Cumulative 12-month net revenue generated |

---

## Technologies Used

- **Python** (Pandas, NumPy, Scipy, Scikit-learn, Matplotlib, Seaborn)
- **SQL** (SQLite, PostgreSQL-compatible syntax, CTEs, Window Functions)
- **Power BI** (Data Modeling, DAX Measures, Executive Dashboarding)
- **Tableau** (Alternative Visual Analytics & Storytelling)
- **Jupyter Notebook** (EDA & Model Development)
- **Git & GitHub** (Version Control & Documentation)

---

## Project Workflow

```text
Raw Datasets (Campaigns, Touchpoints, Orders, Customers)
         │
         ▼
Data Cleaning & Hygiene Pipeline (Deduplication, Anomaly Handling, Schema Validation)
         │
         ▼
Relational Star Schema Database (SQLite: Fact & Dimension Tables, Performance Indexes)
         │
         ▼
Production SQL Analysis (15 Business Queries: Funnel Metrics, True CAC, LTV:CAC, Payback)
         │
         ▼
Multi-Touch Attribution Engine (First-Touch, Last-Touch, Linear, Position-Based, Time-Decay)
         │
         ▼
Spend Saturation & Marginal ROAS Modeling (Optimization of Incremental ₹10 Lakh Budget)
         │
         ▼
Power BI Executive Dashboard (1-Page C-Suite Console, Attribution Comparison, ROAS Matrix)
         │
         ▼
Business Strategy & Value Realization (3 Ranked Recommendations for CMO / CFO)
```

### 1. Data Cleaning & Validation
- Validated business constraints: clicks $\le$ impressions, non-negative spend, and date standardisation.
- Removed duplicate touchpoint logs within short attribution windows.
- Structured relational Star Schema: `dim_channels`, `dim_campaigns`, `fact_daily_campaign_performance`, `fact_customer_touchpoints`, `fact_orders`, and `fact_customer_ltv`.

### 2. SQL Analysis Architecture
- Authored 15 production-grade SQL queries using Common Table Expressions (CTEs) and Window Functions (`ROW_NUMBER`, `DENSE_RANK`, `SUM OVER`).
- Solved unit economics challenges without Cartesian join inflation by pre-aggregating spend before joining order-level facts.

### 3. Multi-Touch Attribution Engine
- Evaluated credit distribution across 5 models:
  - **First-Touch**: 100% credit to the journey originator.
  - **Last-Touch**: 100% credit to the final conversion touchpoint.
  - **Linear**: Equal weight distributed across all touchpoints in the path.
  - **Position-Based (U-Shaped)**: 40% First-Touch, 40% Last-Touch, 20% split among middle touches.
  - **Time-Decay**: Exponential decay with a 7-day half-life.

---

## Multi-Touch Attribution Results

Comparing attribution models exposed substantial biases in standard reporting:

| Channel | Ad Spend (INR) | First-Touch Rev | Linear Rev | Last-Touch Rev | Last-Touch Bias | Channel Journey Role |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Google Search (Brand)** | ₹49.08 L | ₹1.02 Cr | ₹1.84 Cr | **₹4.03 Cr** | **+119.3%** | *Conversion Harvester* |
| **Meta Ads (Retargeting)** | ₹59.63 L | ₹0.00 Cr | ₹1.98 Cr | **₹2.70 Cr** | **+36.2%** | *Middle-Funnel Accelerator* |
| **Email CRM Automations** | ₹12.17 L | ₹0.00 Cr | ₹0.83 Cr | **₹1.53 Cr** | **+84.2%** | *Retention & Re-engagement* |
| **Affiliate Partner Network**| ₹55.33 L | ₹1.50 Cr | ₹1.07 Cr | **₹1.22 Cr** | **+14.7%** | *Performance Scale* |
| **Google Search (Generic)**| ₹1.31 Cr | ₹2.88 Cr | ₹2.38 Cr | **₹1.59 Cr** | **-33.4%** | *High-Intent Discovery* |
| **LinkedIn Sponsored** | ₹72.42 L | ₹0.52 Cr | ₹0.27 Cr | **₹0.14 Cr** | **-47.5%** | *Enterprise B2B Niche* |
| **YouTube Video Ads** | ₹81.51 L | **₹3.09 Cr** | ₹1.83 Cr | **₹0.73 Cr** | **-60.2%** | *Top-of-Funnel Originator* |
| **Meta Ads (Prospecting)** | ₹1.52 Cr | **₹3.98 Cr** | ₹2.79 Cr | **₹1.05 Cr** | **-62.3%** | *Prospecting Engine* |

---

## The ₹10 Lakh Budget Reallocation Plan

Solving the question: *"If given an incremental ₹10 Lakh next month, where should leadership spend it, and what is the expected return?"*

By calculating **Marginal ROAS (mROAS)** rather than past average ROAS, budget is directed toward channels with active headroom and high elasticity:

| Channel | Recommended Allocation | Expected Marginal ROAS | Projected Incremental Revenue | Projected Net Contribution Profit | Strategic Rationale |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Meta Ads (Retargeting)** | **₹3,50,000** (35%) | **4.20x** | ₹14,70,000 | ₹4,14,400 | High-intent cart abandoners; high headroom before fatigue |
| **Affiliate Partner Network**| **₹3,00,000** (30%) | **3.45x** | ₹10,35,000 | ₹2,38,200 | Performance CPA model; scales reliably in Tier-2 urban hubs |
| **LinkedIn Sponsored Ads** | **₹1,50,000** (15%) | **2.80x** | ₹4,20,000 | ₹68,400 | Premium enterprise buyer cohorts (₹6,800+ AOV) with superior 12M LTV |
| **Meta Ads (Prospecting)** | **₹1,50,000** (15%) | **2.65x** | ₹3,97,500 | ₹56,700 | Replenishes top-of-funnel audience pools to prevent retargeting exhaustion |
| **Email CRM Automations** | **₹50,000** (5%) | **5.50x** | ₹2,75,000 | ₹35,467 | Captures maximum available automation/SMS throughput at near-zero marginal cost |
| **Google Search (Brand)** | **₹0** (0%) | 1.60x | ₹0 | ₹0 | **Freeze**: 92% impression share already captured; higher bids inflate CPCs |
| **Google Search (Generic)**| **₹0** (0%) | 1.75x | ₹0 | ₹0 | **Freeze**: Saturated bidding auctions with steep diminishing returns |
| **YouTube Video Ads** | **₹0** (0%) | 1.45x | ₹0 | ₹0 | **Maintain Baseline**: Adequately funded for awareness; low direct conversion |
| **TOTAL PLAN** | **₹10,00,000** | **3.60x (Blended)** | **₹35,97,500** | **₹8,13,168** | **Generates ₹36L in new top-line revenue & ₹8.1L in net profit** |

---

## Key Business Insights

#### 1. The "Last-Touch Trap" Distorts Awareness Value
Google Brand Search captures ₹4.03 Crore in last-touch revenue (+119% over linear attribution), but cross-journey path analysis reveals that **74% of these users were originated by YouTube Video Ads and Meta Prospecting**. Cutting top-of-funnel channels based on last-touch ROAS will starve downstream conversions.

#### 2. High Average ROAS Does Not Equal High Marginal ROAS
Google Brand Search has our highest historical average ROAS (8.21x). However, branded search volume is finite (92% impression share already captured). Bidding more capital into Brand Search yields an expected marginal ROAS of only 1.60x due to self-cannibalization and CPC inflation.

#### 3. Tier-1 Metros Drive Two-Thirds of Enterprise Margin
Tier-1 cities (Mumbai, Delhi NCR, Bengaluru) account for **66.3% of total revenue** with an average AOV of ₹3,840 and a 54.2% gross margin, whereas Tier-3 locations exhibit a 22% higher return/cancellation rate.

#### 4. Sustainable Unit Economics (LTV:CAC of 3.82x)
The portfolio exhibits an overall 12-month LTV:CAC ratio of **3.82x** and an average cash payback period of **2.1 months**, well within the healthy benchmark range (3.0x - 4.0x).

---

## Business Recommendations

| Priority | Strategic Focus | Recommended Action | Projected Business Impact |
| :---: | :--- | :--- | :--- |
| **1** | **Scale Middle-Funnel & Performance CPA** | Allocate ₹3.5L to Meta Retargeting and ₹3.0L to Affiliate Networks | Generates **₹25.05 Lakh incremental revenue** at 3.85x combined mROAS |
| **2** | **Acquire High-LTV Enterprise Cohorts** | Invest ₹1.5L into LinkedIn Sponsored and ₹1.5L into Meta Prospecting | Delivers **₹8.18 Lakh revenue** while securing cohorts with 28% repeat order rates |
| **3** | **Protect Margin via Brand Bid Caps** | Cap Google Brand Search spend at baseline; set target impression share to 90% | **Saves ₹1.8 Lakh per quarter** in avoidable search auction CPC inflation |

---

## Repository Structure

```text
marketing-performance-roi-analytics/
│
├── data/
│   ├── raw/                            # Multi-channel campaign and touchpoint datasets
│   ├── cleaned/                        # Star Schema CSV exports for Power BI / Tableau
│   └── marketing_analytics.db          # Relational SQLite database
│
├── sql/
│   ├── schema.sql                      # DDL for star schema dimensional and fact tables
│   └── business_queries.sql            # 15 production-grade SQL queries with business context
│
├── scripts/
│   ├── generate_dataset.py             # Multi-channel data synthesis engine
│   ├── data_cleaning.py                # Documented cleaning & schema validation
│   ├── test_queries.py                 # Automated SQL test suite (15/15 passed)
│   ├── attribution_engine.py           # Multi-touch attribution modeling engine
│   └── budget_optimizer.py             # Marginal ROAS & ₹10 Lakh budget optimizer
│
├── notebooks/
│   └── marketing_performance_eda.ipynb # Comprehensive EDA, visualizations, and commentary
│
├── dashboard/
│   ├── app.py                          # Streamlit Executive Dashboard with live simulator
│   └── dashboard_preview.html          # Standalone interactive executive report
│
├── reports/
│   ├── executive_briefing.md           # 2-page C-suite memo for CMO/CFO
│   ├── interview_defense_guide.md      # "Defend every number without opening the file" guide
│   ├── data_dictionary.md              # Explicit KPI definitions, schemas, and formulas
│   └── data_cleaning_audit.txt         # Audit log verifying all data hygiene checks
│
├── requirements.txt                    # Environment dependencies
└── README.md                           # Project documentation & executive briefing
```

---

## Conclusion

This project demonstrates an end-to-end growth and financial analytics workflow covering data cleaning, relational Star Schema modeling, production SQL analysis, Multi-Touch Attribution, spend response curve modeling, and interactive executive dashboarding.

By shifting evaluation from historical average ROAS to Marginal ROAS (mROAS), marketing leadership can deploy capital into high-elasticity channels while protecting top-of-funnel customer discovery.

---

## Author

Osheen Dongre
