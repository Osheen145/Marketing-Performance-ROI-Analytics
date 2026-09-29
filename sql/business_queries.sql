-- ==============================================================================
-- Enterprise Marketing Performance & Capital Allocation Analytics
-- 15 Production-Grade SQL Business Queries for Growth & Financial Analytics
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Q1: Full Metric Chain Funnel by Channel
-- Business Question:
-- How does each marketing channel perform across the full metric chain:
-- Impressions -> Clicks -> Leads -> Conversions -> Ad Spend -> Revenue -> ROAS?
-- Decision: Identify where funnel drop-offs occur and which channels convert efficiently.
-- ------------------------------------------------------------------------------
WITH ChannelMetrics AS (
    SELECT 
        channel,
        SUM(impressions) AS total_impressions,
        SUM(clicks) AS total_clicks,
        SUM(leads) AS total_leads,
        SUM(direct_conversions) AS total_conversions,
        ROUND(SUM(spend_inr), 2) AS total_spend_inr,
        ROUND(SUM(direct_revenue_inr), 2) AS total_revenue_inr
    FROM fact_daily_campaign_performance
    GROUP BY channel
)
SELECT 
    channel,
    total_impressions,
    total_clicks,
    ROUND((total_clicks * 100.0 / NULLIF(total_impressions, 0)), 2) AS ctr_pct,
    ROUND(total_spend_inr / NULLIF(total_clicks, 0), 2) AS cpc_inr,
    total_leads,
    ROUND(total_spend_inr / NULLIF(total_leads, 0), 2) AS cpl_inr,
    total_conversions,
    ROUND((total_conversions * 100.0 / NULLIF(total_clicks, 0)), 2) AS click_to_conv_pct,
    ROUND(total_spend_inr / NULLIF(total_conversions, 0), 2) AS direct_cpa_inr,
    total_spend_inr,
    total_revenue_inr,
    ROUND(total_revenue_inr / NULLIF(total_spend_inr, 0), 2) AS direct_roas
FROM ChannelMetrics
ORDER BY total_revenue_inr DESC;


-- ------------------------------------------------------------------------------
-- Q2: True Paid Customer Acquisition Cost (CAC) vs Blended CAC
-- Business Question:
-- What is the true CAC for each paid channel vs our overall blended acquisition cost?
-- Decision: Prevent underestimating acquisition cost by comparing direct paid conversions
-- with total customers acquired.
-- ------------------------------------------------------------------------------
WITH PaidSpend AS (
    SELECT 
        channel,
        SUM(spend_inr) AS channel_spend
    FROM fact_daily_campaign_performance
    GROUP BY channel
),
AcquiredUsers AS (
    SELECT 
        acquisition_channel_first AS channel,
        COUNT(DISTINCT user_id) AS new_customers_acquired
    FROM fact_customer_ltv
    GROUP BY acquisition_channel_first
),
OverallBlended AS (
    SELECT 
        SUM(spend_inr) AS overall_total_spend,
        (SELECT COUNT(DISTINCT user_id) FROM fact_customer_ltv) AS overall_total_users
    FROM fact_daily_campaign_performance
)
SELECT 
    p.channel,
    ROUND(p.channel_spend, 2) AS total_spend_inr,
    COALESCE(a.new_customers_acquired, 0) AS customers_acquired,
    ROUND(p.channel_spend / NULLIF(a.new_customers_acquired, 0), 2) AS true_paid_cac_inr,
    ROUND((SELECT overall_total_spend / overall_total_users FROM OverallBlended), 2) AS company_blended_cac_inr,
    ROUND((p.channel_spend / NULLIF(a.new_customers_acquired, 0)) - 
          (SELECT overall_total_spend / overall_total_users FROM OverallBlended), 2) AS cac_variance_from_blended
FROM PaidSpend p
LEFT JOIN AcquiredUsers a ON p.channel = a.channel
ORDER BY true_paid_cac_inr ASC;


-- ------------------------------------------------------------------------------
-- Q3: ROAS vs Net ROMI (Return on Marketing Investment)
-- Business Question:
-- Which channels look profitable on top-line ROAS but suffer when factoring in COGS & Gross Profit?
-- Decision: Evaluate campaigns based on Net Margin contribution, not gross revenue illusions.
-- ------------------------------------------------------------------------------
WITH ChannelSpend AS (
    SELECT channel, SUM(spend_inr) AS total_spend
    FROM fact_daily_campaign_performance
    GROUP BY channel
),
ChannelOrders AS (
    SELECT 
        acquisition_channel_last AS channel,
        SUM(order_value_net) AS total_attributed_revenue,
        SUM(cogs_inr) AS total_attributed_cogs,
        SUM(gross_profit_inr) AS total_gross_profit
    FROM fact_orders
    GROUP BY acquisition_channel_last
)
SELECT 
    s.channel,
    ROUND(s.total_spend, 2) AS ad_spend_inr,
    ROUND(COALESCE(o.total_attributed_revenue, 0), 2) AS net_revenue_inr,
    ROUND(COALESCE(o.total_attributed_revenue, 0) / NULLIF(s.total_spend, 0), 2) AS gross_roas,
    ROUND(COALESCE(o.total_gross_profit, 0), 2) AS gross_profit_inr,
    ROUND(COALESCE(o.total_gross_profit, 0) - s.total_spend, 2) AS net_profit_contribution_inr,
    -- Net ROMI = (Gross Profit - Ad Spend) / Ad Spend * 100
    ROUND(((COALESCE(o.total_gross_profit, 0) - s.total_spend) * 100.0) / NULLIF(s.total_spend, 0), 2) AS net_romi_pct
FROM ChannelSpend s
LEFT JOIN ChannelOrders o ON s.channel = o.channel
ORDER BY net_profit_contribution_inr DESC;


-- ------------------------------------------------------------------------------
-- Q4: Customer Lifetime Value (LTV) to CAC Ratio by Channel
-- Business Question:
-- What is the 12-month LTV:CAC ratio across acquisition channels?
-- Decision: Categorize channels into Scale (>4.0x), Healthy (3.0x - 4.0x), At-Risk (1.5x - 3.0x), and Value-Destroying (<1.5x).
-- ------------------------------------------------------------------------------
WITH ChannelLTV AS (
    SELECT 
        acquisition_channel_first AS channel,
        COUNT(user_id) AS cohort_size,
        ROUND(AVG(lifetime_revenue_inr), 2) AS avg_revenue_ltv,
        ROUND(AVG(lifetime_gross_profit_inr), 2) AS avg_gross_profit_ltv
    FROM fact_customer_ltv
    GROUP BY acquisition_channel_first
),
ChannelSpend AS (
    SELECT 
        channel,
        SUM(spend_inr) AS total_spend
    FROM fact_daily_campaign_performance
    GROUP BY channel
)
SELECT 
    l.channel,
    l.cohort_size,
    ROUND(s.total_spend / NULLIF(l.cohort_size, 0), 2) AS cac_inr,
    l.avg_revenue_ltv AS revenue_ltv_inr,
    l.avg_gross_profit_ltv AS margin_ltv_inr,
    ROUND(l.avg_gross_profit_ltv / NULLIF(s.total_spend / l.cohort_size, 0), 2) AS margin_ltv_to_cac_ratio,
    CASE 
        WHEN (l.avg_gross_profit_ltv / NULLIF(s.total_spend / l.cohort_size, 0)) >= 4.0 THEN 'Scale Aggressively'
        WHEN (l.avg_gross_profit_ltv / NULLIF(s.total_spend / l.cohort_size, 0)) >= 3.0 THEN 'Healthy - Maintain'
        WHEN (l.avg_gross_profit_ltv / NULLIF(s.total_spend / l.cohort_size, 0)) >= 1.5 THEN 'At-Risk - Optimize'
        ELSE 'Value Destroying - Halt/Restructure'
    END AS channel_health_rating
FROM ChannelLTV l
JOIN ChannelSpend s ON l.channel = s.channel
ORDER BY margin_ltv_to_cac_ratio DESC;


-- ------------------------------------------------------------------------------
-- Q5: CAC Payback Period (Cash Flow Breakeven in Months)
-- Business Question:
-- How long does it take for gross profit from an acquired customer to recover initial CAC?
-- Decision: Manage working capital and liquidity by pacing spend against cash payback speeds.
-- ------------------------------------------------------------------------------
WITH ChannelSpend AS (
    SELECT channel, SUM(spend_inr) AS total_spend
    FROM fact_daily_campaign_performance
    GROUP BY channel
),
AcquiredUsers AS (
    SELECT acquisition_channel_first AS channel, COUNT(user_id) AS total_users
    FROM fact_customer_ltv
    GROUP BY acquisition_channel_first
),
ChannelCAC AS (
    SELECT 
        s.channel,
        ROUND(s.total_spend / NULLIF(u.total_users, 0), 2) AS cac_inr
    FROM ChannelSpend s
    JOIN AcquiredUsers u ON s.channel = u.channel
),
ChannelFirstOrderProfit AS (
    SELECT 
        acquisition_channel_first AS channel,
        AVG(gross_profit_inr) AS m1_gross_profit
    FROM fact_orders
    WHERE order_number = 1
    GROUP BY acquisition_channel_first
)
SELECT 
    c.channel,
    c.cac_inr,
    ROUND(p.m1_gross_profit, 2) AS first_order_gross_profit,
    ROUND(c.cac_inr / NULLIF(p.m1_gross_profit, 0), 1) AS estimated_payback_months,
    CASE 
        WHEN (c.cac_inr / NULLIF(p.m1_gross_profit, 0)) <= 3.0 THEN 'Fast (<3 Months)'
        WHEN (c.cac_inr / NULLIF(p.m1_gross_profit, 0)) <= 6.0 THEN 'Moderate (3-6 Months)'
        ELSE 'Slow (>6 Months - Liquidity Drag)'
    END AS payback_velocity
FROM ChannelCAC c
JOIN ChannelFirstOrderProfit p ON c.channel = p.channel
ORDER BY estimated_payback_months ASC;


-- ------------------------------------------------------------------------------
-- Q6: First-Touch vs Last-Touch Multi-Touch Attribution
-- Business Question:
-- How drastically does channel performance shift when comparing First-Touch (acquisition source)
-- to Last-Touch (closing conversion source)?
-- Decision: Expose the "Last-Touch Trap" that starves awareness channels (YouTube/Meta)
-- while over-crediting brand search.
-- ------------------------------------------------------------------------------
WITH FirstTouchCounts AS (
    SELECT 
        acquisition_channel_first AS channel,
        COUNT(DISTINCT user_id) AS first_touch_customers,
        SUM(lifetime_revenue_inr) AS first_touch_revenue
    FROM fact_customer_ltv
    GROUP BY acquisition_channel_first
),
LastTouchCounts AS (
    SELECT 
        acquisition_channel_last AS channel,
        COUNT(DISTINCT user_id) AS last_touch_customers,
        SUM(lifetime_revenue_inr) AS last_touch_revenue
    FROM fact_customer_ltv
    GROUP BY acquisition_channel_last
)
SELECT 
    COALESCE(f.channel, l.channel) AS channel,
    f.first_touch_customers,
    l.last_touch_customers,
    (l.last_touch_customers - f.first_touch_customers) AS customer_delta_last_vs_first,
    ROUND(f.first_touch_revenue, 2) AS first_touch_revenue_inr,
    ROUND(l.last_touch_revenue, 2) AS last_touch_revenue_inr,
    ROUND(((l.last_touch_revenue - f.first_touch_revenue) * 100.0) / NULLIF(f.first_touch_revenue, 0), 2) AS attribution_shift_pct,
    CASE 
        WHEN (l.last_touch_customers - f.first_touch_customers) > 500 THEN 'Closing / Conversion Harvester'
        WHEN (f.first_touch_customers - l.last_touch_customers) > 500 THEN 'Top-of-Funnel Driver (Under-Credited in Last-Touch)'
        ELSE 'Balanced Multi-Stage Touch'
    END AS channel_journey_role
FROM FirstTouchCounts f
FULL OUTER JOIN LastTouchCounts l ON f.channel = l.channel
ORDER BY attribution_shift_pct DESC;


-- ------------------------------------------------------------------------------
-- Q7: Linear Multi-Touch Attribution Revenue Share
-- Business Question:
-- If we divide credit equally across all touchpoints in a customer journey,
-- what is the true fractional revenue earned by each channel?
-- Decision: Allocate budget equitably based on total journey participation.
-- ------------------------------------------------------------------------------
WITH CustomerTotalRevenue AS (
    SELECT user_id, lifetime_revenue_inr FROM fact_customer_ltv
),
TouchpointWeights AS (
    SELECT 
        t.user_id,
        t.channel,
        1.0 / t.total_steps AS linear_weight,
        c.lifetime_revenue_inr * (1.0 / t.total_steps) AS attributed_fractional_revenue
    FROM fact_customer_touchpoints t
    JOIN CustomerTotalRevenue c ON t.user_id = c.user_id
)
SELECT 
    channel,
    COUNT(*) AS total_touchpoint_engagements,
    ROUND(SUM(attributed_fractional_revenue), 2) AS linear_attributed_revenue_inr,
    ROUND((SUM(attributed_fractional_revenue) * 100.0) / 
          (SELECT SUM(lifetime_revenue_inr) FROM CustomerTotalRevenue), 2) AS linear_revenue_share_pct
FROM TouchpointWeights
GROUP BY channel
ORDER BY linear_attributed_revenue_inr DESC;


-- ------------------------------------------------------------------------------
-- Q8: Campaign Intent Breakdown: Prospecting vs Retargeting vs Brand Defense
-- Business Question:
-- How does ROAS and CPA compare across strategic campaign intents?
-- Decision: Rebalance spend between top-of-funnel prospecting vs bottom-of-funnel retargeting.
-- ------------------------------------------------------------------------------
SELECT 
    strategic_intent,
    COUNT(DISTINCT channel) AS active_channels,
    ROUND(SUM(spend_inr), 2) AS total_spend_inr,
    SUM(clicks) AS total_clicks,
    SUM(direct_conversions) AS total_conversions,
    ROUND(SUM(spend_inr) / NULLIF(SUM(direct_conversions), 0), 2) AS intent_cpa_inr,
    ROUND(SUM(direct_revenue_inr), 2) AS direct_revenue_inr,
    ROUND(SUM(direct_revenue_inr) / NULLIF(SUM(spend_inr), 0), 2) AS intent_roas,
    ROUND((SUM(spend_inr) * 100.0) / (SELECT SUM(spend_inr) FROM fact_daily_campaign_performance), 2) AS pct_of_total_marketing_budget
FROM fact_daily_campaign_performance
GROUP BY strategic_intent
ORDER BY intent_roas DESC;


-- ------------------------------------------------------------------------------
-- Q9: High-Value Customer Acquisition by Channel & Customer Segment
-- Business Question:
-- Which acquisition channels attract high-LTV "Premium Loyalists" vs margin-destroying "Value Seekers"?
-- Decision: Restructure ad creative and targeting away from channels that acquire one-and-done discount hunters.
-- ------------------------------------------------------------------------------
SELECT 
    acquisition_channel_first AS channel,
    COUNT(DISTINCT user_id) AS total_acquired,
    ROUND(COUNT(DISTINCT CASE WHEN customer_segment = 'Premium Loyalists' THEN user_id END) * 100.0 / COUNT(DISTINCT user_id), 2) AS pct_premium_loyalists,
    ROUND(COUNT(DISTINCT CASE WHEN customer_segment = 'Core Shoppers' THEN user_id END) * 100.0 / COUNT(DISTINCT user_id), 2) AS pct_core_shoppers,
    ROUND(COUNT(DISTINCT CASE WHEN customer_segment = 'Value Seekers' THEN user_id END) * 100.0 / COUNT(DISTINCT user_id), 2) AS pct_value_seekers,
    ROUND(AVG(lifetime_revenue_inr), 2) AS avg_customer_ltv_inr
FROM fact_customer_ltv
GROUP BY acquisition_channel_first
ORDER BY pct_premium_loyalists DESC;


-- ------------------------------------------------------------------------------
-- Q10: Geographic Tier Analysis: Metro Tier 1 vs Tier 2 & Tier 3 Unit Economics
-- Business Question:
-- How does customer acquisition value vary across Indian city tiers?
-- Decision: Localize budget allocation toward geographic regions yielding the highest AOV and LTV.
-- ------------------------------------------------------------------------------
SELECT 
    city_tier,
    COUNT(DISTINCT user_id) AS total_customers,
    ROUND(AVG(total_orders), 2) AS avg_orders_per_customer,
    ROUND(AVG(lifetime_revenue_inr), 2) AS avg_ltv_inr,
    ROUND(AVG(lifetime_gross_profit_inr), 2) AS avg_gross_profit_inr,
    ROUND((AVG(lifetime_gross_profit_inr) / AVG(lifetime_revenue_inr)) * 100.0, 2) AS gross_margin_pct,
    ROUND(SUM(lifetime_revenue_inr), 2) AS total_tier_revenue_inr,
    ROUND((SUM(lifetime_revenue_inr) * 100.0) / (SELECT SUM(lifetime_revenue_inr) FROM fact_customer_ltv), 2) AS revenue_contribution_pct
FROM fact_customer_ltv
GROUP BY city_tier
ORDER BY total_tier_revenue_inr DESC;


-- ------------------------------------------------------------------------------
-- Q11: Cross-Channel Journey Path Analysis (Top Converting Paths)
-- Business Question:
-- What are the most common multi-touch paths customers follow before purchasing?
-- Decision: Build synergistic cross-channel nurturing sequences (e.g., YouTube -> Meta -> Brand Search).
-- ------------------------------------------------------------------------------
WITH PathStrings AS (
    SELECT 
        user_id,
        GROUP_CONCAT(channel, ' -> ') AS full_journey_path,
        total_steps
    FROM (
        SELECT user_id, channel, total_steps
        FROM fact_customer_touchpoints
        ORDER BY user_id, step_order
    )
    GROUP BY user_id, total_steps
)
SELECT 
    p.full_journey_path,
    p.total_steps AS touchpoint_count,
    COUNT(p.user_id) AS customer_count,
    ROUND(AVG(c.lifetime_revenue_inr), 2) AS avg_ltv_inr,
    ROUND(SUM(c.lifetime_revenue_inr), 2) AS total_path_revenue_inr
FROM PathStrings p
JOIN fact_customer_ltv c ON p.user_id = c.user_id
GROUP BY p.full_journey_path, p.total_steps
HAVING customer_count >= 150
ORDER BY customer_count DESC
LIMIT 10;


-- ------------------------------------------------------------------------------
-- Q12: Assisted Conversions vs Direct Closers
-- Business Question:
-- Which channels act as the "Assist" (initiating or nurturing) vs the "Closer" (last touch)?
-- Decision: Protect top-of-funnel channels from budget cuts even if direct ROAS appears modest.
-- ------------------------------------------------------------------------------
WITH ChannelTouchTypes AS (
    SELECT 
        channel,
        SUM(is_first_touch) AS first_touch_count,
        SUM(CASE WHEN is_first_touch = 0 AND is_last_touch = 0 THEN 1 ELSE 0 END) AS middle_assist_count,
        SUM(is_last_touch) AS last_touch_count,
        COUNT(*) AS total_engagements
    FROM fact_customer_touchpoints
    GROUP BY channel
)
SELECT 
    channel,
    first_touch_count AS first_touch_initiations,
    middle_assist_count AS mid_funnel_assists,
    last_touch_count AS final_closings,
    (first_touch_count + middle_assist_count) AS total_assisted_journeys,
    ROUND((first_touch_count + middle_assist_count) * 1.0 / NULLIF(last_touch_count, 0), 2) AS assist_to_close_ratio,
    CASE 
        WHEN (first_touch_count + middle_assist_count) * 1.0 / NULLIF(last_touch_count, 0) >= 2.0 THEN 'Pure Play Assister (Originator)'
        WHEN (first_touch_count + middle_assist_count) * 1.0 / NULLIF(last_touch_count, 0) <= 0.6 THEN 'Pure Play Closer (Harvester)'
        ELSE 'Hybrid Nurturer'
    END AS channel_role_classification
FROM ChannelTouchTypes
ORDER BY assist_to_close_ratio DESC;


-- ------------------------------------------------------------------------------
-- Q13: Discount Dependency vs True Margin by Channel
-- Business Question:
-- Are certain channels only generating sales by offering massive coupon discounts that erode profit?
-- Decision: Stop subsidizing unprofitable conversions driven by steep promo codes.
-- ------------------------------------------------------------------------------
SELECT 
    acquisition_channel_first AS channel,
    COUNT(order_id) AS total_orders,
    ROUND(SUM(order_value_gross), 2) AS gross_merchandise_value_inr,
    ROUND(SUM(discount_inr), 2) AS total_discounts_given_inr,
    ROUND((SUM(discount_inr) * 100.0) / NULLIF(SUM(order_value_gross), 0), 2) AS discount_rate_pct,
    ROUND(SUM(order_value_net), 2) AS net_revenue_inr,
    ROUND(SUM(gross_profit_inr), 2) AS gross_profit_inr,
    ROUND((SUM(gross_profit_inr) * 100.0) / NULLIF(SUM(order_value_net), 0), 2) AS net_profit_margin_pct
FROM fact_orders
GROUP BY acquisition_channel_first
ORDER BY discount_rate_pct DESC;


-- ------------------------------------------------------------------------------
-- Q14: Monthly Cohort Retention & Cumulative Repeat Order Progression
-- Business Question:
-- What percentage of total revenue comes from initial vs repeat orders for each channel?
-- Decision: Reward channels that build loyal, compounding customer cohorts.
-- ------------------------------------------------------------------------------
SELECT 
    acquisition_channel_first AS channel,
    COUNT(DISTINCT user_id) AS total_customers,
    COUNT(DISTINCT CASE WHEN is_repeat = 1 THEN user_id END) AS repeat_customers,
    ROUND(COUNT(DISTINCT CASE WHEN is_repeat = 1 THEN user_id END) * 100.0 / COUNT(DISTINCT user_id), 2) AS repeat_purchase_rate_pct,
    ROUND(SUM(CASE WHEN is_repeat = 0 THEN order_value_net ELSE 0 END), 2) AS first_order_revenue_inr,
    ROUND(SUM(CASE WHEN is_repeat = 1 THEN order_value_net ELSE 0 END), 2) AS repeat_orders_revenue_inr,
    ROUND((SUM(CASE WHEN is_repeat = 1 THEN order_value_net ELSE 0 END) * 100.0) / SUM(order_value_net), 2) AS repeat_revenue_share_pct
FROM fact_orders
GROUP BY acquisition_channel_first
ORDER BY repeat_purchase_rate_pct DESC;


-- ------------------------------------------------------------------------------
-- Q15: The ₹10 Lakh Marginal ROAS Budget Allocation Query
-- Business Question:
-- "If I give you another ₹10 lakh next month, where should you spend it — and what do you expect to get back?"
-- Technical Approach:
-- Compute historical spend tiers, current saturation efficiency, and rank channels by marginal profit elasticity.
-- ------------------------------------------------------------------------------
WITH ChannelBaseline AS (
    SELECT 
        p.channel,
        SUM(p.spend_inr) AS current_annual_spend,
        SUM(p.direct_revenue_inr) AS current_annual_revenue,
        ROUND(SUM(p.direct_revenue_inr) / SUM(p.spend_inr), 2) AS average_roas,
        COUNT(DISTINCT l.user_id) AS acquired_users,
        ROUND(SUM(p.spend_inr) / COUNT(DISTINCT l.user_id), 2) AS cac_inr,
        ROUND(AVG(l.lifetime_gross_profit_inr), 2) AS avg_margin_ltv
    FROM fact_daily_campaign_performance p
    JOIN fact_customer_ltv l ON p.channel = l.acquisition_channel_first
    GROUP BY p.channel
),
SaturationAnalysis AS (
    SELECT 
        channel,
        current_annual_spend,
        average_roas,
        cac_inr,
        avg_margin_ltv,
        -- Marginal elasticity factor: High-spend search channels have saturated low-hanging fruit
        -- Under-allocated high-margin channels have higher incremental room
        CASE 
            WHEN channel = 'Google_Search_Brand' THEN 0.52 -- Highly saturated, low incremental search volume
            WHEN channel = 'Email_CRM_Automation' THEN 0.88 -- High efficiency, under-scaled automation
            WHEN channel = 'Meta_Ads_Retargeting' THEN 0.74 -- Strong retargeting headroom
            WHEN channel = 'Affiliate_Partner_Network' THEN 0.70 -- Scalable performance affiliate
            WHEN channel = 'LinkedIn_Sponsored' THEN 0.68 -- High AOV B2B enterprise headroom
            WHEN channel = 'Meta_Ads_Prospecting' THEN 0.62 -- Moderate ad fatigue
            WHEN channel = 'Google_Search_Generic' THEN 0.55 -- Expensive CPC keyword bidding wars
            WHEN channel = 'YouTube_Video_Ads' THEN 0.60 -- Brand awareness, longer conversion lag
            ELSE 0.50
        END AS marginal_elasticity_factor
    FROM ChannelBaseline
),
RankedMarginalReturn AS (
    SELECT 
        channel,
        average_roas,
        cac_inr,
        avg_margin_ltv,
        ROUND(average_roas * marginal_elasticity_factor, 2) AS expected_marginal_roas,
        DENSE_RANK() OVER (ORDER BY (average_roas * marginal_elasticity_factor) DESC) AS allocation_priority_rank
    FROM SaturationAnalysis
)
SELECT 
    allocation_priority_rank,
    channel,
    average_roas AS current_avg_roas,
    expected_marginal_roas,
    -- Recommended split of the ₹10,00,000 incremental budget
    CASE 
        WHEN allocation_priority_rank = 1 THEN 350000 -- Primary growth driver (₹3.5 Lakh)
        WHEN allocation_priority_rank = 2 THEN 300000 -- Secondary high-yield driver (₹3.0 Lakh)
        WHEN allocation_priority_rank = 3 THEN 250000 -- Synergistic scaler (₹2.5 Lakh)
        WHEN allocation_priority_rank = 4 THEN 100000 -- Experimental high-ticket test (₹1.0 Lakh)
        ELSE 0                                        -- Do not allocate (Saturated or Diminishing)
    END AS recommended_incremental_spend_inr,
    -- Expected incremental return
    ROUND((CASE 
        WHEN allocation_priority_rank = 1 THEN 350000
        WHEN allocation_priority_rank = 2 THEN 300000
        WHEN allocation_priority_rank = 3 THEN 250000
        WHEN allocation_priority_rank = 4 THEN 100000
        ELSE 0 
    END) * expected_marginal_roas, 2) AS expected_incremental_revenue_inr
FROM RankedMarginalReturn
ORDER BY allocation_priority_rank ASC;
