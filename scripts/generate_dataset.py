"""
generate_dataset.py
Enterprise Marketing Performance & Capital Allocation Analytics

Generates a realistic, cohesive multi-channel marketing dataset:
1. raw/marketing_campaigns_raw.csv: Daily campaign-level impressions, clicks, spend, leads.
2. raw/customer_touchpoints_raw.csv: Multi-touch user journeys across channels before conversion.
3. raw/customer_orders_raw.csv: Transaction records with order value, COGS, discounts, repeat orders.
4. raw/customer_profiles_raw.csv: Customer demographics, segment, city tier, and calculated 12-month LTV.
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Fix seed for reproducibility
np.random.seed(42)
random.seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(RAW_DATA_DIR, exist_ok=True)

START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 12, 31)
NUM_DAYS = (END_DATE - START_DATE).days + 1

# Define Channels and characteristics
CHANNELS = {
    "Google_Search_Brand": {
        "type": "Search",
        "intent": "High Intent / Brand Defense",
        "avg_cpc": 18.5,
        "ctr": 0.085,
        "conv_rate": 0.092,
        "base_daily_spend": 12000,
        "spend_variance": 2000,
        "diminishing_alpha": 18000,
        "saturation_limit": 35000,
    },
    "Google_Search_Generic": {
        "type": "Search",
        "intent": "Prospecting",
        "avg_cpc": 45.0,
        "ctr": 0.038,
        "conv_rate": 0.031,
        "base_daily_spend": 32000,
        "spend_variance": 5000,
        "diminishing_alpha": 12000,
        "saturation_limit": 60000,
    },
    "Meta_Ads_Prospecting": {
        "type": "Social",
        "intent": "Prospecting / Discovery",
        "avg_cpc": 24.0,
        "ctr": 0.022,
        "conv_rate": 0.024,
        "base_daily_spend": 38000,
        "spend_variance": 6000,
        "diminishing_alpha": 14000,
        "saturation_limit": 70000,
    },
    "Meta_Ads_Retargeting": {
        "type": "Social",
        "intent": "Retargeting",
        "avg_cpc": 28.0,
        "ctr": 0.048,
        "conv_rate": 0.065,
        "base_daily_spend": 15000,
        "spend_variance": 2500,
        "diminishing_alpha": 19000,
        "saturation_limit": 28000,
    },
    "YouTube_Video_Ads": {
        "type": "Video",
        "intent": "Top of Funnel / Awareness",
        "avg_cpc": 12.0,
        "ctr": 0.012,
        "conv_rate": 0.009,
        "base_daily_spend": 20000,
        "spend_variance": 4000,
        "diminishing_alpha": 8000,
        "saturation_limit": 50000,
    },
    "LinkedIn_Sponsored": {
        "type": "B2B_Social",
        "intent": "High-Value Acquisition",
        "avg_cpc": 95.0,
        "ctr": 0.016,
        "conv_rate": 0.028,
        "base_daily_spend": 18000,
        "spend_variance": 3000,
        "diminishing_alpha": 11000,
        "saturation_limit": 30000,
    },
    "Affiliate_Partner_Network": {
        "type": "Affiliate",
        "intent": "Performance CPA",
        "avg_cpc": 16.0,
        "ctr": 0.031,
        "conv_rate": 0.038,
        "base_daily_spend": 14000,
        "spend_variance": 3500,
        "diminishing_alpha": 15000,
        "saturation_limit": 32000,
    },
    "Email_CRM_Automation": {
        "type": "CRM",
        "intent": "Retention & Re-engagement",
        "avg_cpc": 1.5,
        "ctr": 0.120,
        "conv_rate": 0.075,
        "base_daily_spend": 3000,
        "spend_variance": 800,
        "diminishing_alpha": 25000,
        "saturation_limit": 10000,
    },
}

GEOGRAPHIES = [
    ("Tier 1 - Mumbai", 0.22, 1.20),
    ("Tier 1 - Delhi NCR", 0.20, 1.15),
    ("Tier 1 - Bengaluru", 0.18, 1.25),
    ("Tier 2 - Pune", 0.10, 0.95),
    ("Tier 2 - Hyderabad", 0.12, 1.05),
    ("Tier 2 - Ahmedabad", 0.08, 0.90),
    ("Tier 3 - Other Urban", 0.10, 0.80),
]

CUSTOMER_SEGMENTS = [
    ("Value Seekers", 0.40, 1800, 0.18),    # Low AOV, high discount reliance, lower repeat
    ("Core Shoppers", 0.35, 3200, 0.08),    # Solid AOV, steady repeat rate
    ("Premium Loyalists", 0.25, 6800, 0.03) # High AOV, high LTV, minimal discounts
]

def generate_daily_campaigns():
    """Generates daily marketing campaign records."""
    records = []
    campaign_id_seq = 1001

    for channel_name, cfg in CHANNELS.items():
        for d in range(NUM_DAYS):
            cur_date = START_DATE + timedelta(days=d)
            
            # Seasonality boost: Diwali / Festive (Oct-Nov) and Summer sale (May)
            seasonality = 1.0
            if cur_date.month in [10, 11]:
                seasonality = 1.35
            elif cur_date.month in [5, 12]:
                seasonality = 1.15
            elif cur_date.weekday() in [5, 6]: # Weekend boost
                seasonality *= 1.10

            # Daily spend with diminishing return effect on efficiency
            spend = max(500, np.random.normal(cfg["base_daily_spend"] * seasonality, cfg["spend_variance"]))
            
            # Clicks & CPC calculation with spend inflation if over-saturated
            spend_ratio = spend / cfg["saturation_limit"]
            cpc_inflation = 1.0 + (0.35 * (spend_ratio ** 1.8) if spend_ratio > 0.8 else 0.0)
            actual_cpc = cfg["avg_cpc"] * cpc_inflation * np.random.uniform(0.92, 1.08)
            clicks = int(spend / actual_cpc)
            
            # Impressions based on CTR
            ctr = cfg["ctr"] * np.random.uniform(0.88, 1.12)
            impressions = int(clicks / max(0.005, ctr))
            
            # Leads / Add to Carts (intermediate step in the chain)
            lead_rate = cfg["conv_rate"] * 2.2 * np.random.uniform(0.9, 1.1)
            leads = int(clicks * lead_rate)
            
            # Direct Last-Touch Conversions
            direct_conv_rate = cfg["conv_rate"] * np.random.uniform(0.9, 1.1)
            conversions = int(clicks * direct_conv_rate)
            
            # Direct Attributed Revenue
            # Average order value baseline around 3200 INR
            aov = 3400 * np.random.uniform(0.85, 1.25)
            if "LinkedIn" in channel_name:
                aov *= 1.8  # B2B higher value
            elif "Affiliate" in channel_name or "YouTube" in channel_name:
                aov *= 0.9
                
            attributed_revenue = round(conversions * aov, 2)

            records.append({
                "date": cur_date.strftime("%Y-%m-%d"),
                "campaign_id": f"CMP_{campaign_id_seq + (list(CHANNELS.keys()).index(channel_name))}",
                "channel": channel_name,
                "channel_type": cfg["type"],
                "strategic_intent": cfg["intent"],
                "impressions": impressions,
                "clicks": clicks,
                "spend_inr": round(spend, 2),
                "leads": leads,
                "direct_conversions": conversions,
                "direct_revenue_inr": attributed_revenue
            })
            
    df = pd.DataFrame(records)
    output_path = os.path.join(RAW_DATA_DIR, "marketing_campaigns_raw.csv")
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} daily campaign records -> {output_path}")
    return df

def generate_customers_and_journeys():
    """
    Generates multi-touch journeys, orders, and customer lifetime records.
    Crucial for Multi-Touch Attribution, LTV:CAC, and Payback calculations.
    """
    num_customers = 18000
    customer_records = []
    touchpoint_records = []
    order_records = []
    
    geo_names, geo_probs, geo_aov_mults = zip(*GEOGRAPHIES)
    seg_names, seg_probs, seg_base_aovs = zip(*[(s[0], s[1], s[2]) for s in CUSTOMER_SEGMENTS])
    
    # Touchpoint probability weights by intent
    # YouTube and Meta Prospecting often serve as First Touch
    # Google Brand Search and Email CRM often serve as Last Touch
    first_touch_weights = {
        "YouTube_Video_Ads": 0.24,
        "Meta_Ads_Prospecting": 0.30,
        "Google_Search_Generic": 0.22,
        "Affiliate_Partner_Network": 0.12,
        "Google_Search_Brand": 0.08,
        "LinkedIn_Sponsored": 0.04
    }
    
    mid_touch_weights = {
        "Meta_Ads_Prospecting": 0.25,
        "Meta_Ads_Retargeting": 0.35,
        "Google_Search_Generic": 0.20,
        "Email_CRM_Automation": 0.10,
        "YouTube_Video_Ads": 0.10
    }
    
    last_touch_weights = {
        "Google_Search_Brand": 0.38,
        "Meta_Ads_Retargeting": 0.28,
        "Email_CRM_Automation": 0.16,
        "Affiliate_Partner_Network": 0.10,
        "Google_Search_Generic": 0.08
    }

    touchpoint_id = 1
    order_id = 50001
    
    for c_idx in range(1, num_customers + 1):
        user_id = f"USR_{100000 + c_idx}"
        
        # Pick geography & segment
        geo = random.choices(geo_names, weights=geo_probs)[0]
        geo_mult = geo_aov_mults[geo_names.index(geo)]
        
        seg = random.choices(seg_names, weights=seg_probs)[0]
        base_aov = seg_base_aovs[seg_names.index(seg)]
        
        # Journey length (number of touchpoints prior to conversion)
        # 30% have 1 touchpoint, 40% have 2-3, 30% have 4-6
        journey_type = np.random.choice(["direct_single", "medium_path", "long_path"], p=[0.25, 0.50, 0.25])
        if journey_type == "direct_single":
            path_len = 1
        elif journey_type == "medium_path":
            path_len = random.randint(2, 3)
        else:
            path_len = random.randint(4, 6)
            
        # First acquisition timestamp in 2025
        random_day = random.randint(0, NUM_DAYS - 30)
        user_start_time = START_DATE + timedelta(days=random_day, hours=random.randint(8, 22))
        
        # Generate touchpoint sequence
        journey_channels = []
        # First touch
        first_ch = random.choices(list(first_touch_weights.keys()), weights=list(first_touch_weights.values()))[0]
        journey_channels.append(first_ch)
        
        # Middle touches
        for _ in range(path_len - 2):
            mid_ch = random.choices(list(mid_touch_weights.keys()), weights=list(mid_touch_weights.values()))[0]
            journey_channels.append(mid_ch)
            
        # Last touch (if path_len > 1)
        if path_len > 1:
            last_ch = random.choices(list(last_touch_weights.keys()), weights=list(last_touch_weights.values()))[0]
            journey_channels.append(last_ch)
            
        # Write touchpoints
        cur_touch_time = user_start_time
        for step_idx, ch in enumerate(journey_channels):
            touchpoint_records.append({
                "touchpoint_id": touchpoint_id,
                "user_id": user_id,
                "channel": ch,
                "step_order": step_idx + 1,
                "total_steps": path_len,
                "is_first_touch": 1 if step_idx == 0 else 0,
                "is_last_touch": 1 if step_idx == (path_len - 1) else 0,
                "timestamp": cur_touch_time.strftime("%Y-%m-%d %H:%M:%S")
            })
            touchpoint_id += 1
            # Step forward in time (hours to days between touches)
            cur_touch_time += timedelta(days=random.randint(0, 3), hours=random.randint(1, 14))

        conversion_time = cur_touch_time
        
        # Repeat purchases and Orders
        # Segments behave differently
        if seg == "Value Seekers":
            num_orders = np.random.choice([1, 2, 3], p=[0.75, 0.20, 0.05])
            discount_pct = np.random.uniform(0.15, 0.30)
            cogs_ratio = 0.58  # 42% gross margin
        elif seg == "Core Shoppers":
            num_orders = np.random.choice([1, 2, 3, 4], p=[0.45, 0.35, 0.15, 0.05])
            discount_pct = np.random.uniform(0.05, 0.15)
            cogs_ratio = 0.50  # 50% gross margin
        else: # Premium Loyalists
            num_orders = np.random.choice([1, 2, 3, 5, 8], p=[0.20, 0.30, 0.25, 0.15, 0.10])
            discount_pct = np.random.uniform(0.0, 0.05)
            cogs_ratio = 0.42  # 58% gross margin
            
        total_customer_revenue = 0
        total_customer_cogs = 0
        
        order_time = conversion_time
        for o_num in range(1, num_orders + 1):
            order_val = base_aov * geo_mult * np.random.uniform(0.9, 1.15)
            discount_val = round(order_val * discount_pct, 2)
            net_order_val = round(order_val - discount_val, 2)
            order_cogs = round(net_order_val * cogs_ratio, 2)
            gross_profit = round(net_order_val - order_cogs, 2)
            
            total_customer_revenue += net_order_val
            total_customer_cogs += order_cogs
            
            order_records.append({
                "order_id": f"ORD_{order_id}",
                "user_id": user_id,
                "order_number": o_num,
                "order_date": order_time.strftime("%Y-%m-%d"),
                "order_value_gross": round(order_val, 2),
                "discount_inr": discount_val,
                "order_value_net": net_order_val,
                "cogs_inr": order_cogs,
                "gross_profit_inr": gross_profit,
                "acquisition_channel_first": journey_channels[0],
                "acquisition_channel_last": journey_channels[-1],
                "is_repeat": 1 if o_num > 1 else 0
            })
            order_id += 1
            # Interval to next repeat order (30 to 90 days)
            order_time += timedelta(days=random.randint(25, 75))
            if order_time > END_DATE:
                break

        # Customer profile record
        tenure_days = max(1, (min(END_DATE, order_time) - user_start_time).days)
        customer_records.append({
            "user_id": user_id,
            "acquisition_date": user_start_time.strftime("%Y-%m-%d"),
            "acquisition_channel_first": journey_channels[0],
            "acquisition_channel_last": journey_channels[-1],
            "geography": geo,
            "city_tier": geo.split(" - ")[0],
            "customer_segment": seg,
            "total_orders": num_orders,
            "lifetime_revenue_inr": round(total_customer_revenue, 2),
            "lifetime_gross_profit_inr": round(total_customer_revenue - total_customer_cogs, 2),
            "tenure_days": tenure_days
        })
        
    df_touch = pd.DataFrame(touchpoint_records)
    df_orders = pd.DataFrame(order_records)
    df_cust = pd.DataFrame(customer_records)
    
    df_touch.to_csv(os.path.join(RAW_DATA_DIR, "customer_touchpoints_raw.csv"), index=False)
    df_orders.to_csv(os.path.join(RAW_DATA_DIR, "customer_orders_raw.csv"), index=False)
    df_cust.to_csv(os.path.join(RAW_DATA_DIR, "customer_profiles_raw.csv"), index=False)
    
    print(f"Generated {len(df_touch)} touchpoints -> customer_touchpoints_raw.csv")
    print(f"Generated {len(df_orders)} orders -> customer_orders_raw.csv")
    print(f"Generated {len(df_cust)} customer profiles -> customer_profiles_raw.csv")

if __name__ == "__main__":
    print("Beginning dataset generation for Project 5...")
    generate_daily_campaigns()
    generate_customers_and_journeys()
    print("Dataset generation complete!")
