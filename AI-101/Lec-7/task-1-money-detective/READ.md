# Task 1 — Money Detective

## Task Overview

In this task, I will analyze past transaction history to find hidden money leaks. The goal is not to create a new budget, but to study old transactions and identify recurring charges, forgotten subscriptions, duplicate payments, and repeated spending patterns.

## Files Included

```text
task-1-money-detective/
├── READ.md
└── sample_transactions.csv
```

## Sample Data

The `sample_transactions.csv` file contains dummy transaction data with three columns:

```text
date, description, amount
```

The data includes examples of:

- Monthly rent
- Grocery spending
- Food delivery
- Transport rides
- Utility bills
- Subscriptions
- Bank charges
- Possible duplicate payments

## Important Note

The CSV file contains dummy data only. I will replace it with my own real transaction history before running the final analysis.

Before using real data, I should remove sensitive details such as:

- Account number
- Card number
- CNIC or ID number
- Phone number
- Full private names
- Any confidential banking information

## Baseline Figure

To verify the script result, I need one known figure from my real statement.

Example:

```text
My total spending for June is Rs. 177,039.
```

I will compare the script result with my known total to check if the script is working correctly.

## What the Script Should Find

The final Python script should analyze the transaction file and find:

1. Total spending by month
2. Recurring charges or subscriptions
3. Possible forgotten subscriptions
4. Duplicate payments
5. Repeated payments to the same merchant
6. Top spending categories
7. Unusual spending leaks

## Example Findings from Dummy Data

The dummy data contains examples such as:

- Foodpanda appears twice on the same date, which may be a duplicate charge.
- Netflix appears multiple times, which may be a recurring subscription.
- Bank service charges repeat every month.
- Daraz appears twice on the same date in July, which may be another duplicate payment.
- Careem rides appear many times, which shows a repeated transport spending pattern.

## Verification Plan

I will verify at least two results manually:

1. Check the monthly total spending against my bank or wallet statement.
2. Check one duplicate or recurring transaction by comparing it with the original statement.

If these figures match, I can trust the remaining analysis more confidently.

## Learning Outcome

From this task, I will learn how AI can help analyze personal transaction history using a script. I will also learn how to verify AI-generated results manually before trusting them completely.

## Final Submission Statement

For the Money Detective task, I prepared transaction data with date, description, and amount columns. I used AI to help create a script that can detect recurring payments, forgotten subscriptions, duplicate charges, repeated merchants, and monthly spending totals. I verified the results with known figures from my statement before trusting the analysis.
