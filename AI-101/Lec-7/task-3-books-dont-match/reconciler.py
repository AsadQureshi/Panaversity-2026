"""
THE BOOKS DON'T MATCH
-----------------------
Reconciles a hand-counted expected total (e.g. trip dues) against a
messy digital payment record with inconsistent, abbreviated, or
ambiguous sender names.

HOW TO USE:
  - Set EXPECTED_TOTAL and MEMBERS to your real hand-counted numbers.
  - Set NAME_ALIASES to your own rules for "this raw name really means
    this person."
  - Set AMBIGUOUS to any raw names you are NOT confident about --
    these are deliberately left unresolved so the script flags them
    for follow-up instead of guessing.
  - Point PAYMENTS_CSV at your real payment export, exactly as
    received (don't clean it up first).
  - Run: python reconciler.py
"""

import csv
from collections import defaultdict

# ----------------------------------------------------------------------
# 1. THE HAND-COUNTED TRUTH -- edit this
# ----------------------------------------------------------------------

DUES_PER_PERSON = 2000

MEMBERS = [
    "Ali Khan", "Sara Noon", "Bilal Tariq", "Hina Raza", "Omar Farooq",
    "Zara Qureshi", "Ahmed Siddiqui", "Mahnoor Ali", "Usman Tariq",
    "Ayesha Khan", "Hassan Raza", "Sana Ahmed", "Farhan Khalid",
    "Nida Fatima", "Kamran Ali", "Iqra Siddiqui", "Salman Ahmed",
    "Mehak Zafar", "Talha Mir", "Rabia Noor",
]

EXPECTED_TOTAL = len(MEMBERS) * DUES_PER_PERSON   # 20 people x 2000 = 40,000

# ----------------------------------------------------------------------
# 2. YOUR PERSONAL RULES FOR INTERPRETING MESSY NAMES
#    Left side: how the raw text looks (any case/spacing/punctuation --
#    it gets normalized before matching). Right side: who it really is.
# ----------------------------------------------------------------------

PAYMENTS_CSV = "sample_payments.csv"

NAME_ALIASES = {
    "alik":        "Ali Khan",
    "alikhan99":   "Ali Khan",          # same person, a second/duplicate transfer
    "saranoon":    "Sara Noon",
    "btariq":      "Bilal Tariq",
    "hinaraza22":  "Hina Raza",
    "omar":        "Omar Farooq",
    "zaraq":       "Zara Qureshi",
    "ahmeds":      "Ahmed Siddiqui",
    "mahnoor":     "Mahnoor Ali",
    "usman01":     "Usman Tariq",
    "ayeshak":     "Ayesha Khan",
    "hassan":      "Hassan Raza",
    "sana":        "Sana Ahmed",
    "farhank":     "Farhan Khalid",
    "nida":        "Nida Fatima",
    "kamran":      "Kamran Ali",
    "iqra":        "Iqra Siddiqui",
    "salman":      "Salman Ahmed",
    "mehak":       "Mehak Zafar",
    "talha":       "Talha Mir",
}

# Raw names that are genuinely ambiguous -- deliberately NOT auto-matched.
# List the possible candidates so a human can decide. Rule: never guess
# on a shared initial when more than one member could match.
AMBIGUOUS = {
    "sahmed": ["Sana Ahmed", "Salman Ahmed"],   # "S Ahmed" could be either
}


def normalize(raw_name):
    return "".join(ch for ch in raw_name.lower() if ch.isalnum())


# ----------------------------------------------------------------------
# 3. LOAD PAYMENTS EXACTLY AS RECEIVED
# ----------------------------------------------------------------------

def load_payments(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                "date": r["date"].strip(),
                "sender_raw": r["sender_raw"].strip(),
                "amount": float(r["amount"].strip()),
                "memo": r.get("memo", "").strip(),
            })
    return rows


# ----------------------------------------------------------------------
# 4. MATCH EACH PAYMENT TO A PERSON, OR FLAG IT
# ----------------------------------------------------------------------

def match_payments(payments):
    matched = defaultdict(list)     # canonical name -> list of payments
    ambiguous_flagged = []          # payments matching a known-ambiguous pattern
    unmatched = []                  # payments matching nothing at all

    for p in payments:
        key = normalize(p["sender_raw"])
        if key in NAME_ALIASES:
            matched[NAME_ALIASES[key]].append(p)
        elif key in AMBIGUOUS:
            ambiguous_flagged.append((p, AMBIGUOUS[key]))
        else:
            unmatched.append(p)

    return matched, ambiguous_flagged, unmatched


# ----------------------------------------------------------------------
# 5. REPORT
# ----------------------------------------------------------------------

def main():
    payments = load_payments(PAYMENTS_CSV)
    matched, ambiguous_flagged, unmatched = match_payments(payments)

    print("=" * 65)
    print("THE BOOKS DON'T MATCH -- RECONCILIATION REPORT")
    print("=" * 65)

    print(f"\nExpected total (hand-counted): {EXPECTED_TOTAL:,.0f}"
          f"  ({len(MEMBERS)} people x {DUES_PER_PERSON:,.0f})")

    raw_digital_total = sum(p["amount"] for p in payments)
    print(f"Raw digital record total (everything, unmatched included): "
          f"{raw_digital_total:,.0f}")

    # --- Per-member reconciliation -------------------------------------------------
    print("\n--- PER-MEMBER STATUS ---")
    confidently_matched_total = 0.0
    settled, underpaid, overpaid, missing = [], [], [], []

    for member in MEMBERS:
        paid = sum(p["amount"] for p in matched.get(member, []))
        confidently_matched_total += paid
        count = len(matched.get(member, []))

        if paid == 0:
            missing.append(member)
            print(f"  {member}: NO PAYMENT FOUND -- owes full {DUES_PER_PERSON:,.0f}")
        elif paid < DUES_PER_PERSON:
            shortfall = DUES_PER_PERSON - paid
            underpaid.append((member, shortfall, paid))
            print(f"  {member}: paid {paid:,.0f} across {count} transfer(s) "
                  f"-- short by {shortfall:,.0f}")
        elif paid == DUES_PER_PERSON:
            settled.append(member)
            print(f"  {member}: paid {paid:,.0f} -- settled")
        else:
            extra = paid - DUES_PER_PERSON
            overpaid.append((member, extra, paid))
            print(f"  {member}: paid {paid:,.0f} across {count} transfer(s) "
                  f"-- OVERPAID by {extra:,.0f}, needs follow-up")

    # --- Ambiguous entries -----------------------------------------------------------
    print("\n--- AMBIGUOUS ENTRIES (not auto-assigned, needs a human decision) ---")
    ambiguous_total = 0.0
    if ambiguous_flagged:
        for p, candidates in ambiguous_flagged:
            ambiguous_total += p["amount"]
            print(f"  {p['date']}: \"{p['sender_raw']}\" paid {p['amount']:,.0f} "
                  f"-- could be: {', '.join(candidates)}")
    else:
        print("  None.")

    # --- Completely unmatched entries -------------------------------------------------
    print("\n--- UNMATCHED ENTRIES (no rule covers this sender at all) ---")
    unmatched_total = 0.0
    if unmatched:
        for p in unmatched:
            unmatched_total += p["amount"]
            print(f"  {p['date']}: \"{p['sender_raw']}\" paid {p['amount']:,.0f} "
                  f"-- add a NAME_ALIASES rule or investigate")
    else:
        print("  None.")

    # --- The gap -----------------------------------------------------------------------
    print("\n--- THE GAP ---")
    print(f"  Expected total:                {EXPECTED_TOTAL:,.0f}")
    print(f"  Confidently matched & settled: {confidently_matched_total:,.0f}")
    print(f"  Sitting in ambiguous entries:  {ambiguous_total:,.0f}")
    print(f"  Sitting in unmatched entries:  {unmatched_total:,.0f}")
    gap = EXPECTED_TOTAL - confidently_matched_total
    print(f"  Gap still unaccounted for:     {gap:,.0f}")

    # --- Follow-up list --------------------------------------------------------------
    print("\n--- WHO TO FOLLOW UP WITH ---")
    if missing:
        print("  Missing entirely:")
        for m in missing:
            print(f"    - {m} (owes {DUES_PER_PERSON:,.0f})")
    if underpaid:
        print("  Underpaid:")
        for name, shortfall, paid in underpaid:
            print(f"    - {name} (paid {paid:,.0f}, owes {shortfall:,.0f} more)")
    if overpaid:
        print("  Overpaid (confirm why, possibly refund or credit next trip):")
        for name, extra, paid in overpaid:
            print(f"    - {name} (paid {paid:,.0f}, {extra:,.0f} extra)")
    if ambiguous_flagged:
        print("  Ambiguous senders needing identification:")
        for p, candidates in ambiguous_flagged:
            print(f"    - \"{p['sender_raw']}\" ({p['amount']:,.0f} on {p['date']}) "
                  f"-> ask: {' or '.join(candidates)}?")
    if unmatched:
        print("  Totally unrecognized senders:")
        for p in unmatched:
            print(f"    - \"{p['sender_raw']}\" ({p['amount']:,.0f} on {p['date']})")

    if not (missing or underpaid or overpaid or ambiguous_flagged or unmatched):
        print("  Nothing outstanding -- the books match. ✔")

    print("\n" + "=" * 65)
    print("End of report.")
    print("=" * 65)


if __name__ == "__main__":
    main()
