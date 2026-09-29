# Data Dictionary: Marketing Performance & ROI Analytics

## 1. Relational Database Schema (`marketing_analytics.db`)

### Table: `dim_channels`
Dimensional table cataloging all marketing channels and their strategic role.

| Field Name | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `channel_id` | INTEGER | Primary Key; unique identifier for the channel | `1` |
| `channel` | TEXT | Unique name of the channel | `Meta_Ads_Retargeting` |
| `channel_type` | TEXT | Channel media category (`Search`, `Social`, `Video`, `CRM`, `Affiliate`, `B2B_Social`) | `Social` |
| `strategic_intent` | TEXT | Tactical funnel purpose (`Prospecting`, `Retargeting`, `Brand Defense`, `Retention`) | `Retargeting` |

---

### Table: `dim_campaigns`
Dimensional table identifying active campaigns and their intent.

| Field Name | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `campaign_id` | TEXT | Primary Key; unique campaign identifier | `CMP_1004` |
| `channel` | TEXT | Foreign Key referencing `dim_channels(channel)` | `Meta_Ads_Retargeting` |
| `strategic_intent` | TEXT | Strategy intent of the campaign | `Retargeting` |

---

### Table: `fact_daily_campaign_performance`
Daily aggregated fact table tracking ad spend and top-line engagement.

| Field Name | Type | Description | Unit / Format |
| :--- | :--- | :--- | :--- |
| `date` | TEXT | Activity date | `YYYY-MM-DD` |
| `campaign_id` | TEXT | Foreign Key to `dim_campaigns` | `CMP_1001` |
| `channel` | TEXT | Channel name | `Google_Search_Brand` |
| `impressions` | INTEGER | Total ad impressions served | Count |
| `clicks` | INTEGER | Total ad clicks generated | Count |
| `spend_inr` | REAL | Total ad spend in Indian Rupees | INR (₹) |
| `leads` | INTEGER | Qualified leads / Add-to-Carts initiated | Count |
| `direct_conversions` | INTEGER | Direct last-click conversions within 24h | Count |
| `direct_revenue_inr` | REAL | Attributed direct purchase revenue | INR (₹) |
| `cpc_inr` | REAL | Cost Per Click = `spend_inr / clicks` | INR (₹) |
| `ctr_pct` | REAL | Click-Through Rate = `(clicks / impressions) * 100` | % |
| `cpa_inr` | REAL | Cost Per Acquisition = `spend_inr / direct_conversions` | INR (₹) |
| `direct_roas` | REAL | Direct Return on Ad Spend = `direct_revenue_inr / spend_inr` | Ratio ($x$) |

---

### Table: `fact_customer_touchpoints`
Individual customer path log capturing every interaction across channels.

| Field Name | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `touchpoint_id` | INTEGER | Primary Key; unique touchpoint event ID | `1042` |
| `user_id` | TEXT | Foreign Key referencing customer | `USR_105231` |
| `channel` | TEXT | Channel of this specific touchpoint | `YouTube_Video_Ads` |
| `step_order` | INTEGER | Chronological step number in the journey (1, 2, 3...) | `1` |
| `total_steps` | INTEGER | Total touchpoints in customer's path prior to first purchase | `3` |
| `is_first_touch` | INTEGER | 1 if this touchpoint initiated the journey, else 0 | `1` |
| `is_last_touch` | INTEGER | 1 if this touchpoint immediately preceded conversion, else 0 | `0` |
| `timestamp` | TEXT | Precise timestamp of interaction | `YYYY-MM-DD HH:MM:SS` |

---

### Table: `fact_orders`
Transaction-grain fact table capturing gross revenue, discounts, COGS, and profit.

| Field Name | Type | Description | Unit / Format |
| :--- | :--- | :--- | :--- |
| `order_id` | TEXT | Primary Key; unique order ID | `ORD_50012` |
| `user_id` | TEXT | Customer identifier | `USR_100004` |
| `order_number` | INTEGER | Sequential order number for this user (1 = First, 2+ = Repeat) | `1` |
| `order_date` | TEXT | Date order was placed | `YYYY-MM-DD` |
| `order_value_gross` | REAL | Gross Merchandise Value (GMV) before discounts | INR (₹) |
| `discount_inr` | REAL | Total promotional discounts applied | INR (₹) |
| `order_value_net` | REAL | Net Revenue = `order_value_gross - discount_inr` | INR (₹) |
| `cogs_inr` | REAL | Cost of Goods Sold (direct fulfillment & inventory cost) | INR (₹) |
| `gross_profit_inr` | REAL | Gross Profit = `order_value_net - cogs_inr` | INR (₹) |
| `acquisition_channel_first` | TEXT | Channel that originated the customer (First Touch) | Channel Name |
| `acquisition_channel_last` | TEXT | Channel that closed the customer (Last Touch) | Channel Name |
| `is_repeat` | INTEGER | 1 if repeat purchase (`order_number > 1`), else 0 | Flag |
| `margin_pct` | REAL | Gross Margin % = `(gross_profit_inr / order_value_net) * 100` | % |

---

### Table: `fact_customer_ltv`
Aggregated customer-grain table capturing demographic tier and 12-month value.

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `user_id` | TEXT | Primary Key; unique customer ID |
| `acquisition_date` | TEXT | Date customer made their first purchase |
| `acquisition_channel_first` | TEXT | First-Touch acquisition channel |
| `acquisition_channel_last` | TEXT | Last-Touch acquisition channel |
| `geography` | TEXT | City and state/metro classification (`Tier 1 - Mumbai`) |
| `city_tier` | TEXT | Geographic classification (`Tier 1`, `Tier 2`, `Tier 3`) |
| `customer_segment` | TEXT | Behavioral cohort (`Value Seekers`, `Core Shoppers`, `Premium Loyalists`) |
| `total_orders` | INTEGER | Cumulative order count in 12-month observation window |
| `lifetime_revenue_inr` | REAL | Cumulative net revenue generated |
| `lifetime_gross_profit_inr`| REAL | Cumulative gross profit contribution |
| `tenure_days` | INTEGER | Days between first and last recorded activity |

---

## 2. Core Business KPI Definitions & Mathematical Formulas

1. **Return on Ad Spend (ROAS)**:
   $$\text{ROAS} = \frac{\text{Net Revenue Attributed}}{\text{Marketing Ad Spend}}$$
   *Definition*: Measures top-line revenue generated per rupee of advertising spend.

2. **Net Return on Marketing Investment (ROMI)**:
   $$\text{ROMI (\%)} = \frac{\text{Gross Profit} - \text{Ad Spend}}{\text{Ad Spend}} \times 100$$
   *Definition*: Measures bottom-line profit contribution after subtracting direct product COGS and marketing spend.

3. **Paid Customer Acquisition Cost (CAC)**:
   $$\text{Paid CAC} = \frac{\text{Channel Ad Spend}}{\text{New Customers Acquired via Channel}}$$
   *Definition*: True capital expended to acquire one paying customer through paid advertising.

4. **Blended Customer Acquisition Cost (Blended CAC)**:
   $$\text{Blended CAC} = \frac{\text{Total Marketing Spend (All Channels)}}{\text{Total New Customers Acquired (Paid + Organic + Direct)}}$$
   *Definition*: Company-wide average cost per acquired customer.

5. **Customer Lifetime Value to CAC Ratio (LTV:CAC)**:
   $$\text{LTV:CAC} = \frac{\text{Average 12-Month Gross Profit Contribution per Customer}}{\text{Channel CAC}}$$
   *Benchmark*: $>4.0\times$ (Aggressive Scale), $3.0\times - 4.0\times$ (Healthy/Sustainable), $<1.5\times$ (Value Destroying).

6. **CAC Payback Period (Months)**:
   $$\text{Payback Period} = \frac{\text{Channel CAC}}{\text{First-Order Gross Profit Velocity}}$$
   *Definition*: Time in months required for gross margin from an acquired customer to recoup initial acquisition cost.

7. **Marginal ROAS (mROAS)**:
   $$\text{mROAS} = \frac{\Delta \text{Revenue}}{\Delta \text{Spend}} = \frac{R(S + \Delta S) - R(S)}{\Delta S}$$
   *Definition*: Expected return on the *next* incremental rupee of advertising spend, accounting for diminishing returns.
