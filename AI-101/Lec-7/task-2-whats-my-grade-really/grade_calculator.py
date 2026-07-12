"""
WHAT'S MY GRADE, REALLY
------------------------
Calculates your real current grade from your actual scores and your
teacher's grading policy, including dropped-score rules, and tells you
exactly what you need on the final exam to hit your target grade.

HOW TO USE:
  - Edit the SCORES section with your real numbers.
  - Edit the POLICY section to match your teacher's rules (weights,
    how many lowest scores to drop from each category, target grade).
  - Run: python grade_calculator.py
"""

# ----------------------------------------------------------------------
# 1. YOUR SCORES -- edit these
#    Each score is written as (points_earned, points_possible).
#    If something isn't graded yet, leave it out of the list.
# ----------------------------------------------------------------------

ASSIGNMENTS = {
    "A1": (85, 100),
    "A2": (90, 100),
    "A3": (70, 100),
    "A4": (95, 100),
}

QUIZZES = {
    "Q1": (8, 10),
    "Q2": (7, 10),
    "Q3": (10, 10),
    "Q4": (6, 10),
}

MIDTERM = {
    "Midterm": (78, 100),
}

FINAL_EXAM_SCORE = None   # set to (points_earned, points_possible) once taken; leave None if not taken

# ----------------------------------------------------------------------
# 2. GRADING POLICY -- edit to match your teacher's rules
# ----------------------------------------------------------------------

WEIGHTS = {
    "Assignments": 0.30,
    "Quizzes": 0.20,
    "Midterm": 0.20,
    "Final Exam": 0.30,
}

DROP_LOWEST = {
    "Assignments": 0,   # how many lowest scores to drop in this category
    "Quizzes": 1,        # teacher drops the lowest quiz
    "Midterm": 0,
    "Final Exam": 0,
}

TARGET_GRADE = 85.0   # percent

assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-6, "Weights must add up to 100%."


# ----------------------------------------------------------------------
# 3. CORE LOGIC
# ----------------------------------------------------------------------

def category_average(scores_dict, drop_lowest_count):
    """Turns raw scores into percentages, drops the lowest N, and averages the rest."""
    if not scores_dict:
        return None, []

    percentages = []
    for name, (earned, possible) in scores_dict.items():
        pct = (earned / possible) * 100
        percentages.append((name, pct))

    # Sort lowest first so we know exactly what's being dropped
    percentages_sorted = sorted(percentages, key=lambda x: x[1])
    dropped = percentages_sorted[:drop_lowest_count]
    kept = percentages_sorted[drop_lowest_count:]

    if not kept:
        return None, dropped

    avg = sum(pct for _, pct in kept) / len(kept)
    return avg, dropped


def main():
    print("=" * 60)
    print("WHAT'S MY GRADE, REALLY -- REPORT")
    print("=" * 60)

    category_data = {
        "Assignments": ASSIGNMENTS,
        "Quizzes": QUIZZES,
        "Midterm": MIDTERM,
        "Final Exam": {"Final Exam": FINAL_EXAM_SCORE} if FINAL_EXAM_SCORE else {},
    }

    averages = {}
    print("\n--- 1. CATEGORY AVERAGES (with drop rules applied) ---")
    for category, scores in category_data.items():
        drop_n = DROP_LOWEST.get(category, 0)
        avg, dropped = category_average(scores, drop_n)
        averages[category] = avg

        if avg is None:
            print(f"  {category}: no scores yet")
            continue

        detail = ", ".join(f"{name}={pct:.1f}%" for name, (earned, possible) in scores.items()
                            for pct in [earned / possible * 100])
        print(f"  {category}: [{detail}]")
        if dropped:
            dropped_str = ", ".join(f"{name} ({pct:.1f}%)" for name, pct in dropped)
            print(f"    -> Dropped lowest {drop_n}: {dropped_str}")
        print(f"    -> Category average: {avg:.2f}%")

    # ------------------------------------------------------------------
    # 2 & 3. WEIGHTED GRADE SO FAR (categories with real scores only)
    # ------------------------------------------------------------------
    print("\n--- 2. APPLYING WEIGHTS ---")
    graded_weight_used = 0.0
    weighted_points_so_far = 0.0
    for category, avg in averages.items():
        weight = WEIGHTS[category]
        if avg is None:
            print(f"  {category}: {weight*100:.0f}% weight -- not graded yet, excluded from current total")
            continue
        contribution = avg * weight
        weighted_points_so_far += contribution
        graded_weight_used += weight
        print(f"  {category}: {avg:.2f}% x {weight*100:.0f}% weight = {contribution:.2f} points")

    print("\n--- 3. CURRENT WEIGHTED GRADE ---")
    if graded_weight_used > 0:
        current_grade_of_graded_only = weighted_points_so_far / graded_weight_used
        print(f"  Weighted points earned so far (out of {graded_weight_used*100:.0f}% of total): "
              f"{weighted_points_so_far:.2f}")
        print(f"  If final exam weren't required at all, your grade on graded work alone "
              f"would be: {current_grade_of_graded_only:.2f}%")
    else:
        print("  No graded categories yet.")

    # ------------------------------------------------------------------
    # 4. WHAT YOU NEED ON THE FINAL
    # ------------------------------------------------------------------
    print(f"\n--- 4. FINAL EXAM SCORE NEEDED FOR {TARGET_GRADE:.1f}% TARGET ---")
    final_weight = WEIGHTS["Final Exam"]

    if averages["Final Exam"] is not None:
        overall = weighted_points_so_far  # already includes final since it's graded
        print(f"  Final exam already taken. Your overall weighted grade is: {overall:.2f}%")
        if overall >= TARGET_GRADE:
            print(f"  You met your target of {TARGET_GRADE:.1f}%. ✔")
        else:
            print(f"  You are {TARGET_GRADE - overall:.2f} points short of your target.")
    else:
        # weighted_points_so_far currently excludes the final (it wasn't graded)
        remaining_needed = TARGET_GRADE - weighted_points_so_far
        needed_final_pct = remaining_needed / final_weight

        print(f"  Points needed from the final exam category: {remaining_needed:.2f} "
              f"(out of {final_weight*100:.0f}% weight)")
        print(f"  Required final exam score: {needed_final_pct:.2f}%")

        if needed_final_pct > 100:
            print(f"  This is IMPOSSIBLE with a normal 0-100 exam -- even a perfect 100% "
                  f"final would leave you at "
                  f"{weighted_points_so_far + 100 * final_weight:.2f}%, "
                  f"below your {TARGET_GRADE:.1f}% target.")
        elif needed_final_pct < 0:
            print(f"  You have already secured your target grade regardless of the final exam score.")
        else:
            print(f"  You need at least {needed_final_pct:.2f}% on the final exam "
                  f"to reach your {TARGET_GRADE:.1f}% target.")

    print("\n" + "=" * 60)
    print("End of report.")
    print("=" * 60)


if __name__ == "__main__":
    main()
