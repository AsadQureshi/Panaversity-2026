# Task 2: What's My Grade, Really

Calculates a real current grade from actual scores and a teacher's
grading policy — including dropped-score rules — and works out the
exact final exam score needed to hit a target grade.

## Files

- `sample_scores.csv` — the real scores this task is based on, in
  `category,item,earned,possible` format. The Final Exam row is left
  blank because it hasn't been taken yet.
- `grade_calculator.py` — the script itself (see below; add it to this
  folder if it isn't already here).

## My scores

**Assignments**
- A1 = 85/100
- A2 = 90/100
- A3 = 70/100
- A4 = 95/100

**Quizzes**
- Q1 = 8/10
- Q2 = 7/10
- Q3 = 10/10
- Q4 = 6/10

**Midterm**
- Midterm = 78/100

**Final Exam**
- Not taken yet

## Grading policy

- Assignments = 30%
- Quizzes = 20%
- Midterm = 20%
- Final Exam = 30%
- Rule: drop the lowest quiz score
- No bonus marks
- Final exam is required
- Target grade = 85%

## How to run

```
python grade_calculator.py
```

Edit the `SCORES` and `POLICY` sections at the top of the script to
update numbers as new grades come in.

## Result summary

| Category     | Average | Weight | Weighted Points |
|--------------|---------|--------|------------------|
| Assignments  | 85.00%  | 30%    | 25.50            |
| Quizzes      | 83.33% (Q4 dropped) | 20% | 16.67   |
| Midterm      | 78.00%  | 20%    | 15.60            |
| **Total so far** | | **70%** | **57.77 / 70** |

**Final exam score needed for an 85% target: 90.78%**
