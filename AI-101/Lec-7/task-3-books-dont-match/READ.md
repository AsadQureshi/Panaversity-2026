# Task 3: The Books Don't Match

Reconciles a hand-counted expected total (trip dues collected from a
class group) against a messy digital transfer record with inconsistent
sender names, then names exactly who still needs follow-up.

## Files

- `sample_payments.csv` — the raw digital payment record, exactly as
  it would arrive from a transfer app: mixed casing, nicknames,
  initials, dots, no separators. Not cleaned up.
- `reconciler.py` — the script that applies the interpretation rules
  below and produces the gap + follow-up list.

## The scenario

20 classmates each owe 2,000 for a class trip. The expected total was
counted by hand before checking the digital transfer history.

**Expected total = 20 people x 2,000 = 40,000**

## My rules for interpreting ambiguous entries

1. **Nicknames, initials, and typos map to a known name** if there's
   only one member they could reasonably be — e.g. `"Ali K"`,
   `"hinaraza22"`, `"usman01"` all resolve to one specific person.
   These mappings are hand-built from knowing the group, not guessed
   by the script.
2. **A second transfer from someone already fully paid is not
   discarded** — it's added to their total and flagged as an
   overpayment for follow-up (could be a genuine mistake, a duplicate
   send, or covering someone else's dues — needs a human answer).
3. **Shared initials are never auto-resolved.** If a raw name like
   `"S Ahmed"` could belong to more than one member (here: Sana Ahmed
   *or* Salman Ahmed), it is deliberately left unmatched and listed as
   an ambiguous entry rather than guessed. Guessing wrong would hide
   a real gap.
4. **A member with zero matched payments is "missing," not "paid
   zero and forgotten."** They owe the full amount and go straight to
   the follow-up list.
5. **Partial payments reduce what's owed, they don't zero it out.**
   Someone who sent 1,500 of 2,000 still owes exactly 500 — not the
   full 2,000 and not nothing.

## How to run

```
python reconciler.py
```

Edit `MEMBERS`, `DUES_PER_PERSON`, `NAME_ALIASES`, and `AMBIGUOUS` at
the top of the script to match a real group and a real payment export.

## Result summary

| Check | Amount |
|---|---|
| Expected total (hand-counted) | 40,000 |
| Raw digital record total (everything, including unresolved) | 40,500 |
| Confidently matched & settled | 39,500 |
| Sitting in ambiguous entries | 1,000 |
| **Gap still unaccounted for** | **500** |

**Follow-up list:**
- **Rabia Noor** — missing entirely, owes the full 2,000
- **Bilal Tariq** — underpaid, owes 500 more
- **Ali Khan** — overpaid by 2,000 (sent twice — confirm why, refund or credit next trip)
- **"S Ahmed" (1,000, June 12)** — ambiguous sender, could be Sana Ahmed or Salman Ahmed — needs to be asked directly

The raw digital total (40,500) looked *higher* than the expected total
(40,000) at a glance — which would wrongly suggest everything was
covered. Only after applying the rules does the real gap (missing
person, underpayment, and an unresolved ambiguous entry) become
visible.
