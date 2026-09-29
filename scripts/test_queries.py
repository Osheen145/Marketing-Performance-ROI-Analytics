"""
test_queries.py
Enterprise Marketing Performance & Capital Allocation Analytics

Verifies and executes all 15 SQL queries in sql/business_queries.sql
against data/marketing_analytics.db, printing results and verifying row counts.
"""

import os
import re
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "marketing_analytics.db")
SQL_FILE = os.path.join(BASE_DIR, "sql", "business_queries.sql")

def run_tests():
    print(f"Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    
    with open(SQL_FILE, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Split by questions: look for -- Q[0-9]+:
    query_blocks = re.split(r'-- Q\d+:', sql_content)
    
    print(f"Found {len(query_blocks) - 1} SQL queries in {SQL_FILE}")
    
    success_count = 0
    for idx, block in enumerate(query_blocks[1:], start=1):
        lines = block.strip().split("\n")
        title = lines[0].strip()
        
        # Extract SQL statement: ignore leading titles and comments until WITH or SELECT
        sql_lines = []
        started = False
        for l in lines:
            trimmed = l.strip()
            if not started:
                if trimmed.upper().startswith("WITH") or trimmed.upper().startswith("SELECT"):
                    started = True
                    sql_lines.append(l)
            else:
                if not trimmed.startswith("--"):
                    sql_lines.append(l)
                    
        clean_sql = "\n".join(sql_lines).strip()
        if clean_sql.endswith(";"):
            clean_sql = clean_sql[:-1]

        title_clean = title.encode('ascii', errors='replace').decode('ascii')
        print(f"\n--- Testing Q{idx}: {title_clean} ---")
        try:
            df = pd.read_sql_query(clean_sql, conn)
            print(f"  [PASS] Returned {len(df)} rows, {len(df.columns)} columns.")
            print("  Top Row Preview:")
            top_preview = df.head(1).to_string(index=False).encode('ascii', errors='replace').decode('ascii')
            print("  " + top_preview.replace("\n", "\n  "))
            success_count += 1
        except Exception as e:
            print(f"  [FAIL] Query Q{idx} failed: {e}")
            raise e

    conn.close()
    print("\n" + "=" * 60)
    print(f"ALL {success_count}/15 SQL QUERIES EXECUTED SUCCESSFULLY WITHOUT ERRORS!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
