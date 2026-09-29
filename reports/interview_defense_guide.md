# Interview Defense Guide: Marketing Performance & ROI Analytics

> *"A portfolio of five copied projects is not impressive. A portfolio of five projects you can defend in an interview is."*

This document provides exact answers, formulas, numbers, and defense arguments to confidently answer any technical or business question about this project without opening the files.

---

## 1. The Keystone Question (Must Memorize)

### Question:
> **"If I give you another ₹10 lakh next month, where should you spend it — and what do you expect to get back?"**

### Your Answer:
> *"I would allocate the ₹10 Lakh across five specific channels based on their marginal ROAS and current saturation curves, generating **₹35.98 Lakh in incremental net revenue** and **₹8.13 Lakh in net contribution profit**, delivering a **3.60x blended marginal ROAS**.*
>
> *Here is the exact allocation:*
> 1. *₹3,50,000 (35%) into Meta Ads Retargeting $\rightarrow$ Expected mROAS of 4.20x $\rightarrow$ ₹14.70 Lakh revenue.*
> 2. *₹3,00,000 (30%) into Affiliate Partner Network $\rightarrow$ Expected mROAS of 3.45x $\rightarrow$ ₹10.35 Lakh revenue.*
> 3. *₹1,50,000 (15%) into LinkedIn Sponsored Ads $\rightarrow$ Expected mROAS of 2.80x $\rightarrow$ ₹4.20 Lakh revenue (acquiring high-AOV enterprise buyers).*
> 4. *₹1,50,000 (15%) into Meta Ads Prospecting $\rightarrow$ Expected mROAS of 2.65x $\rightarrow$ ₹3.98 Lakh revenue (refilling top-of-funnel audience pools).*
> 5. *₹50,000 (5%) into Email CRM Automations $\rightarrow$ Expected mROAS of 5.50x $\rightarrow$ ₹2.75 Lakh revenue (capped at maximum software/SMS throughput).*
>
> *Crucially, I allocate **₹0 incremental spend to Google Search Brand**, even though it has our highest historical average ROAS (8.21x). Our branded impression share is already at 92%; pouring more capital into brand search simply inflates CPCs and bids against our own organic rankings without generating new demand."*

---

## 2. Follow-Up Interview Questions & Deep Defenses

### Q: "Why not just allocate all ₹10 Lakh into Google Brand Search or Email CRM since they have the highest average ROAS?"
**Defense:**
- **Average ROAS vs Marginal ROAS**: In marketing analytics, average ROAS describes past performance; marginal ROAS dictates future capital efficiency.
- **Diminishing Marginal Returns**: Google Brand Search is constrained by total branded search query volume in the market. Bidding more money does not create more people typing our company name into Google; it merely increases our max CPC bid in the Google Ads auction.
- **Owned Channel Capacity**: Email CRM has near-zero marginal cost, but is strictly constrained by the size of our customer subscriber list. You cannot arbitrarily buy new email audiences on an ad exchange without risking spam penalties and deliverability failure.

---

### Q: "Your dashboard shows YouTube has an ROAS of 0.90x and a high CPA. Shouldn't we pause YouTube to save money?"
**Defense:**
- *"That is the classic **'Last-Touch Trap'**.*
- *If you evaluate channels strictly on Last-Touch Attribution, YouTube looks unprofitable because users rarely click a 15-second YouTube video and buy instantly on a mobile phone.*
- *However, our Multi-Touch Attribution model reveals that **YouTube originates ₹3.09 Crore in First-Touch revenue** across 4,340 acquired customers.*
- *Our cross-channel journey analysis (Query 11 & 12) proved that the most common converting path is: `YouTube (First Touch) -> Meta Retargeting -> Google Brand Search (Closer)`.*
- *If we cut YouTube, Google Brand Search revenue will decline within 60 days because the top of the funnel has dried up."*

---

### Q: "How did you calculate LTV and Payback Period in SQL without creating Cartesian products?"
**Defense:**
- *"A frequent trap when joining daily campaign spend with customer orders is causing a Cartesian product, multiplying spend by order count.*
- *In my SQL implementation (`sql/business_queries.sql`), I used **pre-aggregated Common Table Expressions (CTEs)**:*
  1. *First CTE aggregates total ad spend per channel.*
  2. *Second CTE aggregates user cohort sizes and 12-month gross margin from `fact_customer_ltv`.*
  3. *Third CTE computes first-order gross profit from `fact_orders` where `order_number = 1`.*
- *The Payback Period is calculated as: `CAC / (First-Order Gross Profit * Repeat Velocity Factor)`.*
- *This ensures accurate unit economics without data multiplication."*

---

### Q: "What is your LTV:CAC benchmark and what does it tell you about channel sustainability?"
**Defense:**
- *"We evaluate LTV on a **Gross Margin basis**, not top-line revenue.*
  $$\text{LTV:CAC} = \frac{\text{12-Month Gross Profit Contribution}}{\text{Paid CAC}}$$
- *Our portfolio average is **3.82x**, which is within the healthy SaaS/D2C benchmark of 3.0x to 4.0x.*
- *A ratio below 1.5x indicates value destruction (the customer doesn't even repay their marketing and fulfillment costs).*
- *A ratio above 5.0x indicates under-investment, meaning we are leaving growth on the table."*

---

### Q: "What are the limitations and assumptions in your model?"
**Defense:**
- **30-Day Lookback Window**: Customer touches occurring more than 30 days prior to purchase are not included in attribution weights.
- **Signal Loss (iOS ATT & Privacy)**: Client-side cookies miss cross-device journeys. In production, this is supplemented with server-side CAPI and Media Mix Modeling (MMM).
- **Static Diminishing Returns**: Marginal ROAS was estimated assuming stable competitor bidding; aggressive competitor bids on generic search could further reduce generic ROAS.
