"""
MONEY DETECTIVE
----------------
Analyzes a transaction history (date, description, amount) and reports:
  1. Total spending by month
  2. Recurring charges / subscriptions
  3. Possible duplicate payments
  4. Repeated payments to the same merchant
  5. Top spending categories
  6. Unusual spending leaks

HOW TO USE:
  - Paste your transactions into the CSV_DATA string below (or point
    CSV_PATH to a real .csv file and set USE_FILE = True).
  - Adjust BASELINE_TOTAL to the figure you already know is correct
    (e.g. your bank statement total), so the script can check its math
    against your own number.
  - Run: python money_detective.py
"""

import csv
import io
from collections import defaultdict
from datetime import datetime

# ----------------------------------------------------------------------
# 1. SETTINGS -- edit these two things
# ----------------------------------------------------------------------

BASELINE_TOTAL = -3650   # <-- put your known total spend here (negative = spent)

USE_FILE = False
CSV_PATH = "transactions.csv"

CSV_DATA = """date,description,amount
2026-07-01,Netflix Subscription,-1100
2026-07-02,Careem Ride,-650
2026-07-03,Foodpanda,-1200
2026-07-03,Foodpanda,-1200
2026-07-05,JazzCash Mobile Load,-500
"""

# ----------------------------------------------------------------------
# 2. CATEGORY RULES -- keyword -> category
#    Add more keywords any time you notice something miscategorized.
# ----------------------------------------------------------------------

CATEGORY_KEYWORDS = {
    "Food": ["foodpanda", "food panda", "restaurant", "cafe", "kfc", "mcdonald",
              "cheezious", "bakery", "grocer", "grocery", "imtiaz", "carrefour"],
    "Transport": ["careem", "uber", "indrive", "petrol", "fuel", "shell", "total parco"],
    "Bills": ["electricity", "gas bill", "water bill", "internet", "wifi",
               "ptcl", "k-electric", "lesco", "sui gas"],
    "Shopping": ["daraz", "shopping", "mall", "clothing", "outfitters", "khaadi"],
    "Subscriptions": ["netflix", "spotify", "youtube premium", "amazon prime",
                        "subscription", "disney"],
    "Mobile Load": ["jazzcash", "easypaisa", "mobile load", "load card",
                      "telenor", "ufone", "zong load"],
    "Bank Charges": ["fee", "charges", "atm withdrawal fee", "service charge",
                       "bank charge"],
}
DEFAULT_CATEGORY = "Other"

# Thresholds you can tune
DUPLICATE_WINDOW_DAYS = 1        # same amount+merchant within this many days = possible duplicate
SMALL_LEAK_THRESHOLD = 300       # single charges below this are "small" for leak detection
SMALL_LEAK_COUNT = 3             # 3+ small charges to the same merchant = a leak


# ----------------------------------------------------------------------
# 3. LOAD DATA
# ----------------------------------------------------------------------

def load_transactions():
    if USE_FILE:
        f = open(CSV_PATH, newline="", encoding="utf-8")
    else:
        f = io.StringIO(CSV_DATA.strip())

    reader = csv.DictReader(f)
    rows = []
    for r in reader:
        try:
            date = datetime.strptime(r["date"].strip(), "%Y-%m-%d")
            desc = r["description"].strip()
            amount = float(r["amount"].strip())
            rows.append({"date": date, "description": desc, "amount": amount})
        except Exception as e:
            print(f"Skipping bad row {r}: {e}")
    rows.sort(key=lambda x: x["date"])
    return rows


def categorize(description):
    desc_lower = description.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                return category
    return DEFAULT_CATEGORY


# ----------------------------------------------------------------------
# 4. ANALYSIS FUNCTIONS
# ----------------------------------------------------------------------

def monthly_totals(rows):
    totals = defaultdict(float)
    for r in rows:
        key = r["date"].strftime("%Y-%m")
        totals[key] += r["amount"]
    return dict(sorted(totals.items()))


def find_recurring(rows):
    """A merchant is 'recurring' if it appears in 2+ different months
    with similar (within 5%) amounts each time -- typical subscription behaviour."""
    by_merchant = defaultdict(list)
    for r in rows:
        by_merchant[r["description"]].append(r)

    recurring = {}
    for merchant, txns in by_merchant.items():
        months = set(t["date"].strftime("%Y-%m") for t in txns)
        amounts = [t["amount"] for t in txns]
        avg = sum(amounts) / len(amounts)
        similar = all(abs(a - avg) <= abs(avg) * 0.05 for a in amounts)
        if len(months) >= 2 and similar:
            recurring[merchant] = {"count": len(txns), "avg_amount": avg, "months": sorted(months)}

    # Also flag obvious subscription keywords even if only seen once so far,
    # since new subscriptions will only have one data point.
    for merchant, txns in by_merchant.items():
        if merchant in recurring:
            continue
        if categorize(merchant) == "Subscriptions":
            recurring[merchant] = {
                "count": len(txns),
                "avg_amount": sum(t["amount"] for t in txns) / len(txns),
                "months": sorted(set(t["date"].strftime("%Y-%m") for t in txns)),
                "note": "Flagged by keyword, not yet seen in 2+ months",
            }
    return recurring


def find_duplicates(rows):
    """Same merchant + same amount within DUPLICATE_WINDOW_DAYS days = likely duplicate."""
    duplicates = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            a, b = rows[i], rows[j]
            if a["description"] != b["description"]:
                continue
            if a["amount"] != b["amount"]:
                continue
            gap = abs((b["date"] - a["date"]).days)
            if gap <= DUPLICATE_WINDOW_DAYS:
                duplicates.append((a, b, gap))
    return duplicates


def repeated_merchants(rows):
    by_merchant = defaultdict(list)
    for r in rows:
        by_merchant[r["description"]].append(r["amount"])
    repeated = {m: {"count": len(v), "total": sum(v)}
                for m, v in by_merchant.items() if len(v) > 1}
    return dict(sorted(repeated.items(), key=lambda x: x[1]["total"]))


def top_categories(rows):
    totals = defaultdict(float)
    for r in rows:
        totals[categorize(r["description"])] += r["amount"]
    return dict(sorted(totals.items(), key=lambda x: x[1]))


def find_leaks(rows):
    """Small, frequent charges to the same merchant that quietly add up."""
    by_merchant = defaultdict(list)
    for r in rows:
        by_merchant[r["description"]].append(r["amount"])

    leaks = {}
    for merchant, amounts in by_merchant.items():
        small_ones = [a for a in amounts if abs(a) <= SMALL_LEAK_THRESHOLD]
        if len(small_ones) >= SMALL_LEAK_COUNT:
            leaks[merchant] = {"count": len(small_ones), "total": sum(small_ones)}
    return leaks


# ----------------------------------------------------------------------
# 5. REPORT
# ----------------------------------------------------------------------

def main():
    rows = load_transactions()
    if not rows:
        print("No valid transactions found.")
        return

    grand_total = sum(r["amount"] for r in rows)

    print("=" * 60)
    print("MONEY DETECTIVE REPORT")
    print("=" * 60)

    print(f"\nTransactions loaded: {len(rows)}")
    print(f"Calculated total spend: {grand_total:.2f}")
    print(f"Your baseline figure:   {BASELINE_TOTAL:.2f}")
    diff = grand_total - BASELINE_TOTAL
    if abs(diff) < 0.01:
        print("Match: your baseline matches the transaction total. ✔")
    else:
        print(f"Mismatch of {diff:.2f} -- some transactions may be missing "
              f"from this list, or your baseline needs updating.")

    print("\n--- 1. TOTAL SPENDING BY MONTH ---")
    for month, total in monthly_totals(rows).items():
        print(f"  {month}: {total:.2f}")

    print("\n--- 2. RECURRING CHARGES / SUBSCRIPTIONS ---")
    recurring = find_recurring(rows)
    if recurring:
        for merchant, info in recurring.items():
            note = f" ({info['note']})" if "note" in info else ""
            print(f"  {merchant}: {info['count']}x, avg {info['avg_amount']:.2f}, "
                  f"seen in {info['months']}{note}")
    else:
        print("  None detected yet.")

    print("\n--- 3. POSSIBLE DUPLICATE PAYMENTS ---")
    duplicates = find_duplicates(rows)
    if duplicates:
        for a, b, gap in duplicates:
            print(f"  {a['description']}: {a['amount']:.2f} on {a['date'].date()} "
                  f"and again on {b['date'].date()} ({gap} day(s) apart)")
    else:
        print("  None found.")

    print("\n--- 4. REPEATED PAYMENTS TO THE SAME MERCHANT ---")
    repeated = repeated_merchants(rows)
    if repeated:
        for merchant, info in repeated.items():
            print(f"  {merchant}: {info['count']}x, total {info['total']:.2f}")
    else:
        print("  No merchant appears more than once.")

    print("\n--- 5. TOP SPENDING CATEGORIES ---")
    for cat, total in top_categories(rows).items():
        print(f"  {cat}: {total:.2f}")

    print("\n--- 6. UNUSUAL SPENDING LEAKS ---")
    leaks = find_leaks(rows)
    if leaks:
        for merchant, info in leaks.items():
            print(f"  {merchant}: {info['count']} small charges, "
                  f"totaling {info['total']:.2f}")
    else:
        print("  No small recurring leaks detected.")

    print("\n" + "=" * 60)
    print("End of report.")
    print("=" * 60)


if __name__ == "__main__":
    main()
