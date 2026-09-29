"""
attribution_engine.py
Enterprise Marketing Performance & Capital Allocation Analytics

Implements 5 Multi-Touch Attribution (MTA) Models:
1. First-Touch Attribution (100% to journey originator)
2. Last-Touch Attribution (100% to conversion closer)
3. Linear Attribution (equal split across all touchpoints)
4. Position-Based (U-Shaped) Attribution (40% first, 40% last, 20% distributed across middle)
5. Time-Decay Attribution (exponential decay half-life = 7 days)

Exports comparison matrix and evaluates the "Last-Touch Bias".
"""

import os
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "marketing_analytics.db")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "cleaned")

def calculate_multi_touch_attribution():
    print("=" * 60)
    print("RUNNING MULTI-TOUCH ATTRIBUTION (MTA) ENGINE")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Load Touchpoints and Customer Revenue
    touchpoints_df = pd.read_sql_query("""
        SELECT 
            t.touchpoint_id,
            t.user_id,
            t.channel,
            t.step_order,
            t.total_steps,
            t.is_first_touch,
            t.is_last_touch,
            t.timestamp,
            c.lifetime_revenue_inr
        FROM fact_customer_touchpoints t
        JOIN fact_customer_ltv c ON t.user_id = c.user_id
        ORDER BY t.user_id, t.step_order
    """, conn)
    
    # Load ad spend per channel for CAC / ROAS comparisons
    spend_df = pd.read_sql_query("""
        SELECT channel, SUM(spend_inr) as total_spend_inr
        FROM fact_daily_campaign_performance
        GROUP BY channel
    """, conn)
    conn.close()

    touchpoints_df['timestamp'] = pd.to_datetime(touchpoints_df['timestamp'])
    
    # Compute conversion timestamp (timestamp of last touchpoint for each user)
    last_touch_times = touchpoints_df.groupby('user_id')['timestamp'].transform('max')
    touchpoints_df['days_before_conversion'] = (last_touch_times - touchpoints_df['timestamp']).dt.total_seconds() / 86400.0

    # -------------------------------------------------------------
    # 2. Model 1: First-Touch Weights
    # -------------------------------------------------------------
    touchpoints_df['weight_first_touch'] = touchpoints_df['is_first_touch'].astype(float)

    # -------------------------------------------------------------
    # 3. Model 2: Last-Touch Weights
    # -------------------------------------------------------------
    touchpoints_df['weight_last_touch'] = touchpoints_df['is_last_touch'].astype(float)

    # -------------------------------------------------------------
    # 4. Model 3: Linear Weights
    # -------------------------------------------------------------
    touchpoints_df['weight_linear'] = 1.0 / touchpoints_df['total_steps']

    # -------------------------------------------------------------
    # 5. Model 4: Position-Based (U-Shaped: 40% First, 40% Last, 20% Middle)
    # -------------------------------------------------------------
    def compute_position_weight(row):
        total = row['total_steps']
        if total == 1:
            return 1.0
        elif total == 2:
            return 0.50
        else:
            if row['is_first_touch'] == 1 or row['is_last_touch'] == 1:
                return 0.40
            else:
                mid_count = total - 2
                return 0.20 / mid_count

    touchpoints_df['weight_position_based'] = touchpoints_df.apply(compute_position_weight, axis=1)

    # -------------------------------------------------------------
    # 6. Model 5: Time-Decay Weights (7-day Half-Life)
    # -------------------------------------------------------------
    # weight = 2 ^ (-delta_days / half_life)
    HALF_LIFE_DAYS = 7.0
    touchpoints_df['raw_time_decay'] = 2 ** (-touchpoints_df['days_before_conversion'] / HALF_LIFE_DAYS)
    # Normalize per user so sum = 1.0
    user_time_decay_sum = touchpoints_df.groupby('user_id')['raw_time_decay'].transform('sum')
    touchpoints_df['weight_time_decay'] = touchpoints_df['raw_time_decay'] / user_time_decay_sum

    # -------------------------------------------------------------
    # 7. Aggregate Attributed Revenue by Channel
    # -------------------------------------------------------------
    models = ['first_touch', 'last_touch', 'linear', 'position_based', 'time_decay']
    attribution_results = {}

    for m in models:
        touchpoints_df[f'revenue_{m}'] = touchpoints_df[f'weight_{m}'] * touchpoints_df['lifetime_revenue_inr']
        ch_rev = touchpoints_df.groupby('channel')[f'revenue_{m}'].sum()
        attribution_results[m] = ch_rev

    mta_summary = pd.DataFrame(attribution_results)
    
    # Merge with Ad Spend to calculate Attributed ROAS across models
    mta_summary = mta_summary.reset_index().rename(columns={'channel': 'channel'})
    mta_summary = mta_summary.merge(spend_df, on='channel', how='left')

    for m in models:
        mta_summary[f'roas_{m}'] = round(mta_summary[m] / mta_summary['total_spend_inr'], 2)
        mta_summary[m] = round(mta_summary[m], 2)

    # Calculate Last-Touch Bias (% change between Linear and Last-Touch)
    mta_summary['last_touch_bias_pct'] = round(
        ((mta_summary['last_touch'] - mta_summary['linear']) / mta_summary['linear']) * 100, 2
    )

    output_csv = os.path.join(OUTPUT_DIR, "mta_model_comparison.csv")
    mta_summary.to_csv(output_csv, index=False)
    
    print("\n--- Multi-Touch Attribution Summary (INR) ---")
    cols_to_print = ['channel', 'total_spend_inr', 'first_touch', 'last_touch', 'linear', 'position_based', 'last_touch_bias_pct']
    print(mta_summary[cols_to_print].to_string(index=False))
    print(f"\nSaved MTA Model comparison to: {output_csv}")

    return mta_summary

if __name__ == "__main__":
    calculate_multi_touch_attribution()
